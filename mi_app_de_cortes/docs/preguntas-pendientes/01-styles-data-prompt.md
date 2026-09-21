# Preguntas Pendientes - Feature 002

## Pregunta 1 - styles_data.py

**Fecha:** 2026-09-11
**Resuelta:** 2026-09-20

**Contexto:** Estábamos revisando la implementación de `get_style_prompt()` en `styles_data.py`.

**Pregunta:** ¿Por qué crees que el test `test_contains_face_shape` está bien, pero la implementación actual no es la mejor forma de incluir la forma del rostro en el prompt?

**Pista:** ¿Qué pasaría si quieres agregar más información al prompt, como el tipo de cabello o preferencias del usuario?

**Estado:** ✅ Resuelta

## Resolución

La implementación anterior concatenaba la forma del rostro al final del template:

```python
f"{style['prompt_template']} The face shape is {face_shape}."
```

**Problema:** el prompt dependía de contexto externo invisible (quién llamaba y con qué datos). Cada dato nuevo (tipo de cabello, textura, preferencias) obligaría a concatenar más texto a mano dentro de `get_style_prompt()`, haciéndola frágil e inescalable. El test `test_contains_face_shape` pasaba solo porque el sufijo se agregaba siempre, no porque el diseño fuera correcto.

**Solución (rediseño de Feature 002, 2026-09-20):**
- Cada estilo del catálogo (`styles_data.json`) lleva su `prompt_template` **autocontenido**: instrucción completa de edición ("cambia solo el cabello, preserva identidad", etc.), sin sufijos externos.
- Los datos del usuario se inyectan como **parámetros estructurados** en el prompt de selección de la IA, no por concatenación manual.
- `get_style_prompt()` deja de existir: los templates viven en los datos, no en el código.