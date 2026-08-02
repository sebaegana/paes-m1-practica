#!/usr/bin/env python3
"""
Lleva el estado de rotación semanal de ejes temáticos (multi-materia).

Uso:
    python rotar_eje.py <materia> <ruta_estado.json>

Lee (o crea) un archivo JSON de estado, calcula cuál eje corresponde a esta ronda
según la materia (Matemática, Biología, etc.), actualiza el archivo, e imprime un JSON
con el eje de esta semana y el de la siguiente.

Si el archivo de estado no existe, se asume que esta es la primera ronda del eje inicial.
"""
import json
import sys
import os
from datetime import date

EJES_POR_MATERIA = {
    "matematica": [
        "Numeros",
        "Algebra y funciones",
        "Geometria",
        "Probabilidad y estadistica",
    ],
    "biologia": [
        "Celula",
        "Herencia y variabilidad genetica",
        "Evolucion y biodiversidad",
        "Organismo y ambiente",
        "Cuerpo humano y salud",
    ],
}


def main():
    if len(sys.argv) != 3:
        print("Uso: python rotar_eje.py <materia> <ruta_estado.json>", file=sys.stderr)
        sys.exit(1)

    materia = sys.argv[1].lower()
    state_path = sys.argv[2]

    if materia not in EJES_POR_MATERIA:
        print(f"Error: materia '{materia}' no reconocida. Usa: {', '.join(EJES_POR_MATERIA.keys())}", file=sys.stderr)
        sys.exit(1)

    ejes = EJES_POR_MATERIA[materia]

    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        last_index = state.get("last_eje_index", -1)
    else:
        state = {"history": []}
        last_index = -1

    next_index = (last_index + 1) % len(ejes)
    eje_actual = ejes[next_index]
    eje_siguiente = ejes[(next_index + 1) % len(ejes)]

    state["last_eje_index"] = next_index
    state.setdefault("history", []).append(
        {"fecha": date.today().isoformat(), "eje": eje_actual}
    )

    os.makedirs(os.path.dirname(os.path.abspath(state_path)) or ".", exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "eje_de_esta_semana": eje_actual,
        "eje_de_la_proxima_semana": eje_siguiente,
        "ronda_numero": len(state["history"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
