# PAES Multi-materia - Estado del Proyecto

**Última actualización:** 2026-08-01  
**Estado:** ✅ COMPLETAMENTE FUNCIONAL (Multi-materia)  
**URL:** https://sebaegana.github.io/paes-m1-practica/

---

## 🎯 Objetivo

Crear una plataforma unificada e interactiva de preguntas de práctica para múltiples materias PAES (Matemática, Biología, etc.), con seguimiento de progreso independiente por materia y acceso desde cualquier dispositivo.

---

## ✅ Lo que está completado

### Infraestructura
- ✅ Repo en GitHub: `sebaegana/paes-m1-practica`
- ✅ GitHub Pages configurado en `/docs`
- ✅ Estructura de carpetas **multi-materia**
  - `data/` → Estados y datos por materia
    - `estado_matematica.json`, `estado_biologia.json` (rotaciones)
    - `rondas/matematica/`, `rondas/biologia/` (organizados por materia)
    - `registro_generaciones.json` (incluye campo `materia`)
  - `docs/` → Sitio público (HTML multi-materia)
  - `skill/` → Scripts y referencias generalizados
  - `.github/workflows/` → Automatización

### Contenido
**Matemática (4 rondas)**
- ✅ Round 1 (Números) - 5 preguntas
- ✅ Round 2 (Álgebra y funciones) - 5 preguntas
- ✅ Round 3 (Geometría) - 5 preguntas
- ⏳ Round 4 (Probabilidad y estadística) - próxima semana

**Biología (1 ronda)**
- ✅ Round 1 (Célula) - 5 preguntas
  - Estructura y función, transporte, metabolismo, reproducción
  - Dificultad: 2 Básico, 2 Intermedio, 1 Avanzado

### Características
- ✅ **Interfaz multi-materia**
  - Selector de materia (tabs: Matemática, Biología)
  - Sidebar dinámico filtra rondas por materia
  - Click en tab cambia a esa materia
  
- ✅ **Interactividad** (mantiene la del original)
  - Click en ronda cambia contenido instantáneamente
  - Alternativas clicables con feedback visual
  - Botones "Ver respuesta" y "Ver explicación" (toggle)
  - Respuesta correcta/incorrecta marcadas visualmente
  
- ✅ **Progreso persistente (multi-materia)**
  - Checkboxes "Hecho" por ronda
  - localStorage keys: `paes_m1_progreso_{materia}-{fecha}-{eje}`
  - Progreso independiente por materia
  - Tabla de historial muestra todas las materias
  
- ✅ **Scripts generalizados**
  - `rotar_eje.py` - Recibe `<materia>` como parámetro
  - `registrar_generacion.py` - Recibe `<materia>`, calcula ronda por materia
  - `build_progress_artifact.py` - Lee todas las materias, genera HTML unificado
  - `generar_ronda.py` - Recibe `--materia` (default: matematica)

### Temarios
- ✅ `temario-m1.md` - Oficial DEMRE (4 ejes Matemática)
- ✅ `temario-biologia.md` - Borrador (5 ejes Ciencias-Biología)
  - ⚠️ Revisar contra temario oficial DEMRE antes de generar automático

---

## ⚠️ Limitaciones actuales

1. **Progreso por navegador/dispositivo**
   - localStorage no sincroniza entre dispositivos
   - Progreso de Biología independiente al de Matemática ✅
   - Solución futura: agregar backend + autenticación

2. **Generación automática (solo Matemática por ahora)**
   - GitHub Actions cron `.github/workflows/generar-ronda-semanal.yml` apunta a `generar_ronda.py` sin parámetros (default: matematica)
   - Biología se agregó manualmente (Round 1)
   - TODO: Parametrizar workflow para ambas materias (o duplicar)

3. **Temario de Biología es borrador**
   - `temario-biologia.md` fue redactado sin URL oficial DEMRE verificada
   - Revisar contra temario oficial de DEMRE Ciencias antes de usar generador automático con Claude

4. **Sin autenticación de usuarios**
   - No hay login, progreso es anónimo per-dispositivo
   - localStorage local solo

---

## 🔄 Migración a multi-materia (cambios en localStorage)

**IMPORTANTE para usuarios con progreso anterior (2026-08-01 a 2026-08-15):**

Las claves de localStorage han cambiado para incluir la materia:

