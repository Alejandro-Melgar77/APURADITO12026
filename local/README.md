# Ejecucion local autocontenida

Esta carpeta ejecuta el proyecto en Docker sin duplicar `backend/` ni `frontend/` y sin modificar sus archivos. Los contenedores montan esos directorios originales, por lo que los cambios de codigo se recargan automaticamente.

## Requisitos

- Docker Desktop iniciado (incluye Docker Compose).
- PowerShell 7 o Windows PowerShell.
- Puertos libres: `5173`, `8000`, `5432` y `6379`.

No se necesita instalar Python, Node.js, PostgreSQL ni Redis en el equipo.

## Primera ejecucion

Desde la raiz del repositorio, crea el archivo de configuracion local:

```powershell
Copy-Item .\local\.env.example .\local\.env
```

Genera una clave exclusiva para desarrollo y pegala como `LOCAL_SECRET_KEY` dentro de `local/.env`:

```powershell
[Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))
```

Inicia todos los servicios y construye las imagenes:

```powershell
.\local\start.ps1 -Build
```

Para iniciar además OCR, reconocimiento facial y aprendizaje de rutas:

```powershell
.\local\start.ps1 -Build -Ai
```

Cuando Docker termine de iniciar, abre:

- Frontend: http://localhost:5173
- API: http://localhost:8000/health
- Documentacion OpenAPI: http://localhost:8000/docs

Para cargar los usuarios y datos de demostracion (una vez que la API este saludable):

```powershell
.\local\seed.ps1
```

El administrador de prueba es `admin@apuradito.bo` con la contrasena `Admin2026!`.

## Uso diario

```powershell
.\local\start.ps1
.\local\logs.ps1
.\local\logs.ps1 -Service backend
.\local\stop.ps1
```

Los cambios en `backend/` recargan Uvicorn y los cambios en `frontend/` se actualizan mediante Vite. La base de datos y Redis conservan los datos en volumenes de Docker al detener los servicios.

El perfil `-Ai` inicia tres contenedores especializados: OCR (`8011`), facial
(`8012`) y rutas (`8013`). Requiere más RAM y tarda más en construirse. Para un
equipo limitado, configura `OCR_ENGINE=tesseract` y `FACE_ENGINE=opencv` en
`local/.env`; esos modos son fallbacks funcionales, pero no realizan la misma
verificación biométrica ni ofrecen la precisión de los modelos completos.

## Arquitectura

```text
Navegador -> Frontend Vite (5173) -> API FastAPI (8000)
                                      |-> PostgreSQL + PostGIS (5432)
                                      `-> Redis (6379)
```

El frontend usa la API en `http://localhost:8000`, que es el comportamiento local ya definido por el proyecto. Esta distribucion no contiene credenciales de Supabase ni de produccion.

## Cambiar puertos o credenciales de desarrollo

Edita solamente `local/.env` y reinicia los servicios con `./local/stop.ps1` seguido de `./local/start.ps1`. No uses los valores de este archivo para Render o Supabase.

## Solucion de problemas

- Si un puerto esta ocupado, cambia su valor correspondiente en `local/.env` y reinicia. Si cambias `FRONTEND_PORT`, el CORS del backend se adapta automaticamente.
- Para ver el estado: `docker compose --env-file .\local\.env -f .\local\compose.yaml ps`.
- Para errores de arranque: `./local/logs.ps1 -Service backend`.
- La primera construccion puede tardar porque descarga las dependencias de Python y Node.js.

No ejecutes `docker compose down --volumes` salvo que quieras eliminar de forma irreversible la base de datos y la cache de desarrollo.
