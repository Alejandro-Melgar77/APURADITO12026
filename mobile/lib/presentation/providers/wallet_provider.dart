import 'package:flutter/material.dart';
import 'package:apuradito_mobile/data/repositories/wallet_repository.dart';

/// Provider para la gestión de la Billetera Virtual (Coins)
class WalletProvider extends ChangeNotifier {
  final WalletRepository _repository = WalletRepository();

  double balance = 0.0;
  List<Map<String, dynamic>> payments = [];
  List<Map<String, dynamic>> recharges = [];
  bool isLoading = false;
  String? errorMessage;

  /// Carga el saldo y el historial de transacciones
  Future<void> loadWallet(String userId) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final WalletSnapshot snapshot = await _repository.getSnapshot(userId);
      balance = snapshot.balance;
      // El backend actual registra en este historial las recargas y retiros.
      recharges = snapshot.history;
      payments = <Map<String, dynamic>>[];
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>?> initiateRecharge(double amount) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      return await _repository.initiateRecharge(amount);
    } catch (_) {
      errorMessage = 'No se pudo generar la solicitud de recarga.';
      return null;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
