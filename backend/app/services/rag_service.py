from pathlib import Path

import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sentence_transformers import CrossEncoder

# Racine du projet = 3 niveaux au-dessus de rag_service.py
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class RAGService:

    def __init__(self):
        self.documents_dir = PROJECT_ROOT / "data" / "documents"
        self.vector_db_path = str(PROJECT_ROOT / "data" / "chroma_db")

        # Modèle multilingue, plus adapté que MiniLM pour du contenu FR
        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-small"
        )

        # Reranker multilingue : gère la comparaison question EN / document FR
        self.reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        self.vectorstore = None
        self.initialize()

    # -------------------------------------------------
    # Indexation
    # -------------------------------------------------

    def initialize(self):
        if Path(self.vector_db_path).exists():
            print("Base vectorielle existante détectée, chargement...")
            self.vectorstore = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            return

        all_chunks = self._load_and_split_documents()

        self.vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=self.vector_db_path
        )
        print(f"Base vectorielle créée avec {len(all_chunks)} chunks au total")

    def _load_and_split_documents(self):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )

        all_chunks = []

        pdf_files = sorted(self.documents_dir.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(
                f"Aucun PDF trouvé dans {self.documents_dir}. "
                "Ajoute au moins un document santé avant de lancer l'indexation."
            )

        print(f"{len(pdf_files)} PDF détectés : {[f.name for f in pdf_files]}")

        for pdf_file in pdf_files:
            print(f"Chargement de {pdf_file.name}...")
            try:
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()
            except Exception as e:
                print(f"  ERREUR lors du chargement de {pdf_file.name}: {e}")
                continue

            if not documents:
                print(f"  ATTENTION: {pdf_file.name} n'a produit aucun contenu (PDF scanné ?)")
                continue

            chunks = splitter.split_documents(documents)

            for chunk in chunks:
                chunk.metadata["topic"] = pdf_file.stem
                chunk.metadata["source_file"] = pdf_file.name
                # Préfixe requis par les modèles e5 pour bien encoder les documents
                chunk.page_content = f"passage: {chunk.page_content}"

            all_chunks.extend(chunks)
            print(f"  -> {len(chunks)} chunks")

        return all_chunks

    def rebuild_index(self):
        """Force la reconstruction complète de l'index (à appeler après ajout/suppression de PDF)."""
        import shutil
        if Path(self.vector_db_path).exists():
            shutil.rmtree(self.vector_db_path)
            print("Ancienne base vectorielle supprimée.")

        all_chunks = self._load_and_split_documents()
        self.vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=self.vector_db_path
        )
        print(f"Index reconstruit avec {len(all_chunks)} chunks au total")

    def add_document(self, pdf_path: str):
        """Ajoute un seul nouveau PDF à une base déjà existante, sans tout reconstruire."""
        pdf_file = Path(pdf_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

        loader = PyPDFLoader(str(pdf_file))
        documents = loader.load()
        chunks = splitter.split_documents(documents)

        for chunk in chunks:
            chunk.metadata["topic"] = pdf_file.stem
            chunk.metadata["source_file"] = pdf_file.name
            chunk.page_content = f"passage: {chunk.page_content}"

        self.vectorstore.add_documents(chunks)
        print(f"{len(chunks)} chunks ajoutés depuis {pdf_file.name}")

    # -------------------------------------------------
    # Recherche
    # -------------------------------------------------

    def search(self, question: str, k: int = 4, fetch_k: int = 15,
               score_threshold: float = 0.4, debug: bool = False):
        """
        1. Récupère fetch_k candidats par similarité vectorielle (recall large)
        2. Reranke ces candidats avec un cross-encoder multilingue (précision)
        3. Normalise les scores (logits -> probabilité via sigmoïde)
        4. Filtre par score de pertinence et garde les k meilleurs
        """

        # Préfixe requis par les modèles e5 pour bien encoder les questions
        prefixed_question = f"query: {question}"

        candidates = self.vectorstore.similarity_search(prefixed_question, k=fetch_k)

        if not candidates:
            return []

        pairs = [(question, doc.page_content) for doc in candidates]
        raw_scores = self.reranker.predict(pairs)

        scores = 1 / (1 + np.exp(-raw_scores))

        scored_docs = sorted(
            zip(candidates, scores),
            key=lambda x: x[1],
            reverse=True
        )

        if debug:
            print(f"\n--- Scores de reranking pour: '{question}' ---")
            for doc, score in scored_docs[:8]:
                topic = doc.metadata.get("topic", "?")
                print(f"  [{score:.3f}] ({topic}) {doc.page_content[:80]}...")

        relevant = [doc for doc, score in scored_docs if score >= score_threshold]

        return relevant[:k]