import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/core/network/connectivity_service.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/data/repositories/routes_repository.dart';
import 'package:apuradito_mobile/presentation/providers/map_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';

class RequestRideScreen extends StatefulWidget {
  const RequestRideScreen({super.key, required this.routeId});

  final String routeId;

  @override
  State<RequestRideScreen> createState() => _RequestRideScreenState();
}

class _RequestRideScreenState extends State<RequestRideScreen> {
  final RoutesRepository _repository = RoutesRepository();
  LatLng? _boarding;
  LatLng? _dropoff;
  String _paymentMethod = 'coins';
  bool _isSubmitting = false;

  ActiveRouteModel? get _route {
    final List<ActiveRouteModel> routes =
        context.read<MapProvider>().activeRoutes;
    return routes.cast<ActiveRouteModel?>().firstWhere(
          (ActiveRouteModel? route) => route?.id == widget.routeId,
          orElse: () => null,
        );
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ActiveRouteModel? route = _route;
      if (route == null) return;
      setState(() {
        _boarding = route.origenLat != null && route.origenLng != null
            ? LatLng(route.origenLat!, route.origenLng!)
            : route.currentPosition;
        _dropoff = route.destinoLat != null && route.destinoLng != null
            ? LatLng(route.destinoLat!, route.destinoLng!)
            : route.routePolyline.isNotEmpty
                ? route.routePolyline.last
                : null;
      });
    });
  }

  void _handleTap(TapPosition _, LatLng point) {
    setState(() {
      if (_boarding == null || (_boarding != null && _dropoff != null)) {
        _boarding = point;
        _dropoff = null;
      } else {
        _dropoff = point;
      }
    });
  }

  Future<void> _submit() async {
    final ActiveRouteModel? route = _route;
    if (route == null || _boarding == null || _dropoff == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Marca tu abordaje y tu descenso en el mapa.')),
      );
      return;
    }
    if (!context.read<ConnectivityService>().isOnline) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Solicitar un asiento requiere conexión.')),
      );
      return;
    }
    setState(() => _isSubmitting = true);
    try {
      final double distanceKm = Distance().as(
        LengthUnit.Kilometer,
        _boarding!,
        _dropoff!,
      );
      await _repository.requestRide(
        rutaId: route.id,
        origenLat: _boarding!.latitude,
        origenLng: _boarding!.longitude,
        destinoLat: _dropoff!.latitude,
        destinoLng: _dropoff!.longitude,
        distanciaViajeKm: distanceKm < 0.1 ? 0.1 : distanceKm,
        metodoPago: _paymentMethod,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Solicitud enviada al conductor.')),
      );
      context.go('/passenger/trips');
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
              'No se pudo enviar la solicitud. Revisa los datos e intenta nuevamente.'),
        ),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final ActiveRouteModel? route = _route;
    if (route == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Solicitar viaje')),
        body: const Center(child: Text('La ruta ya no está disponible.')),
      );
    }
    final LatLng initialCenter = route.currentPosition ??
        const LatLng(AppConstants.sczLat, AppConstants.sczLng);
    return Scaffold(
      appBar: AppBar(title: const Text('Solicitar un asiento')),
      body: Column(
        children: <Widget>[
          Expanded(
            child: FlutterMap(
              options: MapOptions(
                initialCenter: initialCenter,
                initialZoom: AppConstants.mapZoomClose,
                onTap: _handleTap,
              ),
              children: <Widget>[
                TileLayer(
                  urlTemplate: AppConstants.osmTileUrl,
                  userAgentPackageName: 'com.apuradito.apuradito_mobile',
                ),
                if (route.hasRoute)
                  PolylineLayer(
                    polylines: <Polyline>[
                      Polyline(
                        points: route.routePolyline,
                        color: const Color(0xFF7C3AED),
                        strokeWidth: 5,
                      ),
                    ],
                  ),
                MarkerLayer(
                  markers: <Marker>[
                    if (_boarding != null)
                      Marker(
                        point: _boarding!,
                        width: 52,
                        height: 52,
                        child: const Icon(Icons.my_location,
                            color: Colors.green, size: 38),
                      ),
                    if (_dropoff != null)
                      Marker(
                        point: _dropoff!,
                        width: 52,
                        height: 52,
                        child: const Icon(Icons.place,
                            color: Colors.red, size: 42),
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
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  Text('${route.origenDireccion} → ${route.destinoDireccion}',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 6),
                  const Text(
                    'Toca el mapa: primero tu punto de abordaje y luego tu descenso.',
                    style: TextStyle(color: Colors.white70),
                  ),
                  const SizedBox(height: 12),
                  SegmentedButton<String>(
                    segments: const <ButtonSegment<String>>[
                      ButtonSegment<String>(
                          value: 'coins', label: Text('Coins')),
                      ButtonSegment<String>(
                          value: 'efectivo', label: Text('Efectivo')),
                    ],
                    selected: <String>{_paymentMethod},
                    onSelectionChanged: (Set<String> selection) =>
                        setState(() => _paymentMethod = selection.first),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: _isSubmitting ? null : _submit,
                    icon: const Icon(Icons.send),
                    label: Text(
                        _isSubmitting ? 'Enviando...' : 'Enviar solicitud'),
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
