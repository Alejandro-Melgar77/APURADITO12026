import 'package:flutter/material.dart';
import 'package:apuradito_mobile/data/models/route_model.dart';
import 'package:apuradito_mobile/data/repositories/wallet_repository.dart';

/// Provider para la gestión de la Billetera Virtual (Coins)
class WalletProvider extends ChangeNotifier {
  final WalletRepository _repository = WalletRepository();

  double balance = 0.0;
  List<PaymentModel> payments = [];
  List<Map<String, dynamic>> recharges = [];
  bool isLoading = false;
  String? errorMessage;

  /// Carga el saldo y el historial de transacciones
  Future<void> loadWallet() async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      balance = await _repository.getBalance();
      payments = await _repository.getPaymentHistory();
      recharges = await _repository.getRechargeHistory();
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
