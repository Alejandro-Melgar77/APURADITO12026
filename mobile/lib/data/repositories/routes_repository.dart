import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/core/storage/offline_store.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:dio/dio.dart';

class RoutesRepository {
  static const String _routesCacheKey = 'available_routes_v1';
  final ApiClient _apiClient = ApiClient();

  Future<List<ActiveRouteModel>> getActiveRoutes() async {
    try {
      final Response<dynamic> response =
          await _apiClient.get<dynamic>('/api/v1/rutas/disponibles');
      final List<ActiveRouteModel> routes = (response.data as List)
          .whereType<Map>()
          .map((Map<dynamic, dynamic> item) =>
              ActiveRouteModel.fromJson(Map<String, dynamic>.from(item)))
          .toList();
      await OfflineStore.write(
        _routesCacheKey,
        routes.map((ActiveRouteModel route) => route.toJson()).toList(),
      );
      return routes;
    } on DioException {
      final List<Map<String, dynamic>> cached =
          await OfflineStore.readList(_routesCacheKey);
      if (cached.isEmpty) rethrow;
      return cached.map(ActiveRouteModel.fromJson).toList(growable: false);
    }
  }

  Future<Map<String, dynamic>> requestRide({
    required String rutaId,
    required double origenLat,
    required double origenLng,
    required double destinoLat,
    required double destinoLng,
    required double distanciaViajeKm,
    required String metodoPago,
  }) async {
    final response = await _apiClient.post<dynamic>(
      '/api/v1/viajes/solicitar',
      data: {
        'ruta_publicada_id': rutaId,
        'punto_abordaje': {'lat': origenLat, 'lon': origenLng},
        'punto_desabordaje': {'lat': destinoLat, 'lon': destinoLng},
        'distancia_caminata_abordaje_m': 0,
        'distancia_caminata_desabordaje_m': 0,
        'distancia_viaje_km': distanciaViajeKm,
        'costo_calculado_bs': 0,
        'metodo_pago': metodoPago,
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<RideRequestModel>> getMyRides(String userId) async {
    final String cacheKey = 'my_rides_$userId';
    try {
      final Response<dynamic> response =
          await _apiClient.get<dynamic>('/api/v1/viajes/mis-solicitudes');
      final List<RideRequestModel> rides = (response.data as List)
          .whereType<Map>()
          .map((Map<dynamic, dynamic> item) =>
              RideRequestModel.fromJson(Map<String, dynamic>.from(item)))
          .toList();
      await OfflineStore.write(
        cacheKey,
        rides.map((RideRequestModel ride) => ride.toJson()).toList(),
      );
      return rides;
    } on DioException {
      final List<Map<String, dynamic>> cached =
          await OfflineStore.readList(cacheKey);
      if (cached.isEmpty) rethrow;
      return cached.map(RideRequestModel.fromJson).toList(growable: false);
    }
  }

  Future<Map<String, dynamic>> rateRide({
    required String solicitudId,
    required String calificadoId,
    required int estrellas,
    String? comentario,
  }) async {
    final response = await _apiClient.post<dynamic>(
      '/api/v1/viajes/$solicitudId/calificar',
      data: {
        'calificado_id': calificadoId,
        'estrellas': estrellas,
        'comentario': comentario,
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<void> cancelRide(String solicitudId) =>
      _apiClient.post<dynamic>('/api/v1/viajes/$solicitudId/cancelar');
}
