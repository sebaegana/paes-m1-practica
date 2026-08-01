#!/usr/bin/env python3
"""
Agrega un registro a la bitacora de generaciones (registro_generaciones.json).
Esto es lo que permite trackear "que se genero, cuando, y de que eje" a lo largo del
tiempo, independiente de si el usuario marco o no la ronda como hecha en el panel.

Uso:
    python registrar_generacion.py <registro.json> <eje> <archivo_json> <archivo_html> [borrador_gmail_id]

Si <registro.json> no existe todavia, se crea. El numero de ronda se calcula solo
(len(registro) + 1).
"""
import json
import sys
import os
from datetime import date


def main():
    if len(sys.argv) not in (5, 6):
        print(
            "Uso: python registrar_generacion.py <registro.json> <eje> <archivo_json> "
            "<archivo_html> [borrador_gmail_id]",
            file=sys.stderr,
        )
        sys.exit(1)

    registro_path = sys.argv[1]
    eje = sys.argv[2]
    archivo_json = sys.argv[3]
    archivo_html = sys.argv[4]
    borrador_gmail_id = sys.argv[5] if len(sys.argv) == 6 else None

    if os.path.exists(registro_path):
        with open(registro_path, "r", encoding="utf-8") as f:
            registro = json.load(f)
    else:
        registro = []

    nueva_ronda = {
        "ronda": len(registro) + 1,
        "fecha": date.today().isoformat(),
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
