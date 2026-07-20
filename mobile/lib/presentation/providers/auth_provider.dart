import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:apuradito_mobile/data/models/user_model.dart';
import 'package:apuradito_mobile/data/repositories/auth_repository.dart';
import 'package:apuradito_mobile/core/constants/app_constants.dart';

class AuthProvider extends ChangeNotifier {
  final AuthRepository _authRepository = AuthRepository();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  
  UserModel? currentUser;
  bool isLoading = false;
  String? errorMessage;
  
  bool get isLoggedIn => currentUser != null;
  
  String _activeRol = 'pasajero';
  String get activeRol => _activeRol;
  
  void switchRol(String rol) {
    _activeRol = rol;
    notifyListeners();
  }
  
  Future<bool> login(String email, String password) async {
    try {
      isLoading = true;
      errorMessage = null;
      notifyListeners();
      
      await _authRepository.login(email, password);
      final profile = await _authRepository.getProfile();
      
      currentUser = profile;
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('user', jsonEncode(profile.toJson()));
      
      isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      isLoading = false;
      errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> register({
    required String email,
    required String password,
    required String nombre,
    required String apellido,
    required String ci,
    required String telefono,
    required String rol,
  }) async {
    try {
      isLoading = true;
      errorMessage = null;
      notifyListeners();
      
      await _authRepository.register(
        email: email,
        password: password,
        nombre: nombre,
        apellido: apellido,
        ci: ci,
        telefono: telefono,
        rol: rol,
      );
      
      final loginSuccess = await login(email, password);
      return loginSuccess;
    } catch (e) {
      isLoading = false;
      errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<void> loadSavedUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userStr = prefs.getString('user');
      if (userStr != null) {
        currentUser = UserModel.fromJson(jsonDecode(userStr));
        notifyListeners();
      }
    } catch (e) {
      // Ignored
    }
  }

  Future<void> logout() async {
    await _secureStorage.delete(key: AppConstants.tokenKey);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('user');
    currentUser = null;
    notifyListeners();
  }

  Future<void> refreshProfile() async {
    try {
      final profile = await _authRepository.getProfile();
      currentUser = profile;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('user', jsonEncode(profile.toJson()));
      notifyListeners();
    } catch (e) {
      // Ignored
    }
  }
}