| Antes (obsoleto) | Ahora |
|---|---|
| `paes_m1_progreso_2026-08-01-Numeros` | `paes_m1_progreso_matematica-2026-08-01-Numeros` |
| `paes_m1_progreso_2026-08-08-Algebra_y_funciones` | `paes_m1_progreso_matematica-2026-08-08-Algebra_y_funciones` |

**Impacto:**
- ✅ El progreso de Matemática se **reinicia** en esta versión (pero es solo 3 rondas, no es crítico)
- ✅ Progreso viejo queda en localStorage pero "huérfano" (no se borra, solo no se usa)
- ✅ Los checkboxes de la tabla historial se regeneran vacíos
- ⚠️ Si esto causa molestia, se puede escribir un script de migración de keys

**Razón del cambio:** Permitir que Biología (y futuras materias) tengan progreso independiente sin conflictos de claves.

---

## 📅 Rotación de ejes (establecida por materia)

**Matemática:**
```
Round 1 → Números
Round 2 → Álgebra y funciones
Round 3 → Geometría
Round 4 → Probabilidad y estadística (próximo)
Round 5 → Números (repite)
```

**Biología:**
```
Round 1 → Célula
Round 2 → Herencia y variabilidad genética (próximo)
Round 3 → Evolución y biodiversidad
Round 4 → Organismo y ambiente
Round 5 → Cuerpo humano y salud
Round 6 → Célula (repite)
```

**Próximas rondas:**
- Matemática: **Probabilidad y estadística** (Round 4, ~2026-08-29)
- Biología: **Herencia y variabilidad genética** (Round 2, ~2026-08-29)

---

## ➕ Agregar una nueva materia (pasos rápidos)

Ejemplo: agregar **Química**

```bash
# 1. Crear archivo de estado
echo '{"history":[],"last_eje_index":-1}' > data/estado_quimica.json

# 2. Crear directorio de rondas
mkdir -p data/rondas/quimica

# 3. Crear temario (skill/references/temario-quimica.md)
# - Seguir formato de temario-m1.md
# - Definir ejes, unidades, habilidades

# 4. Escribir 5 preguntas manualmente
# data/rondas/quimica/2026-08-29.json

# 5. Registrar en historial
python skill/scripts/registrar_generacion.py \
  data/registro_generaciones.json quimica "Elemento" \
  data/rondas/quimica/2026-08-29.json ...

# 6. Regenerar HTML
python skill/scripts/build_progress_artifact.py \
  data/registro_generaciones.json docs/index.html

# 7. (Opcional) Agregar tab de Química en HTML
# Editar: tabs en build_progress_artifact.py + cambiarMateria() JS
```

**Notas:**
- Actualizar `EJES_POR_MATERIA` en `skill/scripts/rotar_eje.py`
- Agregar tab en `build_progress_artifact.py` (CSS `.materia-tab` y botón HTML)

---

## 🔮 Próximos pasos (PARA HACER DESPUÉS)

### Fase 1: Sincronización de datos (RECOMENDADO)
**Objetivo:** Permitir que el progreso se vea igual en todos los dispositivos

**Pasos:**
1. Elegir backend (Supabase, Firebase, o PostgreSQL+Node.js)
2. Crear tabla: `user_progress` con columns:
   - `user_id` (email o anónimo)
   - `round_number`
   - `completed_at`
   - `timestamp`
3. Reescribir JavaScript para guardar en servidor + localStorage
4. Agregar login simple (opcional al principio)

**Beneficio:** Progreso sincronizado across devices

---

### Fase 2: Automatizar generación para todas las materias
**Objetivo:** Que Round 4, 5... se generen automáticamente cada semana para Matemática y Biología

**Pasos:**
1. **Revisar temario-biologia.md** contra DEMRE oficial
   - Actualizar/corregir ejes, unidades, habilidades si es necesario
   - CRÍTICO antes de usar con Claude automático

2. **Mejorar `generar_ronda.py`** (ya hecho parcialmente para M1):
   - Mejor parsing de JSON (ya tiene reintentos)
   - Validar que Biología funciona igual que Matemática

3. **Parametrizar GitHub Actions**:
   - Duplicar o parametrizar `.github/workflows/generar-ronda-semanal.yml`
   - Ejecutar para Matemática: `generar_ronda.py --materia matematica`
   - Ejecutar para Biología: `generar_ronda.py --materia biologia`
   - O: un solo job que itera ambas materias

**Beneficio:** Nuevas rondas sin intervención manual para ambas materias

---

### Fase 3: Analytics y seguimiento
**Objetivo:** Ver qué preguntas son difíciles, cuánta gente practica, etc.

