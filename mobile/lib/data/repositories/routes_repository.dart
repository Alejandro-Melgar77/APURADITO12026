import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';

class RoutesRepository {
  final ApiClient _apiClient = ApiClient();

  Future<List<ActiveRouteModel>> getActiveRoutes() async {
    final response = await _apiClient.get(
      '/api/v1/rutas/',
      queryParameters: {'estado': 'activa'},
    );
    
    return (response.data as List)
        .map((e) => ActiveRouteModel.fromJson(e))
        .toList();
  }

  Future<Map<String, dynamic>> requestRide({
    required String rutaId,
    required double origenLat,
    required double origenLng,
    required double destinoLat,
    required double destinoLng,
  }) async {
    final response = await _apiClient.post(
      '/api/v1/solicitudes/',
      data: {
        'ruta_publicada_id': rutaId,
        'origen_lat': origenLat,
        'origen_lng': origenLng,
        'destino_lat': destinoLat,
        'destino_lng': destinoLng,
        'metodo_pago': 'coins',
      },
    );
    return response.data;
  }

  Future<List<RideRequestModel>> getMyRides() async {
    final response = await _apiClient.get('/api/v1/solicitudes/mis-solicitudes');
    return (response.data as List)
        .map((e) => RideRequestModel.fromJson(e))
        .toList();
  }

  Future<Map<String, dynamic>> rateRide({
    required String solicitudId,
    required int estrellas,
    String? comentario,
  }) async {
    final response = await _apiClient.post(
      '/api/v1/calificaciones/',
      data: {
        'solicitud_viaje_id': solicitudId,
        'estrellas': estrellas,
        'comentario': comentario,
      },
    );
    return response.data;
  }
}
