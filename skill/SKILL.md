---
name: paes-m1-prep
description: Genera un set semanal de 5 preguntas originales de práctica para la PAES de Competencia Matemática 1 (M1) en Chile, rotando por eje temático (Números, Álgebra y funciones, Geometría, Probabilidad y estadística), listo para enviarse por correo con soluciones al final. Usa esta skill siempre que el usuario mencione preparación PAES, prueba de matemática M1, DEMRE, "preguntas de práctica para la PAES", quiera un correo periódico de estudio, o pida generar/actualizar el set de preguntas semanal de matemática. También úsala si el usuario pregunta por el estado de la rotación de ejes o quiere ajustar la dificultad/cantidad de un envío ya configurado.
---

# Generador de preguntas de práctica PAES M1

## Por qué existe esta skill

El usuario quiere recibir, cada cierto tiempo, un set corto de preguntas de matemática
tipo PAES M1 para practicar, con soluciones explicadas. Esta skill estandariza cómo se
genera ese set para que sea consistente semana a semana: mismo formato, cobertura
rotativa de los 4 ejes de la prueba, y sin depender de copiar material real del DEMRE
(que está expresamente prohibido reutilizar para generar contenido con IA).

Antes de escribir preguntas, lee `references/temario-m1.md` — ahí está el resumen oficial
de ejes, unidades y habilidades que sirve de marco de contenido. Lee también
`references/formato-pregunta.md` — define el formato exacto que debe mantenerse igual en
todos los envíos.

## Flujo para generar un set

1. **Determinar el eje de esta ronda.** Corre el script de rotación pasándole la ruta del
   archivo de estado (por defecto `paes_m1_state.json` en la carpeta donde se están
   guardando los sets, p. ej. `lucas_classroom/paes_m1/paes_m1_state.json`):

   ```
   python scripts/rotar_eje.py <carpeta_destino>/paes_m1_state.json
   ```

   Esto devuelve el eje que toca hoy y actualiza el historial. Si el usuario no tiene
   todavía una carpeta de destino definida, pregúntale dónde quiere guardar los sets (o
   usa la carpeta de trabajo actual) antes de crear el archivo de estado — así la
   rotación queda anclada a un solo lugar y no se reinicia por accidente.

   Si el usuario pide explícitamente un eje distinto al que toca por rotación (p. ej.
   "esta semana quiero solo álgebra"), respeta su pedido pero no actualices el índice de
   rotación normal — trátalo como una ronda extra fuera de ciclo.

2. **Elegir unidades y habilidades.** Dentro del eje asignado, elige 1-2 unidades
   temáticas de `references/temario-m1.md` (no hace falta cubrir todas las unidades del
   eje en un solo set de 5 preguntas — la prueba real tampoco lo hace). Distribuye las 5
   preguntas entre al menos 2-3 habilidades distintas (Resolver problemas, Modelar,
   Representar, Argumentar) para no repetir siempre el mismo tipo de razonamiento.

3. **Escribir 5 preguntas originales.** Cada una en el formato exacto de
   `references/formato-pregunta.md`: encabezado con ID/eje/unidad/habilidad/dificultad/
   contexto, enunciado con datos concretos, 4 alternativas (A-D), alternativa correcta, y
   solución paso a paso. Usa una distribución de dificultad de 2 Básico / 2 Intermedio / 1
   Avanzado salvo que el usuario pida otra cosa. Las preguntas deben ser inéditas —
   inspiradas en el estilo y contenido del temario, nunca copiadas ni parafraseadas de
   pruebas oficiales reales del DEMRE.

4. **Armar el envío como HTML interactivo.** El entregable NO es texto plano — es una
   página HTML donde cada pregunta tiene sus 4 alternativas como botones clicables y un
   botón "Ver respuesta" que revela la solución (así la persona intenta responder antes
   de ver la respuesta). Arma el JSON de las 5 preguntas según el esquema de
   `references/formato-pregunta.md` y genera el HTML con:

   ```
   python scripts/build_quiz_html.py <preguntas.json> <salida.html>
   ```

   No reescribas a mano el HTML/CSS/JS del quiz — el script ya lo resuelve de forma
   consistente entre envíos. Guarda tanto el JSON de entrada como el HTML de salida en la
   carpeta de destino, con nombre `paes-m1-<AAAA-MM-DD>.html` (y su `.json` homónimo).

5. **Entregar.** Si esto se envía por correo, el HTML interactivo va como **adjunto**
   (nunca pegado inline en el cuerpo del correo) porque casi ningún cliente de correo
   ejecuta JavaScript embebido — ver la nota al final de `references/formato-pregunta.md`.
   El cuerpo del correo es un texto corto (saludo + qué eje toca esta semana) que invita a
   abrir el adjunto. Si el usuario quiere que esto se envíe automáticamente cada cierto
   número de días, ese es un paso aparte: usa la skill `schedule` para programar la tarea
   recurrente (ej. cada 7 días) que invoque esta misma skill y envíe el HTML resultante
   por Gmail — no asumas que ya existe esa programación, confírmalo con el usuario.

## Errores comunes a evitar

- No inventes datos del temario que no estén en `references/temario-m1.md` — si necesitas
  un tema que no aparece ahí, dile al usuario que no está cubierto por el temario oficial
  M1 (podría corresponder a M2).
- No generes menos o más de 4 alternativas por pregunta, ni dejes ambigüedad sobre cuál es
  la correcta.
- No repitas el mismo eje dos rondas seguidas si la rotación normal indica que toca otro
  (a menos que el usuario lo pida explícitamente, ver paso 1).
- No muestres la alternativa correcta ni la solución antes del separador — el objetivo es
  que la persona intente resolver primero.
