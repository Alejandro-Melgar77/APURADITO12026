import 'dart:convert';

/// Modelo de usuario autenticado.
class UserModel {
  const UserModel({
    required this.id,
    required this.email,
    required this.nombre,
    required this.apellido,
    required this.rol,
    required this.saldoCoins,
    required this.estado,
    this.telefono,
    this.fotoUrl,
    this.verificadoFacial = false,
    this.conductorId,
  });

  final String id;
  final String email;
  final String nombre;
  final String apellido;
  final String rol; // 'pasajero' | 'conductor' | 'admin'
  final double saldoCoins;
  final String estado;
  final String? telefono;
  final String? fotoUrl;
  final bool verificadoFacial;
  final String? conductorId;

  String get nombreCompleto => '$nombre $apellido';
  bool get esConductor => rol == 'conductor';
  bool get esPasajero => rol == 'pasajero';

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String? ?? '',
      email: json['email'] as String? ?? '',
      nombre: json['nombre'] as String? ?? '',
      apellido: json['apellido'] as String? ?? '',
      rol: json['rol'] as String? ?? 'pasajero',
      saldoCoins: (json['saldo_coins'] as num?)?.toDouble() ?? 0.0,
      estado: json['estado'] as String? ?? 'activo',
      telefono: json['telefono'] as String?,
      fotoUrl: json['foto_url'] as String?,
      verificadoFacial: json['verificado_facial'] as bool? ?? false,
      conductorId: json['conductor_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'nombre': nombre,
      'apellido': apellido,
      'rol': rol,
      'saldo_coins': saldoCoins,
      'estado': estado,
      'telefono': telefono,
      'foto_url': fotoUrl,
      'verificado_facial': verificadoFacial,
      'conductor_id': conductorId,
    };
  }

  /// Serializa a JSON string para almacenamiento local.
  String toJsonString() => json.encode(toJson());

  /// Deserializa desde JSON string del almacenamiento local.
  static UserModel fromJsonString(String jsonString) {
    return UserModel.fromJson(json.decode(jsonString) as Map<String, dynamic>);
  }

  UserModel copyWith({
    String? id,
    String? email,
    String? nombre,
    String? apellido,
    String? rol,
    double? saldoCoins,
    String? estado,
    String? telefono,
    String? fotoUrl,
    bool? verificadoFacial,
    String? conductorId,
  }) {
    return UserModel(
      id: id ?? this.id,
      email: email ?? this.email,
      nombre: nombre ?? this.nombre,
      apellido: apellido ?? this.apellido,
      rol: rol ?? this.rol,
      saldoCoins: saldoCoins ?? this.saldoCoins,
      estado: estado ?? this.estado,
      telefono: telefono ?? this.telefono,
      fotoUrl: fotoUrl ?? this.fotoUrl,
      verificadoFacial: verificadoFacial ?? this.verificadoFacial,
      conductorId: conductorId ?? this.conductorId,
    );
  }
}
