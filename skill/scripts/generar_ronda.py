#!/usr/bin/env python3
"""
Script de automatización semanal para generar un set de 5 preguntas PAES M1
usando Claude. Se ejecuta desde GitHub Actions (semanal) o manualmente.

Flujo:
1. Determina el eje de esta semana (rotar_eje.py)
2. Lee temario y formato (referencias)
3. Llama a Claude para generar 5 preguntas JSON
4. Valida el JSON resultante
5. Guarda: data/rondas/<fecha>.json
6. Regenera docs/index.html (build_progress_artifact.py)
7. Registra en data/registro_generaciones.json

Uso:
    ANTHROPIC_API_KEY=sk-... python generar_ronda.py [--output-dir path]
"""
import json
import sys
import os
import subprocess
from datetime import date
from pathlib import Path


def get_project_root():
    """Encuentra la raíz del proyecto (directorio con .github/workflows)."""
    current = Path(__file__).parent.parent.parent
    if (current / ".github" / "workflows").exists():
        return current
    raise RuntimeError("No se puede encontrar la raíz del proyecto")


def run_rotar_eje(state_path):
    """Ejecuta rotar_eje.py para determinar el eje de esta semana."""
    result = subprocess.run(
        [sys.executable, "skill/scripts/rotar_eje.py", str(state_path)],
        capture_output=True,
        text=True,
        cwd=get_project_root(),
    )
    if result.returncode != 0:
        print(f"Error en rotar_eje.py: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def read_file(path):
    """Lee un archivo de texto."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generar_preguntas_con_claude(eje_info, temario, formato, registro):
    """Llama a Claude para generar 5 preguntas."""
    try:
        import anthropic
    except ImportError:
        print("Error: instala 'anthropic' con: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic()

    # Construir contexto de lo ya cubierto
    unidades_cubiertas = set()
    if registro:
        for ronda in registro:
            ronda_json_path = get_project_root() / "data" / "rondas" / f"{ronda['fecha']}.json"
            if ronda_json_path.exists():
                with open(ronda_json_path, "r", encoding="utf-8") as f:
                    ronda_data = json.load(f)
                    for p in ronda_data.get("preguntas", []):
                        unidades_cubiertas.add(p.get("unidad", ""))

    prompt = f"""Eres un generador de preguntas para la PAES M1 de matemáticas (Chile).

TEMARIO OFICIAL (DEMRE):
{temario}

---

FORMATO EXACTO (obligatorio):
{formato}

---

Tarea esta semana: Eje "{eje_info['eje_de_esta_semana']}"

Unidades YA cubiertas en semanas anteriores: {', '.join(unidades_cubiertas) if unidades_cubiertas else '(ninguna aún)'}

Instrucciones:
1. Genera EXACTAMENTE 5 preguntas originales (NUNCA copiadas del DEMRE)
2. Todas deben ser del eje "{eje_info['eje_de_esta_semana']}"
3. Cubre unidades DISTINTAS a las ya cubiertas (varía cada semana)
4. Dificultad: 2 Básico, 2 Intermedio, 1 Avanzado
5. Habilidades: mezcla al menos 2-3 distintas (Resolver problemas, Modelar, Representar, Argumentar)
6. Contexto: alterna entre Cotidiano y Matemático
7. Cada pregunta: ID + eje + unidad + habilidad + dificultad + contexto + enunciado + 4 alternativas (A-D) + correcta + explicación (concepto + pasos)

Devuelve un JSON válido, COMPACTO (en una sola línea, sin saltos de línea dentro de strings), con esta estructura:
{{
  "fecha": "{date.today().isoformat()}",
  "eje_semana": "{eje_info['eje_de_esta_semana']}",
  "saludo": "1-2 líneas saludando y explicando por qué toca este eje",
  "preguntas": [
    {{
      "id": "M1-<EJE_ABREV>-{date.today().isoformat()}-01",
      "eje": "{eje_info['eje_de_esta_semana']}",
      "unidad": "...",
      "habilidad": "Resolver problemas|Modelar|Representar|Argumentar",
      "dificultad": "Básico|Intermedio|Avanzado",
      "contexto": "Cotidiano|Matemático",
      "enunciado": "...",
      "alternativas": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correcta": "A|B|C|D",
      "explicacion": {{
        "concepto": "1-2 frases del concepto clave",
        "pasos": ["Paso 1: ...", "Paso 2: ...", "Paso final: ..."]
      }}
    }},
    ...
  ],
  "cobertura": {{
    "unidades": ["unidad1", "unidad2"],
    "habilidades": ["Resolver problemas", "Modelar"],
    "proxima_semana": "{eje_info['eje_de_la_proxima_semana']}"
  }}
}}

CRÍTICO: El JSON debe ser válido y parseable. Responde SOLO el JSON, sin explicaciones extra."""

    message = client.messages.create(
        model="claude-opus-5",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extraer el texto de la respuesta (manejar thinking blocks)
    response_text = ""
    for block in message.content:
        if hasattr(block, 'text'):
            response_text = block.text.strip()
            break

    if not response_text:
        print(f"Error: No se encontró texto en la respuesta de Claude", file=sys.stderr)
        print(f"Contenido recibido: {message.content}", file=sys.stderr)
        sys.exit(1)

    # Limpiar el JSON: extraer desde el primer { al último }
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")

    if start_idx == -1 or end_idx == -1:
        print(f"Error: No se encontraron { o } en la respuesta", file=sys.stderr)
        print(f"Respuesta completa:\n{response_text[:1000]}", file=sys.stderr)
        sys.exit(1)

    response_text = response_text[start_idx:end_idx + 1]

    # Intentar parsear el JSON con reintentos
    for intento in range(3):
        try:
            preguntas_json = json.loads(response_text)
            return preguntas_json
        except json.JSONDecodeError as e:
            print(f"Intento {intento + 1} falló: {e}", file=sys.stderr)

            if intento < 2:
                # Intentar arreglar caracteres comunes problemáticos
                print(f"Intentando reparar JSON...", file=sys.stderr)

                # Reemplazar algunos caracteres problemáticos
                response_text = response_text.replace('\n', ' ')  # Saltos de línea
                response_text = response_text.replace('\r', '')    # Retornos
                response_text = response_text.replace('\t', ' ')   # Tabs

                # Intentar nuevamente
                print(f"Reintentando con caracteres reparados...", file=sys.stderr)
            else:
                print(f"Error final al parsear JSON de Claude después de 3 intentos", file=sys.stderr)
                print(f"Primeros 1000 caracteres:\n{response_text[:1000]}", file=sys.stderr)
                sys.exit(1)


def validar_json(data):
    """Valida que el JSON tenga la estructura esperada."""
    required_top_level = {"fecha", "eje_semana", "saludo", "preguntas", "cobertura"}
    missing = required_top_level - set(data.keys())
    if missing:
        print(f"DEBUG: Falta claves: {missing}", file=sys.stderr)
        print(f"DEBUG: JSON tiene claves: {set(data.keys())}", file=sys.stderr)
        raise ValueError(f"Falta alguna clave obligatoria: {missing}")

    if not data.get("preguntas"):
        raise ValueError("No hay preguntas en el JSON")

    if len(data["preguntas"]) != 5:
        raise ValueError(f"Debe haber exactamente 5 preguntas, hay {len(data['preguntas'])}")

    for i, preg in enumerate(data["preguntas"]):
        required_preg = {
            "id", "eje", "unidad", "habilidad", "dificultad", "contexto",
            "enunciado", "alternativas", "correcta", "explicacion"
        }
        if not all(key in preg for key in required_preg):
            missing_keys = required_preg - set(preg.keys())
            raise ValueError(f"Pregunta {i+1} falta claves: {missing_keys}")

        if len(preg["alternativas"]) != 4 or set(preg["alternativas"].keys()) != {"A", "B", "C", "D"}:
            raise ValueError(f"Pregunta {i+1}: alternativas debe tener exactamente A, B, C, D")

        if preg["correcta"] not in ["A", "B", "C", "D"]:
            raise ValueError(f"Pregunta {i+1}: correcta debe ser A, B, C o D")

        if "concepto" not in preg.get("explicacion", {}) or "pasos" not in preg.get("explicacion", {}):
            raise ValueError(f"Pregunta {i+1}: explicación falta concepto o pasos")


def main():
    project_root = get_project_root()
    os.chdir(project_root)

    # Rutas
    state_path = project_root / "data" / "paes_m1_state.json"
    registro_path = project_root / "data" / "registro_generaciones.json"
    temario_path = project_root / "skill" / "references" / "temario-m1.md"
    formato_path = project_root / "skill" / "references" / "formato-pregunta.md"
    rondas_dir = project_root / "data" / "rondas"

    # Crear directorio de rondas si no existe
    rondas_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Generando ronda semanal PAES M1...")

    # 1. Rotar eje
    print("1️⃣  Determinando eje de esta semana...")
    eje_info = run_rotar_eje(state_path)
    print(f"   Eje: {eje_info['eje_de_esta_semana']} (próxima: {eje_info['eje_de_la_proxima_semana']})")

    # 2. Leer referencias
    print("2️⃣  Leyendo referencias...")
    temario = read_file(temario_path)
    formato = read_file(formato_path)

    # Leer registro si existe
    if registro_path.exists():
        with open(registro_path, "r", encoding="utf-8") as f:
            registro = json.load(f)
    else:
        registro = []

    # 3. Generar preguntas con Claude
    print("3️⃣  Llamando a Claude para generar preguntas...")
    preguntas_json = generar_preguntas_con_claude(eje_info, temario, formato, registro)

    # 4. Validar
    print("4️⃣  Validando JSON...")
    try:
        validar_json(preguntas_json)
        print("   ✓ JSON válido")
    except ValueError as e:
        print(f"   ✗ Error de validación: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Guardar JSON
    print("5️⃣  Guardando preguntas...")
    fecha_hoy = date.today().isoformat()
    json_path = rondas_dir / f"{fecha_hoy}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(preguntas_json, f, ensure_ascii=False, indent=2)
    print(f"   Guardado: {json_path}")

    # 6. Regenerar docs/index.html
    print("6️⃣  Regenerando docs/index.html...")
    html_path = project_root / "docs" / "index.html"
    result = subprocess.run(
        [
            sys.executable,
            "skill/scripts/build_progress_artifact.py",
            str(json_path),
            str(registro_path),
            str(html_path),
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    if result.returncode != 0:
        print(f"Error en build_progress_artifact.py: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"   Guardado: {html_path}")

    # 7. Registrar generación
    print("7️⃣  Registrando en historial...")
    result = subprocess.run(
        [
            sys.executable,
            "skill/scripts/registrar_generacion.py",
            str(registro_path),
            eje_info['eje_de_esta_semana'],
            str(json_path),
            str(json_path.parent / f"{fecha_hoy}.html"),  # HTML placeholder
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    if result.returncode != 0:
        print(f"Error en registrar_generacion.py: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"   Registrado en: {registro_path}")

    print("\n✅ Ronda completada:")
    print(f"   Eje: {eje_info['eje_de_esta_semana']}")
    print(f"   Fecha: {fecha_hoy}")
    print(f"   Preguntas: 5")
    print(f"\n📁 Archivos generados:")
    print(f"   - {json_path}")
    print(f"   - {html_path}")
    print(f"\n⏭️  Próxima semana: {eje_info['eje_de_la_proxima_semana']}")


if __name__ == "__main__":
    main()
