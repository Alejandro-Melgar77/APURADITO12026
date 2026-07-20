import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/presentation/providers/driver_provider.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

/// Vista de apoyo para una ruta en curso. El recorrido real se consulta en la
/// pantalla de pasajeros; aquí el conductor gestiona personas y cierre.
class ActiveRideScreen extends StatelessWidget {
  const ActiveRideScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final DriverProvider provider = context.watch<DriverProvider>();
    final route = provider.activeRoute;
    if (route == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Ruta activa')),
        body: Center(
          child: TextButton(
            onPressed: () => context.go('/driver'),
            child: const Text('No hay una ruta activa. Volver al inicio'),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Ruta en curso')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: <Widget>[
          const Icon(Icons.directions_car,
              size: 64, color: AppTheme.primaryLight),
          const SizedBox(height: 20),
          _RouteStop(
            icon: Icons.my_location,
            label: 'Origen',
            value: route.origenDireccion,
            color: AppTheme.success,
          ),
          const Padding(
            padding: EdgeInsets.only(left: 16),
            child: Icon(Icons.more_vert, color: AppTheme.textMuted),
          ),
          _RouteStop(
            icon: Icons.place,
            label: 'Destino',
            value: route.destinoDireccion,
            color: AppTheme.error,
          ),
          const SizedBox(height: 20),
          Text('Estado: ${route.estado}', textAlign: TextAlign.center),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => context.push('/driver/requests'),
            icon: const Icon(Icons.people_alt),
            label: const Text('Gestionar pasajeros'),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: provider.isLoading ? null : provider.finishRoute,
            icon: const Icon(Icons.flag),
            label: const Text('Finalizar ruta'),
          ),
        ],
      ),
    );
  }
}

class _RouteStop extends StatelessWidget {
  const _RouteStop({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  final IconData icon;
  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) => ListTile(
        leading: Icon(icon, color: color),
        title: Text(label),
        subtitle: Text(value),
      );
}
