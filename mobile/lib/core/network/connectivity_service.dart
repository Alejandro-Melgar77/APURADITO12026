import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

/// Estado de red de la aplicacion.
///
/// Una interfaz de red no garantiza acceso a Internet; las operaciones remotas
/// siguen manejando sus propios errores. Este servicio solo evita intentar una
/// sincronizacion cuando el dispositivo informa que esta desconectado.
class ConnectivityService extends ChangeNotifier {
  ConnectivityService({Connectivity? connectivity})
      : _connectivity = connectivity ?? Connectivity();

  final Connectivity _connectivity;
  StreamSubscription<List<ConnectivityResult>>? _subscription;
  List<ConnectivityResult> _results = const <ConnectivityResult>[
    ConnectivityResult.none,
  ];

  bool get isOnline => _results.any(
        (ConnectivityResult result) => result != ConnectivityResult.none,
      );

  Future<void> initialize() async {
    await refresh();
    _subscription ??= _connectivity.onConnectivityChanged.listen(
      _updateResults,
      onError: (_, __) => _updateResults(
        const <ConnectivityResult>[ConnectivityResult.none],
      ),
    );
  }

  Future<void> refresh() async {
    try {
      _updateResults(await _connectivity.checkConnectivity());
    } catch (_) {
      _updateResults(const <ConnectivityResult>[ConnectivityResult.none]);
    }
  }

  void _updateResults(List<ConnectivityResult> results) {
    if (listEquals(_results, results)) return;
    _results = List<ConnectivityResult>.unmodifiable(results);
    notifyListeners();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
