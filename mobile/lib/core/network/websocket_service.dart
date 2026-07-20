import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../constants/app_constants.dart';

enum WsConnectionState { disconnected, connecting, connected }

/// Mantiene el feed de viajes activo y se reconecta solo cuando corresponde.
class WebSocketService extends ChangeNotifier {
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  Timer? _reconnectTimer;
  WsConnectionState _state = WsConnectionState.disconnected;
  bool _shouldReconnect = true;
  final Set<void Function(Map<String, dynamic>)> _messageListeners =
      <void Function(Map<String, dynamic>)>{};

  WsConnectionState get connectionState => _state;
  bool get isConnected => _state == WsConnectionState.connected;

  Future<void> connect() async {
    if (_state != WsConnectionState.disconnected) return;

    _shouldReconnect = true;
    _setState(WsConnectionState.connecting);
    try {
      final WebSocketChannel channel = WebSocketChannel.connect(
        Uri.parse(AppConstants.wsViajesUrl),
      );
      _channel = channel;
      await channel.ready;
      if (_channel != channel || !_shouldReconnect) return;

      _setState(WsConnectionState.connected);
      _subscription = channel.stream.listen(
        _handleMessage,
        onDone: _handleConnectionClosed,
        onError: (Object error, StackTrace stackTrace) {
          debugPrint('[WS] $error');
          _handleConnectionClosed();
        },
        cancelOnError: true,
      );
    } catch (error) {
      debugPrint('[WS] No se pudo conectar: $error');
      _handleConnectionClosed();
    }
  }

  void _handleMessage(dynamic message) {
    if (message is! String) return;
    try {
      final Object? decoded = jsonDecode(message);
      if (decoded is! Map<String, dynamic>) return;
      for (final void Function(Map<String, dynamic>) listener
          in Set<void Function(Map<String, dynamic>)>.from(_messageListeners)) {
        listener(decoded);
      }
    } on FormatException catch (error) {
      debugPrint('[WS] Mensaje inválido: $error');
    }
  }

  void _handleConnectionClosed() {
    _subscription?.cancel();
    _subscription = null;
    _channel = null;
    _setState(WsConnectionState.disconnected);
    if (_shouldReconnect) _scheduleReconnect();
  }

  void _scheduleReconnect() {
    if (_reconnectTimer?.isActive ?? false) return;
    _reconnectTimer = Timer(
      const Duration(milliseconds: AppConstants.wsReconnectDelayMs),
      connect,
    );
  }

  void addMessageListener(void Function(Map<String, dynamic>) listener) {
    _messageListeners.add(listener);
  }

  void removeMessageListener(void Function(Map<String, dynamic>) listener) {
    _messageListeners.remove(listener);
  }

  Future<void> disconnect() async {
    _shouldReconnect = false;
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
    await _subscription?.cancel();
    _subscription = null;
    await _channel?.sink.close();
    _channel = null;
    _setState(WsConnectionState.disconnected);
  }

  void _setState(WsConnectionState state) {
    if (_state == state) return;
    _state = state;
    notifyListeners();
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
