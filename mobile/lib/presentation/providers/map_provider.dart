import 'package:flutter/material.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';

class MapProvider extends ChangeNotifier {
  List<ActiveRouteModel> activeRoutes = [];
  ActiveRouteModel? selectedRoute;
  bool isConnected = false;

  void handleWsMessage(Map<String, dynamic> message) {
    if (message['tipo'] == 'viajes_activos' && message['data'] != null) {
      final List data = message['data'];
      final List<ActiveRouteModel> parsedRoutes = data
          .map((e) => ActiveRouteModel.fromJson(e))
          .where((route) => route.hasPosition == true)
          .toList();
      
      activeRoutes = parsedRoutes;
      notifyListeners();
    }
  }

  void selectRoute(ActiveRouteModel? route) {
    selectedRoute = route;
    notifyListeners();
  }

  void clearSelection() {
    selectedRoute = null;
    notifyListeners();
  }

  void setConnectionStatus(bool status) {
    if (isConnected != status) {
      isConnected = status;
      notifyListeners();
    }
  }
}
