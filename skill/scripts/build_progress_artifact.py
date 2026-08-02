#!/usr/bin/env python3
"""
Genera el panel persistente ("la app") de practica PAES M1: el quiz interactivo de la
semana en curso + un historial de rondas anteriores con casillas para marcar "hecho",
guardadas en localStorage del navegador (no requiere servidor ni base de datos).

Este HTML esta pensado para publicarse como un Cowork artifact (mcp__cowork__create_artifact
/ update_artifact), que persiste entre sesiones y se reabre desde el sidebar. Cada semana
se vuelve a generar con este mismo script y se actualiza el artifact existente (mismo id),
para que el localStorage de progreso no se pierda.

Uso:
    python build_progress_artifact.py <preguntas_semana.json> <registro.json> <salida.html>

<preguntas_semana.json>: mismo esquema que usa build_quiz_html.py (ver ese script).
<registro.json>: lista de rondas generadas hasta ahora, esquema:
[
  {"fecha": "2026-08-01", "ronda": 1, "eje": "Numeros"},
  {"fecha": "2026-08-08", "ronda": 2, "eje": "Algebra y funciones"}
]
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


def render_historial_row(record):
    ronda_id = f"{record['fecha']}-{record['eje']}".replace(" ", "_")
    return f"""
      <tr data-ronda-id="{esc(ronda_id)}">
        <td>{esc(record['ronda'])}</td>
        <td>{esc(record['fecha'])}</td>
        <td>{esc(record['eje'])}</td>
        <td class="col-check">
          <label class="check-label">
            <input type="checkbox" class="check-hecho" onchange="marcarHecho('{esc(ronda_id)}', this)">
            <span class="check-texto">Hecho</span>
          </label>
        </td>
        <td class="col-fecha-hecho" id="fecha-hecho-{esc(ronda_id)}"></td>
      </tr>
