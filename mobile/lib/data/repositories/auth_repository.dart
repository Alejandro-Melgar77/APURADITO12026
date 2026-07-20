import 'package:apuradito_mobile/core/constants/app_constants.dart';
import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/data/models/user_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthRepository {
  AuthRepository({ApiClient? apiClient, FlutterSecureStorage? secureStorage})
      : _apiClient = apiClient ?? ApiClient(),
        _secureStorage = secureStorage ?? const FlutterSecureStorage();

  final ApiClient _apiClient;
  final FlutterSecureStorage _secureStorage;

  Future<void> login(String email, String password) async {
    final response = await _apiClient.post<dynamic>(
      AppConstants.loginEndpoint,
      data: <String, String>{
        'email': email.trim(),
        'password': password,
      },
    );
    final Map<String, dynamic> data = _asMap(response.data);
    final String? token = data['access_token'] as String?;
    if (token == null || token.isEmpty) {
      throw const FormatException(
          'El servidor no devolvió un token de acceso.');
    }
    await _secureStorage.write(key: AppConstants.tokenKey, value: token);
  }

  Future<void> register({
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
    final bool isDriver = rol == AppConstants.rolConductor;
    await _apiClient.post<dynamic>(
      isDriver
          ? '/api/v1/auth/registro/conductor'
          : '/api/v1/auth/registro/pasajero',
      data: <String, dynamic>{
        'email': email.trim(),
        'password': password,
        'nombre': nombre.trim(),
        'apellido': apellido.trim(),
        'ci_carnet': ci.trim().isEmpty ? null : ci.trim(),
        'telefono': telefono.trim(),
        if (fechaNacimiento != null)
          'fecha_nacimiento':
              fechaNacimiento.toIso8601String().split('T').first,
        if (isDriver) ...<String, dynamic>{
          'placa': placa?.trim().toUpperCase(),
          'marca': marca?.trim(),
          'modelo': modelo?.trim(),
          'color': color?.trim(),
          'anio': anioVehiculo,
          'asientos_totales': asientosTotales,
          'tipo': 'automovil',
          'combustible': 'gasolina',
        },
      },
    );
  }

  Future<UserModel> getProfile() async {
    final Response<dynamic> response =
        await _apiClient.get<dynamic>(AppConstants.profileEndpoint);
    return UserModel.fromJson(_asMap(response.data));
  }

  Future<bool> hasToken() async {
    final String? token = await _secureStorage.read(key: AppConstants.tokenKey);
    return token != null && token.isNotEmpty;
  }

  Future<void> clearToken() =>
      _secureStorage.delete(key: AppConstants.tokenKey);

  Map<String, dynamic> _asMap(Object? data) {
    if (data is Map<String, dynamic>) return data;
    if (data is Map) return Map<String, dynamic>.from(data);
    throw const FormatException(
        'La respuesta del servidor no tiene el formato esperado.');
  }
}
