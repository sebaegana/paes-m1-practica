#!/usr/bin/env python3
"""
Genera un HTML interactivo autocontenido para un set de preguntas PAES M1.

Cada pregunta se muestra con 4 alternativas seleccionables (A-D) y un boton
"Ver respuesta" que revela la alternativa correcta (y si la seleccionada era
distinta, la marca como incorrecta) junto con la solucion explicada. No hay
nada que calificar ni enviar a un servidor: todo ocurre en el navegador con
JS plano, sin dependencias externas ni localStorage.

Uso:
    python build_quiz_html.py <preguntas.json> <salida.html>

Esquema esperado de <preguntas.json>:
{
  "fecha": "2026-08-01",
  "eje_semana": "Geometria",
  "saludo": "texto breve de 1-2 lineas sobre por que toca este eje",
  "preguntas": [
    {
      "id": "M1-GEO-2026-08-01-01",
      "eje": "Geometria",
      "unidad": "Figuras geometricas (Teorema de Pitagoras)",
      "habilidad": "Resolver problemas",
      "dificultad": "Basico",
      "contexto": "Cotidiano",
      "enunciado": "texto...",
      "alternativas": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correcta": "C",
      "explicacion": {
        "concepto": "1-2 frases: que contenido/idea matematica hay que saber para resolver esta pregunta",
        "pasos": [
          "Paso 1: ...",
          "Paso 2: ...",
          "Paso 3 (conclusion): ..."
        ]
      }
    },
    ...
  ],
  "cobertura": {
    "unidades": ["..."],
    "habilidades": ["..."],
    "proxima_semana": "Probabilidad y estadistica"
  }
}
"""
import json
import sys
import html


def esc(s):
    return html.escape(str(s), quote=True)


def render_question(idx, q):
    qid = esc(q["id"])
    alt_buttons = ""
    for letra in ["A", "B", "C", "D"]:
        texto = esc(q["alternativas"][letra])
        alt_buttons += (
            f'<button type="button" class="alt-btn" data-letra="{letra}" '
            f'onclick="seleccionar(\'{qid}\', this)">{letra}) {texto}</button>\n'
        )

    explicacion = q.get("explicacion", {})
    concepto = explicacion.get("concepto", "")
    pasos = explicacion.get("pasos", [])
    pasos_html = "\n".join(f"      <li>{esc(p)}</li>" for p in pasos)

    return f"""
  <section class="pregunta" id="preg-{qid}">
    <div class="meta">{esc(q['eje'])} &middot; {esc(q['unidad'])} &middot; {esc(q['habilidad'])} &middot; Dificultad: {esc(q['dificultad'])}</div>
    <h3>Pregunta {idx}</h3>
    <p class="enunciado">{esc(q['enunciado'])}</p>
    <div class="alternativas" data-correcta="{esc(q['correcta'])}">
      {alt_buttons}
    </div>
    <div class="botones-revelar">
      <button type="button" class="ver-respuesta" onclick="mostrarRespuesta('{qid}')">Ver respuesta</button>
      <button type="button" class="ver-explicacion" onclick="mostrarExplicacion('{qid}')">Ver explicación paso a paso</button>
    </div>
    <div class="respuesta oculto" id="resp-{qid}">
      <span class="respuesta-icono" id="resp-icono-{qid}"></span>
      <span>Alternativa correcta: <strong>{esc(q['correcta'])}</strong></span>
    </div>
    <div class="solucion oculto" id="sol-{qid}">
      <p class="concepto"><strong>Concepto clave:</strong> {esc(concepto)}</p>
      <p class="pasos-titulo"><strong>Resolución paso a paso</strong></p>
      <ol class="pasos">
{pasos_html}
      </ol>
    </div>
  </section>
"""


