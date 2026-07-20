import 'package:apuradito_mobile/core/storage/offline_store.dart';

enum PendingActionType { publishRoute, rateRide }

class PendingAction {
  const PendingAction({
    required this.id,
    required this.userId,
    required this.type,
    required this.payload,
    required this.createdAt,
  });

  final String id;
  final String userId;
  final PendingActionType type;
  final Map<String, dynamic> payload;
  final DateTime createdAt;

  factory PendingAction.fromJson(Map<String, dynamic> json) {
    return PendingAction(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      type: PendingActionType.values.byName(json['type'] as String),
      payload: Map<String, dynamic>.from(json['payload'] as Map),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => <String, dynamic>{
        'id': id,
        'user_id': userId,
        'type': type.name,
        'payload': payload,
        'created_at': createdAt.toIso8601String(),
      };
}

/// Cola de acciones no financieras que pueden enviarse al volver la red.
/// Acciones que reservan asientos, cobran Coins o cambian el viaje requieren
/// conexion para no crear conflictos ni operaciones financieras duplicadas.
class OfflineActionQueue {
  static const String _storageKey = 'offline_actions_v1';

  Future<List<PendingAction>> forUser(String userId) async {
    final List<Map<String, dynamic>> raw =
        await OfflineStore.readList(_storageKey);
    final List<PendingAction> actions = <PendingAction>[];
    for (final Map<String, dynamic> item in raw) {
      try {
        final PendingAction action = PendingAction.fromJson(item);
        if (action.userId == userId) actions.add(action);
      } on FormatException {
        // Una entrada danada no impide recuperar las restantes.
      } on ArgumentError {
        // Una version antigua de la app puede contener un tipo desconocido.
      }
    }
    return actions
      ..sort((PendingAction a, PendingAction b) =>
          a.createdAt.compareTo(b.createdAt));
  }

  Future<void> enqueue({
    required String userId,
    required PendingActionType type,
    required Map<String, dynamic> payload,
  }) async {
    final List<Map<String, dynamic>> current =
        await OfflineStore.readList(_storageKey);
    final DateTime now = DateTime.now().toUtc();
    current.add(
      PendingAction(
        id: '${now.microsecondsSinceEpoch}-${type.name}',
        userId: userId,
        type: type,
        payload: payload,
        createdAt: now,
      ).toJson(),
    );
    await OfflineStore.write(_storageKey, current);
  }

  Future<void> remove(String id) async {
    final List<Map<String, dynamic>> current =
        await OfflineStore.readList(_storageKey);
    current.removeWhere((Map<String, dynamic> item) => item['id'] == id);
    await OfflineStore.write(_storageKey, current);
  }
}
