import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/core/storage/offline_store.dart';
import 'package:dio/dio.dart';

class WalletSnapshot {
  const WalletSnapshot({required this.balance, required this.history});

  final double balance;
  final List<Map<String, dynamic>> history;
}

/// Repositorio de Billetera Virtual
class WalletRepository {
  final ApiClient _apiClient = ApiClient();

  /// El endpoint de Coins centraliza saldo e historial de recargas/retiros.
  Future<WalletSnapshot> getSnapshot(String userId) async {
    final String cacheKey = 'wallet_snapshot_$userId';
    try {
      final Response<dynamic> response =
          await _apiClient.get<dynamic>('/api/v1/coins/saldo');
      final Map<String, dynamic> data =
          Map<String, dynamic>.from(response.data as Map);
      await OfflineStore.write(cacheKey, data);
      return _snapshotFromJson(data);
    } on DioException {
      final Map<String, dynamic>? cached = await OfflineStore.readMap(cacheKey);
      if (cached == null) rethrow;
      return _snapshotFromJson(cached);
    }
  }

  Future<Map<String, dynamic>> initiateRecharge(double amount) async {
    final Response<dynamic> response = await _apiClient.post<dynamic>(
      '/api/v1/coins/iniciar-recarga',
      data: <String, double>{'monto_bs': amount},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  WalletSnapshot _snapshotFromJson(Map<String, dynamic> data) {
    final List<Map<String, dynamic>> history = (data['historial'] as List? ??
            [])
        .whereType<Map>()
        .map((Map<dynamic, dynamic> item) => Map<String, dynamic>.from(item))
        .toList();
    return WalletSnapshot(
      balance: (data['saldo_coins'] as num? ?? 0).toDouble(),
      history: history,
    );
  }
}
