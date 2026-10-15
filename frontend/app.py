import streamlit as st
import requests
import time
from datetime import datetime

from backend.app.services.auth_service import AuthService
from backend.app.services.conversation_service import ConversationService

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="Assistant IA Santé",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000"

auth_service = AuthService()
conversation_service = ConversationService()

SYSTEM_PROMPT = (
    "You are a helpful healthcare assistant covering multiple health topics "
    "(diabetes, hypertension, nutrition, mental health, and more). "
    "Answer questions using the provided medical context."
)

# ============================================================
# CSS PERSONNALISÉ
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { padding-top: 0.5rem; }

    .header-container {
        padding: 24px 28px;
        border-radius: 16px;
        background: linear-gradient(135deg, #0f766e 0%, #0891b2 100%);
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(8, 145, 178, 0.25);
    }

    .title { font-size: 32px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
    .subtitle { font-size: 15px; color: #e0f2fe; font-weight: 400; }

    .info-card {
        padding: 18px;
        border-radius: 12px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        height: 100%;
        transition: box-shadow 0.2s ease;
    }
    .info-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
    .info-title { font-size: 15px; font-weight: 600; margin-bottom: 4px; color: #0f172a; }
    .info-text { font-size: 13px; color: #64748b; line-height: 1.5; }

    .disclaimer {
        padding: 14px 16px;
        border-radius: 10px;
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a3412;
        font-size: 12.5px;
        margin-top: 24px;
        line-height: 1.5;
    }

    .sidebar-title { font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
    .sidebar-text { color: #64748b; font-size: 13.5px; line-height: 1.5; }

    .status-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12.5px;
        font-weight: 600;
    }
    .status-online { background-color: #dcfce7; color: #15803d; }
    .status-offline { background-color: #fee2e2; color: #b91c1c; }

    .timestamp { font-size: 11px; color: #94a3b8; margin-top: -6px; margin-bottom: 8px; }
    .response-meta { font-size: 11.5px; color: #94a3b8; margin-top: 6px; }

    .topic-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 600;
        background-color: #e0f2fe;
        color: #0369a1;
        margin: 3px 4px 3px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# AUTHENTIFICATION
# ============================================================

def login_screen():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; margin-top: 60px; margin-bottom: 24px;">
                <div style="font-size: 40px;">🩺</div>
                <div style="font-size: 26px; font-weight: 700; color: #0f172a;">Assistant IA Santé</div>
                <div style="font-size: 14px; color: #64748b;">Connectez-vous pour accéder à l'assistant</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_login, tab_signup = st.tabs(["Connexion", "Créer un compte"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Nom d'utilisateur")
                password = st.text_input("Mot de passe", type="password")
                submitted = st.form_submit_button("Se connecter", use_container_width=True)

                if submitted:
                    if auth_service.check_credentials(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

        with tab_signup:
            with st.form("signup_form"):
                new_username = st.text_input("Choisir un nom d'utilisateur")
                new_password = st.text_input("Choisir un mot de passe", type="password")
                confirm_password = st.text_input("Confirmer le mot de passe", type="password")
                signup_submitted = st.form_submit_button("Créer mon compte", use_container_width=True)

                if signup_submitted:
                    if new_password != confirm_password:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        success, message = auth_service.register(new_username, new_password)
                        if success:
                            st.success(message + " Vous pouvez maintenant vous connecter.")
                        else:
                            st.error(message)


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_screen()
    st.stop()

# ============================================================
# ÉTAT DE SESSION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "confirm_new" not in st.session_state:
    st.session_state.confirm_new = False

# ============================================================
# BARRE LATÉRALE
# ============================================================

with st.sidebar:

    st.markdown('<div class="sidebar-title">🩺 Assistant Santé</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-text">Assistant IA pour des informations générales de santé, '
        'propulsé par Mistral 7B, RAG et une base de connaissances médicales multi-thèmes.</div>',
        unsafe_allow_html=True
    )

    st.divider()
    st.markdown(f"👤 Connecté : **{st.session_state.username}**")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pop("username", None)
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

    st.divider()
    st.markdown("### 🔌 État du système")

    backend_online = False
    try:
        health_response = requests.get(f"{BACKEND_URL}/docs", timeout=2)
        backend_online = health_response.status_code == 200
    except requests.exceptions.RequestException:
        backend_online = False

    if backend_online:
        st.markdown('<span class="status-pill status-online">🟢 Backend en ligne</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill status-offline">🔴 Backend hors ligne</span>', unsafe_allow_html=True)

    st.divider()

    # Nouvelle conversation : sauvegarde AVANT de repartir à zéro
    if st.session_state.confirm_new:
        st.warning("Sauvegarder la conversation actuelle et en démarrer une nouvelle ?")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("✅ Oui", use_container_width=True, key="new_yes"):
                conversation_service.save_conversation(
                    st.session_state.username,
                    st.session_state.messages
                )
                st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                st.session_state.confirm_new = False
                st.rerun()
        with col_no:
            if st.button("❌ Annuler", use_container_width=True, key="new_no"):
                st.session_state.confirm_new = False
                st.rerun()
    else:
        if st.button("💬 Nouvelle conversation", use_container_width=True):
            st.session_state.confirm_new = True
            st.rerun()

    st.divider()
    st.markdown("### 📚 Base de connaissances")
    st.markdown(
        '<span class="topic-tag">Diabète</span>'
        '<span class="topic-tag">Hypertension</span>'
        '<span class="topic-tag">Dépression</span>'
        '<span class="topic-tag">Maladie cœliaque</span>'
        '<span class="topic-tag">Nutrition</span>'
        '<span class="topic-tag">Obésité</span>'
        '<span class="topic-tag">Insuffisance cardiaque</span>',
        unsafe_allow_html=True
    )

    st.divider()
    st.markdown("### 🕑 Conversations précédentes")

    saved_conversations = conversation_service.get_conversations(st.session_state.username)

    if not saved_conversations:
        st.caption("Aucune conversation sauvegardée.")
    else:
        for conv in saved_conversations[:5]:
            col_title, col_delete = st.columns([0.85, 0.15])
            with col_title:
                if st.button(f"📄 {conv['title']}", key=f"load_{conv['id']}", use_container_width=True):
                    st.session_state.messages = (
                        [{"role": "system", "content": SYSTEM_PROMPT}] + conv["messages"]
                    )
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"del_{conv['id']}"):
                    conversation_service.delete_conversation(conv["id"], st.session_state.username)
                    st.rerun()

    st.divider()
    st.markdown("### 💡 Exemples de questions")
    example_questions = [
        "Qu'est-ce que le diabète ?",
        "Quels sont les symptômes de l'hypertension ?",
        "Quels sont les signes de la dépression ?",
        "Qu'est-ce que la maladie cœliaque ?",
        "Quels aliments privilégier au quotidien ?",
    ]
    for eq in example_questions:
        if st.button(eq, key=f"ex_{eq}", use_container_width=True):
            st.session_state["pending_question"] = eq

    st.divider()

    transcript = "\n\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in st.session_state.messages if m["role"] != "system"
    )
    st.download_button(
        "⬇️ Exporter la conversation",
        data=transcript if transcript else "Aucune conversation pour le moment.",
        file_name=f"conversation_sante_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        use_container_width=True
    )

# ============================================================
# EN-TÊTE PRINCIPAL
# ============================================================

st.markdown(
    """
    <div class="header-container">
        <div class="title">🩺 Assistant IA Santé</div>
        <div class="subtitle">Votre assistant intelligent pour des informations générales de santé</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# CARTES D'INFORMATION
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """<div class="info-card"><div class="info-title">🤖 Mistral 7B</div>
        <div class="info-text">Modèle de langage local utilisé pour générer les réponses.</div></div>""",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """<div class="info-card"><div class="info-title">📚 RAG</div>
        <div class="info-text">Recherche les informations pertinentes dans plusieurs guides de santé.</div></div>""",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """<div class="info-card"><div class="info-title">🗄️ ChromaDB</div>
        <div class="info-text">Stocke les embeddings des documents pour la recherche sémantique.</div></div>""",
        unsafe_allow_html=True
    )

st.divider()

# ============================================================
# MESSAGE DE BIENVENUE
# ============================================================

if len(st.session_state.messages) == 1:
    st.markdown("### 👋 Bienvenue !")
    st.write(
        "Posez-moi une question de santé. Je vais chercher dans la base de connaissances "
        "médicales et utiliser les informations trouvées pour générer une réponse."
    )

# ============================================================
# AFFICHAGE DE L'HISTORIQUE DE CHAT
# ============================================================

for i, message in enumerate(st.session_state.messages):
    if message["role"] == "system":
        continue

    avatar = "🧑" if message["role"] == "user" else "🩺"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "timestamp" in message:
            st.markdown(f'<div class="timestamp">{message["timestamp"]}</div>', unsafe_allow_html=True)
        if message["role"] == "assistant" and "elapsed" in message:
            st.markdown(
                f'<div class="response-meta">⏱️ Généré en {message["elapsed"]:.1f}s</div>',
                unsafe_allow_html=True
            )

# ============================================================
# SAISIE UTILISATEUR
# ============================================================

question = st.chat_input("Posez votre question de santé...")

if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

# ============================================================
# TRAITEMENT DE LA QUESTION
# ============================================================

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("🔎 Recherche dans la base de connaissances médicales..."):
            start = time.time()
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"messages": st.session_state.messages},
                    timeout=180
                )
                elapsed = time.time() - start

                if response.status_code == 200:
                    answer = response.json()["response"]
                    st.markdown(answer)
                    st.markdown(
                        f'<div class="response-meta">⏱️ Généré en {elapsed:.1f}s</div>',
                        unsafe_allow_html=True
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "elapsed": elapsed
                    })
                else:
                    st.error(f"Erreur du backend : {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Impossible de se connecter au backend FastAPI. Vérifiez qu'Uvicorn est lancé.")
            except requests.exceptions.Timeout:
                st.error("⏳ La réponse a pris trop de temps. Mistral est peut-être encore en train de générer la réponse.")
            except Exception as e:
                st.error(f"Erreur inattendue : {str(e)}")

# ============================================================
# AVERTISSEMENT MÉDICAL
# ============================================================

st.markdown(
    """
    <div class="disclaimer">
        ⚠️ <b>Avertissement médical :</b> Cet assistant IA fournit des informations éducatives basées sur
        sa base de connaissances médicales. Il ne remplace pas un médecin, un diagnostic, ou un avis médical professionnel.
    </div>
    """,
    unsafe_allow_html=True
)