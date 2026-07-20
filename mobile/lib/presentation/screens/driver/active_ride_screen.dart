import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:provider/provider.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/presentation/providers/driver_provider.dart';

class ActiveRideScreen extends StatelessWidget {
  const ActiveRideScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<DriverProvider>();
    final route = provider.activeRoute;

    if (route == null) {
      return const Scaffold(
        backgroundColor: AppTheme.bgDark,
        body: Center(
          child: Text('No hay ruta activa', style: TextStyle(color: AppTheme.textPrimary)),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Viaje en Curso'),
        backgroundColor: AppTheme.bgDark,
      ),
      body: Column(
        children: [
          Expanded(
            child: FlutterMap(
              options: const MapOptions(
                initialCenter: latlong2.LatLng(AppConstants.sczLat, AppConstants.sczLng),
                initialZoom: 14,
              ),
              children: [
                TileLayer(
                  urlTemplate: AppConstants.osmTileUrl,
                  userAgentPackageName: 'com.apuradito.mobile',
                ),
                // Aquí irían los polyline de routePolyline si es un ActiveRouteModel
                // Para PublishedRouteModel dibujamos una simulación.
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(24.0),
            decoration: const BoxDecoration(
              color: AppTheme.bgSurface,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(AppTheme.radiusXl),
                topRight: Radius.circular(AppTheme.radiusXl),
              ),
              boxShadow: [
                BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, -4))
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Row(
                  children: [
                    Icon(Icons.directions_car, color: AppTheme.primaryLight, size: 28),
                    SizedBox(width: 12),
                    Text(
                      'En Ruta',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    const Icon(Icons.my_location, color: AppTheme.success),
                    const SizedBox(width: 8),
                    Expanded(child: Text(route.origenDireccion, style: const TextStyle(color: AppTheme.textPrimary))),
                  ],
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  child: Icon(Icons.more_vert, color: AppTheme.textMuted, size: 16),
                ),
                Row(
                  children: [
                    const Icon(Icons.place, color: AppTheme.error),
                    const SizedBox(width: 8),
                    Expanded(child: Text(route.destinoDireccion, style: const TextStyle(color: AppTheme.textPrimary))),
                  ],
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.success,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  onPressed: () async {
                    await provider.finishRoute();
                    if (context.mounted) Navigator.pop(context);
                  },
                  child: const Text('Finalizar Viaje', style: TextStyle(fontSize: 18)),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
