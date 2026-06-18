import os

import streamlit as st

from asistente import responder, responder_sin_api

st.set_page_config(
    page_title="Sabio Interior - Biodescodificación",
    page_icon="\U0001f343",
    layout="wide",
)

ESTILOS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(160deg, #f5f0e8 0%, #e8e0d0 30%, #d8d0c0 100%);
    }

    .main > div { padding: 0 1.5rem; }

    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #4a3728 !important;
        font-weight: 600 !important;
    }

    .title-zen {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3rem;
        font-weight: 600;
        color: #4a3728;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: 2px;
    }

    .subtitle-zen {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.1rem;
        color: #8a7a6a;
        text-align: center;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #c8b8a8;
        padding-bottom: 0.8rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3d2c1e 0%, #2a1f14 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e8ddd0 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #d4c4a8 !important;
        font-family: 'Cormorant Garamond', serif !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #d4c4a8 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #5a4a3a;
    }

    [data-testid="stChatMessage"] {
        border: none !important;
        box-shadow: none !important;
        margin: 0.1rem 0 !important;
    }

    .mensaje-usuario {
        background: #5a4a3a;
        color: #f5f0e8;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        max-width: 80%;
        margin-left: auto;
        margin-bottom: 12px;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .mensaje-sabio {
        background: #ffffffd9;
        backdrop-filter: blur(4px);
        border-left: 3px solid #7a9a6a;
        border-radius: 4px 18px 18px 18px;
        padding: 14px 20px;
        max-width: 85%;
        margin-right: auto;
        margin-bottom: 16px;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #2a1f14;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        position: relative;
    }

    .sabio-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: #5a7a4a;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .sabio-header span.hoja {
        font-size: 1.2rem;
    }

    .mensaje-sabio p {
        margin: 0 0 6px 0;
    }
    .mensaje-sabio p:last-child {
        margin-bottom: 0;
    }

    [data-testid="stChatInput"] textarea {
        background: #ffffffcc !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid #c8b8a8 !important;
        border-radius: 24px !important;
        padding: 10px 18px !important;
        font-size: 0.95rem !important;
        color: #2a1f14 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #7a9a6a !important;
        box-shadow: 0 0 0 2px #7a9a6a44 !important;
    }
    [data-testid="stChatInput"] button {
        background: #5a7a4a !important;
        color: white !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
    }

    .stSpinner > div {
        border-color: #7a9a6a !important;
    }

    footer { visibility: hidden; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #e8e0d0; }
    ::-webkit-scrollbar-thumb { background: #b8a898; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #9a8a7a; }

    @media (max-width: 768px) {
        .mensaje-usuario, .mensaje-sabio { max-width: 95%; }
        .title-zen { font-size: 2rem; }
    }
</style>
"""


def formato_mensaje_sabio(contenido: str) -> str:
    lineas = contenido.strip().split("\n")
    parrafos = []
    for l in lineas:
        l = l.strip()
        if l:
            if l.startswith("##"):
                parrafos.append(f"<strong>{l.lstrip('#').strip()}</strong>")
            elif l.startswith("*") and l.endswith("*"):
                parrafos.append(f"<em>{l.strip('*')}</em>")
            elif l.startswith("-"):
                parrafos.append(f"&nbsp;&nbsp;• {l.lstrip('- ')}")
            else:
                parrafos.append(l)
        else:
            parrafos.append("<br>")
    cuerpo = "\n".join(parrafos)
    return f"""<div class="mensaje-sabio">
<div class="sabio-header"><span class="hoja">\U0001f343</span> Sabio Interior</div>
{cuerpo}
</div>"""


st.markdown(ESTILOS, unsafe_allow_html=True)

st.markdown(
    '<div class="title-zen">\U0001f343 Sabio Interior</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle-zen">'
    "— orientación en biodescodificación —"
    "</div>",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("### \u262e Conexión")

    modo = st.radio(
        "Modo",
        ["Automático", "Groq", "OpenAI", "Ollama (local)", "Sin API"],
        index=0,
        label_visibility="collapsed",
    )

    with st.expander(" Groq", expanded=False):
        os.environ["GROQ_API_KEY"] = st.text_input(
            "API Key", value=os.getenv("GROQ_API_KEY", ""),
            type="password", key="groq_key",
        )
        os.environ["GROQ_MODEL"] = st.text_input(
            "Modelo", value=os.getenv("GROQ_MODEL", "llama3-70b-8192"),
            key="groq_model",
        )

    with st.expander(" OpenAI", expanded=False):
        os.environ["OPENAI_API_KEY"] = st.text_input(
            "API Key", value=os.getenv("OPENAI_API_KEY", ""),
            type="password", key="openai_key",
        )
        os.environ["OPENAI_MODEL"] = st.text_input(
            "Modelo", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            key="openai_model",
        )

    with st.expander(" Ollama", expanded=False):
        os.environ["OLLAMA_URL"] = st.text_input(
            "URL", value=os.getenv("OLLAMA_URL", "http://localhost:11434/v1"),
            key="ollama_url",
        )
        os.environ["OLLAMA_MODEL"] = st.text_input(
            "Modelo", value=os.getenv("OLLAMA_MODEL", "llama3"),
            key="ollama_model",
        )

    st.markdown("---")
    gh_ok = bool(os.getenv("GITHUB_TOKEN"))
    groq_ok = bool(os.getenv("GROQ_API_KEY"))
    if groq_ok:
        st.caption("\U0001f7e2 Groq conectado")
    if gh_ok:
        st.caption("\U0001f7e2 GitHub conectado")
    if not groq_ok and not gh_ok:
        st.caption("\U0001f7e1 Solo modo local")

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.85rem; opacity:0.7; line-height:1.5;">'
        "La biodescodificación es un enfoque complementario "
        "que no reemplaza la atención médica profesional."
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("\U0001f9f9 Limpiar", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'<div class="mensaje-usuario">{message["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            formato_mensaje_sabio(message["content"]),
            unsafe_allow_html=True,
        )

if prompt := st.chat_input("Pregúntale al Sabio Interior..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(
        f'<div class="mensaje-usuario">{prompt}</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("El Sabio Interior medita su respuesta..."):
        api_key = os.getenv("OPENAI_API_KEY", "")
        groq_key = os.getenv("GROQ_API_KEY", "")
        use_ollama = modo == "Ollama (local)"
        use_api = modo == "OpenAI"
        use_groq = modo == "Groq"
        auto = modo == "Automático"
        only_kb = modo == "Sin API"

        if only_kb:
            respuesta = responder_sin_api(st.session_state.messages)
        elif use_groq:
            os.environ["USE_GROQ"] = "true"
            os.environ["USE_OLLAMA"] = "false"
            respuesta = responder(st.session_state.messages)
        elif use_ollama:
            os.environ["USE_OLLAMA"] = "true"
            os.environ["USE_GROQ"] = "false"
            respuesta = responder(st.session_state.messages)
        elif use_api or (auto and api_key):
            os.environ["USE_OLLAMA"] = "false"
            os.environ["USE_GROQ"] = "false"
            respuesta = responder(st.session_state.messages)
        elif auto and groq_key:
            os.environ["USE_GROQ"] = "true"
            os.environ["USE_OLLAMA"] = "false"
            try:
                respuesta = responder(st.session_state.messages)
            except Exception:
                respuesta = responder_sin_api(st.session_state.messages)
        elif auto:
            os.environ["USE_OLLAMA"] = "true"
            os.environ["USE_GROQ"] = "false"
            try:
                respuesta = responder(st.session_state.messages)
            except Exception:
                respuesta = responder_sin_api(st.session_state.messages)
        else:
            respuesta = responder_sin_api(st.session_state.messages)

    st.markdown(formato_mensaje_sabio(respuesta), unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
