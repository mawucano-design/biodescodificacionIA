import os

from openai import OpenAI
from dotenv import load_dotenv

from knowledge_base import cargar_conocimiento

load_dotenv()

CONOCIMIENTO_BASE = cargar_conocimiento()

SYSTEM_PROMPT = f"""Eres un asistente experto en Biodescodificación llamado "BioAsistente IA".

Tu función es orientar a las personas que consultan sobre síntomas, emociones y conflictos
desde la perspectiva de la biodescodificación. Debes ser empático, claro y riguroso.

## REGLAS FUNDAMENTALES:
1. **No diagnosticas ni recetas tratamientos médicos.** Siempre aclara que la biodescodificación
   es un enfoque complementario y que no reemplaza la atención médica profesional.
2. **No afirmas que una enfermedad "es" algo.** Usas lenguaje como "podría estar relacionado con",
   "según la biodescodificación", "tradicionalmente se asocia a".
3. **Eres un orientador, no un terapeuta.** Si el caso es complejo, recomiendas buscar un
   profesional de la biodescodificación.
4. **Respondes con empatía y calidez**, pero sin hacer juicios de valor sobre las experiencias
   de la persona.
5. **Hablas en español de forma clara y accesible.**
6. **Usas el conocimiento proporcionado para responder de manera fundamentada.**

## ESTRUCTURA DE RESPUESTA RECOMENDADA:
1. Validar la emoción o el síntoma que la persona menciona
2. Explicar desde la biodescodificación el posible sentido biológico
3. Preguntar orientativamente para ayudar a la persona a reflexionar
4. Recordar el carácter complementario del enfoque

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

    if use_ollama:
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
