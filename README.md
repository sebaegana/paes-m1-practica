# PAES M1 — Práctica Semanal de Matemáticas

Plataforma de preguntas de práctica semanales para la **Prueba de Competencia Matemática 1 (M1)** del PAES (Chile). Genera 5 preguntas originales cada semana, rotando por los 4 ejes temáticos, con interfaz interactiva y seguimiento de progreso.

## 🚀 Acceso

**Sitio en vivo**: https://sebaegana.github.io/paes-m1-practica/

- Sin requerimientos de login ni backend
- Funciona offline una vez cargado
- Progreso guardado por navegador (localStorage)

## 📁 Estructura del proyecto

```
paes-m1-practica/
├── docs/                     # GitHub Pages (root)
│   └── index.html           # Panel completo con quiz + progreso
├── data/
│   ├── paes_m1_state.json   # Estado de rotación de ejes
│   ├── registro_generaciones.json  # Historial de rondas
│   └── rondas/              # Preguntas por ronda (JSON)
│       └── 2026-08-01.json
├── skill/                    # Scripts y referencias
│   ├── SKILL.md             # Cómo generar un set de preguntas
│   ├── scripts/
│   │   ├── rotar_eje.py
│   │   ├── build_quiz_html.py
│   │   ├── build_progress_artifact.py
│   │   ├── registrar_generacion.py
│   │   └── generar_ronda.py  # Automatización semanal
│   └── references/
│       ├── temario-m1.md     # Oficial DEMRE
│       └── formato-pregunta.md  # Estándar de pregunta
└── .github/workflows/
    └── generar-ronda-semanal.yml  # GitHub Actions
```

## 🤖 Generación automática

Cada **sábado a las 19:00 (hora Chile)** se ejecuta automáticamente:

1. Un script genera 5 preguntas originales del eje que toca esa semana
2. Se genera el HTML interactivo
3. Se abre un **Pull Request** con los cambios para revisión
4. Al mergear el PR, la página se actualiza automáticamente

Para disparar manualmente: GitHub → Actions → "Generar ronda" → "Run workflow"

### Configuración necesaria

Para que el workflow funcione, debes agregar un secret en GitHub:
- **`ANTHROPIC_API_KEY`**: Tu API key de Anthropic (console.anthropic.com)
  - Settings → Secrets and variables → Actions → New secret

## 📝 Generar una ronda manualmente

```bash
python skill/scripts/generar_ronda.py
```

Esto:
1. Determina el eje de esta semana (rotación automática)
2. Llama a Claude para generar 5 preguntas
3. Construye el HTML en `docs/index.html`
4. Registra la generación en el historial

## 📊 Características

- **5 preguntas originales** por semana (nunca copiadas del DEMRE)
- **Interfaz interactiva**: selecciona alternativa, botones para ver respuesta y explicación
- **Rotación de ejes** fija: Números → Álgebra → Geometría → Probabilidad → repite
- **Dificultad calibrada**: 2 Básico, 2 Intermedio, 1 Avanzado
- **Progreso persistente**: checkbox "Hecho" en cada ronda, guardado localmente
- **Multi-dispositivo**: funciona en celular, tablet, computador

## ⚠️ Limitaciones conocidas

- El progreso se guarda **por navegador/dispositivo** (localStorage), no en un servidor
  - Si usas el sitio en múltiples dispositivos, los checkmarks no se sincronizan
  - Solución futura: agregar backend (Supabase, etc.) si se necesita sincronización

## 📚 Referencias

- **Temario oficial PAES M1** (DEMRE): `skill/references/temario-m1.md`
- **Formato estándar de pregunta**: `skill/references/formato-pregunta.md`
- **Instrucciones completas para generar sets**: `skill/SKILL.md`

## 📋 Notas técnicas

- HTML autocontenido (CSS + JS inline, sin dependencias externas)
- Compatible con navegadores modernos (Chrome, Firefox, Safari, Edge)
- Responsive: se adapta a celular, tablet y desktop

---

**Última actualización**: 2026-08-01  
**Rondas completadas**: 1  
**Próximo eje**: Álgebra y funciones
