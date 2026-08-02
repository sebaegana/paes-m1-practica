# Arquitectura - PAES Multi-materia

**Plataforma unificada de práctica para múltiples materias PAES (Matemática, Biología, etc.).**

---

## 🏗️ Arquitectura general

```
┌──────────────────────────────────────────────────────────────┐
│                     GitHub Pages (Hosting)                   │
│               https://sebaegana.github.io/paes-m1-practica/  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    docs/index.html                     │  │
│  │   (HTML + CSS + JS inlined, sin dependencias)          │  │
│  │                                                        │  │
│  │  - Selector de materia (tabs: Matemática, Biología)   │  │
│  │  - Sidebar por materia (4 rondas Mate, 1 Bio, etc.)   │  │
│  │  - Quiz interactivo (5 preguntas por ronda)           │  │
│  │  - Progress tracking (localStorage, namespaceado)     │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         ↑
         │ (git push)
         │
┌──────────────────────────────────────────────────────────────┐
│                   GitHub Repository                          │
│             sebaegana/paes-m1-practica (main)                │
│                                                              │
│  ├─ data/                   (Datos y generaciones)           │
│  │  ├─ estado_matematica.json                               │
│  │  ├─ estado_biologia.json                                 │
│  │  ├─ registro_generaciones.json (incluye "materia")       │
│  │  └─ rondas/                                              │
│  │     ├─ matematica/  (1-N.json)                           │
│  │     └─ biologia/    (1-N.json)                           │
│  │                                                          │
│  ├─ docs/                   (Sitio público)                  │
│  ├─ skill/                  (Scripts de generación)          │
│  └─ .github/workflows/      (Automatización)                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         ↑
         │ (offline: generar_ronda.py --materia X)
         │ (online: GitHub Actions)
         │
┌──────────────────────────────────────────────────────────────┐
│                  Generador de Contenido                      │
│                                                              │
│  generar_ronda.py --materia {matematica,biologia}            │
│    ├─ Rota ejes según materia (rotar_eje.py)                │
│    ├─ Lee temario + referencias (materia-específico)         │
│    ├─ Llama a Claude API                                     │
│    ├─ Genera JSON de preguntas                               │
│    ├─ Registra en historial (registrar_generacion.py)        │
│    └─ Regenera docs/index.html multi-materia                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 💾 Persistencia de datos

### Cliente (Frontend)
```
Browser (Chrome/Firefox/Safari/etc.)
  └─ localStorage
     ├─ paes_m1_progreso_matematica-2026-08-01-Numeros
     │  └─ {"fecha_hecho": "1 ago 2026"}
     ├─ paes_m1_progreso_matematica-2026-08-08-Algebra_y_funciones
     │  └─ {"fecha_hecho": "2 ago 2026"}
     ├─ paes_m1_progreso_matematica-2026-08-15-Geometria
     │  └─ null (no completada)
     └─ paes_m1_progreso_biologia-2026-08-22-Celula
        └─ null (no completada)
```

**Cambio respecto a versión anterior:**
- Las claves de localStorage ahora incluyen la materia como prefijo (p. ej. `matematica-` antes de fecha+eje)
- Permite tener progreso independiente por materia sin conflictos de keys

**Ventajas:**
- ✅ Sin servidor (0 costo hosting)
- ✅ Offline-first (funciona sin internet)
- ✅ Privado (datos solo locales)
- ✅ Instantáneo (acceso local)

**Limitaciones:**
- ❌ No sincroniza entre dispositivos
- ❌ Perdido si limpias datos del navegador
- ❌ ~5-10MB de límite por sitio

### Servidor (Backend) - FUTURO
Cuando agregues sincronización (Fase 1):

```
Base de datos (Supabase/Firebase/PostgreSQL)
  └─ user_progress table
     ├─ user_id (email o anónimo)
     ├─ round_number
     ├─ completed_at
     └─ timestamp

API (Node.js/Python/Go)
  ├─ GET /api/progress/:user_id
  ├─ POST /api/progress
  └─ PATCH /api/progress/:id
