import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';

/// Repositorio de Conductor
class DriverRepository {
  final ApiClient _apiClient = ApiClient();

  /// Obtener perfil del conductor
  Future<Map<String, dynamic>> getDriverProfile() async {
    final response = await _apiClient.get('/api/v1/conductores/me');
    return response.data as Map<String, dynamic>;
  }

  /// Publicar una nueva ruta
  Future<PublishedRouteModel> publishRoute({
    required double origenLat,
    required double origenLng,
    required double destinoLat,
    required double destinoLng,
    required String origenDireccion,
    required String destinoDireccion,
    required int asientos,
    required double costo,
    required DateTime horaSalida,
  }) async {
    final data = {
      'origen_lat': origenLat,
      'origen_lng': origenLng,
      'destino_lat': destinoLat,
      'destino_lng': destinoLng,
      'origen_direccion': origenDireccion,
      'destino_direccion': destinoDireccion,
      'asientos_disponibles': asientos,
      'costo_calculado_bs': costo,
      'hora_salida': horaSalida.toIso8601String(),
    };
    final response = await _apiClient.post('/api/v1/rutas/', data: data);
    return PublishedRouteModel.fromJson(response.data);
  }

  /// Obtener solicitudes pendientes
  Future<List<RideRequestModel>> getPendingRequests({required String rutaId}) async {
    final response = await _apiClient.get(
      '/api/v1/solicitudes/?ruta_publicada_id=$rutaId&estado=pendiente',
    );
    final List list = response.data as List;
    return list.map((e) => RideRequestModel.fromJson(e)).toList();
  }

  /// Aceptar solicitud de viaje
  Future<void> acceptRequest(String solicitudId) async {
    await _apiClient.patch(
      '/api/v1/solicitudes/$solicitudId/estado',
      data: {'nuevo_estado': 'aceptado'},
    );
  }

  /// Rechazar solicitud de viaje
  Future<void> rejectRequest(String solicitudId) async {
    await _apiClient.patch(
      '/api/v1/solicitudes/$solicitudId/estado',
      data: {'nuevo_estado': 'rechazado'},
    );
  }

  /// Iniciar viaje
  Future<void> startRide(String rutaId) async {
    await _apiClient.patch(
      '/api/v1/rutas/$rutaId/estado',
      data: {'nuevo_estado': 'en_curso'},
    );
  }

  /// Finalizar viaje
  Future<void> finishRide(String rutaId) async {
    await _apiClient.patch(
      '/api/v1/rutas/$rutaId/estado',
      data: {'nuevo_estado': 'completada'},
    );
  }

  /// Obtener rutas del conductor
  Future<List<PublishedRouteModel>> getMyRoutes() async {
    final response = await _apiClient.get('/api/v1/rutas/mis-rutas');
    final List list = response.data as List;
    return list.map((e) => PublishedRouteModel.fromJson(e)).toList();
  }
}
