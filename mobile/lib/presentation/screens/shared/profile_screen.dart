import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Nota: Estamos usando dynamic temporalmente si el authProvider real no ha sido actualizado en todo el entorno.
    // El prompt indica que authProvider tiene currentUser, switchRol, logout, activeRol.
    final authProvider = context.watch<AuthProvider>() as dynamic;
    final user = authProvider.currentUser;
    final bool isDriver = authProvider.activeRol == 'conductor';

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('Mi Perfil'),
        elevation: 0,
        backgroundColor: Colors.transparent,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // Avatar
            Center(
              child: Container(
                width: 100,
                height: 100,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: AppTheme.primaryGradient,
                  boxShadow: [
                    BoxShadow(color: Colors.black45, blurRadius: 10, offset: Offset(0, 4))
                  ],
                ),
                child: Center(
                  child: Text(
                    user?.name?.substring(0, 1).toUpperCase() ?? 'U',
                    style: const TextStyle(
                      fontSize: 40,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              user?.name ?? 'Usuario',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
            ),
            const SizedBox(height: 4),
            Text(
              user?.email ?? 'correo@ejemplo.com',
              style: const TextStyle(fontSize: 16, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: isDriver ? AppTheme.primary.withOpacity(0.2) : AppTheme.success.withOpacity(0.2),
                borderRadius: BorderRadius.circular(AppTheme.radiusFull),
                border: Border.all(color: isDriver ? AppTheme.primary : AppTheme.success),
              ),
              child: Text(
                isDriver ? 'Modo Conductor' : 'Modo Pasajero',
                style: TextStyle(
                  color: isDriver ? AppTheme.primaryLight : AppTheme.success,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 32),

            // Estadísticas (solo conductor)
            if (isDriver)
              Padding(
                padding: const EdgeInsets.only(bottom: 24.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildStatColumn('Viajes', '142'),
                    Container(width: 1, height: 40, color: AppTheme.divider),
                    _buildStatColumn('Km', '850'),
                    Container(width: 1, height: 40, color: AppTheme.divider),
                    _buildStatColumn('Calificación', '⭐ 4.8'),
                  ],
                ),
              ),

            // Opciones
            Card(
              margin: const EdgeInsets.only(bottom: 16),
              child: ListTile(
                leading: const Icon(Icons.verified_user, color: AppTheme.success),
                title: const Text('Verificación de Identidad', style: TextStyle(color: AppTheme.textPrimary)),
                subtitle: const Text('Perfil verificado', style: TextStyle(color: AppTheme.textSecondary)),
                trailing: const Icon(Icons.chevron_right, color: AppTheme.textMuted),
                onTap: () {},
              ),
            ),

            Card(
              margin: const EdgeInsets.only(bottom: 16),
              child: ListTile(
                leading: const Icon(Icons.swap_horiz, color: AppTheme.primaryLight),
                title: Text(
                  isDriver ? 'Cambiar a Pasajero' : 'Cambiar a Conductor',
                  style: const TextStyle(color: AppTheme.textPrimary),
                ),
                trailing: const Icon(Icons.chevron_right, color: AppTheme.textMuted),
                onTap: () {
                  authProvider.switchRol();
                },
              ),
            ),

            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.logout),
              label: const Text('Cerrar Sesión'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.error.withOpacity(0.1),
                foregroundColor: AppTheme.error,
                elevation: 0,
                side: const BorderSide(color: AppTheme.error),
              ),
              onPressed: () {
                authProvider.logout();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatColumn(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 14, color: AppTheme.textSecondary),
        ),
      ],
    );
  }
}
