import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/presentation/providers/wallet_provider.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<WalletProvider>().loadWallet();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _showRechargeBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.bgSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(AppTheme.radiusXl)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Recargar Coins',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
              ),
              const SizedBox(height: 24),
              Wrap(
                spacing: 16,
                runSpacing: 16,
                alignment: WrapAlignment.center,
                children: [20, 50, 100, 200].map((amount) {
                  return ActionChip(
                    backgroundColor: AppTheme.primary.withOpacity(0.1),
                    side: const BorderSide(color: AppTheme.primary),
                    labelPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    label: Text(
                      '$amount Bs',
                      style: const TextStyle(color: AppTheme.primaryLight, fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {
                      Navigator.pop(context);
                      _showQR(context, amount);
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),
            ],
          ),
        );
      },
    );
  }

  void _showQR(BuildContext context, int amount) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: AppTheme.bgSurface,
          title: Text('Pago de $amount Bs', style: const TextStyle(color: AppTheme.textPrimary)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 200,
                height: 200,
                color: Colors.white,
                child: const Center(
                  child: Icon(Icons.qr_code_2, size: 180, color: Colors.black),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Escanea este código QR para completar la recarga de Coins.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppTheme.textSecondary),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cerrar', style: TextStyle(color: AppTheme.primaryLight)),
            )
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('Billetera Virtual'),
        elevation: 0,
      ),
      body: Consumer<WalletProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.balance == 0) {
            return const Center(child: CircularProgressIndicator(color: AppTheme.primary));
          }

          return Column(
            children: [
              // Tarjeta de Balance
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24.0),
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(AppTheme.radiusXl),
                    boxShadow: AppTheme.primaryShadow,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Saldo Disponible',
                            style: TextStyle(color: Colors.white70, fontSize: 16),
                          ),
                          Icon(Icons.account_balance_wallet, color: Colors.white, size: 28),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        '💰 ${provider.balance.toStringAsFixed(2)} Coins',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 36,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: AppTheme.primaryDark,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(AppTheme.radiusFull),
                          ),
                        ),
                        onPressed: () => _showRechargeBottomSheet(context),
                        child: const Text('Recargar Coins'),
                      ),
                    ],
                  ),
                ),
              ),
              TabBar(
                controller: _tabController,
                indicatorColor: AppTheme.primary,
                labelColor: AppTheme.primaryLight,
                unselectedLabelColor: AppTheme.textMuted,
                tabs: const [
                  Tab(text: 'Pagos'),
                  Tab(text: 'Recargas'),
                ],
              ),
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    // Lista de Pagos
                    provider.payments.isEmpty
                        ? const Center(child: Text('No hay pagos recientes', style: TextStyle(color: AppTheme.textSecondary)))
                        : ListView.separated(
                            padding: const EdgeInsets.all(16),
                            itemCount: provider.payments.length,
                            separatorBuilder: (_, __) => const Divider(color: AppTheme.divider),
                            itemBuilder: (context, index) {
                              final pago = provider.payments[index];
                              return ListTile(
                                leading: const CircleAvatar(
                                  backgroundColor: AppTheme.bgSurfaceHigh,
                                  child: Icon(Icons.payment, color: AppTheme.textMuted),
                                ),
                                title: Text(pago.metodo, style: const TextStyle(color: AppTheme.textPrimary)),
                                subtitle: Text(pago.creadoEn.split('T').first, style: const TextStyle(color: AppTheme.textSecondary)),
                                trailing: Text(
                                  '-${pago.montoBs.toStringAsFixed(2)}',
                                  style: const TextStyle(color: AppTheme.error, fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                              );
                            },
                          ),
                    // Lista de Recargas
                    provider.recharges.isEmpty
                        ? const Center(child: Text('No hay recargas recientes', style: TextStyle(color: AppTheme.textSecondary)))
                        : ListView.separated(
                            padding: const EdgeInsets.all(16),
                            itemCount: provider.recharges.length,
                            separatorBuilder: (_, __) => const Divider(color: AppTheme.divider),
                            itemBuilder: (context, index) {
                              final recarga = provider.recharges[index];
                              final monto = recarga['monto_bs'] ?? 0;
                              final fecha = recarga['creado_en'] ?? '';
                              return ListTile(
                                leading: const CircleAvatar(
                                  backgroundColor: AppTheme.bgSurfaceHigh,
                                  child: Icon(Icons.download, color: AppTheme.success),
                                ),
                                title: const Text('Recarga QR', style: TextStyle(color: AppTheme.textPrimary)),
                                subtitle: Text(fecha.toString().split('T').first, style: const TextStyle(color: AppTheme.textSecondary)),
                                trailing: Text(
                                  '+${monto.toString()}',
                                  style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                              );
                            },
                          ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
