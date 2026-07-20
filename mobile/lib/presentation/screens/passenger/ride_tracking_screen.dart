import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/presentation/providers/map_provider.dart';

class RideTrackingScreen extends StatefulWidget {
  final String routeId;

  const RideTrackingScreen({super.key, required this.routeId});

  @override
  State<RideTrackingScreen> createState() => _RideTrackingScreenState();
}

class _RideTrackingScreenState extends State<RideTrackingScreen> {
  final MapController _mapController = MapController();

  void _showRatingDialog() {
    int _rating = 5;
    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: const Color(0xFF1A1035),
              title: const Text('Califica tu viaje', style: TextStyle(color: Colors.white)),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(5, (index) {
                      return IconButton(
                        icon: Icon(
                          index < _rating ? Icons.star : Icons.star_border,
                          color: Colors.amber,
                          size: 32,
                        ),
                        onPressed: () {
                          setState(() {
                            _rating = index + 1;
                          });
                        },
                      );
                    }),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    Navigator.of(context).pop(); // Volver al inicio
                  },
                  child: const Text('Enviar', style: TextStyle(color: Color(0xFF7C3AED))),
                ),
              ],
            );
          }
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final mapProvider = context.watch<MapProvider>();
    final ActiveRouteModel? route = mapProvider.activeRoutes.firstWhere(
      (r) => r.id == widget.routeId,
      orElse: () => ActiveRouteModel(
        id: widget.routeId,
        conductorNombre: '',
        conductorApellido: '',
        origenDireccion: '',
        destinoDireccion: '',
        asientosDisponibles: 0,
        estado: '',
        horaSalida: '',
        lat: AppConstants.sczLat,
        lng: AppConstants.sczLng,
      ),    );

    final points = route?.routePolyline ?? [];
    final currentLat = route?.lat ?? AppConstants.sczLat;
    final currentLng = route?.lng ?? AppConstants.sczLng;

    return Scaffold(
      body: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: LatLng(currentLat, currentLng),
              initialZoom: 15.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              ),
              if (points.isNotEmpty)
                PolylineLayer(
                  polylines: [
                    Polyline(
                      points: points,
                      color: const Color(0xFF7C3AED),
                      strokeWidth: 5.0,
                      strokeJoin: StrokeJoin.round,
                    ),
                  ],
                ),
              MarkerLayer(
                markers: [
                  Marker(
                    point: LatLng(currentLat, currentLng),
                    width: 48,
                    height: 48,
                    child: const CircleAvatar(
                      backgroundColor: Color(0xFF7C3AED),
                      child: Icon(Icons.directions_car, color: Colors.white, size: 28),
                    ),
                  ),
                ],
              ),
            ],
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: CircleAvatar(
                backgroundColor: const Color(0xFF1A1035),
                child: IconButton(
                  icon: const Icon(Icons.arrow_back, color: Colors.white),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ),
            ),
          ),
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: const BoxDecoration(
                color: Color(0xFF0F0A1E),
                borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      const CircleAvatar(
                        radius: 24,
                        backgroundColor: Colors.grey,
                        child: Icon(Icons.person, color: Colors.white),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              route?.conductorNombreCompleto ?? 'Conductor',
                              style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            const Text('Toyota Corolla • 1234ABC', style: TextStyle(color: Colors.white54)),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1A1035),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Column(
                          children: [
                            Text('ETA', style: TextStyle(color: Colors.white54, fontSize: 10)),
                            Text('12 min', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: Colors.red),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          onPressed: () {
                            // Cancelar viaje
                            Navigator.of(context).pop();
                          },
                          child: const Text('Cancelar', style: TextStyle(color: Colors.red)),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF7C3AED),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          onPressed: _showRatingDialog,
                          child: const Text('Llegué / Finalizar', style: TextStyle(color: Colors.white)),
                        ),
                      ),
                    ],
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
