import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/presentation/providers/driver_provider.dart';

class PublishRouteScreen extends StatefulWidget {
  const PublishRouteScreen({super.key});

  @override
  State<PublishRouteScreen> createState() => _PublishRouteScreenState();
}

class _PublishRouteScreenState extends State<PublishRouteScreen> {
  LatLng? _origen;
  LatLng? _destino;
  
  final _origenCtrl = TextEditingController();
  final _destinoCtrl = TextEditingController();
  final _costoCtrl = TextEditingController(text: '10.0');
  
  int _asientos = 4;
  DateTime _horaSalida = DateTime.now().add(const Duration(minutes: 15));

  void _handleMapTap(TapPosition tapPosition, LatLng point) {
    setState(() {
      if (_origen == null) {
        _origen = point;
      } else if (_destino == null) {
        _destino = point;
      } else {
        _origen = point;
        _destino = null;
      }
    });
  }

  Future<void> _selectTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(_horaSalida),
    );
    if (picked != null) {
      setState(() {
        _horaSalida = DateTime(
          _horaSalida.year,
          _horaSalida.month,
          _horaSalida.day,
          picked.hour,
          picked.minute,
        );
      });
    }
  }

  void _publish() async {
    if (_origen == null || _destino == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecciona origen y destino en el mapa')),
      );
      return;
    }

    if (_origenCtrl.text.isEmpty || _destinoCtrl.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ingresa las descripciones de las direcciones')),
      );
      return;
    }

    final driverProvider = context.read<DriverProvider>();
    await driverProvider.publishRoute(
      origenLat: _origen!.latitude,
      origenLng: _origen!.longitude,
      destinoLat: _destino!.latitude,
      destinoLng: _destino!.longitude,
      origenDireccion: _origenCtrl.text,
      destinoDireccion: _destinoCtrl.text,
      asientos: _asientos,
      costo: double.tryParse(_costoCtrl.text) ?? 10.0,
      horaSalida: _horaSalida,
    );

    if (driverProvider.errorMessage == null && mounted) {
      Navigator.pop(context);
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(driverProvider.errorMessage ?? 'Error desconocido')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('Nueva Ruta'),
      ),
      body: Column(
        children: [
          SizedBox(
            height: 300,
            child: FlutterMap(
              options: MapOptions(
                initialCenter: const LatLng(AppConstants.sczLat, AppConstants.sczLng),
                initialZoom: 13,
                onTap: _handleMapTap,
              ),
              children: [
                TileLayer(
                  urlTemplate: AppConstants.osmTileUrl,
                  userAgentPackageName: 'com.apuradito.mobile',
                ),
                if (_origen != null && _destino != null)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: [_origen!, _destino!],
                        color: AppTheme.primary,
                        strokeWidth: 4.0,
                      )
                    ],
                  ),
                MarkerLayer(
                  markers: [
                    if (_origen != null)
                      Marker(
                        point: _origen!,
                        width: 80,
                        height: 80,
                        child: const Column(
                          children: [
                            Icon(Icons.location_on, color: AppTheme.success, size: 40),
                            Text('Origen', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, backgroundColor: Colors.white70)),
                          ],
                        ),
                      ),
                    if (_destino != null)
                      Marker(
                        point: _destino!,
                        width: 80,
                        height: 80,
                        child: const Column(
                          children: [
                            Icon(Icons.location_on, color: AppTheme.error, size: 40),
                            Text('Destino', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, backgroundColor: Colors.white70)),
                          ],
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: Container(
              decoration: const BoxDecoration(
                color: AppTheme.bgSurface,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(AppTheme.radiusXl),
                  topRight: Radius.circular(AppTheme.radiusXl),
                ),
              ),
              child: ListView(
                padding: const EdgeInsets.all(24.0),
                children: [
                  TextFormField(
                    controller: _origenCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Descripción del Origen',
                      prefixIcon: Icon(Icons.my_location, color: AppTheme.success),
                    ),
                    style: const TextStyle(color: AppTheme.textPrimary),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _destinoCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Descripción del Destino',
                      prefixIcon: Icon(Icons.place, color: AppTheme.error),
                    ),
                    style: const TextStyle(color: AppTheme.textPrimary),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Asientos', style: TextStyle(color: AppTheme.textSecondary)),
                            Slider(
                              value: _asientos.toDouble(),
                              min: 1,
                              max: 4,
                              divisions: 3,
                              label: _asientos.toString(),
                              activeColor: AppTheme.primaryLight,
                              onChanged: (val) => setState(() => _asientos = val.toInt()),
                            ),
                          ],
                        ),
                      ),
                      Expanded(
                        child: TextFormField(
                          controller: _costoCtrl,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'Precio (Bs)',
                            prefixIcon: Icon(Icons.attach_money, color: AppTheme.warning),
                          ),
                          style: const TextStyle(color: AppTheme.textPrimary),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  OutlinedButton.icon(
                    icon: const Icon(Icons.access_time),
                    label: Text('Salida: ${_horaSalida.hour}:${_horaSalida.minute.toString().padLeft(2, '0')}'),
                    onPressed: _selectTime,
                  ),
                  const SizedBox(height: 32),
                  Consumer<DriverProvider>(
                    builder: (context, provider, child) {
                      return ElevatedButton(
                        onPressed: provider.isLoading ? null : _publish,
                        child: provider.isLoading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : const Text('Publicar Ruta'),
                      );
                    },
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
