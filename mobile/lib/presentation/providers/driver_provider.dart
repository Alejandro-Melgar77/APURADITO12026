import 'package:flutter/material.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/data/repositories/driver_repository.dart';

/// Provider para la gestión del conductor
class DriverProvider extends ChangeNotifier {
  final DriverRepository _repository = DriverRepository();

  PublishedRouteModel? activeRoute;
  List<RideRequestModel> pendingRequests = [];
  
  bool isLoading = false;
  bool isOnline = false;
  String? errorMessage;

  /// Cambia el estado de disponibilidad del conductor
  void toggleOnline() {
    isOnline = !isOnline;
    notifyListeners();
  }

  /// Publica una nueva ruta
  Future<void> publishRoute({
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
    isLoading = true;
    errorMessage = null;
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
        costo: costo,
        horaSalida: horaSalida,
      );
    } catch (e) {
      errorMessage = e.toString();
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
      pendingRequests = await _repository.getPendingRequests(rutaId: activeRoute!.id);
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Acepta una solicitud de pasajero
  Future<void> acceptRequest(String solicitudId) async {
    try {
      await _repository.acceptRequest(solicitudId);
      pendingRequests.removeWhere((req) => req.id == solicitudId);
      notifyListeners();
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
    }
  }

  /// Rechaza una solicitud de pasajero
  Future<void> rejectRequest(String solicitudId) async {
    try {
      await _repository.rejectRequest(solicitudId);
      pendingRequests.removeWhere((req) => req.id == solicitudId);
      notifyListeners();
    } catch (e) {
      errorMessage = e.toString();
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
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
