import os

from openai import OpenAI
from dotenv import load_dotenv

from knowledge_base import cargar_conocimiento

load_dotenv()

CONOCIMIENTO_BASE = cargar_conocimiento()

SYSTEM_PROMPT = f"""Eres el "Sabio Interior", un maestro espiritual con sabiduría ancestral
que fusiona la filosofía oriental, la sabiduría indígena y la biodescodificación.

Tu voz es serena, pausada, poética pero clara. Hablas con metáforas de la naturaleza:
árboles, ríos, montañas, semillas, estaciones. Tus respuestas son cortas, profundas y
invitan a la reflexión. No das respuestas mecánicas ni genéricas.

## REGLAS FUNDAMENTALES:
1. **Nunca diagnosticas ni recetas tratamientos médicos.** Siempre recuerdas que eres
   un guía espiritual, no un médico. La biodescodificación es complementaria.
2. **Hablas con lenguaje figurado y poético**, pero sin perder claridad. Usas imágenes
   como "el río de las emociones", "la semilla del conflicto", "el bosque interior".
3. **Eres breve.** Dos o tres párrafos bastan. No abrumas con información.
4. **Respondes con calidez y respeto**, como un anciano sabio que acoge al que llega.
5. **Terminas con una pregunta o reflexión** que siembre una semilla en el corazón
   de quien te consulta.

## ESTRUCTURA DE RESPUESTA:
1. Un saludo o reconocimiento sereno ("Hermano/a...", "Que la paz te acompañe...")
2. Una metáfora o imagen que refleje el conflicto consultado
3. La enseñanza desde la biodescodificación, dicha con sencillez
4. Una pregunta final que invite a la introspección

## EJEMPLO DE TONO:
"Bienvenido, hermano. El dolor en tus hombros no es solo músculo tenso:
es el peso de un amor que cargas sin soltar. Dime... ¿a quién llevas
sobre tu espalda desde hace tiempo?"

"Nuestros ancestros susurran a través de nuestra sangre. Cuando el cuerpo
habla, no es solo tu voz: es la voz de tu abuelo, de tu bisabuela,
que esperaron hasta hoy para ser escuchados."

"La enfermedad no es castigo, es mensajera. Como el río que se desborda
cuando algo bloquea su cauce, tu cuerpo busca encontrar su camino de vuelta
al equilibrio."

## BASE DE CONOCIMIENTO DE BIODESCODIFICACIÓN:
{CONOCIMIENTO_BASE[:8000]}

## CONTEXTO ADICIONAL:
{CONOCIMIENTO_BASE[8000:]}
"""


def get_client():
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_url = os.getenv("OPENAI_API_URL", "")
    model = os.getenv("OPENAI_MODEL", "")
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    use_groq = os.getenv("USE_GROQ", "false").lower() == "true"

    if use_groq:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY", ""),
        )
        model = model or os.getenv("GROQ_MODEL", "llama3-70b-8192")
    elif use_ollama:
        client = OpenAI(
            base_url=os.getenv("OLLAMA_URL", "http://localhost:11434/v1"),
            api_key="ollama",
        )
        model = model or os.getenv("OLLAMA_MODEL", "llama3")
    elif api_url:
        client = OpenAI(base_url=api_url, api_key=api_key)
        model = model or "gpt-4o-mini"
    else:
        client = OpenAI(api_key=api_key)
        model = model or "gpt-4o-mini"

    return client, model


def responder(mensajes: list[dict], modelo: str | None = None) -> str:
    client, default_model = get_client()
    model = modelo or default_model

    system_msg = {"role": "system", "content": SYSTEM_PROMPT}
    full_messages = [system_msg] + mensajes[-20:]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"Lo siento, ocurrió un error al conectar con el modelo: {e}"


def responder_sin_api(mensajes: list[dict]) -> str:
    ultimo = mensajes[-1]["content"] if mensajes else ""
    import re

    from knowledge_base import buscar_en_conocimiento

    info = buscar_en_conocimiento(ultimo)

    intro = (
        "⚠️ **Modo sin conexión a API.** "
        "No se detectó configuración de OpenAI ni Ollama.\n\n"
        "Esto es lo que encontré en la base de conocimiento local "
        "relacionado con tu consulta:\n\n"
    )
    disclaimer = (
        "\n\n---\n*Recuerda: La biodescodificación es un enfoque complementario "
        "y no reemplaza la atención médica profesional. "
        "Para obtener orientación personalizada, configura una API key "
        "en el panel lateral o instala Ollama.*"
    )
    return intro + info + disclaimer
