# 📊 RESUMEN GENERAL — AVANCES DE IMPLEMENTACIÓN APURADITO

## Estado General del Proyecto

| Fase | Nombre | Estado | Agente |
|------|--------|--------|--------|
| 0 | Fundamentos y Configuración | 🔄 En progreso | Agente Arquitecto |
| 1a | Backend Core (Modelos + Auth + CRUDs) | 🔄 En progreso | Agente Backend |
| 1b | Fórmulas, Matching y Pagos/Coins | 🔄 En progreso | Agente Fórmulas |
| 2a | Web Admin UI (Layout + Páginas) | 🔄 En progreso | Agente Frontend UI |
| 2b | Mapa en Vivo (Leaflet + WebSocket) | ⏳ Pendiente | Agente Mapas |
| 2c | Reportes Dinámicos y Exportación | ⏳ Pendiente | Agente Reportes |
| 3 | Motor de Simulación WebSocket | ⏳ Pendiente | Agente Simulación |
| 4 | IA/ML (Facial, Placas, ML Rutas) | ⏳ Pendiente | Agente IA/ML |
| 5 | App Móvil Flutter | ⏳ Pendiente | Agente Flutter |

## Arquitectura de la Solución

```
APURADITO/
├── backend/          FastAPI + SQLAlchemy + PostGIS + WebSockets
├── frontend/         React 18 + TypeScript + Vite + Recharts + Leaflet
├── mobile/           Flutter + Firebase (Fase 5)
└── docs/             Documentación técnica y legal
```

## Decisiones Técnicas Clave

| Decisión | Tecnología elegida | Razón |
|----------|-------------------|-------|
| BD geoespacial | PostgreSQL + PostGIS | Soporte nativo para geometrías y consultas espaciales |
| Estado frontend | Zustand | Más simple que Redux, suficiente para este proyecto |
| Gráficos | Recharts | Diseño limpio, compatible con React |
| Mapas web | Leaflet + react-leaflet | Gratuito, compatible con OSM |
| Auth móvil | Firebase | Notificaciones push + Google Auth |
| ML local | Scikit-learn | Offline, sin costo, suficiente para el MVP |
| Reconocimiento facial | InsightFace (ArcFace) | Offline, alta precisión, gratuito |
| OCR placas | EasyOCR | Offline, multilenguaje, gratuito |
| Scheduler | APScheduler | Integrado con FastAPI, sin dependencias extra |
| Exportación PDF | ReportLab (backend) | Más control que jsPDF |
| Exportación Excel | openpyxl (backend) | Nativo Python, sin dependencias JS |

## Variables de Configuración Global (editables desde admin)

| Variable | Valor Default | Unidad |
|----------|--------------|--------|
| precio_gasolina_bs_litro | 6.50 | Bs/litro |
| precio_diesel_bs_litro | 3.72 | Bs/litro |
| precio_gas_bs_metro_cubico | 2.50 | Bs/m³ |
| consumo_automovil_gasolina_l_por_km | 0.08 | L/km |
| consumo_automovil_diesel_l_por_km | 0.065 | L/km |
| consumo_automovil_gas_m3_por_km | 0.10 | m³/km |
| consumo_moto_gasolina_l_por_km | 0.03 | L/km |
| tarifa_base_automovil_bs | 3.00 | Bs |
| tarifa_base_moto_bs | 2.00 | Bs |
| comision_app_porcentaje | 15.0 | % |
| tipo_cambio_bs_usd | 6.86 | Bs/USD |
| radio_maximo_caminata_m | 800 | metros |
| limite_rutas_pasajero | 10 | rutas |
| meses_morosidad_congelamiento | 2 | meses |
| penalizacion_cancelacion_porcentaje | 10.0 | % |

## Credenciales por Defecto (Desarrollo)

| Servicio | Dato | Valor |
|----------|------|-------|
| Admin web | Email | admin@apuradito.bo |
| Admin web | Contraseña | Admin2026! |
| PostgreSQL | Usuario | apuradito_user |
| PostgreSQL | Contraseña | apuradito_pass_dev |
| PostgreSQL | BD | apuradito_db |
| PostgreSQL | Puerto | 5432 |
| Redis | Puerto | 6379 |

## Cómo Arrancar el Proyecto (Desarrollo Local)

```bash
# 1. Levantar la base de datos
docker-compose up -d

# 2. Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m seeds.run_all
uvicorn app.main:app --reload --port 8000

# 3. Frontend (nueva terminal)
cd frontend
npm install
npm run dev

# Acceder en: http://localhost:5173
```
