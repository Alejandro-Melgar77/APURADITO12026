import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final AuthProvider auth = context.watch<AuthProvider>();
    final user = auth.currentUser;
    if (user == null) return const SizedBox.shrink();

    return Scaffold(
      appBar: AppBar(title: const Text('Mi perfil')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: <Widget>[
          CircleAvatar(
            radius: 48,
            backgroundColor: AppTheme.primary,
            child: Text(
              user.nombre.isEmpty ? 'U' : user.nombre[0].toUpperCase(),
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 36,
                  fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 16),
          Text(user.nombreCompleto,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 4),
          Text(user.email,
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppTheme.textSecondary)),
          const SizedBox(height: 24),
          Card(
            child: ListTile(
              leading: Icon(
                  user.esConductor ? Icons.directions_car : Icons.person,
                  color: AppTheme.primaryLight),
              title: Text(user.esConductor ? 'Conductor' : 'Pasajero'),
              subtitle: Text(user.verificadoFacial
                  ? 'Identidad verificada'
                  : 'Identidad pendiente de verificación'),
            ),
          ),
          if (user.telefono?.isNotEmpty ?? false)
            Card(
                child: ListTile(
                    leading: const Icon(Icons.phone),
                    title: Text(user.telefono!))),
          const SizedBox(height: 20),
          OutlinedButton.icon(
            onPressed: () async {
              await context.read<AuthProvider>().logout();
              if (context.mounted) context.go('/login');
            },
            icon: const Icon(Icons.logout),
            label: const Text('Cerrar sesión'),
            style: OutlinedButton.styleFrom(
                foregroundColor: AppTheme.error,
                side: const BorderSide(color: AppTheme.error)),
          ),
        ],
      ),
    );
  }
}
