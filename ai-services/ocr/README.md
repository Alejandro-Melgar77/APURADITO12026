---
title: Apuradito OCR
emoji: "🚘"
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8011
pinned: false
---

# Apuradito OCR Service

API FastAPI para reconocer placas bolivianas. El endpoint público es `POST /v1/ocr/plates` y el estado se consulta en `GET /health`.

Configura `OCR_ENGINE=easyocr` para máxima precisión o `OCR_ENGINE=tesseract` para el fallback ligero.
