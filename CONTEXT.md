# Contexto: PAES M1 — App de práctica semanal

Este archivo es el punto de partida para continuar este proyecto desde Claude Code (o
cualquier otra sesión). Empezó en Cowork; se traspasa acá porque Cowork no tiene acceso
de red para hacer `git push` ni llamar a la API de GitHub (ver sección "Bloqueo técnico").

## Objetivo

Sebastián quiere una app de preguntas de práctica para la PAES de Competencia Matemática 1
(M1, Chile): un set semanal de 5 preguntas originales (inspiradas en el temario oficial del
DEMRE, nunca copiadas de pruebas reales), presentadas como quiz interactivo (clic en la
alternativa, botón para ver respuesta, botón separado para ver explicación paso a paso), con
tracking de progreso (qué rondas se completaron), rotando por los 4 ejes de la prueba, y
accesible también desde el celular — de ahí que se decidiera publicarla en GitHub Pages.

## Decisiones tomadas (no las reabras sin razón)

- **Formato de pregunta estándar**: ID, eje, unidad temática, habilidad (Resolver problemas /
  Modelar / Representar / Argumentar), dificultad, contexto, enunciado, 4 alternativas (A-D,
  nunca 5), alternativa correcta, y explicación estructurada en `concepto` + `pasos` (lista).
  Detalle completo en `skill/references/formato-pregunta.md`.
- **Rotación de ejes**: fija, en este orden — Números → Álgebra y funciones → Geometría →
  Probabilidad y estadística → se repite. El estado vive en `paes_m1_state.json` (ver más
  abajo) y lo actualiza `skill/scripts/rotar_eje.py`.
- **Distribución de dificultad** por set de 5: 2 Básico, 2 Intermedio, 1 Avanzado (ajustable
  si el usuario pide reforzar algo puntual).
- **Entregable = HTML interactivo**, nunca texto plano ni Markdown con la respuesta a la
  vista. Cada pregunta tiene alternativas clicables y DOS botones independientes, cada uno
  toggle (apretar de nuevo resetea/oculta):
  - "Ver respuesta" → marca la alternativa correcta/incorrecta.
  - "Ver explicación paso a paso" → despliega concepto clave + pasos numerados.
  Esto está resuelto en `skill/scripts/build_quiz_html.py` (versión standalone) y
  `skill/scripts/build_progress_artifact.py` (versión con historial/progreso). No reescribir
  este HTML a mano — usar los scripts.
- **Tracking de progreso**: decisión fue "panel simple" (no tracking por pregunta/eje con
  estadísticas). Se implementó con `localStorage` en el navegador — cada ronda tiene una fila
  con checkbox "Hecho" que guarda fecha de completado. Limitación conocida y aceptada: el
  progreso es por navegador/dispositivo, no hay backend compartido. Si más adelante se quiere
  sync entre dispositivos, eso requiere agregar una base de datos (ej. Supabase) — no se ha
  hecho, es una decisión pendiente si el usuario lo pide.
- **DEMRE prohíbe** usar su material real (pruebas oficiales, selección de preguntas) para
  entrenar/mejorar modelos de IA — por eso las preguntas son siempre originales, inspiradas
  solo en el temario público (`skill/references/temario-m1.md`), nunca copiadas.
- **Gmail**: el conector disponible en Cowork solo puede crear borradores, no enviar correos
  reales. Se usa como "recordatorio" (borrador), no como envío automático.
- **Hosting elegido: GitHub Pages**, no Render/Vercel (el usuario prefirió GitHub explícitamente
  después de que le mostré que Render tenía herramientas de deploy reales vía MCP — ver
  bloqueo técnico abajo sobre por qué no se pudo automatizar del todo desde Cowork).

## Estado actual (qué ya está hecho)

- Repo de GitHub creado por el usuario: **https://github.com/sebaegana/paes-m1-practica**
  (público, vacío, `default_branch: main`, `has_pages: false` a la fecha de este documento).
- Token personal (fine-grained, scope solo a este repo, permiso Contents: Read and write)
  guardado en: `../paes_m1/.github_config.json` (mismo nivel que esta carpeta, dentro de
  `lucas_classroom/paes_m1/`). **Es un secreto en texto plano — NO debe subirse al repo.**
  Si inicializas git en `sitio/` o en este repo, agrega `.github_config.json` a `.gitignore`
  antes del primer commit.
- Round 1 ya generado con datos reales (no es solo una muestra de prueba), guardado en
  `../paes_m1/`:
  - `paes_m1_state.json` — estado de rotación (ronda 1 = Números, próxima = Álgebra y funciones).
  - `paes-m1-2026-08-01.json` — las 5 preguntas de la ronda 1 (Porcentaje + Números enteros
    y racionales).
  - `paes-m1-2026-08-01.html` — versión HTML standalone de esa ronda.
  - `registro_generaciones.json` — bitácora de generaciones (ronda, fecha, eje, archivos,
    id del borrador de Gmail creado).