```

---

## 📝 Formato de datos

### Pregunta JSON
```json
{
  "id": "M1-NUM-2026-08-01-01",
  "eje": "Numeros",
  "unidad": "Porcentaje",
  "habilidad": "Resolver problemas",
  "dificultad": "Básico",
  "contexto": "Cotidiano",
  "enunciado": "Una polera cuesta...",
  "alternativas": {
    "A": "$11.000",
    "B": "$12.000",
    "C": "$13.000",
    "D": "$3.000"
  },
  "correcta": "B",
  "explicacion": {
    "concepto": "Descuentos en precios...",
    "pasos": [
      "Paso 1: ...",
      "Paso 2: ...",
      "Paso final: ..."
    ]
  }
}
```

### Ronda completa
```json
{
  "fecha": "2026-08-22",
  "eje_semana": "Celula",
  "saludo": "¡Hola! Esta semana...",
  "preguntas": [...],
  "cobertura": {
    "unidades": ["Estructura celular", "Transporte celular"],
    "habilidades": ["Reconocer y recordar", "Comprender"],
    "proxima_semana": "Herencia y variabilidad genetica"
  }
}
```

**Nota:** El campo `materia` está en `registro_generaciones.json` (ver abajo), no en los JSONs de preguntas.

---

## 🔄 Rotación de ejes (por materia)

Archivos: `data/estado_matematica.json` y `data/estado_biologia.json`

```json
{
  "history": [
    { "fecha": "2026-08-01", "eje": "Numeros" },
    { "fecha": "2026-08-08", "eje": "Algebra y funciones" }
  ],
  "last_eje_index": 1
}
```

**Ciclos por materia:**

Matemática:
```
0 → Números
1 → Álgebra y funciones
2 → Geometría
3 → Probabilidad y estadística
0 → Números (repite)
```

Biología:
```
0 → Célula
1 → Herencia y variabilidad genética
2 → Evolución y biodiversidad
3 → Organismo y ambiente
4 → Cuerpo humano y salud
0 → Célula (repite)
```

Script: `skill/scripts/rotar_eje.py <materia> <ruta_estado.json>`
- Recibe materia como parámetro (p. ej. "biologia")
- Lee el índice actual del archivo de estado de esa materia
- Calcula el siguiente eje dentro de la lista de ejes de esa materia
- Actualiza el archivo de estado
- Retorna eje asignado

---

## 🛠️ Flujo de generación (multi-materia)

### Generación manual (probado: Rounds 1-3 Mate, Round 1 Bio)
```bash
# Para Biología (ejemplo):
1. Crear JSON: data/rondas/biologia/2026-08-22.json (5 preguntas)
2. Registrar: python skill/scripts/registrar_generacion.py \
     data/registro_generaciones.json biologia "Celula" \
     data/rondas/biologia/2026-08-22.json ...
3. Construir HTML: python skill/scripts/build_progress_artifact.py \
     data/registro_generaciones.json docs/index.html
4. Git push
```

### Generación automática (futuro, actualmente solo Matemática)
```bash
1. GitHub Actions dispara cron (sábado 19:00 UTC)
2. generar_ronda.py (sin --materia = default matematica):
   - Rota eje (rotar_eje.py matematica ...)
   - Lee temario-m1.md
   - Llama a Claude API
   - Genera JSON en data/rondas/matematica/
   - Registra en historial
   - Regenera HTML con todas las materias
3. Abre PR o hace push automático
4. GitHub Pages se actualiza (~2 min)

**TODO:** Parametrizar el cron para que también genere Biología u otras materias automáticamente.

---

## 🖥️ Frontend - JavaScript

### Estructura del HTML generado

```html
<html>
  <head>
    <style>/* CSS inline, responsive */</style>
  </head>
  <body>
    <div class="container"> <!-- flex -->
      <div class="sidebar">
        <!-- 3 items: ronda-1, ronda-2, ronda-3 -->
        <div onclick="mostrarRonda(1)">Round 1: Números</div>
        <div onclick="mostrarRonda(2)">Round 2: Álgebra</div>
        <div onclick="mostrarRonda(3)">Round 3: Geometría</div>
      </div>
      <div class="main">
        <!-- Contenido por ronda -->
        <div class="ronda-content" id="ronda-1">
          <!-- 5 preguntas con botones, etc. -->
        </div>
        <div class="ronda-content" id="ronda-2">...</div>
        <div class="ronda-content" id="ronda-3">...</div>
        
        <!-- Tabla de progreso -->
        <table class="historial">...</table>
      </div>
    </div>
    <script>
      function mostrarRonda(num) { /* toggle visibility */ }
      function seleccionar(qid, btn) { /* mark alternative */ }
      function mostrarRespuesta(qid) { /* toggle answer */ }
      function mostrarExplicacion(qid) { /* toggle explanation */ }
      function marcarHecho(rondaId, checkbox) { /* save to localStorage */ }
    </script>
  </body>
</html>
```

### Responsive design

**Desktop (>768px):**
- Sidebar: fixed width (280px)
- Main: flex (takes remaining space)
- Both scroll independently

**Mobile (<768px):**
- Sidebar: 100% width, max-height 120px
- Main: 100% width below sidebar
- flex-direction: column

---

## 🔌 Scripts Python

### generar_ronda.py
**Genera preguntas automáticamente con Claude**