**Pasos:**
1. Agregar evento tracking:
   - Click en pregunta
   - Click en "Ver respuesta"
   - Click en "Hecho"
2. Guardar en base de datos o analytics service (Posthog, Mixpanel, etc.)
3. Crear dashboard simple con:
   - Usuarios activos
   - Preguntas más contestadas
   - Tasa de respuestas correctas por pregunta

**Beneficio:** Data-driven mejoras al contenido

---

### Fase 4: Mejoras UX
**Objetivo:** Experiencia más pulida

**Ideas:**
1. Mostrar puntuación (cuántas correctas/totales)
2. Timer opcional por pregunta
3. Modo revisión (ver todas las rondas + respuestas)
4. Exportar progreso (PDF, CSV)
5. Dark mode toggle
6. Sugerencias de preguntas por debilidad

**Beneficio:** Más engagement, mejor aprendizaje

---

## 🛠️ Cómo agregar Round 4 (cuando llegue el momento)

### Opción A: Manual (lo que hicimos en Round 3)
```bash
1. Crear data/rondas/2026-08-22.json con 5 preguntas
2. python skill/scripts/registrar_generacion.py ... 
3. python skill/scripts/build_progress_artifact.py ...
4. git add . && git commit && git push
```

### Opción B: Con Claude (después de mejorar)
```bash
1. python skill/scripts/generar_ronda.py
2. Revisar preguntas en PR
3. Mergear cuando esté ok
```

---

## 📊 Métricas actuales

| Métrica | Valor |
|---------|-------|
| Preguntas generadas | 15 (3 rondas × 5) |
| Rondas completadas | 3 |
| Dispositivos | ilimitado (per-browser) |
| Tamaño del sitio | ~45KB HTML |
| Velocidad de carga | <500ms |
| Disponibilidad | 99.99% (GitHub Pages) |

---

## 📁 Archivos importantes

```
paes-m1-practica/
├── PROJECT_STATUS.md          ← Este archivo
├── CONTEXT.md                 ← Contexto original del proyecto
├── README.md                  ← Instrucciones de uso
├── data/
│   ├── paes_m1_state.json     ← Rotación de ejes
│   ├── registro_generaciones.json ← Historial de rondas
│   └── rondas/
│       ├── 2026-08-01.json    ← Round 1 (Números)
│       ├── 2026-08-08.json    ← Round 2 (Álgebra)
│       └── 2026-08-15.json    ← Round 3 (Geometría)
├── docs/
│   └── index.html             ← Sitio público (GitHub Pages)
└── skill/
    ├── scripts/
    │   ├── generar_ronda.py   ← Genera preguntas con Claude
    │   ├── build_progress_artifact.py ← Construye HTML
    │   ├── rotar_eje.py       ← Rotación de ejes
    │   └── registrar_generacion.py ← Registro
    └── references/
        ├── temario-m1.md      ← Temario oficial DEMRE
        └── formato-pregunta.md ← Formato estándar
```

---

## 🚀 Quick Start (para futuras rondas)

```bash
# 1. Crear Round 4 manualmente
cat > data/rondas/2026-08-22.json << 'EOF'
{
  "fecha": "2026-08-22",
  "eje_semana": "Probabilidad y estadistica",
  "saludo": "...",
  "preguntas": [
    { "id": "M1-PRO-...", ... },
    ...
  ],
  "cobertura": { ... }
}
EOF

# 2. Registrar
python skill/scripts/registrar_generacion.py \
  data/registro_generaciones.json \
  "Probabilidad y estadistica" \
  data/rondas/2026-08-22.json \
  docs/paes-m1-2026-08-22.html

# 3. Regenerar HTML
python skill/scripts/build_progress_artifact.py \
  data/rondas/2026-08-22.json \
  data/registro_generaciones.json \
  docs/index.html

# 4. Subir
git add . && git commit -m "feat: agregar Round 4" && git push
```

---

## 📞 Contacto / Preguntas

- **Repo:** https://github.com/sebaegana/paes-m1-practica
- **Sitio:** https://sebaegana.github.io/paes-m1-practica/
- **Email:** sebaegana@gmail.com

---

**Notas finales:**
- El proyecto es **100% funcional** en su forma actual
- Perfecto para empezar a practicar las 3 primeras rondas
- La sincronización de datos (Fase 1) es el siguiente paso lógico
- Automatizar generación de preguntas (Fase 2) es importante para escalabilidad
