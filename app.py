import os

import streamlit as st

from asistente import responder, responder_sin_api

st.set_page_config(
    page_title="BioAsistente IA - Biodescodificación",
    page_icon="",
    layout="wide",
)

ESTILOS = """
<style>
    .stApp { background: linear-gradient(135deg, #f5f0e8 0%, #e8f0e8 100%); }
    .main > div { padding: 0 2rem; }
    .stChatMessage { border-radius: 12px; padding: 8px; }
    h1, h2, h3 { color: #2d5a3a !important; }
    .stSidebar { background: #f0f5f0; }
    .stAlert { border-radius: 8px; }
</style>
"""
st.markdown(ESTILOS, unsafe_allow_html=True)

st.title(" BioAsistente IA")
st.markdown(
    "**Asistente de orientación personalizada en Biodescodificación**"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ Configuración")

    modo = st.radio(
        "Modo de conexión",
        ["Automático", "OpenAI", "Ollama (local)", "Sin API (solo KB)"],
        index=0,
        help=(
            "Automático: usa OpenAI si hay API key, si no Ollama si está disponible, "
            "si no usa solo la base de conocimiento local."
        ),
    )

    with st.expander(" Configuración OpenAI", expanded=False):
        os.environ["OPENAI_API_KEY"] = st.text_input(
            "API Key de OpenAI",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
        )
        os.environ["OPENAI_MODEL"] = st.text_input(
            "Modelo OpenAI",
            value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )

    with st.expander(" Configuración Ollama", expanded=False):
        os.environ["OLLAMA_URL"] = st.text_input(
            "URL de Ollama",
            value=os.getenv("OLLAMA_URL", "http://localhost:11434/v1"),
        )
        os.environ["OLLAMA_MODEL"] = st.text_input(
            "Modelo Ollama",
            value=os.getenv("OLLAMA_MODEL", "llama3"),
        )

    st.markdown("---")
    st.markdown("###  Conexiones")

    gh_token = os.getenv("GITHUB_TOKEN", "")
    if gh_token:
        st.success(" GitHub token configurado")
    else:
        st.warning(" GitHub token no configurado")

    st.markdown("---")
    st.markdown("###  Acerca de")
    st.markdown(
        "**BioAsistente IA** es una herramienta de orientación "
        "basada en los principios de la Biodescodificación."
    )
    st.info(
        " La biodescodificación es un enfoque complementario "
        "que no reemplaza la atención médica profesional. "
        "Si tienes un síntoma físico, consulta primero con un médico."
    )

    if st.button(" Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

if prompt := st.chat_input("Describe tu síntoma, emoción o consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la base de conocimiento..."):
            api_key = os.getenv("OPENAI_API_KEY", "")
            use_ollama = modo == "Ollama (local)"
            use_api = modo == "OpenAI"
            auto = modo == "Automático"
            only_kb = modo == "Sin API (solo KB)"

            if only_kb:
                respuesta = responder_sin_api(st.session_state.messages)
            elif use_ollama:
                os.environ["USE_OLLAMA"] = "true"
                respuesta = responder(st.session_state.messages)
            elif use_api or (auto and api_key):
                os.environ["USE_OLLAMA"] = "false"
                respuesta = responder(st.session_state.messages)
            elif auto:
                os.environ["USE_OLLAMA"] = "true"
                try:
                    respuesta = responder(st.session_state.messages)
                except Exception:
                    respuesta = responder_sin_api(st.session_state.messages)
            else:
                respuesta = responder_sin_api(st.session_state.messages)

        st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
