import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/core/network/connectivity_service.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/presentation/providers/map_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';

class RideTrackingScreen extends StatelessWidget {
  const RideTrackingScreen({super.key, required this.routeId});

  final String routeId;

  @override
  Widget build(BuildContext context) {
    final MapProvider routes = context.watch<MapProvider>();
    final ActiveRouteModel? route =
        routes.activeRoutes.cast<ActiveRouteModel?>().firstWhere(
              (ActiveRouteModel? item) => item?.id == routeId,
              orElse: () => null,
            );
    if (route == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Vehículo')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                const Icon(Icons.location_off, size: 48),
                const SizedBox(height: 12),
                const Text('Este vehículo ya no está disponible.',
                    textAlign: TextAlign.center),
                TextButton(
                    onPressed: () => context.pop(),
                    child: const Text('Volver')),
              ],
            ),
          ),
        ),
      );
    }

    final LatLng position = route.currentPosition ??
        const LatLng(AppConstants.sczLat, AppConstants.sczLng);
    return Scaffold(
      appBar: AppBar(title: const Text('Recorrido en vivo')),
      body: Column(
        children: <Widget>[
          Expanded(
            child: FlutterMap(
              options: MapOptions(
                  initialCenter: position,
                  initialZoom: AppConstants.mapZoomClose),
              children: <Widget>[
                TileLayer(
                    urlTemplate: AppConstants.osmTileUrl,
                    userAgentPackageName: 'com.apuradito.apuradito_mobile'),
                if (route.hasRoute)
                  PolylineLayer(
                    polylines: <Polyline>[
                      Polyline(
                          points: route.routePolyline,
                          color: const Color(0xFF7C3AED),
                          strokeWidth: 5)
                    ],
                  ),
                MarkerLayer(
                  markers: <Marker>[
                    Marker(
                      point: position,
                      width: 48,
                      height: 48,
                      child: const CircleAvatar(
                        backgroundColor: Color(0xFF7C3AED),
                        child: Icon(Icons.directions_car, color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(route.conductorNombreCompleto,
                      style: Theme.of(context).textTheme.titleLarge),
                  if (route.vehiculoPlaca?.isNotEmpty ?? false)
                    Text('Placa: ${route.vehiculoPlaca}',
                        style: const TextStyle(color: Colors.white70)),
                  const SizedBox(height: 12),
                  Text('${route.origenDireccion} → ${route.destinoDireccion}'),
                  const SizedBox(height: 4),
                  Text('${route.asientosDisponibles} asientos disponibles',
                      style: const TextStyle(color: Colors.white70)),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: routes.loadActiveRoutes,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Actualizar ubicación'),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: route.asientosDisponibles <= 0
                        ? null
                        : () {
                            if (!context.read<ConnectivityService>().isOnline) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text(
                                    'Conéctate a Internet para solicitar un asiento.',
                                  ),
                                ),
                              );
                              return;
                            }
                            context.push('/passenger/request/$routeId');
                          },
                    icon: const Icon(Icons.event_seat),
                    label: Text(route.asientosDisponibles <= 0
                        ? 'Sin asientos disponibles'
                        : 'Solicitar un asiento'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