- `sitio/index.html` en esta misma carpeta: el HTML del panel completo (quiz de la ronda 1 +
  tabla de progreso), generado con `skill/scripts/build_progress_artifact.py`. Es el
  candidato a subir como página principal del repo para GitHub Pages.
- Ya existe un Cowork artifact llamado `paes-m1-progreso` con este mismo contenido (vive
  dentro de Cowork, no en la web pública) — se puede seguir usando en paralelo o deprecar
  una vez que el sitio en GitHub Pages esté funcionando.
- La skill completa `paes-m1-prep` (SKILL.md + references + scripts) está copiada en
  `skill/` dentro de esta misma carpeta de contexto. **Ojo:** esta skill todavía NO se guardó
  con la herramienta `save_skill` de Cowork (el usuario interrumpió esa acción una vez);
  por eso se copió aquí a mano, para no perderla entre sesiones.

## Bloqueo técnico encontrado (importante)

El sandbox de Cowork donde se hizo este trabajo **no tiene acceso de red general**: se
probó `curl`/`git` contra `api.github.com`, `raw.githubusercontent.com` y `codeload.github.com`
y todas fallan (timeout / connection reset). Solo `github.com` a secas responde, y ni así
alcanza para `git push` (protocolo HTTP smart de git tampoco funcionó). La herramienta de
fetch interna de Cowork sí pudo hacer un GET simple a `api.github.com` (confirmar que el
repo existe), pero no soporta headers de autenticación ni verbos POST/PUT — o sea, sirve
para leer, no para escribir.

Por eso se decidió continuar desde **Claude Code**, que corre con acceso de red completo del
computador del usuario y puede hacer `git push` y llamar a la API de GitHub normalmente.

## Próximos pasos concretos para Claude Code

1. Leer `../paes_m1/.github_config.json` para obtener usuario, repo y token.
2. Clonar o inicializar `https://github.com/sebaegana/paes-m1-practica` en algún directorio
   de trabajo (fuera de `lucas_classroom` si se quiere evitar mezclar con OneDrive/Downloads,
   o dentro si el usuario prefiere tenerlo ahí — preguntarle).
3. Agregar `.gitignore` que excluya cualquier archivo de config/token antes del primer commit.
4. Copiar `sitio/index.html` como página principal del repo (renombrar si hace falta) y hacer
   push a `main`.
5. Habilitar GitHub Pages (vía API `PUT /repos/sebaegana/paes-m1-practica/pages` con
   `{"source": {"branch": "main", "path": "/"}}`, o vía la UI en Settings → Pages).
6. Verificar que el sitio quede accesible en `https://sebaegana.github.io/paes-m1-practica/`.
7. Definir el mecanismo de actualización semanal automática (ronda 2 = Álgebra y funciones,
   sábado siguiente a las 19:00 según lo pedido originalmente). Un cron job local, una GitHub
   Action programada, o correr la skill manualmente y hacer push — a decidir con el usuario,
   ya que los scheduled tasks de Cowork dependen de que la app esté abierta y no tienen
   acceso de red para publicar de todas formas.
8. Revisar con el usuario si el tracking de progreso por navegador (localStorage, no
   compartido entre dispositivos) sigue siendo suficiente ahora que el sitio es multi-dispositivo,
   o si vale la pena agregar un backend simple.
9. Considerar guardar formalmente la skill `paes-m1-prep` (la copia está en `skill/`) con el
   mecanismo de skills que corresponda en el entorno donde se continúe.

## Mapa de archivos

```
lucas_classroom/
├── paes-m1-contexto/          <- esta carpeta (contexto para retomar)
│   ├── CONTEXT.md             <- este archivo
│   ├── skill/                 <- copia completa de la skill paes-m1-prep
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── temario-m1.md
│   │   │   └── formato-pregunta.md
│   │   ├── scripts/
│   │   │   ├── rotar_eje.py
│   │   │   ├── build_quiz_html.py
│   │   │   ├── build_progress_artifact.py
│   │   │   └── registrar_generacion.py
│   │   └── evals/muestra-preguntas.json
│   └── sitio/
│       └── index.html         <- candidato a pagina principal de GitHub Pages
└── paes_m1/                   <- datos reales generados (no tocar a mano si se puede evitar)
    ├── .github_config.json    <- SECRETO: usuario/repo/token de GitHub, no commitear
    ├── paes_m1_state.json
    ├── registro_generaciones.json
    ├── paes-m1-2026-08-01.json
    └── paes-m1-2026-08-01.html
```
