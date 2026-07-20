import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/data/repositories/routes_repository.dart';
import 'package:flutter/material.dart';

class MapProvider extends ChangeNotifier {
  MapProvider({RoutesRepository? routesRepository})
      : _routesRepository = routesRepository ?? RoutesRepository();

  final RoutesRepository _routesRepository;
  List<ActiveRouteModel> activeRoutes = <ActiveRouteModel>[];
  ActiveRouteModel? selectedRoute;
  bool isLoading = false;
  String? errorMessage;

  Future<void> loadActiveRoutes() async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      activeRoutes = await _routesRepository.getActiveRoutes();
    } catch (_) {
      errorMessage = 'No se pudieron cargar los vehículos disponibles.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  void handleWsMessage(Map<String, dynamic> message) {
    if (message['tipo'] != AppConstants.wsViajesActivos ||
        message['data'] is! List) return;
    final List<ActiveRouteModel> liveRoutes = (message['data'] as List<dynamic>)
        .whereType<Map>()
        .map((Map<dynamic, dynamic> route) => ActiveRouteModel.fromJson(
              Map<String, dynamic>.from(route),
            ))
        .where((ActiveRouteModel route) => route.hasPosition)
        .toList();
    final Map<String, ActiveRouteModel> routesById = <String, ActiveRouteModel>{
      for (final ActiveRouteModel route in activeRoutes)
        if (route.estado == 'programada') route.id: route,
      for (final ActiveRouteModel route in liveRoutes) route.id: route,
    };
    activeRoutes = routesById.values.toList()
      ..sort((ActiveRouteModel a, ActiveRouteModel b) =>
          a.horaSalida.compareTo(b.horaSalida));
    if (selectedRoute != null) {
      final int index = activeRoutes.indexWhere(
          (ActiveRouteModel route) => route.id == selectedRoute!.id);
      selectedRoute = index == -1 ? null : activeRoutes[index];
    }
    notifyListeners();
  }

  void selectRoute(ActiveRouteModel? route) {
    selectedRoute = route;
    notifyListeners();
  }

  void clearSelection() => selectRoute(null);
}
