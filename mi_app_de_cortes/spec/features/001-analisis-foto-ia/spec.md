# Feature: Análisis de Foto con IA

## Descripción
El usuario sube una foto de su rostro y Google Gemini analiza sus características faciales para determinar la forma del rostro, tipo de cabello y facciones principales.

## Usuario objetivo
Hombres jóvenes (18-35) que quieren saber qué corte de cabello les queda bien.

---

## Criterios de Aceptación

### CA-1: Subida de imagen
- [ ] El endpoint acepta archivos JPG y PNG
- [ ] Tamaño máximo: 10MB
- [ ] Retorna error 400 si el formato no es válido

### CA-2: Análisis con IA
- [ ] La imagen se envía a Google Gemini para análisis
- [ ] Se extrae: forma del rostro, tipo de piel, tipo de cabello, facciones
- [ ] El análisis se completa en menos de 10 segundos

### CA-3: Respuesta estructurada
- [ ] Retorna JSON con el análisis completo
- [ ] Incluye confianza del análisis (alta/media/baja)
- [ ] Campo `success: true` cuando exitoso

### CA-4: Manejo de errores
- [ ] Error 400: imagen no válida o formato incorrecto
- [ ] Error 500: fallo en la API de Google Gemini
- [ ] Error 413: imagen excede tamaño máximo

---

## Datos de Salida (Response JSON)

```json
{
  "success": true,
  "analysis": {
    "face_shape": "ovalado",
    "hair_type": "ondulado",
    "hair_texture": "grueso",
    "skin_tone": "medio",
    "features": [
      "frente amplia",
      "mandíbula definida",
      "pómulos altos"
    ],
    "confidence": "alta"
  }
}
```

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/analyze` | Analiza una foto y retorna el análisis facial |

---

## Dependencias
- **google-genai SDK** - Para análisis de imágenes con Gemini
- **Pillow** - Para procesamiento y validación de imágenes
- **python-multipart** - Para recibir archivos en FastAPI

---

## Notas Técnicas
- Usar Gemini Vision para análisis de imágenes
- Enviar imagen como base64 o URL
- Prompt específico para extraer datos faciales estructurados
- Considerar rate limiting de la API de Google
