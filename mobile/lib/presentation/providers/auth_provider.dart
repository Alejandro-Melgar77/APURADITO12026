import 'dart:convert';

import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/data/models/user_model.dart';
import 'package:apuradito_mobile/data/repositories/auth_repository.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthProvider extends ChangeNotifier {
  AuthProvider({AuthRepository? authRepository})
      : _authRepository = authRepository ?? AuthRepository();

  final AuthRepository _authRepository;
  UserModel? currentUser;
  bool isLoading = false;
  String? errorMessage;
  bool registrationPendingApproval = false;
  String _activeRol = AppConstants.rolPasajero;

  bool get isLoggedIn => currentUser != null;
  String get activeRol => _activeRol;

  Future<bool> login(String email, String password) async {
    await _runLoading(() async {
      await _authRepository.login(email, password);
      final UserModel profile = await _authRepository.getProfile();
      await _saveSession(profile);
    });
    return errorMessage == null;
  }

  Future<bool> register({
    required String email,
    required String password,
    required String nombre,
    required String apellido,
    required String ci,
    required String telefono,
    required String rol,
    DateTime? fechaNacimiento,
    String? placa,
    String? marca,
    String? modelo,
    String? color,
    int? anioVehiculo,
    int? asientosTotales,
  }) async {
    await _runLoading(() async {
      await _authRepository.register(
        email: email,
        password: password,
        nombre: nombre,
        apellido: apellido,
        ci: ci,
        telefono: telefono,
        rol: rol,
        fechaNacimiento: fechaNacimiento,
        placa: placa,
        marca: marca,
        modelo: modelo,
        color: color,
        anioVehiculo: anioVehiculo,
        asientosTotales: asientosTotales,
      );
      if (rol == AppConstants.rolConductor) {
        registrationPendingApproval = true;
        return;
      }
      await _authRepository.login(email, password);
      final UserModel profile = await _authRepository.getProfile();
      await _saveSession(profile);
    });
    return errorMessage == null;
  }

  /// Restaura la sesión únicamente si existe tanto un token como un usuario.
  /// Evita entrar a la app con un perfil persistido pero sin credenciales.
  Future<void> loadSavedUser() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final String? userJson = prefs.getString(AppConstants.userKey);
    final bool hasToken = await _authRepository.hasToken();
    if (!hasToken || userJson == null) {
      await _clearLocalSession(prefs, clearToken: true);
      return;
    }

    try {
      currentUser =
          UserModel.fromJson(jsonDecode(userJson) as Map<String, dynamic>);
      _activeRol = prefs.getString(AppConstants.rolKey) ?? currentUser!.rol;
      notifyListeners();
    } catch (_) {
      await _clearLocalSession(prefs, clearToken: true);
    }
  }

  Future<void> refreshProfile() async {
    try {
      final UserModel profile = await _authRepository.getProfile();
      await _saveSession(profile);
    } on DioException catch (error) {
      if (error.response?.statusCode == 401) await logout();
    } catch (_) {
      // Mantiene el perfil local ante fallos temporales de conectividad.
    }
  }

  Future<void> logout() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    await _clearLocalSession(prefs, clearToken: true);
    errorMessage = null;
    notifyListeners();
  }

  Future<void> _saveSession(UserModel profile) async {
    currentUser = profile;
    _activeRol = profile.rol;
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.userKey, jsonEncode(profile.toJson()));
    await prefs.setString(AppConstants.rolKey, _activeRol);
  }

  Future<void> _clearLocalSession(
    SharedPreferences prefs, {
    required bool clearToken,
  }) async {
    if (clearToken) await _authRepository.clearToken();
    await prefs.remove(AppConstants.userKey);
    await prefs.remove(AppConstants.rolKey);
    currentUser = null;
    _activeRol = AppConstants.rolPasajero;
  }

  Future<void> _runLoading(Future<void> Function() operation) async {
    isLoading = true;
    errorMessage = null;
    registrationPendingApproval = false;
    notifyListeners();
    try {
      await operation();
    } on DioException catch (error) {
      errorMessage = _messageForDioError(error);
    } on FormatException catch (error) {
      errorMessage = error.message.toString();
    } catch (_) {
      errorMessage = 'Ocurrió un error inesperado. Inténtalo nuevamente.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  String _messageForDioError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      return 'No se pudo conectar al servidor. Verifica tu conexión e inténtalo de nuevo.';
    }
    final Object? detail = error.response?.data is Map
        ? (error.response!.data as Map)['detail']
        : null;
    if (detail is String && detail.isNotEmpty) return detail;
    if (error.response?.statusCode == 401)
      return 'Correo o contraseña incorrectos.';
    if (error.response?.statusCode == 409)
      return 'Ya existe una cuenta con esos datos.';
    return 'No se pudo completar la operación. Inténtalo nuevamente.';
  }
}
