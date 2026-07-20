/// Constantes globales de la aplicación Apuradito.
/// Effective Dart: use const for compile-time constants.
class AppConstants {
  AppConstants._();

  // ── URLs de API ────────────────────────────────────────────────────────────
  /// Base URL para emulador Android (10.0.2.2 apunta a localhost del host)
  static const String baseUrl = 'http://10.0.2.2:8000';

  /// URL WebSocket del feed unificado de viajes activos
  static const String wsViajesUrl = 'ws://10.0.2.2:8000/ws/viajes';

  // ── Endpoints ──────────────────────────────────────────────────────────────
  static const String loginEndpoint = '/api/v1/auth/login';
  static const String registerEndpoint = '/api/v1/auth/register';
  static const String profileEndpoint = '/api/v1/auth/me';
  static const String rutasEndpoint = '/api/v1/rutas/';
  static const String solicitudesEndpoint = '/api/v1/solicitudes/';
  static const String pagosEndpoint = '/api/v1/pagos/';
  static const String walletEndpoint = '/api/v1/wallet/';
  static const String recargasEndpoint = '/api/v1/recargas/';
  static const String calificacionesEndpoint = '/api/v1/calificaciones/';
  static const String conductorEndpoint = '/api/v1/conductores/me';
  static const String vehiculosEndpoint = '/api/v1/vehiculos/';
  static const String matchingEndpoint = '/api/v1/matching/';

  // ── Almacenamiento Local ───────────────────────────────────────────────────
  static const String tokenKey = 'auth_token';
  static const String userKey = 'auth_user';
  static const String rolKey = 'active_rol';

  // ── Tiempos de Espera ──────────────────────────────────────────────────────
  static const int connectTimeoutMs = 10000;
  static const int receiveTimeoutMs = 15000;
  static const int wsReconnectDelayMs = 3000;

  // ── Mapa (Santa Cruz de la Sierra) ────────────────────────────────────────
  static const double sczLat = -17.7832;
  static const double sczLng = -63.1821;
  static const double mapZoomDefault = 13.0;
  static const double mapZoomClose = 15.0;
  static const String osmTileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

  // ── OSRM Routing ──────────────────────────────────────────────────────────
  static const String osrmUrl =
      'http://router.project-osrm.org/route/v1/driving';

  // ── Roles ─────────────────────────────────────────────────────────────────
  static const String rolPasajero = 'pasajero';
  static const String rolConductor = 'conductor';
  static const String rolAdmin = 'admin';

  // ── WebSocket mensaje tipos ────────────────────────────────────────────────
  static const String wsViajesActivos = 'viajes_activos';

  // ── Texto app ─────────────────────────────────────────────────────────────
  static const String appName = 'Apuradito';
  static const String appTagline = 'Tu viaje, tu ruta';
}
