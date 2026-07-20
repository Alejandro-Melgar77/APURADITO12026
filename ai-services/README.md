# Servicios de IA de Apuradito

Tres procesos independientes que el backend puede consumir por HTTP. No acceden
a Supabase ni almacenan fotos: el backend conserva autorización, usuarios y
archivos, y envía solo la imagen o el historial estrictamente necesario.

| Servicio | Puerto | Endpoint | Función |
| --- | ---: | --- | --- |
| `ocr` | `8011` | `POST /v1/ocr/plates` | Lee una placa boliviana desde una imagen. |
| `face` | `8012` | `POST /v1/facial/detect` | Detecta rostros. |
| `face` | `8012` | `POST /v1/facial/verify` | Compara una referencia con una prueba. |
| `routes` | `8013` | `POST /v1/routes/train` | Entrena por lote con viajes históricos. |
| `routes` | `8013` | `POST /v1/routes/score` | Ordena rutas candidatas para un pasajero. |

Cada contenedor publica `GET /health`.

## Ejecutar localmente

Desde esta carpeta:

```bash
docker compose up --build
```

Comprueba los tres procesos:

```bash
curl http://localhost:8011/health
curl http://localhost:8012/health
curl http://localhost:8013/health
```

Las URL que el backend deberá configurar tras su integración son:

```text
OCR_SERVICE_URL=http://localhost:8011
FACE_SERVICE_URL=http://localhost:8012
ROUTES_AI_SERVICE_URL=http://localhost:8013
```

No se ha modificado el backend todavía; esto evita romper el despliegue actual.

## Contratos HTTP

OCR (campo multipart obligatorio `file`):

```bash
curl -F "file=@placa.jpg" http://localhost:8011/v1/ocr/plates
```

Una respuesta informa siempre el motor real empleado, por ejemplo:

```json
{"plate":"1234ABC","confidence":0.92,"raw_text":"1234ABC","is_valid_format":true,"engine":"easyocr","fallback_used":false}
```

Si EasyOCR/PyTorch no puede iniciar, se usa Tesseract y se devuelve
`fallback_used: true`. Tesseract es un fallback funcional pero con menor
precisión. Para producción, despliega OCR con al menos 2 GB de RAM y un volumen
de caché para los pesos de EasyOCR.

Detección facial:

```bash
curl -F "file=@rostro.jpg" http://localhost:8012/v1/facial/detect
```

Verificación facial (dos campos multipart):

```bash
curl -F "reference=@documento.jpg" -F "probe=@selfie.jpg" http://localhost:8012/v1/facial/verify
```

`face_recognition` proporciona la comparación biométrica. Si falla, el servicio
no finge una coincidencia: retorna `match: false`, `fallback_used: true` y queda
en detección OpenCV/Haar. Para la verificación real, usa un servicio con al
menos 1 GB de RAM. La decisión final de validar un conductor debe seguir siendo
del backend y de una revisión humana cuando el resultado sea ambiguo.

Entrenamiento de rutas: se requieren al menos 20 viajes completados. El modelo
se persiste en el volumen `route_models` y no se pierde al recrear el proceso.

```bash
curl -X POST http://localhost:8013/v1/routes/train \
  -H "Content-Type: application/json" \
  -d '{"trips":[{"completed_at":"2026-07-20T12:00:00Z","origin":{"lat":-17.783,"lng":-63.182},"destination":{"lat":-17.80,"lng":-63.15},"passenger_count":1,"completed":true}]}'
```

Para pruebas reales, envía 20 o más objetos. El modelo estima demanda según
hora, día, cuadrícula origen/destino y distancia. `POST /v1/routes/score`
requiere `passenger_origin`, `passenger_destination` y `candidates`; ordena por
proximidad, asientos, calificación, precio y demanda. Antes del entrenamiento
usa un score heurístico y lo señala con `fallback_used: true`.

Ejemplo de puntuación:

```json
{
  "passenger_origin":{"lat":-17.783,"lng":-63.182},
  "passenger_destination":{"lat":-17.80,"lng":-63.15},
  "candidates":[
    {"route_id":"r-1","origin":{"lat":-17.784,"lng":-63.181},"destination":{"lat":-17.801,"lng":-63.151},"available_seats":3,"price_bs":7,"driver_rating":4.8}
  ]
}
```

## Despliegue y recursos

Despliega cada carpeta (`ocr`, `face`, `routes`) como servicio Docker separado.
No es apropiado poner OCR o facial en un Render Free de 512 MB: `torch` y el
modelo facial pueden excederlo. `routes` sí suele caber en un servicio pequeño.
Para ambientes de demostración se puede configurar `OCR_ENGINE=tesseract`, que
evita cargar EasyOCR aunque la imagen todavía contiene la dependencia.

En producción: limita estas APIs a la red privada o protege las llamadas con el
proxy/API del backend; no expongas endpoints biométricos directamente al
frontend. Usa HTTPS, borra imágenes temporales y no persistas embeddings sin
consentimiento explícito.

## Pruebas

Las pruebas mínimas cubren el fallback, el entrenamiento batch y la puntuación:

```bash
python -m pip install -r routes/requirements.txt -r tests/requirements.txt
python -m pytest tests -q
```

