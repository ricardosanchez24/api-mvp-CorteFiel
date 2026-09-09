# Feature: Recomendación Personalizada de Cortes

## Descripción
Basándose en el análisis facial de la Feature 001, el sistema recomienda 3-5 cortes de cabello adecuados para el usuario, con explicaciones de por qué cada corte es favorable.

## Usuario objetivo
Hombres jóvenes (18-35) que buscan un corte que favorezca sus facciones.

---

## Criterios de Aceptación

### CA-1: Recomendaciones personalizadas
- [ ] El endpoint recibe el análisis facial (de Feature 001)
- [ ] Retorna 3-5 cortes recomendados
- [ ] Cada corte incluye: nombre, descripción, razón, imagen de referencia

### CA-2: Matching por forma de rostro
- [ ] Algoritmo que cruza forma de rostro con cortes adecuados
- [ ] Ovalado → mayor variedad de opciones
- [ ] Redondo → cortes que alargan visualmente
- [ ] Cuadrado → cortos o con volumen arriba
- [ ] Corazón → cortes con textura en la parte superior

### CA-3: Explicación personalizada
- [ ] Cada recomendación incluye "razón" específica
- [ ] Explica POR QUÉ ese corte favorece al usuario
- [ ] Lenguaje claro y fácil de entender

### CA-4: Base de datos de estilos
- [ ] Catálogo inicial con 10+ cortes de referencia
- [ ] Cada corte tiene: nombre, descripción, imagen, formas compatibles
- [ ] Almacenamiento en JSON (fácil de expandir)

---

## Datos de Salida (Response JSON)

```json
{
  "success": true,
  "recommendations": [
    {
      "id": "undercut",
      "name": "Undercut",
      "description": "Laterales cortos con la parte superior larga y peinada hacia atrás",
      "reason": "Ideal para rostro ovalado. Los laterales cortos estilizan y la parte superior añade dimensión.",
      "reference_image": "undercut.jpg",
      "difficulty": "media",
      "maintenance": "Cada 3-4 semanas"
    },
    {
      "id": "textured-crop",
      "name": "Textured Crop",
      "description": "Corte corto con textura en la parte superior, mechones hacia adelante",
      "reason": "Perfecto para mandíbula definida. Resalta los pómulos y estructura facial.",
      "reference_image": "textured-crop.jpg",
      "difficulty": "baja",
      "maintenance": "Cada 2-3 semanas"
    }
  ],
  "face_shape": "ovalado"
}
```

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/recommend` | Recibe análisis y retorna recomendaciones |
| GET | `/api/styles` | Lista todos los estilos disponibles |

---

## Dependencias
- **Feature 001** (Análisis de Foto) - Requerida
- **Base de datos de estilos** - JSON con catálogo de cortes

---

## Base de Datos Inicial (styles.json)

```json
{
  "styles": [
    {
      "id": "undercut",
      "name": "Undercut",
      "description": "Laterales cortos, parte superior larga",
      "face_shapes": ["ovalado", "corazón"],
      "hair_types": ["liso", "ondulado"],
      "image": "undercut.jpg"
    },
    {
      "id": "textured-crop",
      "name": "Textured Crop",
      "description": "Corte corto con textura",
      "face_shapes": ["ovalado", "cuadrado"],
      "hair_types": ["liso", "ondulado", "rizado"],
      "image": "textured-crop.jpg"
    },
    {
      "id": "fade",
      "name": "Fade",
      "description": "Transición gradual de largo a corto",
      "face_shapes": ["ovalado", "redondo", "cuadrado"],
      "hair_types": ["liso", "ondulado"],
      "image": "fade.jpg"
    }
  ]
}
```

---

## Notas Técnicas
- El algoritmo de matching puede ser simple al principio (basado en reglas)
- Considerar usar IA para generar explicaciones personalizadas
- Futuro: permitir filtros por preferencia del usuario (formal, casual, deportivo)
