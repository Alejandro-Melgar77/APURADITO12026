import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../constants/app_constants.dart';

/// Cliente HTTP centralizado con autenticación JWT y tiempos de espera.
class ApiClient {
  ApiClient._internal();
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  late final Dio _dio;
  bool _initialized = false;

  void initialize() {
    if (_initialized) return;
    _initialized = true;
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout:
            const Duration(milliseconds: AppConstants.connectTimeoutMs),
        receiveTimeout:
            const Duration(milliseconds: AppConstants.receiveTimeoutMs),
        headers: const <String, String>{'Accept': 'application/json'},
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest:
            (RequestOptions options, RequestInterceptorHandler handler) async {
          final String? token = await _storage.read(key: AppConstants.tokenKey);
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (DioException error, ErrorInterceptorHandler handler) {
          if (error.response?.statusCode == 401) {
            _storage.delete(key: AppConstants.tokenKey);
          }
          handler.next(error);
        },
      ),
    );
  }

  Dio get dio {
    initialize();
    return _dio;
  }

  Future<Response<T>> get<T>(String path,
      {Map<String, dynamic>? queryParameters}) {
    return dio.get<T>(path, queryParameters: queryParameters);
  }

  Future<Response<T>> post<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
  }) {
    return dio.post<T>(path, data: data, queryParameters: queryParameters);
  }

  Future<Response<T>> postForm<T>(String path, FormData formData) {
    return dio.post<T>(path, data: formData);
  }

  Future<Response<T>> postUrlEncoded<T>(String path, Map<String, String> data) {
    return dio.post<T>(
      path,
      data: data,
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );
  }

  Future<Response<T>> patch<T>(String path, {Object? data}) =>
      dio.patch<T>(path, data: data);
  Future<Response<T>> put<T>(String path, {Object? data}) =>
      dio.put<T>(path, data: data);
  Future<Response<T>> delete<T>(String path) => dio.delete<T>(path);

  Future<Response<T>> postMultipart<T>(String path, FormData formData) {
    return dio.post<T>(path, data: formData);
  }
}
