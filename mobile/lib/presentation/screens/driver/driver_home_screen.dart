import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:apuradito_mobile/presentation/providers/driver_provider.dart';

class DriverHomeScreen extends StatefulWidget {
  const DriverHomeScreen({super.key});

  @override
  State<DriverHomeScreen> createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DriverProvider>().loadMyRoutes();
    });
  }

  Future<void> _finishRoute(DriverProvider provider) async {
    await provider.finishRoute();
    if (!mounted || provider.errorMessage == null) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(provider.errorMessage!)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final driverProvider = context.watch<DriverProvider>();
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.currentUser;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        leading: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Image.asset('assets/icons/logo.png'),
        ),
        title: const Text('Conductor'),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Chip(
              backgroundColor: driverProvider.isOnline
                  ? AppTheme.success.withOpacity(0.2)
                  : AppTheme.bgSurfaceHigh,
              label: Text(
                driverProvider.activeRoute == null
                    ? 'Sin ruta activa'
                    : driverProvider.activeRoute!.estado == 'en_curso'
                        ? 'En recorrido'
                        : 'Programada',
                style: TextStyle(
                  color: driverProvider.isOnline
                      ? AppTheme.success
                      : AppTheme.textSecondary,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          )
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(AppTheme.radiusLg),
              boxShadow: AppTheme.primaryShadow,
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Hola, ${user?.nombreCompleto ?? "Conductor"}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Row(
                          children: [
                            Icon(Icons.star, color: AppTheme.warning, size: 16),
                            SizedBox(width: 4),
                            Text(
                              '4.8',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const Icon(Icons.verified_user,
                        color: Colors.white70, size: 32),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Ruta Activa o Nueva Ruta
          if (driverProvider.activeRoute != null)
            Card(
              elevation: 4,
              shadowColor: AppTheme.primary.withOpacity(0.3),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppTheme.radiusLg),
                side: const BorderSide(color: AppTheme.primary, width: 2),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.directions_car, color: AppTheme.primary),
                        SizedBox(width: 8),
                        Text(
                          'Ruta Activa',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryLight,
                          ),
                        ),
                      ],
                    ),
                    const Divider(color: AppTheme.divider, height: 24),
                    Row(
                      children: [
                        const Icon(Icons.my_location,
                            color: AppTheme.success, size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                            child: Text(
                                driverProvider.activeRoute!.origenDireccion,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis)),
                      ],
                    ),
                    const Padding(
                      padding: EdgeInsets.only(left: 8.0, top: 4, bottom: 4),
                      child: Icon(Icons.arrow_downward,
                          color: AppTheme.textMuted, size: 16),
                    ),
                    Row(
                      children: [
                        const Icon(Icons.place,
                            color: AppTheme.error, size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                            child: Text(
                                driverProvider.activeRoute!.destinoDireccion,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis)),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (driverProvider.activeRoute!.estado == 'programada')
                      ElevatedButton.icon(
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('Iniciar recorrido'),
                        onPressed: driverProvider.isLoading
                            ? null
                            : driverProvider.startRoute,
                      )
                    else
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              icon: const Icon(Icons.list_alt),
                              label: const Text('Pasajeros'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppTheme.bgSurfaceHigh,
                                foregroundColor: AppTheme.textPrimary,
                              ),
                              onPressed: () => context.push('/driver/requests'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton.icon(
                              icon: const Icon(Icons.check_circle),
                              label: const Text('Finalizar'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppTheme.error,
                              ),
                              onPressed: driverProvider.isLoading
                                  ? null
                                  : () => _finishRoute(driverProvider),
                            ),
                          ),
                        ],
                      )
                  ],
                ),
              ),
            )
          else
            InkWell(
              onTap: () => context.push('/driver/publish'),
              borderRadius: BorderRadius.circular(AppTheme.radiusLg),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 24),
                decoration: BoxDecoration(
                  gradient: AppTheme.cardGradient,
                  borderRadius: BorderRadius.circular(AppTheme.radiusLg),
                  border: Border.all(color: AppTheme.border, width: 1.5),
                  boxShadow: AppTheme.cardShadow,
                ),
                child: const Column(
                  children: [
                    Icon(Icons.add_circle,
                        size: 48, color: AppTheme.primaryLight),
                    SizedBox(height: 12),
                    Text(
                      'Publicar Nueva Ruta',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            ),

          const SizedBox(height: 24),
          const Text(
            'Mis últimas rutas',
            style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppTheme.textPrimary),
          ),
          const SizedBox(height: 12),
          if (driverProvider.myRoutes
              .where((route) => route.id != driverProvider.activeRoute?.id)
              .isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(20.0),
                child: Text('No hay rutas recientes.',
                    style: TextStyle(color: AppTheme.textMuted)),
              ),
            )
          else
            ...driverProvider.myRoutes
                .where((route) => route.id != driverProvider.activeRoute?.id)
                .take(5)
                .map(
                  (route) => Card(
                    child: ListTile(
                      leading: const Icon(Icons.route),
                      title: Text(
                          '${route.origenDireccion} → ${route.destinoDireccion}'),
                      subtitle: Text(route.horaSalida.replaceFirst('T', ' ')),
                      trailing: Text(route.estado),
                    ),
                  ),
                )
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          if (index == 1) {
            context.push('/driver/publish');
            return;
          }
          if (index == 2) {
            context.push('/shared/wallet');
            return;
          }
          if (index == 3) {
            context.push('/shared/profile');
            return;
          }
          setState(() => _currentIndex = index);
        },
        items: const [
          BottomNavigationBarItem(
              icon: Icon(Icons.directions_car), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Rutas'),
          BottomNavigationBarItem(
              icon: Icon(Icons.account_balance_wallet), label: 'Wallet'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Perfil'),
        ],
      ),
    );
  }
}
