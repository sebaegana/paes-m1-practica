#!/usr/bin/env python3
"""
Genera el panel interactivo PAES multi-materia: quiz + historial de rondas con progreso
persistente en localStorage (sin servidor).

Uso:
    python build_progress_artifact.py <registro.json> <salida.html>

<registro.json>: lista de rondas generadas, esquema:
[
  {"fecha": "2026-08-01", "ronda": 1, "materia": "matematica", "eje": "Numeros", "archivo_json": "..."},
  {"fecha": "2026-08-22", "ronda": 1, "materia": "biologia", "eje": "Celula", "archivo_json": "..."}
]
"""
import json
import sys
import html
from pathlib import Path


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
    materia = esc(record.get('materia', 'matematica'))
    ronda_id = f"{materia}-{record['fecha']}-{record['eje']}".replace(" ", "_")
    return f"""
      <tr data-ronda-id="{esc(ronda_id)}">
        <td>{esc(record.get('materia', 'matematica').capitalize())}</td>
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


def load_questions_for_record(record):
    """Carga las preguntas de un registro de ronda (si existen)."""
    try:
        materia = record.get('materia', 'matematica')
        archivo_json = record.get('archivo_json', f"{record.get('fecha', '')}.json")
        ronda_json_path = Path(__file__).parent.parent / "data" / "rondas" / materia / archivo_json
        if ronda_json_path.exists():
            with open(ronda_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return None


def build_html(registro):
    # Encontrar la última ronda de cada materia para determinar activas
    last_by_materia = {}
    for record in registro:
        materia = record.get('materia', 'matematica')
        if materia not in last_by_materia or record.get('ronda', 0) > last_by_materia[materia].get('ronda', 0):
            last_by_materia[materia] = record

    # Materias únicas
    materias = sorted(set(r.get('materia', 'matematica') for r in registro))

    # Generar barra lateral por materia + contenido
    sidebar_html = ""
    main_content = ""

    for i, record in enumerate(sorted(registro, key=lambda r: (r.get("materia", "matematica"), r.get("ronda", 0)))):
        materia = record.get('materia', 'matematica')
        ronda_num = record.get("ronda", i + 1)
        eje = esc(record.get("eje", ""))
        fecha_ronda = esc(record.get("fecha", ""))
        content_id = f"ronda-{materia}-{ronda_num}"
        is_active = record == last_by_materia.get(materia)
        active_class = "active" if is_active else ""

        # Item en sidebar (con data-materia para filtro JS)
        sidebar_html += f'      <div class="sidebar-item {active_class}" onclick="mostrarRonda(\'{content_id}\')" data-ronda="{content_id}" data-materia="{materia}">\n        <div class="sidebar-ronda">Round {ronda_num}</div>\n        <div class="sidebar-eje">{eje}</div>\n        <div class="sidebar-fecha">{fecha_ronda}</div>\n      </div>\n'

        # Cargar preguntas para esta ronda
        ronda_data = load_questions_for_record(record)
        if ronda_data:
            preguntas_html = "\n".join(
                render_question(i + 1, q) for i, q in enumerate(ronda_data.get("preguntas", []))
            )
            saludo = esc(ronda_data.get("saludo", ""))
            main_content += f'    <div class="ronda-content {active_class}" id="{content_id}">\n      <p class="saludo">{saludo}</p>\n{preguntas_html}\n    </div>\n'
        else:
            main_content += f'    <div class="ronda-content {active_class}" id="{content_id}"><p style="text-align:center;color:#999;padding:40px;">Preguntas de Round {ronda_num} ({eje}) - {fecha_ronda}</p></div>\n'

    # Historial de todas las rondas
    registro_ordenado = sorted(registro, key=lambda r: (r.get("materia", "matematica"), r.get("ronda", 0)), reverse=True)
    historial_html = "\n".join(render_historial_row(r) for r in registro_ordenado)

    # Encontrar última ronda activab para mostrar datos en el header
    last_record = last_by_materia.get('matematica') if last_by_materia else None
    if not last_record and registro:
        last_record = sorted(registro, key=lambda r: r.get("ronda", 0))[-1]

    header_info = ""
    if last_record:
        header_info = f"Última generación: {esc(last_record.get('fecha', ''))} · Eje ({esc(last_record.get('materia', 'matematica').capitalize())}): {esc(last_record.get('eje', ''))}"
    else:
        header_info = "Bienvenido a la plataforma de práctica PAES"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>PAES - Panel de práctica multi-materia</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; padding: 0;
         color: #1d1d1f; background: #fafafa; display: flex; min-height: 100vh; }}
  .container {{ display: flex; width: 100%; }}
  .sidebar {{ width: 280px; background: #fff; border-right: 1px solid #e2e2e2; overflow-y: auto;
              padding: 0; position: relative; display: flex; flex-direction: column; }}
  .materia-tabs {{ display: flex; gap: 0; padding: 12px 0 0 0; border-bottom: 1px solid #e2e2e2;
                   position: sticky; top: 0; background: #fff; }}
  .materia-tab {{ flex: 1; padding: 8px 12px; text-align: center; cursor: pointer; border: none;
                  background: #f5f5f7; color: #666; font-weight: 500; font-size: 0.85em;
                  transition: all 0.2s; border-bottom: 2px solid transparent; }}
  .materia-tab:hover {{ background: #eee; }}
  .materia-tab.active {{ background: #fff; color: #6b6bd6; border-bottom-color: #6b6bd6; }}
  .sidebar-items-container {{ flex: 1; overflow-y: auto; padding: 12px 0; }}
  .sidebar-header {{ padding: 0 16px 8px; margin-bottom: 8px; }}
  .sidebar-title {{ font-size: 0.75em; font-weight: 600; color: #999; text-transform: uppercase;
                    letter-spacing: 0.05em; margin: 0; }}
  .sidebar-item {{ padding: 12px 16px; margin: 0 8px; border-radius: 8px; cursor: pointer;
                   transition: all 0.2s; border-left: 3px solid transparent; display: none; }}
  .sidebar-item.visible {{ display: block; }}
  .sidebar-item:hover {{ background: #f2f2f7; }}
  .sidebar-item.active {{ background: #eeeeff; border-left-color: #6b6bd6; }}
  .sidebar-ronda {{ font-weight: 600; font-size: 0.95em; margin-bottom: 4px; }}
  .sidebar-eje {{ font-size: 0.85em; color: #666; margin-bottom: 2px; }}
  .sidebar-fecha {{ font-size: 0.75em; color: #999; }}
  .main {{ flex: 1; overflow-y: auto; padding: 24px 32px; }}
  .header {{ margin-bottom: 24px; }}
  h1 {{ font-size: 1.4em; margin: 0 0 8px; }}
  .actualizado {{ font-size: 0.8em; color: #999; margin: 0; }}
  .saludo {{ color: #444; margin-bottom: 24px; font-size: 1em; line-height: 1.5; }}
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
  .ronda-content {{ display: none; }}
  .ronda-content.active {{ display: block; }}
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
  @media (max-width: 768px) {{
    .container {{ flex-direction: column; }}
    .sidebar {{ width: 100%; border-right: none; border-bottom: 1px solid #e2e2e2; max-height: auto; }}
    .materia-tabs {{ padding: 8px 0; }}
    .main {{ padding: 16px; }}
  }}
</style>
</head>
<body>
  <div class="container">
    <div class="sidebar">
      <div class="materia-tabs">
        <button class="materia-tab active" onclick="cambiarMateria('matematica')">Matemática</button>
        <button class="materia-tab" onclick="cambiarMateria('biologia')">Biología</button>
      </div>
      <div class="sidebar-items-container">
        <div class="sidebar-header">
          <p class="sidebar-title" id="titulo-materia">Rondas Matemática</p>
        </div>
{sidebar_html}      </div>
    </div>
    <div class="main">
      <div class="header">
        <h1>PAES &mdash; Panel de práctica</h1>
        <p class="actualizado">{header_info}</p>
      </div>
{main_content}
      <h2>Progreso</h2>
      <table class="historial">
        <thead>
          <tr><th>Materia</th><th>Ronda</th><th>Fecha</th><th>Eje</th><th>Estado</th><th></th></tr>
        </thead>
        <tbody>
          {historial_html}
        </tbody>
      </table>
    </div>
  </div>

<script>
function cambiarMateria(materia) {{
  // Actualizar tabs
  document.querySelectorAll('.materia-tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');

  // Actualizar sidebar items visibles
  document.querySelectorAll('.sidebar-item').forEach(item => {{
    if (item.dataset.materia === materia) {{
      item.classList.add('visible');
    }} else {{
      item.classList.remove('visible');
    }}
  }});

  // Actualizar título del sidebar
  const titulo = materia === 'matematica' ? 'Rondas Matemática' : 'Rondas Biología';
  document.getElementById('titulo-materia').textContent = titulo;

  // Mostrar primera ronda de la materia
  const firstItem = document.querySelector(`.sidebar-item[data-materia="{{materia}}"]`);
  if (firstItem) {{
    firstItem.click();
  }}
}}

function mostrarRonda(contentId) {{
  const allContent = document.querySelectorAll('.ronda-content');
  const allItems = document.querySelectorAll('.sidebar-item');
  allContent.forEach(c => c.classList.remove('active'));
  allItems.forEach(i => i.classList.remove('active'));
  document.getElementById(contentId).classList.add('active');
  document.querySelector('[data-ronda="' + contentId + '"]').classList.add('active');
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

// Inicializar: mostrar Matemática por defecto
document.querySelectorAll('.sidebar-item').forEach(item => {{
  if (item.dataset.materia === 'matematica') {{
    item.classList.add('visible');
  }}
}});

// Restaurar progreso guardado
document.querySelectorAll('table.historial tbody tr').forEach(pintarFilaHistorial);

// Mostrar primera ronda (Matemática)
const firstRonda = document.querySelector('.sidebar-item[data-materia="matematica"]');
if (firstRonda) {{
  setTimeout(() => firstRonda.click(), 50);
}}
</script>
    </div>
  </div>
</body>
</html>
"""


def main():
    if len(sys.argv) != 3:
        print("Uso: python build_progress_artifact.py <registro.json> <salida.html>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        registro = json.load(f)

    out = build_html(registro)

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(out)

    print(f"HTML generado: {sys.argv[2]}")


if __name__ == "__main__":
    main()
