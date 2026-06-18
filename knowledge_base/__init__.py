import os

from .fundamentos import FUNDAMENTOS
from .emociones import EMOCIONES
from .conflictos import CONFLICTOS
from .enfermedades import ENFERMEDADES
from .tecnicas import TECNICAS
from .citas import CITAS


def cargar_conocimiento():
    return "\n\n".join([
        FUNDAMENTOS,
        EMOCIONES,
        CONFLICTOS,
        ENFERMEDADES,
        TECNICAS,
        CITAS,
    ])


def buscar_en_conocimiento(consulta: str) -> str:
    consulta_lower = consulta.lower()
    secciones = {
        "fundamentos": FUNDAMENTOS,
        "emociones": EMOCIONES,
        "conflictos": CONFLICTOS,
        "enfermedades": ENFERMEDADES,
        "técnicas": TECNICAS,
        "citas": CITAS,
    }
    resultados = []
    for palabra in consulta_lower.split():
        for nombre, contenido in secciones.items():
            if palabra in contenido.lower():
                lineas = contenido.split("\n")
                relevantes = [
                    l for l in lineas if palabra in l.lower()
                ]
                if relevantes:
                    resultados.append(f"[{nombre.upper()}]: " + " | ".join(relevantes[:5]))
    if resultados:
        return "\n".join(resultados[:15])
    return "No se encontró información específica en la base de conocimiento."