"""


def build_html(preguntas_data, registro):
    fecha = esc(preguntas_data.get("fecha", ""))
    eje_semana = esc(preguntas_data.get("eje_semana", ""))
    saludo = esc(preguntas_data.get("saludo", ""))
    preguntas_html = "\n".join(
        render_question(i + 1, q) for i, q in enumerate(preguntas_data["preguntas"])
    )

    cobertura = preguntas_data.get("cobertura", {})
    unidades = ", ".join(cobertura.get("unidades", []))
    habilidades = ", ".join(cobertura.get("habilidades", []))
    proxima = esc(cobertura.get("proxima_semana", ""))

    # Generar pestañas de rondas
    tabs_html = ""
    tabs_content = ""
    for i, record in enumerate(sorted(registro, key=lambda r: r.get("ronda", 0))):
        ronda_num = record.get("ronda", i+1)
        eje = esc(record.get("eje", ""))
        fecha_ronda = esc(record.get("fecha", ""))
        tab_id = f"tab-ronda-{ronda_num}"
        active = "active" if ronda_num == preguntas_data.get("ronda_numero", len(registro)) else ""

        tabs_html += f'      <button class="tab-btn {active}" onclick="cambiarTab({ronda_num})" data-ronda="{ronda_num}">Round {ronda_num}: {eje}</button>\n'

        # Solo mostrar preguntas de la ronda actual (la que se pasó como argumento)
        if ronda_num == preguntas_data.get("ronda_numero", len(registro)):
            tabs_content += f'    <div class="tab-content active" id="{tab_id}">\n      <p class="saludo">{saludo}</p>\n{preguntas_html}\n    </div>\n'
        else:
            tabs_content += f'    <div class="tab-content" id="{tab_id}"><p style="text-align:center;color:#999;padding:40px;">Preguntas de Round {ronda_num} ({eje}) - {fecha_ronda}</p></div>\n'

    registro_ordenado = sorted(registro, key=lambda r: r.get("ronda", 0), reverse=True)
    historial_html = "\n".join(render_historial_row(r) for r in registro_ordenado)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>PAES M1 - Panel de práctica</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; max-width: 760px;
         margin: 0 auto; padding: 24px 16px 48px; color: #1d1d1f; background: #fafafa; }}
  h1 {{ font-size: 1.4em; margin-bottom: 4px; }}
  h2 {{ font-size: 1.1em; margin-top: 36px; }}
  .actualizado {{ font-size: 0.8em; color: #999; margin-bottom: 18px; }}
  .saludo {{ color: #444; margin-bottom: 24px; }}
  .pregunta {{ background: #fff; border: 1px solid #e2e2e2; border-radius: 10px;
               padding: 18px 20px; margin-bottom: 18px; }}
  .meta {{ font-size: 0.78em; color: #888; text-transform: uppercase; letter-spacing: 0.02em;
           margin-bottom: 6px; }}
  .enunciado {{ font-size: 1.02em; line-height: 1.5; margin-bottom: 14px; }}
  .alternativas {{ display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }}
  .alt-btn {{ text-align: left; padding: 10px 14px; border-radius: 8px; border: 1px solid #d0d0d5;
              background: #fff; cursor: pointer; font-size: 0.96em; color: #1d1d1f; }}
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
  .tabs {{ display: flex; gap: 8px; margin-bottom: 24px; border-bottom: 2px solid #e2e2e2; overflow-x: auto; }}
  .tab-btn {{ padding: 12px 18px; border: none; background: transparent; cursor: pointer;
              font-size: 0.95em; color: #666; border-bottom: 3px solid transparent;
              transition: all 0.2s; white-space: nowrap; }}
  .tab-btn:hover {{ color: #1d1d1f; }}
  .tab-btn.active {{ color: #1d1d1f; border-bottom-color: #6b6bd6; font-weight: 600; }}
  .tabs-container {{ position: relative; }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}
  .cobertura {{ font-size: 0.85em; color: #666; border-top: 1px solid #e2e2e2; padding-top: 14px;
                margin-top: 20px; }}
  table.historial {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px;
                      overflow: hidden; border: 1px solid #e2e2e2; }}
  table.historial th, table.historial td {{ text-align: left; padding: 10px 12px; font-size: 0.9em; }}
  table.historial th {{ background: #f5f5f7; font-weight: 600; color: #444; }}
  table.historial tr + tr td {{ border-top: 1px solid #eee; }}
  .col-check {{ white-space: nowrap; }}
  .check-label {{ display: flex; align-items: center; gap: 6px; cursor: pointer; }}
  .col-fecha-hecho {{ color: #888; font-size: 0.85em; }}
</style>
</head>
<body>
  <h1>PAES M1 &mdash; Panel de práctica</h1>
  <p class="actualizado">Última generación: {fecha} &middot; Eje de esta semana: {eje_semana}</p>

  <h2>Rondas de práctica</h2>
  <div class="tabs">
{tabs_html}  </div>

  <div class="tabs-container">
{tabs_content}  </div>

  <div class="cobertura">
    <strong>Cobertura de este set:</strong> {eje_semana}<br>
    Unidades cubiertas: {esc(unidades)}<br>
    Habilidades cubiertas: {esc(habilidades)}<br>
    Próxima semana: {proxima}
  </div>

  <h2>Progreso</h2>
  <table class="historial">
    <thead>
      <tr><th>Ronda</th><th>Fecha</th><th>Eje</th><th>Estado</th><th></th></tr>
    </thead>
    <tbody>
      {historial_html}
    </tbody>
  </table>

<script>
function cambiarTab(rondaNum) {{
  const allTabs = document.querySelectorAll('.tab-content');
  const allBtns = document.querySelectorAll('.tab-btn');
  allTabs.forEach(t => t.classList.remove('active'));
  allBtns.forEach(b => b.classList.remove('active'));
  document.getElementById('tab-ronda-' + rondaNum).classList.add('active');
  document.querySelector('[data-ronda="' + rondaNum + '"]').classList.add('active');
}}

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
  document.getElementById('sol-' + qid).classList.toggle('oculto');
}}

// --- Progreso: persistido en localStorage, sobrevive a que este HTML se regenere ---
const PREFIJO_STORAGE = 'paes_m1_progreso_';

function pintarFilaHistorial(fila) {{
  const rondaId = fila.dataset.rondaId;
  const raw = localStorage.getItem(PREFIJO_STORAGE + rondaId);
  const checkbox = fila.querySelector('.check-hecho');
  const fechaCelda = document.getElementById('fecha-hecho-' + rondaId);
  if (raw) {{
    const info = JSON.parse(raw);
    checkbox.checked = true;
    fechaCelda.textContent = 'Completado el ' + info.fecha_hecho;
  }} else {{
    checkbox.checked = false;
    fechaCelda.textContent = '';
  }}
}}

function marcarHecho(rondaId, checkbox) {{
  const key = PREFIJO_STORAGE + rondaId;
  if (checkbox.checked) {{
    const ahora = new Date().toLocaleDateString('es-CL', {{ year: 'numeric', month: 'short', day: 'numeric' }});
    localStorage.setItem(key, JSON.stringify({{ fecha_hecho: ahora }}));
  }} else {{
    localStorage.removeItem(key);
  }}
  const fila = checkbox.closest('tr');
  pintarFilaHistorial(fila);
}}

document.querySelectorAll('table.historial tbody tr').forEach(pintarFilaHistorial);
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) != 4:
        print("Uso: python build_progress_artifact.py <preguntas_semana.json> <registro.json> <salida.html>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        preguntas_data = json.load(f)

    with open(sys.argv[2], "r", encoding="utf-8") as f:
        registro = json.load(f)

    # Agregar número de ronda al JSON actual basado en el registro
    preguntas_data["ronda_numero"] = len(registro)

    out = build_html(preguntas_data, registro)

    with open(sys.argv[3], "w", encoding="utf-8") as f:
        f.write(out)

    print(f"HTML generado: {sys.argv[3]}")


if __name__ == "__main__":
    main()
