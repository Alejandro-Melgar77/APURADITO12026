import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/core/network/websocket_service.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:apuradito_mobile/presentation/providers/map_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';

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
      if (!mounted) return;
      final WebSocketService webSocket = context.read<WebSocketService>();
      final MapProvider routes = context.read<MapProvider>();
      webSocket.addMessageListener(routes.handleWsMessage);
      webSocket.connect();
      routes.loadActiveRoutes();
    });
  }

  @override
  void dispose() {
    final WebSocketService webSocket = context.read<WebSocketService>();
    webSocket
        .removeMessageListener(context.read<MapProvider>().handleWsMessage);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final MapProvider routes = context.watch<MapProvider>();
    final WebSocketService webSocket = context.watch<WebSocketService>();
    final int balance =
        context.watch<AuthProvider>().currentUser?.saldoCoins.round() ?? 0;

    return Scaffold(
      body: Stack(
        children: <Widget>[
          FlutterMap(
            mapController: _mapController,
            options: const MapOptions(
              initialCenter: LatLng(AppConstants.sczLat, AppConstants.sczLng),
              initialZoom: AppConstants.mapZoomDefault,
            ),
            children: <Widget>[
              TileLayer(
                urlTemplate: AppConstants.osmTileUrl,
                userAgentPackageName: 'com.apuradito.apuradito_mobile',
              ),
              PolylineLayer(
                polylines: routes.activeRoutes
                    .where((ActiveRouteModel route) => route.hasRoute)
                    .map((ActiveRouteModel route) => Polyline(
                          points: route.routePolyline,
                          color: routes.selectedRoute?.id == route.id
                              ? const Color(0xFF9F67FF)
                              : const Color(0xFF7C3AED),
                          strokeWidth:
                              routes.selectedRoute?.id == route.id ? 7 : 5,
                        ))
                    .toList(),
              ),
              MarkerLayer(
                markers: routes.activeRoutes
                    .where((ActiveRouteModel route) => route.hasPosition)
                    .map((ActiveRouteModel route) => Marker(
                          point: route.currentPosition!,
                          width: 42,
                          height: 42,
                          child: InkWell(
                            onTap: () => routes.selectRoute(route),
                            child: const CircleAvatar(
                              backgroundColor: Color(0xFF7C3AED),
                              child: Icon(Icons.directions_car,
                                  color: Colors.white),
                            ),
                          ),
                        ))
                    .toList(),
              ),
            ],
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  const Text(
                    AppConstants.appName,
                    style: TextStyle(
                        color: Color(0xFF1A0B3B),
                        fontSize: 22,
                        fontWeight: FontWeight.bold),
                  ),
                  Row(
                    children: <Widget>[
                      _ConnectionChip(connected: webSocket.isConnected),
                      const SizedBox(width: 8),
                      Chip(
                        backgroundColor: const Color(0xFF1A1035),
                        label: Text('$balance Coins',
                            style: const TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          DraggableScrollableSheet(
            initialChildSize: 0.37,
            minChildSize: 0.2,
            maxChildSize: 0.7,
            builder:
                (BuildContext context, ScrollController scrollController) =>
                    Container(
              decoration: const BoxDecoration(
                color: Color(0xFF0F0A1E),
                borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
              ),
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.all(16),
                children: <Widget>[
                  Center(
                    child: Container(
                      width: 44,
                      height: 4,
                      decoration: BoxDecoration(
                          color: Colors.white24,
                          borderRadius: BorderRadius.circular(4)),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text('Vehículos disponibles cerca',
                      style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  const Text(
                      'Selecciona un vehículo para ver su recorrido en tiempo real.',
                      style: TextStyle(color: Colors.white60)),
                  const SizedBox(height: 16),
                  if (routes.isLoading)
                    const Center(
                        child: Padding(
                            padding: EdgeInsets.all(24),
                            child: CircularProgressIndicator()))
                  else if (routes.activeRoutes.isEmpty)
                    _EmptyRoutes(
                        onRetry: routes.loadActiveRoutes,
                        errorMessage: routes.errorMessage)
                  else
                    ...routes.activeRoutes.map(
                        (ActiveRouteModel route) => _RouteCard(route: route)),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        onTap: (int index) {
          switch (index) {
            case 1:
              context.push('/passenger/trips');
              break;
            case 2:
              context.push('/shared/wallet');
              break;
            case 3:
              context.push('/shared/profile');
              break;
            default:
              break;
          }
        },
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Inicio'),
          BottomNavigationBarItem(
              icon: Icon(Icons.receipt_long), label: 'Mis viajes'),
          BottomNavigationBarItem(
              icon: Icon(Icons.account_balance_wallet), label: 'Billetera'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Perfil'),
        ],
      ),
    );
  }
}

class _ConnectionChip extends StatelessWidget {
  const _ConnectionChip({required this.connected});
  final bool connected;

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: CircleAvatar(
          radius: 5, backgroundColor: connected ? Colors.green : Colors.orange),
      label: Text(connected ? 'En vivo' : 'Reconectando'),
    );
  }
}

class _EmptyRoutes extends StatelessWidget {
  const _EmptyRoutes({required this.onRetry, this.errorMessage});
  final VoidCallback onRetry;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: <Widget>[
            const Icon(Icons.no_transfer, color: Colors.white54, size: 42),
            const SizedBox(height: 8),
            Text(errorMessage ?? 'No hay vehículos disponibles por el momento.',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70)),
            TextButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Reintentar')),
          ],
        ),
      ),
    );
  }
}

class _RouteCard extends StatelessWidget {
  const _RouteCard({required this.route});
  final ActiveRouteModel route;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: const CircleAvatar(child: Icon(Icons.directions_car)),
        title: Text(route.conductorNombreCompleto),
        subtitle: Text('${route.origenDireccion} → ${route.destinoDireccion}',
            maxLines: 2, overflow: TextOverflow.ellipsis),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          context.read<MapProvider>().selectRoute(route);
          context.push('/passenger/tracking/${route.id}');
        },
      ),
    );
  }
}
