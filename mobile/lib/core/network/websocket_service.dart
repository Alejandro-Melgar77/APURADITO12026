import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../constants/app_constants.dart';

/// Estado de la conexión WebSocket.
enum WsConnectionState { disconnected, connecting, connected }

/// Servicio singleton de WebSocket para el feed en vivo de viajes.
/// Se reconecta automáticamente si la conexión se pierde.
class WebSocketService extends ChangeNotifier {
  WebSocketService._internal();
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  WsConnectionState _state = WsConnectionState.disconnected;
  final List<void Function(Map<String, dynamic>)> _listeners = [];

  WsConnectionState get connectionState => _state;
  bool get isConnected => _state == WsConnectionState.connected;

  /// Conecta al WebSocket de viajes activos.
  void connect() {
    if (_state == WsConnectionState.connecting ||
        _state == WsConnectionState.connected) {
      return;
    }
    _state = WsConnectionState.connecting;
    notifyListeners();

    try {
      _channel = WebSocketChannel.connect(
        Uri.parse(AppConstants.wsViajesUrl),
      );
      _state = WsConnectionState.connected;
      notifyListeners();

      _subscription = _channel!.stream.listen(
        (dynamic message) {
          if (message is String) {
            try {
              final Map<String, dynamic> data =
                  json.decode(message) as Map<String, dynamic>;
              for (final listener in List.from(_listeners)) {
                listener(data);
              }
            } catch (e) {
              debugPrint('[WS] Error parsing message: $e');
            }
          }
        },
        onDone: () {
          _state = WsConnectionState.disconnected;
          notifyListeners();
          _scheduleReconnect();
        },
        onError: (dynamic error) {
          debugPrint('[WS] Error: $error');
          _state = WsConnectionState.disconnected;
          notifyListeners();
          _scheduleReconnect();
        },
      );
    } catch (e) {
      debugPrint('[WS] Connection failed: $e');
      _state = WsConnectionState.disconnected;
      notifyListeners();
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    Future.delayed(
      const Duration(milliseconds: AppConstants.wsReconnectDelayMs),
      connect,
    );
  }

  /// Registra un listener para mensajes del WebSocket.
  void addListener2(void Function(Map<String, dynamic>) listener) {
    if (!_listeners.contains(listener)) {
      _listeners.add(listener);
    }
  }

  /// Elimina un listener registrado.
  void removeListener2(void Function(Map<String, dynamic>) listener) {
    _listeners.remove(listener);
  }

  /// Desconecta el WebSocket limpiamente.
  void disconnect() {
    _subscription?.cancel();
    _channel?.sink.close();
    _state = WsConnectionState.disconnected;
    notifyListeners();
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
