import 'package:apuradito_mobile/core/network/connectivity_service.dart';
import 'package:apuradito_mobile/core/storage/offline_action_queue.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/data/repositories/routes_repository.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

class PassengerTripsScreen extends StatefulWidget {
  const PassengerTripsScreen({super.key});

  @override
  State<PassengerTripsScreen> createState() => _PassengerTripsScreenState();
}

class _PassengerTripsScreenState extends State<PassengerTripsScreen> {
  final RoutesRepository _repository = RoutesRepository();
  final OfflineActionQueue _queue = OfflineActionQueue();
  List<RideRequestModel> _rides = <RideRequestModel>[];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    final String? userId = context.read<AuthProvider>().currentUser?.id;
    if (userId == null) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      _rides = await _repository.getMyRides(userId);
    } catch (_) {
      _errorMessage = 'No hay viajes guardados todavía.';
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _cancelRide(RideRequestModel ride) async {
    if (!context.read<ConnectivityService>().isOnline) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cancelar un viaje requiere conexión.')),
      );
      return;
    }
    final bool? confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext dialogContext) => AlertDialog(
        title: const Text('¿Cancelar solicitud?'),
        content: const Text(
          'Si ya fue aceptada puede aplicarse una penalización según las políticas de Apuradito.',
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Volver'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('Cancelar solicitud'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    try {
      await _repository.cancelRide(ride.id);
      await _load();
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No se pudo cancelar el viaje.')),
        );
      }
    }
  }

  Future<void> _rateRide(RideRequestModel ride) async {
    if (ride.conductorId == null) return;
    int stars = 5;
    final bool? submit = await showDialog<bool>(
      context: context,
      builder: (BuildContext dialogContext) => StatefulBuilder(
        builder: (BuildContext context, StateSetter setDialogState) =>
            AlertDialog(
          title: const Text('Califica tu viaje'),
          content: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List<Widget>.generate(5, (int index) {
              final int value = index + 1;
              return IconButton(
                onPressed: () => setDialogState(() => stars = value),
                icon: Icon(value <= stars ? Icons.star : Icons.star_border,
                    color: Colors.amber),
              );
            }),
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Ahora no'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, true),
              child: const Text('Enviar'),
            ),
          ],
        ),
      ),
    );
    if (submit != true || !mounted) return;
    final String? userId = context.read<AuthProvider>().currentUser?.id;
    try {
      if (context.read<ConnectivityService>().isOnline) {
        await _repository.rateRide(
          solicitudId: ride.id,
          calificadoId: ride.conductorId!,
          estrellas: stars,
        );
      } else if (userId != null) {
        await _queue.enqueue(
          userId: userId,
          type: PendingActionType.rateRide,
          payload: <String, dynamic>{
            'solicitud_id': ride.id,
            'calificado_id': ride.conductorId,
            'estrellas': stars,
          },
        );
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(context.read<ConnectivityService>().isOnline
                ? 'Calificación enviada. ¡Gracias!'
                : 'Calificación guardada para sincronizar.'),
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('No se pudo registrar la calificación.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Mis viajes')),
        body: RefreshIndicator(
          onRefresh: _load,
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _rides.isEmpty
                  ? ListView(
                      children: <Widget>[
                        const SizedBox(height: 120),
                        const Icon(Icons.directions_car_outlined, size: 54),
                        const SizedBox(height: 12),
                        Center(
                          child: Text(_errorMessage ?? 'Aún no tienes viajes.'),
                        ),
                        TextButton(
                          onPressed: () => context.go('/passenger'),
                          child: const Text('Buscar rutas'),
                        ),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _rides.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (BuildContext context, int index) {
                        final RideRequestModel ride = _rides[index];
                        final bool canCancel = ride.estado == 'pendiente' ||
                            ride.estado == 'aceptada';
                        return Card(
                          child: Padding(
                            padding: const EdgeInsets.all(14),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Row(
                                  children: <Widget>[
                                    const Icon(Icons.directions_car),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                          ride.conductorNombre ?? 'Conductor',
                                          style: Theme.of(context)
                                              .textTheme
                                              .titleMedium),
                                    ),
                                    _StatusChip(status: ride.estado),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                Text(
                                  '${ride.origenDireccion ?? 'Origen'} → ${ride.destinoDireccion ?? 'Destino'}',
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '${ride.costoCalculadoBs.toStringAsFixed(2)} Bs · ${ride.metodoPago}',
                                  style: const TextStyle(color: Colors.white70),
                                ),
                                if (canCancel ||
                                    ride.estado == 'completada') ...<Widget>[
                                  const SizedBox(height: 8),
                                  Row(
                                    children: <Widget>[
                                      if (canCancel)
                                        TextButton(
                                          onPressed: () => _cancelRide(ride),
                                          child: const Text('Cancelar'),
                                        ),
                                      if (ride.estado == 'completada' &&
                                          ride.conductorId != null)
                                        TextButton.icon(
                                          onPressed: () => _rateRide(ride),
                                          icon: const Icon(Icons.star_outline),
                                          label: const Text('Calificar'),
                                        ),
                                    ],
                                  ),
                                ],
                              ],
                            ),
                          ),
                        );
                      },
                    ),
        ),
      );
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final Color color = switch (status) {
      'aceptada' => Colors.green,
      'completada' => Colors.blue,
      'rechazada' || 'cancelada' => Colors.red,
      _ => Colors.orange,
    };
    return Chip(
      label: Text(status),
      side: BorderSide(color: color),
      labelStyle: TextStyle(color: color),
    );
  }
}
