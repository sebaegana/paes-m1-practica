# Formato estándar de pregunta (acordado con el usuario)

Cada pregunta generada debe traer estos campos, siempre en este orden. Este formato no
cambia entre envíos — es lo que permite comparar semanas y llevar registro de cobertura.

```
ID: M1-<EJE-abrev>-<AAAA-MM-DD>-<secuencia de 2 dígitos>
Eje temático: <uno de los 4 ejes>
Unidad temática: <unidad específica dentro del eje, según references/temario-m1.md>
Habilidad: <Resolver problemas | Modelar | Representar | Argumentar>
Dificultad: <Básico | Intermedio | Avanzado>
Contexto: <Cotidiano | Matemático>

Enunciado:
<texto de la pregunta, con datos numéricos concretos>

A) <alternativa>
B) <alternativa>
C) <alternativa>
D) <alternativa>

Alternativa correcta: <A|B|C|D>

Explicación:
Concepto clave: <qué idea/contenido matemático hay que dominar para resolver esto>
Pasos:
1. <paso del razonamiento>
2. <paso del razonamiento>
3. <paso final / conclusión>
```

(Este "Explicación" con concepto + pasos es lo que luego se traduce 1:1 al campo
`explicacion` del JSON que consume `scripts/build_quiz_html.py` — ver más abajo.)

Abreviaturas de eje para el ID (depende de la materia):
**Matemática:** NUM (Números), ALG (Álgebra y funciones), GEO (Geometría), PRO (Probabilidad y estadística)
**Biología:** CEL (Célula), GEN (Herencia genética), EVO (Evolución), ECO (Ecología), SAL (Cuerpo y salud)

## Distribución de dificultad sugerida por set de 5 preguntas

2 Básico, 2 Intermedio, 1 Avanzado — refleja a grandes rasgos la progresión de una prueba
real. Ajustable si el usuario pide reforzar un nivel específico.

## Resumen de cobertura (al final de cada set)

Después de las 5 preguntas y sus soluciones, agregar un bloque corto:

```
--- Cobertura de este set ---
Eje: <eje de esta semana>
Unidades cubiertas: <lista>
Habilidades cubiertas: <lista>
Próxima semana: <eje siguiente en la rotación>
```

## Entregable: HTML interactivo (no markdown plano)

El usuario pidió que el set final sea una interfaz donde se pueda seleccionar la
alternativa haciendo clic, y que la respuesta/solución quede detrás de un botón "Ver
respuesta" (no visible de entrada). Para esto NO se escribe el envío a mano en HTML —
se arma un JSON con los datos de las 5 preguntas (ver esquema abajo) y se genera el HTML
con `scripts/build_quiz_html.py`, que ya trae los botones, el estado de seleccionada/
correcta/incorrecta y el toggle de la solución en JavaScript plano (sin dependencias
externas, sin localStorage). Cada pregunta tiene dos botones independientes, no uno solo:
"Ver respuesta" (marca la alternativa correcta/incorrecta) y "Ver explicación" (revela el
razonamiento paso a paso). Se pueden abrir en cualquier orden, y ninguno se muestra de
entrada.

```
python scripts/build_quiz_html.py <preguntas.json> <salida.html>
```

Esquema del JSON de entrada (un objeto con las 5 preguntas):

```json
{
  "fecha": "AAAA-MM-DD",
  "eje_semana": "<eje de esta ronda>",
  "saludo": "1-2 líneas: qué eje toca y por qué",
  "preguntas": [
    {
      "id": "M1-<EJE>-<fecha>-01",
      "eje": "...", "unidad": "...", "habilidad": "...",
      "dificultad": "Básico|Intermedio|Avanzado", "contexto": "Cotidiano|Matemático",
      "enunciado": "...",
      "alternativas": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correcta": "A|B|C|D",
      "explicacion": {
        "concepto": "1-2 frases: qué idea o contenido matemático hay que dominar para resolver esta pregunta (no el cálculo en sí, sino el concepto detrás)",
        "pasos": ["Paso 1: ...", "Paso 2: ...", "Paso final (conclusión / por qué las otras alternativas están mal si aporta): ..."]
      }
    }
  ],
  "cobertura": {"unidades": ["..."], "habilidades": ["..."], "proxima_semana": "..."}
}
```

Un ejemplo completo y funcionando está en `evals/muestra-preguntas.json`.

### Sobre el envío por correo

La mayoría de los clientes de correo bloquean JavaScript dentro del cuerpo del email, así
que el HTML interactivo no debe pegarse inline en el correo — debe ir como **archivo
adjunto** (o como link a un archivo guardado en la carpeta de destino) que la persona abre
en su navegador. El cuerpo del correo mismo puede ser un texto corto: saludo, qué eje toca
esta semana, y la indicación de abrir el adjunto/enlace para responder.
