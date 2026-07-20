import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/core/network/websocket_service.dart';
import 'package:apuradito_mobile/presentation/providers/map_provider.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';

class PassengerHomeScreen extends StatefulWidget {
  const PassengerHomeScreen({super.key});

  @override
  State<PassengerHomeScreen> createState() => _PassengerHomeScreenState();
}

class _PassengerHomeScreenState extends State<PassengerHomeScreen> {
  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initWebSocket();
    });
  }

  void _initWebSocket() {
    final wsService = context.read<WebSocketService>();
    final mapProvider = context.read<MapProvider>();

    if (!wsService.isConnected) {
      wsService.connect();
    }
    
    wsService.addListener2(mapProvider.handleWsMessage);
  }

  @override
  void dispose() {
    final wsService = context.read<WebSocketService>();
    final mapProvider = context.read<MapProvider>();
    wsService.removeListener2(mapProvider.handleWsMessage);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final mapProvider = context.watch<MapProvider>();
    final wsService = context.watch<WebSocketService>();
    final authProvider = context.watch<AuthProvider>();
    
    final selectedRoute = mapProvider.selectedRoute;
    final userCoins = authProvider.currentUser?.saldoCoins ?? 0;

    return Scaffold(
      body: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: LatLng(AppConstants.sczLat, AppConstants.sczLng),
              initialZoom: 13.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              ),
              PolylineLayer(
                polylines: mapProvider.activeRoutes.where((r) => r.hasRoute == true).map((route) {
                  final isSelected = selectedRoute?.id == route.id;
                  // convert double[2] to LatLng
                  final points = route.routePolyline ?? [];
                  return Polyline(
                    points: points,
                    color: isSelected ? const Color(0xFF9F67FF) : const Color(0xFF7C3AED),
                    strokeWidth: isSelected ? 7.0 : 5.0,
                    strokeJoin: StrokeJoin.round,
                  );
                }).toList(),
              ),
              MarkerLayer(
                markers: mapProvider.activeRoutes.where((r) => r.hasPosition == true).map((route) {
                  return Marker(
                    point: LatLng(route.lat!, route.lng!),
                    width: 36,
                    height: 36,
                    child: GestureDetector(
                      onTap: () {
                        mapProvider.selectRoute(route);
                      },
                      child: const CircleAvatar(
                        backgroundColor: Color(0xFF7C3AED),
                        child: Icon(Icons.directions_car, color: Colors.white, size: 20),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
          
          SafeArea(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Image.asset('assets/icons/logo.png', width: 30, height: 30, errorBuilder: (_,__,___) => const Icon(Icons.local_taxi, color: Color(0xFF7C3AED), size: 30)),
                          const SizedBox(width: 8),
                          const Text('Apuradito', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: Color(0xFF1A0B3B))),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1A1035),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '💰 $userCoins Cs',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          Positioned(
            top: MediaQuery.of(context).padding.top + 70,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.9),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: wsService.isConnected ? Colors.green : Colors.red,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    wsService.isConnected ? 'En vivo' : 'Sin conexión',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.black87),
                  ),
                ],
              ),
            ),
          ),

          DraggableScrollableSheet(
            initialChildSize: 0.35,
            minChildSize: 0.15,
            maxChildSize: 0.6,
            builder: (context, scrollController) {
              return Container(
                decoration: const BoxDecoration(
                  color: Color(0xFF0F0A1E),
                  borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                  boxShadow: [
                    BoxShadow(color: Colors.black26, blurRadius: 10, spreadRadius: 0),
                  ],
                ),
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.all(16),
                  children: [
                    Center(
                      child: Container(
                        width: 40,
                        height: 5,
                        decoration: BoxDecoration(
                          color: Colors.grey[700],
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      '¿A dónde vas hoy?',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 16),
                    GestureDetector(
                      onTap: () {
                        // Navigate to search screen
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1A1035),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.search, color: Colors.white54),
                            SizedBox(width: 12),
                            Text('Buscar destino...', style: TextStyle(color: Colors.white54)),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Row(
                      children: [
                        const Text(
                          'Vehículos disponibles cerca',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF7C3AED),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            '${mapProvider.activeRoutes.length}',
                            style: const TextStyle(color: Colors.white, fontSize: 12),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      height: 180,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: mapProvider.activeRoutes.length,
                        itemBuilder: (context, index) {
                          final route = mapProvider.activeRoutes[index];
                          return Container(
                            width: 280,
                            margin: const EdgeInsets.only(right: 16),
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1A1035),
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: selectedRoute?.id == route.id ? const Color(0xFF7C3AED) : Colors.transparent, width: 2),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    const CircleAvatar(
                                      radius: 20,
                                      backgroundColor: Colors.grey,
                                      child: Icon(Icons.person, color: Colors.white),
                                    ),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(route.conductorNombreCompleto ?? 'Conductor', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                          Text('Asientos: ${route.asientosDisponibles}', style: const TextStyle(color: Colors.white54, fontSize: 12)),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                Text('${route.origenDireccion} → ${route.destinoDireccion}', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white70, fontSize: 13)),
                                const Spacer(),
                                SizedBox(
                                  width: double.infinity,
                                  height: 36,
                                  child: ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: const Color(0xFF7C3AED),
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                    ),
                                    onPressed: () {
                                      mapProvider.selectRoute(route);
                                    },
                                    child: const Text('Ver Ruta', style: TextStyle(color: Colors.white)),
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: const Color(0xFF0F0A1E),
        selectedItemColor: const Color(0xFF7C3AED),
        unselectedItemColor: Colors.white54,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.receipt), label: 'Mis Viajes'),
          BottomNavigationBarItem(icon: Icon(Icons.account_balance_wallet), label: 'Wallet'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Perfil'),
        ],
      ),
    );
  }
}
