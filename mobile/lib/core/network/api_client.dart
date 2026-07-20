import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';

/// Cliente HTTP centralizado con interceptor JWT automático.
/// Implementa PEP-equivalente Effective Dart: type annotations, const, docs.
class ApiClient {
  ApiClient._internal();
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  late final Dio _dio;

  /// Inicializa Dio con interceptores JWT + logging.
  void initialize() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: const Duration(milliseconds: AppConstants.connectTimeoutMs),
        receiveTimeout: const Duration(milliseconds: AppConstants.receiveTimeoutMs),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: AppConstants.tokenKey);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) {
          // 401 → token expirado, limpiar sesión
          if (error.response?.statusCode == 401) {
            _storage.delete(key: AppConstants.tokenKey);
          }
          return handler.next(error);
        },
      ),
    );
  }

  Dio get dio => _dio;

  // ── Helpers de conveniencia ────────────────────────────────────────────────

  /// GET request con manejo de errores unificado.
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.get<T>(path, queryParameters: queryParameters);
  }

  /// POST request con manejo de errores unificado.
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.post<T>(path, data: data, queryParameters: queryParameters);
  }

  /// PATCH request.
  Future<Response<T>> patch<T>(String path, {dynamic data}) async {
    return _dio.patch<T>(path, data: data);
  }

  /// PUT request.
  Future<Response<T>> put<T>(String path, {dynamic data}) async {
    return _dio.put<T>(path, data: data);
  }

  /// DELETE request.
  Future<Response<T>> delete<T>(String path) async {
    return _dio.delete<T>(path);
  }

  /// POST multipart (para subida de imágenes — verificación facial).
  Future<Response<T>> postForm<T>(
    String path,
    FormData formData,
  ) async {
    return _dio.post<T>(
      path,
      data: formData,
      options: Options(contentType: 'multipart/form-data'),
    );
  }
}
