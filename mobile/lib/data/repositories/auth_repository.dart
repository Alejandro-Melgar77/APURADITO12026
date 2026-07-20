import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';
import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/data/models/user_model.dart';
import 'package:apuradito_mobile/core/constants/app_constants.dart';

class AuthRepository {
  final ApiClient _apiClient = ApiClient();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _apiClient.postForm(
      '/api/v1/auth/login',
      FormData.fromMap({
        'username': email,
        'password': password,
        'grant_type': 'password',
      }),
    );

    final data = response.data;
    if (data['access_token'] != null) {
      await _secureStorage.write(
        key: AppConstants.tokenKey,
        value: data['access_token'],
      );
    }
    
    return data;
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String nombre,
    required String apellido,
    required String ci,
    required String telefono,
    required String rol,
  }) async {
    final response = await _apiClient.post(
      '/api/v1/auth/register',
      data: {
        'email': email,
        'password': password,
        'nombre': nombre,
        'apellido': apellido,
        'ci': ci,
        'telefono': telefono,
        'rol': rol,
      },
    );
    return response.data;
  }

  Future<UserModel> getProfile() async {
    final response = await _apiClient.get('/api/v1/auth/me');
    return UserModel.fromJson(response.data);
  }
}
