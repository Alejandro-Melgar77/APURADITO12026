# 🚗 Apuradito — App de Viajes Compartidos

**Plataforma de carpooling para Santa Cruz de la Sierra, Bolivia**

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | FastAPI (Python) |
| Frontend Web | React + TypeScript + Vite |
| App Móvil | Flutter |
| Base de Datos | PostgreSQL 16 + PostGIS 3.4 |
| Caché | Redis 7 |
| Mapas | OpenStreetMap + Leaflet |
| Auth Móvil | Firebase |
| Despliegue Backend | Render |
| Despliegue Frontend | Vercel |
| BD Producción | Supabase |

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Python 3.11+
- Node.js 20+
- Git

## Instalación y Arranque Local

### 1. Clonar el repositorio
```bash
git clone [url-del-repositorio]
cd APURADITO
```

### 2. Levantar la base de datos
```bash
docker-compose up -d
```
Esperar ~10 segundos para que PostgreSQL inicie.

### 3. Configurar el backend
```bash
cd backend
cp .env.example .env
# Editar .env si es necesario (por defecto funciona con Docker)
pip install -r requirements.txt
alembic upgrade head
python -m seeds.run_all
uvicorn app.main:app --reload --port 8000
```

### 4. Iniciar el frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Acceder
- **API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Admin Web**: http://localhost:5173

### Credenciales por defecto del admin
- Email: `admin@apuradito.bo`
- Contraseña: `Admin2026!`

## Estructura del Proyecto

```
APURADITO/
├── APARIENCIA VISUAL/     # Mockups y logo
├── AVANCES DE IMPLEMENTACION/  # Documentación por fase
├── backend/               # FastAPI
├── frontend/              # React + Vite
├── mobile/                # Flutter
├── docs/                  # Documentación técnica y legal
├── docker-compose.yml
└── README.md
```

## Convenciones

- **Commits**: En español. Ejemplo: `feat: agregar módulo de rutas`
- **Ramas**: `fase-X/nombre-modulo`
- **Código**: Comentarios en español
- **UI**: 100% en español
