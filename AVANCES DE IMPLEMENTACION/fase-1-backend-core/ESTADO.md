# Estado de la Fase 1 — Backend Core, Fórmulas y Pagos

## Estado: COMPLETADO ✅

Se ha completado al 100% el Backend Core y las Fórmulas y Pagos (Fase 1a y Fase 1b).

## Entregables Implementados

### 1. Modelos SQLAlchemy (PostgreSQL + PostGIS)
- **Usuario**: Gestión de cuentas de admin, conductores, pasajeros, saldo de coins, verificado facial, google_uid, etc.
- **Conductor**: Calificación promedio, km totales, viajes realizados, comisiones impagas y lógica de congelamiento de cuenta.
- **Vehiculo**: Registro de automóviles y motos (placa, tipo de combustible, año, asientos, estado activo).
- **RutaPublicada**: Origen, destino y línea del recorrido como objetos PostGIS Geography (srid: 4326), hora de salida y asientos.
- **SolicitudViaje**: Puntos de abordaje y desabordaje PostGIS, costos calculados, penalización y método de pago (coins, efectivo, nfc).
- **Pago**: Comisiones calculadas automáticamente (15% por defecto) y distribución de ganancias del conductor.
- **RecargaCoins**: Referencia única para QR (`APU-XXXX-YYYY`) y saldo.
- **Calificacion**: Calificación 1-5 estrellas bidireccional por viaje, recalculando promedio del conductor.
- **ConfiguracionGlobal**: Variables dinámicas (combustible, consumo, tarifas, comisiones, límites).
- **Notificacion**: Registro persistente para la app.
- **Reclamo**: Plantillas y bandeja de entrada de denuncias de usuarios.
- **Politica**: Versionamiento de consentimientos y políticas legales.

### 2. Algoritmos Core y Fórmulas
- **Costo de combustible por Km**: Consumo del vehículo por precio de combustible de la configuración global.
- **Fórmula maestra de costo de viaje**: Prorrateado según número de asientos compartidos, tarifa base y comisiones de app.
- **Algoritmo de matching geoespacial**: Busca las 10 mejores rutas usando funciones espaciales PostGIS (`ST_DWithin`, `ST_ClosestPoint`, `ST_LineLocatePoint`, `ST_LineSubstring`).
- **Verificación de morosidad**: Bloquea a los conductores con más de 2 meses de deudas impagas.
- **Penalización por cancelación**: Carga el 10% del viaje al saldo del cancelador tras haber aceptado el viaje.

### 3. API Ruteada Completamente (/api/v1)
- **Auth**: Registro de pasajeros y conductores (creando su vehículo base), login seguro por email/pass con JWT (access/refresh token).
- **Usuarios**: CRUD y filtros de cuenta por el Administrador.
- **Conductores**: CRUD, veracidad facial y congelamiento manual.
- **Vehiculos**: Registro y validación de patentes.
- **Rutas**: Publicación y motor de búsqueda geoespacial para pasajeros.
- **Viajes**: Aceptación, rechazo, cancelación con multa, completado con cobro en coins o registro de deuda por efectivo, calificación.
- **Coins**: Generación de QR con referencia única, recarga simulada automatizada y wallet.
- **Configuracion**: Modificación de variables y reset de fábrica.
- **Reportes**: Cómputo de KPIs financieros y de uso para el panel de administración.
- **Políticas y Reclamos**: Registro y estado del workflow.

### 4. Semillas de Base de Datos (Seeds)
- `seed_configuracion.py`: Carga las 15 variables por defecto del sistema.
- `seed_usuarios.py`: Crea la cuenta de administrador (`admin@apuradito.bo` / `Admin2026!`), 3 conductores reales con vehículos y rutas predeterminadas, y 3 pasajeros con saldo cargado sobre la ciudad de Santa Cruz.
- `run_all.py`: Cargador unificado.
