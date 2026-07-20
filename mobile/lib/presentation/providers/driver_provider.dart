import 'package:apuradito_mobile/core/storage/offline_action_queue.dart';
import 'package:flutter/material.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/data/repositories/driver_repository.dart';
import 'package:dio/dio.dart';

/// Provider para la gestión del conductor
class DriverProvider extends ChangeNotifier {
  final DriverRepository _repository = DriverRepository();
  final OfflineActionQueue _offlineQueue = OfflineActionQueue();

  PublishedRouteModel? activeRoute;
  List<RideRequestModel> pendingRequests = [];
  List<PublishedRouteModel> myRoutes = [];

  bool isLoading = false;
  bool isOnline = false;
  String? errorMessage;
  bool lastActionQueued = false;

  /// Cambia el estado de disponibilidad del conductor
  void toggleOnline() {
    isOnline = !isOnline;
    notifyListeners();
  }

  /// Publica una nueva ruta
  Future<void> publishRoute({
    required String userId,
    required double origenLat,
    required double origenLng,
    required double destinoLat,
    required double destinoLng,
    required String origenDireccion,
    required String destinoDireccion,
    required int asientos,
    required DateTime horaSalida,
  }) async {
    isLoading = true;
    errorMessage = null;
    lastActionQueued = false;
    notifyListeners();
    try {
      activeRoute = await _repository.publishRoute(
        origenLat: origenLat,
        origenLng: origenLng,
        destinoLat: destinoLat,
        destinoLng: destinoLng,
        origenDireccion: origenDireccion,
        destinoDireccion: destinoDireccion,
        asientos: asientos,
        horaSalida: horaSalida,
      );
    } on DioException catch (error) {
      if (_isOfflineError(error)) {
        await _offlineQueue.enqueue(
          userId: userId,
          type: PendingActionType.publishRoute,
          payload: <String, dynamic>{
            'origen_lat': origenLat,
            'origen_lng': origenLng,
            'destino_lat': destinoLat,
            'destino_lng': destinoLng,
            'origen_direccion': origenDireccion,
            'destino_direccion': destinoDireccion,
            'asientos_disponibles': asientos,
            'hora_salida': horaSalida.toIso8601String(),
          },
        );
        lastActionQueued = true;
      } else {
        errorMessage = _messageFromError(error);
      }
    } catch (_) {
      errorMessage = 'No se pudo publicar la ruta. Intentalo nuevamente.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadMyRoutes() async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      myRoutes = await _repository.getMyRoutes();
      activeRoute = myRoutes.cast<PublishedRouteModel?>().firstWhere(
            (PublishedRouteModel? route) =>
                route?.estado == 'programada' || route?.estado == 'en_curso',
            orElse: () => null,
          );
    } on DioException catch (error) {
      errorMessage = _messageFromError(error);
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Carga solicitudes pendientes para la ruta activa
  Future<void> loadPendingRequests() async {
    if (activeRoute == null) return;
    isLoading = true;
    notifyListeners();
    try {
      pendingRequests = await _repository.getPendingRequests(
        rutaId: activeRoute!.id,
      );
    } on DioException catch (error) {
      errorMessage = _messageFromError(error);
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Acepta una solicitud de pasajero
  Future<void> acceptRequest(String solicitudId) async {
    try {
      await _repository.acceptRequest(solicitudId);
      pendingRequests = pendingRequests
          .map((RideRequestModel request) => request.id == solicitudId
              ? RideRequestModel(
                  id: request.id,
                  estado: 'aceptada',
                  costoCalculadoBs: request.costoCalculadoBs,
                  metodoPago: request.metodoPago,
                  pasajeroNombre: request.pasajeroNombre,
                  rutaId: request.rutaId,
                  conductorId: request.conductorId,
                  conductorNombre: request.conductorNombre,
                )
              : request)
          .toList();
      notifyListeners();
    } on DioException catch (error) {
      errorMessage = _messageFromError(error);
      notifyListeners();
    }
  }

  /// Rechaza una solicitud de pasajero
  Future<void> rejectRequest(String solicitudId) async {
    try {
      await _repository.rejectRequest(solicitudId);
      pendingRequests
          .removeWhere((RideRequestModel req) => req.id == solicitudId);
      notifyListeners();
    } on DioException catch (error) {
      errorMessage = _messageFromError(error);
      notifyListeners();
    }
  }

  /// Finaliza la ruta activa actual
  Future<void> finishRoute() async {
    if (activeRoute == null) return;
    isLoading = true;
    notifyListeners();
    try {
      await _repository.finishRide(activeRoute!.id);
      activeRoute = null;
      pendingRequests.clear();
    } on DioException catch (error) {
      errorMessage = _messageFromError(error);
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> startRoute() async {
    if (activeRoute == null) return;
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      await _repository.startRide(activeRoute!.id);
      activeRoute = activeRoute!.copyWith(estado: 'en_curso');
      myRoutes = myRoutes
          .map((PublishedRouteModel route) =>
              route.id == activeRoute!.id ? activeRoute! : route)
          .toList();
    } on DioException catch (error) {
      errorMessage = _messageFromError(error);
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> completeRequest(String solicitudId) async {
    try {
      await _repository.completeRide(solicitudId);
      pendingRequests
          .removeWhere((RideRequestModel request) => request.id == solicitudId);
      notifyListeners();
    } on DioException catch (error) {
      errorMessage = _messageFromError(error);
      notifyListeners();
    }
  }

  bool _isOfflineError(DioException error) =>
      error.response == null &&
      <DioExceptionType>{
        DioExceptionType.connectionError,
        DioExceptionType.connectionTimeout,
        DioExceptionType.receiveTimeout,
        DioExceptionType.sendTimeout,
      }.contains(error.type);

  String _messageFromError(DioException error) {
    final Object? detail = error.response?.data is Map
        ? (error.response!.data as Map)['detail']
        : null;
    return detail is String && detail.isNotEmpty
        ? detail
        : 'No se pudo completar la operacion. Revisa tu conexion.';
  }
}