def build_html(data):
    fecha = esc(data.get("fecha", ""))
    eje_semana = esc(data.get("eje_semana", ""))
    saludo = esc(data.get("saludo", ""))
    preguntas_html = "\n".join(
        render_question(i + 1, q) for i, q in enumerate(data["preguntas"])
    )

    cobertura = data.get("cobertura", {})
    unidades = ", ".join(cobertura.get("unidades", []))
    habilidades = ", ".join(cobertura.get("habilidades", []))
    proxima = esc(cobertura.get("proxima_semana", ""))

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Practica PAES M1 - {fecha}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; max-width: 720px;
         margin: 0 auto; padding: 24px 16px; color: #1d1d1f; background: #fafafa; }}
  h1 {{ font-size: 1.3em; }}
  .saludo {{ color: #444; margin-bottom: 24px; }}
  .pregunta {{ background: #fff; border: 1px solid #e2e2e2; border-radius: 10px;
               padding: 18px 20px; margin-bottom: 18px; }}
  .meta {{ font-size: 0.78em; color: #888; text-transform: uppercase; letter-spacing: 0.02em;
           margin-bottom: 6px; }}
  .enunciado {{ font-size: 1.02em; line-height: 1.5; margin-bottom: 14px; }}
  .alternativas {{ display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }}
  .alt-btn {{ text-align: left; padding: 10px 14px; border-radius: 8px; border: 1px solid #d0d0d5;
              background: #fff; cursor: pointer; font-size: 0.96em; }}
  .alt-btn:hover {{ background: #f2f2f7; }}
  .alt-btn.seleccionada {{ border-color: #6b6bd6; background: #eeeeff; font-weight: 600; }}
  .alt-btn.correcta {{ border-color: #2e7d32; background: #e8f5e9; font-weight: 600; }}
  .alt-btn.incorrecta {{ border-color: #c62828; background: #fdecea; }}
  .alt-btn[disabled] {{ cursor: default; }}
  .botones-revelar {{ display: flex; gap: 10px; }}
  .ver-respuesta, .ver-explicacion {{ padding: 9px 16px; border-radius: 8px; border: none;
                     cursor: pointer; font-size: 0.92em; }}
  .ver-respuesta {{ background: #1d1d1f; color: #fff; }}
  .ver-respuesta:hover {{ background: #3a3a3c; }}
  .ver-explicacion {{ background: #eeeeff; color: #1d1d1f; border: 1px solid #d0d0f0 !important; }}
  .ver-explicacion:hover {{ background: #e2e2fb; }}
  .respuesta {{ margin-top: 14px; padding: 8px 14px; background: #f5f5f7; border-radius: 999px;
                font-size: 0.9em; display: inline-flex; align-items: center; gap: 8px; }}
  .respuesta-icono::before {{ content: "•"; color: #888; }}
  .respuesta.ok .respuesta-icono::before {{ content: "✓"; color: #2e7d32; font-weight: 700; }}
  .respuesta.mal .respuesta-icono::before {{ content: "✗"; color: #c62828; font-weight: 700; }}
  .solucion {{ margin-top: 12px; padding: 14px 16px; background: #f7f7fb; border: 1px solid #e6e6f2;
               border-radius: 8px; font-size: 0.94em; line-height: 1.55; }}
  .solucion .concepto {{ margin: 0 0 10px 0; color: #33334d; }}
  .solucion .pasos-titulo {{ margin: 0 0 6px 0; }}
  .solucion .pasos {{ margin: 0; padding-left: 20px; }}
  .solucion .pasos li {{ margin-bottom: 6px; }}
  .oculto {{ display: none; }}
  .cobertura {{ font-size: 0.85em; color: #666; border-top: 1px solid #e2e2e2; padding-top: 14px;
                margin-top: 20px; }}
</style>
</head>
<body>
  <h1>Practica semanal PAES M1 &mdash; {eje_semana}</h1>
  <p class="saludo">{saludo}</p>

  {preguntas_html}

  <div class="cobertura">
    <strong>Cobertura de este set:</strong> {eje_semana}<br>
    Unidades cubiertas: {esc(unidades)}<br>
    Habilidades cubiertas: {esc(habilidades)}<br>
    Proxima semana: {proxima}
  </div>

<script>
function seleccionar(qid, btn) {{
  const cont = btn.closest('.alternativas');
  cont.querySelectorAll('.alt-btn').forEach(b => b.classList.remove('seleccionada'));
  btn.classList.add('seleccionada');
  cont.dataset.elegida = btn.dataset.letra;
}}

function mostrarRespuesta(qid) {{
  const cont = document.querySelector('#preg-' + qid + ' .alternativas');
  const respBox = document.getElementById('resp-' + qid);
  const yaVisible = !respBox.classList.contains('oculto');

  if (yaVisible) {{
    // Apretar de nuevo el boton resetea: se oculta la respuesta y se
    // vuelven a habilitar las alternativas para poder elegir otra vez.
    respBox.classList.add('oculto');
    respBox.classList.remove('ok', 'mal');
    cont.querySelectorAll('.alt-btn').forEach(b => {{
      b.disabled = false;
      b.classList.remove('correcta', 'incorrecta');
    }});
    return;
  }}

  const correcta = cont.dataset.correcta;
  const elegida = cont.dataset.elegida;
  cont.querySelectorAll('.alt-btn').forEach(b => {{
    b.disabled = true;
    if (b.dataset.letra === correcta) {{
      b.classList.add('correcta');
    }} else if (b.dataset.letra === elegida) {{
      b.classList.add('incorrecta');
    }}
  }});
  respBox.classList.remove('oculto');
  if (elegida) {{
    respBox.classList.add(elegida === correcta ? 'ok' : 'mal');
  }}
}}

function mostrarExplicacion(qid) {{
  const solBox = document.getElementById('sol-' + qid);
  solBox.classList.toggle('oculto');
}}
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) != 3:
        print("Uso: python build_quiz_html.py <preguntas.json> <salida.html>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    out = build_html(data)

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(out)

    print(f"HTML generado: {sys.argv[2]}")


if __name__ == "__main__":
    main()
