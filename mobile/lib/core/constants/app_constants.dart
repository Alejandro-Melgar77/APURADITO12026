/// Configuración y constantes compartidas de la aplicación.
///
/// La URL se inyecta al compilar con `--dart-define`; así ningún servidor de
/// desarrollo o producción queda codificado en la app publicada.
library;

import 'package:flutter/foundation.dart';

class AppConstants {
  AppConstants._();

  /// API local para el emulador Android. Sobrescribir en un dispositivo físico
  /// o producción con `--dart-define=API_BASE_URL=...`.
  static const String _configuredApiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  /// URL WebSocket opcional. Si se omite se deriva de [apiBaseUrl].
  static const String _configuredWsViajesUrl = String.fromEnvironment(
    'WS_VIAJES_URL',
    defaultValue: '',
  );

  static String get baseUrl {
    final String fallback =
        kIsWeb ? 'http://localhost:8000' : 'http://10.0.2.2:8000';
    return (_configuredApiBaseUrl.isEmpty ? fallback : _configuredApiBaseUrl)
        .replaceFirst(RegExp(r'/+$'), '');
  }

  static String get wsViajesUrl {
    if (_configuredWsViajesUrl.isNotEmpty) {
      return _configuredWsViajesUrl;
    }
    final Uri apiUri = Uri.parse(baseUrl);
    final String scheme = apiUri.scheme == 'https' ? 'wss' : 'ws';
    return apiUri.replace(scheme: scheme, path: '/ws/viajes').toString();
  }

  static const String loginEndpoint = '/api/v1/auth/login';
  static const String profileEndpoint = '/api/v1/auth/me';

  static const String tokenKey = 'auth_token';
  static const String userKey = 'auth_user';
  static const String rolKey = 'active_rol';

  static const int connectTimeoutMs = 10000;
  static const int receiveTimeoutMs = 15000;
  static const int wsReconnectDelayMs = 3000;

  static const double sczLat = -17.7832;
  static const double sczLng = -63.1821;
  static const double mapZoomDefault = 13.0;
  static const double mapZoomClose = 15.0;
  static const String osmTileUrl =
      'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

  static const String rolPasajero = 'pasajero';
  static const String rolConductor = 'conductor';
  static const String rolAdmin = 'admin';

  static const String wsViajesActivos = 'viajes_activos';
  static const String appName = 'Apuradito';
  static const String appTagline = 'Tu viaje, tu ruta';
}