Flujo:
```
1. Llama a rotar_eje.py → obtiene eje de hoy
2. Lee temario y formato de referencias
3. Llama a Claude API con prompt
4. Parsea JSON retornado
5. Valida estructura de respuesta
6. Guarda en data/rondas/<fecha>.json
7. Corre build_progress_artifact.py
8. Corre registrar_generacion.py
```

Estado: Parcialmente funcional
- ❌ Claude devuelve JSON con caracteres mal escapados
- ✅ Estructura de generación lista para mejorar
- ✅ Fallback con preguntas manuales (usado en Round 3)

### build_progress_artifact.py
**Construye HTML con quiz + progreso**

Lee:
- JSON de preguntas
- JSON de registro (historial)

Genera:
- HTML standalone con CSS/JS inlined
- Responsive (desktop + mobile)
- localStorage integration

### rotar_eje.py
**Determina eje de esta semana**

Lee: `data/paes_m1_state.json`

Retorna:
```json
{
  "eje_de_esta_semana": "Geometria",
  "eje_de_la_proxima_semana": "Probabilidad y estadistica",
  "ronda_numero": 3
}
```

Actualiza: `last_eje_index` en state.json

### registrar_generacion.py
**Registra cada ronda en historial**

Entrada:
```
registro.json, eje, archivo_json, archivo_html
```

Output:
```json
{
  "ronda": 3,
  "fecha": "2026-08-15",
  "eje": "Geometria",
  "archivo_json": "2026-08-15.json",
  "archivo_html": "paes-m1-2026-08-15.html",
  "borrador_gmail_id": null
}
```

---

## 🚀 Cómo extender

### Agregar Round 4 (manual)
```bash
1. Crear 5 preguntas sobre "Probabilidad y estadística"
2. Guardar en data/rondas/2026-08-22.json
3. python skill/scripts/registrar_generacion.py
4. python skill/scripts/build_progress_artifact.py
5. git push
```

### Mejorar generación automática
```
1. Refine generar_ronda.py parsing (mejor manejo de JSON)
2. Agregar reintentos inteligentes
3. Implementar fallback con plantillas
4. Testar en local primero
5. Configurar GitHub Actions
```

### Agregar sincronización backend
```
1. Elegir backend (Supabase/Firebase)
2. Crear tabla user_progress
3. Reescribir JavaScript:
   - localStorage local
   - POST al servidor
   - GET del servidor al recargar
4. Agregar login (opcional)
5. Probar sincronización cross-device
```

---

## 📊 Métricas y monitoreo (futuro)

Qué trackear:
- Usuarios activos por semana
- Preguntas más contestadas
- Tasa de respuestas correctas
- Tiempo promedio por pregunta
- Dispositivos más usados

Dónde guardar:
- Base de datos (Supabase/BigQuery)
- Analytics (Posthog/Mixpanel)
- Logs (CloudWatch/Datadog)

---

## 🔐 Seguridad

### Actual
- ✅ Todo es estático (GitHub Pages)
- ✅ Sin auth requerida
- ✅ Sin datos sensibles
- ✅ localStorage solo (no está compartido)

### Futuro (si agregamos backend)
- [ ] Hash de password con bcrypt
- [ ] JWT tokens
- [ ] HTTPS (obligatorio en GitHub Pages)
- [ ] Rate limiting en API
- [ ] Validación de entrada (server-side)

---

## 📈 Escalabilidad

### Actual (100% local)
- Max: Ilimitado de usuarios (cada uno con su localStorage)
- Costo: 0 (GitHub Pages es gratis)
- Complejidad: Baja

### Con sincronización (Fase 1)
- Max: ~1000 usuarios (depende del backend)
- Costo: ~$10-50/mes (Supabase/Firebase)
- Complejidad: Media

### Con análitics (Fase 3)
- Max: ~10k usuarios (con escala de DB)
- Costo: ~$50-200/mes
- Complejidad: Alta

---

## 🎯 Roadmap

```
HECHO ✅
├─ Round 1, 2, 3 con 5 preguntas c/u
├─ Quiz interactivo
├─ Progress tracking (localStorage)
├─ Responsive design
└─ GitHub Pages deployment

FASE 1 (Data sync)
├─ Backend (Supabase/Firebase)
├─ API endpoints
├─ Cross-device sync
└─ Optional: login

FASE 2 (Automation)
├─ Mejorar generar_ronda.py
├─ GitHub Actions cron
├─ Auto-generate Round 4, 5, 6...
└─ PR review workflow (opcional)

FASE 3 (Analytics)
├─ Event tracking
├─ Dashboard
├─ Mejoras basadas en data
└─ Metrics monitoring

FASE 4 (UX enhancements)
├─ Scoring system
├─ Dark mode
├─ Timer opcional
├─ Export progress (PDF/CSV)
└─ Recomendaciones personalizadas
```

---

**Última revisión:** 2026-08-02  
**Próxima revisión:** Cuando agregues Fase 1
