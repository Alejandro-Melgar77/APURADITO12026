import 'dart:async';

import 'package:apuradito_mobile/core/network/connectivity_service.dart';
import 'package:apuradito_mobile/core/storage/offline_action_queue.dart';
import 'package:apuradito_mobile/data/repositories/driver_repository.dart';
import 'package:apuradito_mobile/data/repositories/routes_repository.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

/// Sincroniza las acciones no financieras que el usuario guardo sin conexion.
class OfflineSyncProvider extends ChangeNotifier {
  final OfflineActionQueue _queue = OfflineActionQueue();
  final DriverRepository _driverRepository = DriverRepository();
  final RoutesRepository _routesRepository = RoutesRepository();

  ConnectivityService? _connectivity;
  String? _userId;
  int pendingCount = 0;
  bool isSyncing = false;
  String? errorMessage;

  void configure(ConnectivityService connectivity, String? userId) {
    if (!identical(_connectivity, connectivity)) {
      _connectivity?.removeListener(_onConnectivityChanged);
      _connectivity = connectivity;
      _connectivity!.addListener(_onConnectivityChanged);
    }
    if (_userId == userId) return;
    _userId = userId;
    unawaited(_refreshAndSync());
  }

  Future<void> _refreshAndSync() async {
    await refreshPendingCount();
    if (_connectivity?.isOnline ?? false) await sync();
  }

  void _onConnectivityChanged() {
    if (_connectivity?.isOnline ?? false) {
      unawaited(_refreshAndSync());
    } else {
      unawaited(refreshPendingCount());
    }
  }

  Future<void> refreshPendingCount() async {
    final String? userId = _userId;
    final int nextCount =
        userId == null ? 0 : (await _queue.forUser(userId)).length;
    if (pendingCount == nextCount) return;
    pendingCount = nextCount;
    notifyListeners();
  }

  Future<void> sync() async {
    final String? userId = _userId;
    if (userId == null || !(_connectivity?.isOnline ?? false) || isSyncing)
      return;

    isSyncing = true;
    errorMessage = null;
    notifyListeners();
    try {
      final List<PendingAction> actions = await _queue.forUser(userId);
      for (final PendingAction action in actions) {
        try {
          switch (action.type) {
            case PendingActionType.publishRoute:
              await _driverRepository.publishRouteFromPayload(action.payload);
              break;
            case PendingActionType.rateRide:
              await _routesRepository.rateRide(
                solicitudId: action.payload['solicitud_id'] as String,
                calificadoId: action.payload['calificado_id'] as String,
                estrellas: action.payload['estrellas'] as int,
                comentario: action.payload['comentario'] as String?,
              );
              break;
          }
          await _queue.remove(action.id);
        } on DioException catch (error) {
          // Sin red no se descarta la accion. Un error de servidor se conserva
          // para que el usuario pueda corregirlo al volver a abrir la app.
          errorMessage = _messageFromError(error);
          break;
        } on FormatException {
          errorMessage = 'Una accion pendiente tiene datos invalidos.';
          break;
        }
      }
    } finally {
      isSyncing = false;
      await refreshPendingCount();
      notifyListeners();
    }
  }

  String _messageFromError(DioException error) {
    final Object? detail = error.response?.data is Map
        ? (error.response!.data as Map)['detail']
        : null;
    return detail is String && detail.isNotEmpty
        ? detail
        : 'No se pudo sincronizar una accion pendiente.';
  }

  @override
  void dispose() {
    _connectivity?.removeListener(_onConnectivityChanged);
    super.dispose();
  }
}
