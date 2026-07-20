# Estado de la Fase 2 — Web Admin UI

## Estado: EN PROGRESO 🔄 (Estructura y Formularios Listos)

Se ha completado el diseño visual y la integración de las principales páginas del panel web de administración basándose en los mockups de `APARIENCIA VISUAL`.

## Entregables Implementados

### 1. Estructura y Entorno del Frontend
- **package.json, vite.config.ts, tsconfig.json**: Configuración lista con proxy al backend FastAPI y dependencias necesarias (React Router, Zustand, Axios, Recharts, Leaflet, Lucide-React).
- **index.html y index.css**: Carga de tipografía Inter, hoja de estilos de Leaflet y definición de variables CSS para el tema claro/oscuro morado y blanco.
- **useEnvStore (Zustand)**: Control global de entorno mediante el botón "⚡ Local" o "🌐 En línea" en el encabezado, actualizando automáticamente el cliente Axios.
- **useAuthStore (Zustand)**: Control y persistencia local de la sesión del administrador y JWT.

### 2. Componentes y Layout Premium
- **Sidebar**: Barra lateral con enlaces activos en color violeta, logo de Apuradito e íconos.
- **Header**: Con buscador central, notificaciones, cambio de tema claro/oscuro, y perfil con avatar.
- **ThemeToggle**: Selector que aplica `data-theme="dark"` al root HTML y persiste en el navegador.
- **KPICard**: Tarjeta con visualización de tendencias, subtítulos e íconos.
- **SkeletonLoader**: Vistas de esqueleto animado para las tarjetas de KPIs, gráficos y filas de tablas.

### 3. Páginas Principales
- **LoginPage**: Replicado del mockup `LOGIN.png`, con formulario limpio, toggle para ver contraseña y autenticación JWT con control de rol admin.
- **DashboardPage**: Replicado del mockup `INTERFAZ WEB PARTE 2.png`, con filtro de periodos, 4 KPICards y 2 gráficos interactivos (Recharts): viajes diarios y registros de usuarios.
- **UsuariosPage**: Replicado del mockup `INTERFAZ WEB PARTE 3.png`, con buscador por texto, combos de filtro (rol y estado), tabla con paginación, cambio de estado (suspender/activar), eliminación lógica y modal para crear nuevos usuarios.
- **ConfiguracionPage**: Formulario agrupado para la edición directa en el backend de las 15 variables globales, e incorporación de una **Calculadora de Tarifas** para testeo rápido de precios.

### 4. Rutas y Placeholders
- **App.tsx**: Enrutamiento protegido de las páginas implementadas e incorporación de placeholders dinámicos para los módulos que se construirán en las siguientes fases (Viajes con mapa Leaflet, Simulador WebSockets, Reportes con PDFs/Excel, Políticas editor y Reclamos).
