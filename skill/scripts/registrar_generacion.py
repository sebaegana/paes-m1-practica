#!/usr/bin/env python3
"""
Agrega un registro a la bitácora de generaciones (registro_generaciones.json).
Permite trackear qué se generó, cuándo, de qué materia/eje, a lo largo del tiempo.

Uso:
    python registrar_generacion.py <registro.json> <materia> <eje> <archivo_json> <archivo_html> [borrador_gmail_id]

Si <registro.json> no existe, se crea. El número de ronda se calcula por materia
(len([r for r in registro if r["materia"] == materia]) + 1).
"""
import json
import sys
import os
from datetime import date


def main():
    if len(sys.argv) not in (6, 7):
        print(
            "Uso: python registrar_generacion.py <registro.json> <materia> <eje> <archivo_json> "
            "<archivo_html> [borrador_gmail_id]",
            file=sys.stderr,
        )
        sys.exit(1)

    registro_path = sys.argv[1]
    materia = sys.argv[2].lower()
    eje = sys.argv[3]
    archivo_json = sys.argv[4]
    archivo_html = sys.argv[5]
    borrador_gmail_id = sys.argv[6] if len(sys.argv) == 7 else None

    if os.path.exists(registro_path):
        with open(registro_path, "r", encoding="utf-8") as f:
            registro = json.load(f)
    else:
        registro = []

    # Calcular número de ronda por materia
    ronda_num = len([r for r in registro if r.get("materia") == materia]) + 1

    nueva_ronda = {
        "ronda": ronda_num,
        "fecha": date.today().isoformat(),
        "materia": materia,
        "eje": eje,
        "archivo_json": os.path.basename(archivo_json),
        "archivo_html": os.path.basename(archivo_html),
        "borrador_gmail_id": borrador_gmail_id,
    }
    registro.append(nueva_ronda)

    os.makedirs(os.path.dirname(os.path.abspath(registro_path)) or ".", exist_ok=True)
    with open(registro_path, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)

    print(json.dumps(nueva_ronda, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
