# Feature: Recomendación Personalizada de Cortes

## Descripción
Basándose en el **análisis facial ya realizado por la Feature 001** (que el cliente obtiene vía `/api/analyze`), el sistema selecciona 3 cortes de un **catálogo curado de 60 estilos** mediante IA y **edita la foto del usuario** para que se visualice con cada corte propuesto. El proceso es **asíncrono**: el request encola un job y el cliente hace polling hasta obtener el resultado (la generación de imágenes toma 1-2 minutos).

## Usuario objetivo
Hombres jóvenes (18-35) que buscan un corte que favorezca sus facciones y quieren visualizarse con él antes de ir a la barbería.

---

## Cambios respecto al diseño anterior (2026-09-20)

| Cambio | Antes | Ahora |
|---|---|---|
| Re-análisis facial en 002 | ❌ `/api/recommend` re-analizaba la foto | ✅ Consume el `analysis` de la Feature 001 (ahorra 1 llamada Gemini por request) |
| Catálogo | ❌ 3 estilos fijos (`undercut`, `fade`, `textured-crop`) | ✅ 60 estilos curados en `styles_data.json`; la IA elige 3 compatibles |
| Ejecución | ❌ Síncrona | ✅ Asíncrona (`202` + `job_id` + polling) |
| Entrega de imágenes | ❌ `image_url` (bytes crudos) | ✅ `image_base64` inline |
| Resultado | ❌ Solo nombre + descripción | ✅ Recomendación + **foto del usuario editada** con ese corte |
| Gate de cara | ❌ No existía | ✅ Reutiliza `confidence` del analysis (`low` → 400) |
| Manejo de errores | ❌ Fallo parcial silencioso | ✅ Fail-all con 1 retry por imagen |

---

## Criterios de Aceptación

### CA-1: Consumo del análisis de Feature 001 (sin re-análisis)
- [ ] `/api/recommend` recibe `file` (foto JPG/PNG, máx 10MB) + `analysis` (JSON de `/api/analyze`) en multipart
- [ ] El `analysis` es obligatorio: si falta o no tiene `face_shape` válida → 400
- [ ] La feature **no llama** a Gemini para analizar el rostro
- [ ] Gate de cara: si `analysis.confidence == "low"` → 400 (evita gastar en edición)

### CA-2: Catálogo de 60 estilos
- [ ] `styles_data.json` con **60 estilos reales**, cada uno: `id`, `name` (en español, pedible en barbería), `description`, `prompt_template` (EN, "solo modifica el cabello, preserva identidad"), `face_shapes`, `hair_types`
- [ ] Los 60 cubren todas las `face_shapes` y `hair_types` del análisis (oval, round, square, heart, oblong / straight, wavy, curly, coily)
- [ ] Carga validada al iniciar (esquema, duplicados)

### CA-3: Selección por IA (3 estilos compatibles)
- [ ] El service filtra el catálogo por `face_shape` + `hair_type`/`hair_texture`
- [ ] Gemini recibe la lista de candidatos y elige exactamente **3 IDs + razón** de por qué le quedan a esa cara
- [ ] La selección no usa `skin_tone` (sesgo)
- [ ] Si la IA devuelve menos de 3 o IDs inválidos → job `failed`

### CA-4: Edición de la foto del usuario
- [ ] Por cada estilo seleccionado, Replicate (`google/nano-banana-pro`) **edita la foto del usuario** cambiando solo el cabello
- [ ] **1 retry** por imagen ante fallo; si persiste → job `failed`
- [ ] El resultado se entrega en **base64 inline**

### CA-5: Proceso asíncrono
- [ ] `POST /api/recommend` → `202 Accepted` + `job_id` + `status_url`
- [ ] `GET /api/recommend/{job_id}` → `pending` | `processing` | `completed` | `failed`
- [ ] Al completar: `recommendations` con 3 items
- [ ] Job store **en memoria** (trade-off aceptado: reinicio del server pierde jobs)

### CA-6: Respuesta final
- [ ] Cada recomendación: `style_id`, `style_name`, `description`, `reason`, `image_base64`
- [ ] `success: true` cuando `status == completed`

---

## Datos de Salida (Response JSON)

```json
{
  "job_id": "uuid-...",
  "status": "completed",
  "recommendations": [
    {
      "style_id": "fade-clasico",
      "style_name": "Fade Clásico",
      "description": "Transición gradual de largo a corto en los laterales",
      "reason": "Tu rostro ovalado se beneficia de los laterales cortos y el volumen superior",
      "image_base64": "<foto del usuario con el corte, base64>"
    }
  ]
}
```

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/recommend` | Recibe foto + `analysis` de 001, encola job → `202` + `job_id` |
| GET | `/api/recommend/{job_id}` | Consulta estado del job y resultado (polling) |

---

## Dependencias
- **Feature 001** (Análisis de Foto) - Requerida (produce el `analysis`)
- **Replicate API** - Edición de la foto del usuario (`google/nano-banana-pro`)
- **Google Gemini** - Solo selección de estilos (sin análisis en esta feature)

---

## Módulos (objetivo)
- `src/services/styles_data.py` + `styles_data.json` → catálogo de 60 estilos + carga validada
- `src/services/recommend_job.py` → job store en memoria + worker en background
- `src/clients/replicate_client.py` → edición con retry
- `src/services/haircut_service.py` → orquestación (filtrado, selección IA, edición)
- `src/controllers/haircut_controller.py` → endpoints async POST/GET
- `src/models/recommend.py` → `Recommendation` (con `image_base64`) + modelos de job/status

---

## Notas Técnicas
- Imágenes procesadas en memoria (BytesIO); el resultado viaja como base64 inline
- La generación tarda ~1-2 min → por eso el diseño asíncrono
- Replicate API tiene rate limits → 1 retry por imagen y fail-all
- Costo estimado: ~$0.03-0.15 por job completado (3 imágenes)
- Trade-off aceptado: job store en memoria (el stateless del MVP se rompe parcialmente; un reinicio pierde los jobs en curso)