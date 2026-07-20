import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';

/// Repositorio de Billetera Virtual
class WalletRepository {
  final ApiClient _apiClient = ApiClient();

  /// Obtener el saldo del usuario
  Future<double> getBalance() async {
    final response = await _apiClient.get('/api/v1/auth/me');
    final num balance = response.data['saldo_coins'] ?? 0;
    return balance.toDouble();
  }

  /// Obtener historial de pagos
  Future<List<PaymentModel>> getPaymentHistory() async {
    final response = await _apiClient.get('/api/v1/pagos/?limit=50');
    final List list = response.data as List;
    return list.map((e) => PaymentModel.fromJson(e)).toList();
  }

  /// Obtener historial de recargas
  Future<List<Map<String, dynamic>>> getRechargeHistory() async {
    final response = await _apiClient.get('/api/v1/recargas/mis-recargas');
    final List list = response.data as List;
    return List<Map<String, dynamic>>.from(list);
  }
}
