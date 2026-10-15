from app.services.rag_service import RAGService

rag = RAGService()

questions = [
    "What are the symptoms of diabetes?",
    "Quels sont les symptômes de l'hypertension ?",
    "Quels sont les signes de la dépression ?",
    "Qu'est-ce que la maladie cœliaque ?",
    "Quels aliments privilégier au quotidien ?",
]

for question in questions:

    print(f"\n{'='*60}")
    print("Question:", question)

    results = rag.search(question, debug=True)

    print(f"\n===== SEARCH RESULTS ({len(results)}) =====\n")

    for i, document in enumerate(results):
        print(f"--- Result {i + 1} ---")
        print(document.page_content[:500])
        print("\nMetadata:", document.metadata)
        print()