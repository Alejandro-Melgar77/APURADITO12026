import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:dio/dio.dart';

/// Repositorio de Conductor
class DriverRepository {
  final ApiClient _apiClient = ApiClient();

  /// Publicar una nueva ruta
  Future<PublishedRouteModel> publishRoute({
    required double origenLat,
    required double origenLng,
    required double destinoLat,
    required double destinoLng,
    required String origenDireccion,
    required String destinoDireccion,
    required int asientos,
    required DateTime horaSalida,
  }) async {
    final Map<String, dynamic> data = <String, dynamic>{
      'origen_lat': origenLat,
      'origen_lng': origenLng,
      'destino_lat': destinoLat,
      'destino_lng': destinoLng,
      'origen_direccion': origenDireccion,
      'destino_direccion': destinoDireccion,
      'asientos_disponibles': asientos,
      'hora_salida': horaSalida.toIso8601String(),
    };
    return publishRouteFromPayload(data);
  }

  Future<PublishedRouteModel> publishRouteFromPayload(
      Map<String, dynamic> payload) async {
    final double origenLat = (payload['origen_lat'] as num).toDouble();
    final double origenLng = (payload['origen_lng'] as num).toDouble();
    final double destinoLat = (payload['destino_lat'] as num).toDouble();
    final double destinoLng = (payload['destino_lng'] as num).toDouble();
    final Response<dynamic> response = await _apiClient.post<dynamic>(
      '/api/v1/rutas/',
      data: <String, dynamic>{
        'origen_coor': <String, double>{'lat': origenLat, 'lon': origenLng},
        'destino_coor': <String, double>{'lat': destinoLat, 'lon': destinoLng},
        'linea_ruta_coor': <Map<String, double>>[
          <String, double>{'lat': origenLat, 'lon': origenLng},
          <String, double>{'lat': destinoLat, 'lon': destinoLng},
        ],
        'origen_direccion': payload['origen_direccion'],
        'destino_direccion': payload['destino_direccion'],
        'asientos_disponibles': payload['asientos_disponibles'],
        'hora_salida': payload['hora_salida'],
        'distancia_total_km': payload['distancia_total_km'],
        'duracion_estimada_min': payload['duracion_estimada_min'],
        'guardar_recorrido': true,
      },
    );
    return PublishedRouteModel.fromJson(
      Map<String, dynamic>.from(response.data as Map),
    );
  }

  /// Obtener solicitudes pendientes
  Future<List<RideRequestModel>> getPendingRequests(
      {required String rutaId}) async {
    final Response<dynamic> response = await _apiClient
        .get<dynamic>('/api/v1/viajes/rutas/$rutaId/solicitudes');
    final List list = response.data as List;
    return list
        .whereType<Map>()
        .map((Map<dynamic, dynamic> item) =>
            RideRequestModel.fromJson(Map<String, dynamic>.from(item)))
        .toList();
  }

  /// Aceptar solicitud de viaje
  Future<void> acceptRequest(String solicitudId) async {
    await _apiClient.post<dynamic>('/api/v1/viajes/$solicitudId/aceptar');
  }

  /// Rechazar solicitud de viaje
  Future<void> rejectRequest(String solicitudId) async {
    await _apiClient.post<dynamic>('/api/v1/viajes/$solicitudId/rechazar');
  }

  /// Iniciar viaje
  Future<void> startRide(String rutaId) async {
    await _apiClient.post<dynamic>('/api/v1/rutas/$rutaId/iniciar');
  }

  /// Finalizar viaje
  Future<void> finishRide(String rutaId) async {
    await _apiClient.post<dynamic>('/api/v1/rutas/$rutaId/finalizar');
  }

  Future<void> completeRide(String solicitudId) =>
      _apiClient.post<dynamic>('/api/v1/viajes/$solicitudId/completar');

  /// Obtener rutas del conductor
  Future<List<PublishedRouteModel>> getMyRoutes() async {
    final Response<dynamic> response =
        await _apiClient.get<dynamic>('/api/v1/rutas/mias');
    final List list = response.data as List;
    return list
        .whereType<Map>()
        .map((Map<dynamic, dynamic> item) =>
            PublishedRouteModel.fromJson(Map<String, dynamic>.from(item)))
        .toList();
  }
}
