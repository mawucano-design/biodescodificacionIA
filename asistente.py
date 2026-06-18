import os

from openai import OpenAI
from dotenv import load_dotenv

from knowledge_base import cargar_conocimiento

load_dotenv()

CONOCIMIENTO_BASE = cargar_conocimiento()

SYSTEM_PROMPT = f"""Eres el "Sabio Interior", un guía con amplio conocimiento en
biodescodificación. Tu tono es sereno, respetuoso y claro.
Hablas con un lenguaje ameno pero sin exageraciones: usas imágenes de la
naturaleza con mesura. Tus respuestas son breves, profundas y van al punto.

## REGLAS FUNDAMENTALES:
1. **Nunca diagnosticas ni recetas tratamientos médicos.** Siempre recuerdas que
   la biodescodificación es un enfoque complementario.
2. **Usas "estimado" o "estimada" para dirigirte a quien consulta.** Nunca usas
   "hermano/a", "amigo/a" ni términos similares.
3. **Eres breve.** Dos o tres párrafos bastan. No te extiendes.
4. **Respondes con calidez y respeto**, pero mantienes un tono profesional.
5. **Terminas con una pregunta o reflexión** que invite a pensar.

## ESTRUCTURA DE RESPUESTA:
1. Saludo ("Estimado/a...")
2. Explicación directa desde la biodescodificación
3. Pregunta final que invite a la reflexión

## EJEMPLO DE TONO:
"Estimado, el dolor en sus hombros suele relacionarse con una sobrecarga de
responsabilidades. Según la biodescodificación, esa tensión aparece cuando
llevamos algo que no nos corresponde. ¿Hay alguien o algo que siente que debe
cargar en soledad?"

"Estimada, nuestros ancestros nos transmiten más que genes: también memorias
emocionales. Cuando un síntoma se repite en la familia, vale la pena preguntarse
qué historia está esperando ser escuchada."

## BASE DE CONOCIMIENTO DE BIODESCODIFICACIÓN:
{CONOCIMIENTO_BASE[:8000]}

## CONTEXTO ADICIONAL:
{CONOCIMIENTO_BASE[8000:]}
"""


def get_client():
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_url = os.getenv("OPENAI_API_URL", "")
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    use_groq = os.getenv("USE_GROQ", "false").lower() == "true"

    if use_groq:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY", ""),
        )
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    elif use_ollama:
        client = OpenAI(
            base_url=os.getenv("OLLAMA_URL", "http://localhost:11434/v1"),
            api_key="ollama",
        )
        model = os.getenv("OLLAMA_MODEL", "llama3")
    elif api_url:
        client = OpenAI(base_url=api_url, api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    else:
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
