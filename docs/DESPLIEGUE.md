# Despliegue de Apuradito

## Arquitectura

| Componente | Plataforma propuesta | Función |
| --- | --- | --- |
| Base de datos y archivos | Supabase | PostgreSQL, PostGIS y Storage para evidencias autorizadas. |
| API principal | Render Web Service | Autenticación, viajes, pagos, WebSocket y pasarela de IA. |
| Panel web | Render Static Site | Administración React/Vite. |
| OCR, rostro y rutas | Hugging Face Docker Spaces | Inferencia aislada y entrenamiento de demanda. |

## 1. Supabase

1. Crea el proyecto y habilita las extensiones ejecutando `backend/migrations/init.sql` en el SQL Editor.
2. Ejecuta después `backend/migrations/001_hardening.sql`.
3. Crea un bucket privado en **Storage** para documentos e imágenes de verificación. No almacenes fotos biométricas en el sistema de archivos de Render.
4. Copia la URI del **Session pooler**. Si empieza por `postgres://` o `postgresql://`, el backend la adapta automáticamente a `postgresql+asyncpg://`.

## 2. Servicios de IA

En Hugging Face, crea tres **Docker Spaces** y sube, respectivamente, el contenido de estas carpetas:

- `ai-services/ocr`
- `ai-services/face`
- `ai-services/routes`

Los `README.md` de cada carpeta ya declaran `sdk: docker` y el puerto correcto. La edición gratuita de CPU Basic proporciona memoria suficiente para pruebas de OCR y rostro, aunque puede dormirse y producir un primer acceso lento. No expongas estas URLs en el frontend ni compartas sus secretos.

Guarda las URLs públicas resultantes, por ejemplo:

```text
https://USUARIO-apuradito-ocr.hf.space
https://USUARIO-apuradito-face.hf.space
https://USUARIO-apuradito-routes.hf.space
```

## 3. Backend de Render

Crea un **Web Service** con `backend` como Root Directory. Usa:

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Variables requeridas:

```text
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=<URI Session pooler de Supabase>
SECRET_KEY=<valor aleatorio de más de 32 caracteres>
CORS_ORIGINS=https://<tu-frontend>.onrender.com
OCR_SERVICE_URL=<URL del Space OCR>
FACE_SERVICE_URL=<URL del Space facial>
ROUTES_AI_SERVICE_URL=<URL del Space de rutas>
AI_SERVICE_TOKEN=<token aleatorio compartido con los tres Spaces>
```

No uses `*` para `CORS_ORIGINS` una vez que conozcas la URL real del frontend.
Configura ese mismo `AI_SERVICE_TOKEN` como secreto en cada Space de Hugging Face.

## 4. Frontend de Render

Crea un **Static Site** con `frontend` como Root Directory:

```text
Build Command: npm ci && npm run build
Publish Directory: dist
VITE_API_URL_PROD=<host o URL del Web Service de Render>
```

El frontend acepta tanto un host de Render como una URL completa y genera `wss://` automáticamente para WebSocket.

## 5. Verificación

1. `https://<backend>/health` debe responder 200 cuando Supabase esté disponible.
2. Inicia sesión desde el panel web.
3. Comprueba los estados de IA a través de `https://<space>/health`.
4. Prueba OCR y detección facial desde un usuario autorizado.
5. Entrena rutas solo con 20 o más viajes completados y con datos anonimizados.

## Desarrollo local

Consulta `local/README.md`. Para levantar también los servicios de IA:

```powershell
.\local\start.ps1 -Build -Ai
```
