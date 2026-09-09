# AGENTS.md - AI Haircut Advisor MVP

## Project Overview
FastAPI app that analyzes face photos via Google Gemini AI and recommends haircut styles. Stateless MVP - no database, no auth, no sessions.

## Architecture (Strict Layered)
```
mi_app_de_cortes/
├── app.py                 # FastAPI entry point
├── requirements.txt       # Dependencies
└── src/
    ├── controllers/       # HTTP layer - validate inputs, format responses
    ├── services/          # Business logic - prompts, formatting
    └── clients/           # External APIs - AI client (Singleton pattern)
```

**Data flow:** `Controller → Service → Client` (never skip layers, never mix responsibilities)

## Commands
```bash
# Activate venv first (mandatory before any pip install)
.venv\Scripts\activate

# Install dependencies
pip install -r mi_app_de_cortes/requirements.txt

# Run dev server
uvicorn mi_app_de_cortes.app:app --reload
```

## Tech Stack (Mandatory)
- **Framework:** FastAPI + Pydantic validation
- **AI:** Google GenAI SDK (`google-genai`) with Structured Outputs
- **Images:** Pillow (PIL) + BytesIO for in-memory compression
- **Server:** Uvicorn

## Key Conventions
- Endpoints prefix: `/api/` (e.g., `/api/analyze`, `/api/recommend`)
- Image limits: JPG/PNG, max 10MB
- AI responses must use structured JSON outputs
- Client layer uses Singleton pattern
- Python type hints required
- Code comments and docs in Spanish and English

## Feature Specs
- `mi_app_de_cortes/spec/features/001-analisis-foto-ia/spec.md` - Photo analysis
- `mi_app_de_cortes/spec/features/002-recomendacion-personalizada/spec.md` - Recommendations

## Gotchas
- `.venv/` must be active before installing packages
- No database - all state is request-scoped
- Image processing happens in-memory (BytesIO), no temp files
- Google Gemini API has rate limits


## Working Style Rules
- **Flujo obligatorio:** Plan → aprobación → ejecución. No escribir código sin visto bueno del usuario
- **Methodo Socrático:** Cuando el usuario aprenda algo nuevo, pedirle que justifique por qué esa implementación y no otra
- **Errores:** Explicar POR QUÉ ocurre y DÓNDE está. No dar la solución directa — desafiar al usuario a resolverlo
- **Git:** No ejecutar comandos git sin permiso explícito del usuario
- **Arquitectura:** No tomar decisiones de arquitectura. Solo dar recomendaciones
- **Dependencias:** Instalar SOLO en el entorno virtual activado
- **Consultas faltantes:** Si falta información para continuar, preguntar. No asumir
- **Código:** Siempre explicar el por qué de los cambios. No dar código ilegible sin contexto

## Micro-Commits (Tarea por Tarea)
- **Flujo:** Ejecutar tarea → Reportar cambios → Esperar aprobación → Preguntar si hace commit/push
- **Regla de oro:** NUNCA ejecutar comandos git sin autorización explícita del usuario
- **Reporte por tarea:** Después de cada tarea, reportar:
  - ✅ Estado (completada)
  - 📦 Archivos creados/modificados
  - 📍 Descripción breve del cambio
- **Commit:** Solo si el usuario aprueba Y autoriza explícitamente
- **Formato commit:** `feat(feature-002): descripción del cambio`
- **Push:** Solo si el usuario autoriza después del commit
- **Un paso a la vez:** No ejecutar múltiples tareas sin reporte intermedio

## Git Flow (Ramas)
- **NUNCA trabajar en la rama `main`** — siempre crear una rama nueva para cada feature/cambio
- **Naming de ramas:** `feature/002-recomendacion-personalizada`, `fix/bug-descripcion`, `chore/tarea-descripcion`
- **Fusión a main:** Solo cuando la feature esté lista Y aprobada explícitamente por el usuario
- **Merge:** NUNCA hacer merge sin aprobación explícita del usuario

## consejos
- si necesitas buscar funciones o algo acerca de una tecnologia, usa el mcp istalado de context7 para actualizar tu conocimiento antes de escribir codigo, para asegurar que siempre se este al dia con las tecnologias
- A la hora del desarrollo siempre debes usar este flujo: Plan -> aprobacion -> ejecucion. Solo debes escribir codigo despues de que yo le de la aprobacion a un plan que hayas hecho antes, no escribas codigo sin planeacion y aprobacion mia