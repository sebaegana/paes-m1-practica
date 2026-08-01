#!/usr/bin/env python3
"""
Lleva el estado de rotación semanal de ejes tematicos para la skill paes-m1-prep.

Uso:
    python rotar_eje.py <ruta_estado.json>

Lee (o crea) un archivo JSON de estado, calcula cual eje corresponde a esta ronda
(rotacion fija Numeros -> Algebra y funciones -> Geometria -> Probabilidad y estadistica),
actualiza el archivo, e imprime un JSON con el eje de esta semana y el de la siguiente.

Si el archivo de estado no existe todavia, se asume que esta es la primera ronda y se
parte por "Numeros".
"""
import json
import sys
import os
from datetime import date

EJES = [
    "Numeros",
    "Algebra y funciones",
    "Geometria",
    "Probabilidad y estadistica",
]


def main():
    if len(sys.argv) != 2:
        print("Uso: python rotar_eje.py <ruta_estado.json>", file=sys.stderr)
        sys.exit(1)

    state_path = sys.argv[1]

    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        last_index = state.get("last_eje_index", -1)
    else:
        state = {"history": []}
        last_index = -1

    next_index = (last_index + 1) % len(EJES)
    eje_actual = EJES[next_index]
    eje_siguiente = EJES[(next_index + 1) % len(EJES)]

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
