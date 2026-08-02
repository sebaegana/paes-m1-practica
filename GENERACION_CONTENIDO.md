# Generar las 38 unidades de contenido

La arquitectura ya está lista. Ahora necesitas llenar `data/rondas/{materia}/{unidad-slug}.json` con 5 preguntas originales por unidad.

## Estructura de un archivo de ronda

```json
{
  "eje": "Nombre del eje",
  "unidad": "Nombre de la unidad",
  "saludo": "1-2 líneas saludando y explicando esta unidad",
  "preguntas": [
    {
      "id": "SIGLA-ABREV-01",
      "eje": "...",
      "unidad": "...",
      "habilidad": "Resolver problemas|Comprender|Aplicar|Analizar",
      "dificultad": "Básico|Intermedio|Avanzado",
      "contexto": "Cotidiano|Matemático",
      "enunciado": "...",
      "alternativas": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correcta": "A|B|C|D",
      "explicacion": {
        "concepto": "1-2 frases del concepto clave",
        "pasos": ["Paso 1: ...", "Paso 2: ...", "Paso 3: ..."]
      }
    },
    ...
  ]
}
```

**Importante:** NO incluyas los campos `fecha`, `eje_semana`, `cobertura` ni `proxima_semana`.

## IDs de pregunta (siglas por materia/eje)

**Matemática:**
- Números → NUM
- Álgebra y funciones → ALG
- Geometría → GEO
- Probabilidad y estadística → PRO

**Biología:**
- Célula → CEL
- Herencia y variabilidad genética → GEN
- Evolución y biodiversidad → EVO
- Organismo y ambiente → ECO
- Cuerpo humano y salud → SAL

Ejemplo: `M1-NUM-01` (Matemática 1, Números, pregunta 01)

## Flujo de generación

### Opción A: Manual (Recomendado para empezar)

```bash
# 1. Crear un JSON de 5 preguntas para una unidad
# Ej: data/rondas/matematica/porcentaje.json

# 2. Registrarlo en el catálogo
python skill/scripts/registrar_contenido.py \
  data/catalogo_contenido.json \
  matematica \
  "Números" \
  "Porcentaje" \
  data/rondas/matematica/porcentaje.json

# 3. Regenerar HTML
python skill/scripts/build_progress_artifact.py \
  data/catalogo_contenido.json \
  docs/index.html

# 4. Abrir docs/index.html en navegador para probar
```

### Opción B: Con Claude (En lotes, en sesiones posteriores)

Pedirle a Claude que genere 3-4 unidades a la vez:

```
Genera JSON para estas 3 unidades de Biología:
1. Transporte celular
2. Metabolismo celular  
3. Reproducción celular

Usa el esquema [...]. 5 preguntas por unidad, dificultad 2B+2I+1A.
Lee temario-biologia.md para contexto. IDs empiezan con BIO-CEL-.
```

Luego:

```bash
python skill/scripts/registrar_contenido.py \
  data/catalogo_contenido.json biologia "Célula" \
  "Transporte celular" data/rondas/biologia/transporte-celular.json

# ... (registrar el resto)

python skill/scripts/build_progress_artifact.py \
  data/catalogo_contenido.json docs/index.html
```

## Checklist: 38 unidades

### Matemática (15 unidades)
- [ ] Números enteros y racionales
- [ ] Porcentaje
- [ ] Potencias y raíces
- [ ] Expresiones algebraicas
- [ ] Proporcionalidad
- [ ] Ecuaciones e inecuaciones
- [ ] Sistemas de ecuaciones
- [ ] Función lineal y afín
- [ ] Función cuadrática
- [ ] Figuras geométricas
- [ ] Cuerpos geométricos
- [ ] Transformaciones isométricas
- [ ] Representación de datos
- [ ] Medidas de posición
- [ ] Probabilidades

### Biología (23 unidades)

**Célula (4)**
- [ ] Estructura y función celular
- [ ] Transporte celular
- [ ] Metabolismo celular
- [ ] Reproducción celular

**Herencia y variabilidad genética (4)**
- [ ] Fundamentos de genética
- [ ] Leyes de Mendel
- [ ] Cromosomas y herencia
- [ ] Mutaciones y variabilidad

**Evolución y biodiversidad (4)**
- [ ] Teoría de la evolución
- [ ] Evidencias de evolución
- [ ] Historia de la vida
- [ ] Clasificación biológica

**Organismo y ambiente (5)**
- [ ] Niveles de organización ecológica
- [ ] Relaciones interespecíficas
- [ ] Flujo de energía y ciclos
- [ ] Dinámicas de población
- [ ] Impacto humano y conservación

**Cuerpo humano y salud (6)**
- [ ] Sistemas de órganos
- [ ] Nutrición y digestión
- [ ] Respiración y circulación
- [ ] Respuesta y regulación
- [ ] Reproducción humana
- [ ] Salud y enfermedad

## Validación rápida

Después de agregar un JSON, valida que sea JSON válido:

```bash
python -m json.tool data/rondas/matematica/porcentaje.json > /dev/null && \
  echo "✅ JSON válido" || echo "❌ Error de JSON"
```

Luego abre `docs/index.html` en el navegador y verifica:
- El título de la unidad aparece en el sidebar
- Las 5 preguntas cargan
- Puedes seleccionar alternativas, ver respuesta, ver explicación
- El checkbox "Hecho" persiste al recargar

## Notas

- No hay "fechas" ni "números de ronda": cada unidad es independiente.
- El progreso se guarda como `paes_progreso_{materia}-{unidad}` en localStorage.
- El catálogo ordena por materia → eje → unidad (orden del JSON).
- Cambios al catálogo no afectan localStorage (clave de progreso es por unidad, no por orden).
