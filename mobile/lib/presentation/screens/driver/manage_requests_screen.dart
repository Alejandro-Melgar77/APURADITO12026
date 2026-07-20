import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/presentation/providers/driver_provider.dart';

class ManageRequestsScreen extends StatefulWidget {
  const ManageRequestsScreen({super.key});

  @override
  State<ManageRequestsScreen> createState() => _ManageRequestsScreenState();
}

class _ManageRequestsScreenState extends State<ManageRequestsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DriverProvider>().loadPendingRequests();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('Solicitudes Pendientes'),
      ),
      body: Consumer<DriverProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator(color: AppTheme.primary));
          }

          if (provider.pendingRequests.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.inbox, size: 64, color: AppTheme.textMuted),
                  SizedBox(height: 16),
                  Text(
                    'Sin solicitudes pendientes',
                    style: TextStyle(color: AppTheme.textSecondary, fontSize: 16),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: provider.loadPendingRequests,
            color: AppTheme.primary,
            child: ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: provider.pendingRequests.length,
              itemBuilder: (context, index) {
                final req = provider.pendingRequests[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 28,
                          backgroundColor: AppTheme.primary.withOpacity(0.2),
                          child: Text(
                            req.pasajeroNombre?.substring(0, 1).toUpperCase() ?? 'P',
                            style: const TextStyle(
                              color: AppTheme.primaryLight,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                req.pasajeroNombre ?? 'Pasajero',
                                style: const TextStyle(
                                  color: AppTheme.textPrimary,
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${req.costoCalculadoBs.toStringAsFixed(2)} Bs • ${req.metodoPago}',
                                style: const TextStyle(color: AppTheme.textSecondary),
                              ),
                            ],
                          ),
                        ),
                        Column(
                          children: [
                            IconButton(
                              icon: const Icon(Icons.check_circle, color: AppTheme.success, size: 32),
                              onPressed: () => provider.acceptRequest(req.id),
                            ),
                            IconButton(
                              icon: const Icon(Icons.cancel, color: AppTheme.error, size: 32),
                              onPressed: () => provider.rejectRequest(req.id),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
