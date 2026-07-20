import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

/// Persistencia JSON pequena para datos que pueden mostrarse sin conexion.
/// No guarda tokens ni informacion de pago sensible.
class OfflineStore {
  const OfflineStore._();

  static Future<void> write(String key, Object value) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    await preferences.setString(key, jsonEncode(value));
  }

  static Future<Map<String, dynamic>?> readMap(String key) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    final String? raw = preferences.getString(key);
    if (raw == null) return null;
    try {
      final Object? decoded = jsonDecode(raw);
      return decoded is Map ? Map<String, dynamic>.from(decoded) : null;
    } on FormatException {
      await preferences.remove(key);
      return null;
    }
  }

  static Future<List<Map<String, dynamic>>> readList(String key) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    final String? raw = preferences.getString(key);
    if (raw == null) return <Map<String, dynamic>>[];
    try {
      final Object? decoded = jsonDecode(raw);
      if (decoded is! List) return <Map<String, dynamic>>[];
      return decoded
          .whereType<Map>()
          .map((Map<dynamic, dynamic> item) => Map<String, dynamic>.from(item))
          .toList();
    } on FormatException {
      await preferences.remove(key);
      return <Map<String, dynamic>>[];
    }
  }
}
