#!/usr/bin/env python3
"""
Registra o actualiza una entrada en el catálogo de contenido.

Uso:
    python registrar_contenido.py <catalogo.json> <materia> <eje> "<unidad>" <archivo_json>

Busca por (materia, eje, unidad). Si existe, actualiza archivo_json. Si no, agrega.
"""
import json
import sys
import os


def main():
    if len(sys.argv) != 6:
        print(
            "Uso: python registrar_contenido.py <catalogo.json> <materia> <eje> "
            '"<unidad>" <archivo_json>',
            file=sys.stderr,
        )
        sys.exit(1)

    catalogo_path = sys.argv[1]
    materia = sys.argv[2].lower()
    eje = sys.argv[3]
    unidad = sys.argv[4]
    archivo_json = sys.argv[5]

    if os.path.exists(catalogo_path):
        with open(catalogo_path, "r", encoding="utf-8") as f:
            catalogo = json.load(f)
    else:
        catalogo = []

    # Buscar entrada existente
    idx = None
    for i, entry in enumerate(catalogo):
        if (entry.get("materia") == materia and
            entry.get("eje") == eje and
            entry.get("unidad") == unidad):
            idx = i
            break

    entrada = {
        "materia": materia,
        "eje": eje,
        "unidad": unidad,
        "archivo_json": os.path.basename(archivo_json),
    }

    if idx is not None:
        catalogo[idx] = entrada
        print(f"Actualizado: {materia} → {eje} → {unidad}")
    else:
        catalogo.append(entrada)
        print(f"Agregado: {materia} → {eje} → {unidad}")

    os.makedirs(os.path.dirname(os.path.abspath(catalogo_path)) or ".", exist_ok=True)
    with open(catalogo_path, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)

    print(f"Catálogo actualizado: {catalogo_path}")


if __name__ == "__main__":
    main()
