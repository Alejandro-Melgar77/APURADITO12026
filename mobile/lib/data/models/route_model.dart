import 'package:latlong2/latlong.dart';

/// Ruta activa recibida del WebSocket /ws/viajes.
/// Incluye posición en tiempo real y la polilínea OSRM (calles reales).
class ActiveRouteModel {
  const ActiveRouteModel({
    required this.id,
    required this.conductorNombre,
    required this.conductorApellido,
    required this.origenDireccion,
    required this.destinoDireccion,
    required this.asientosDisponibles,
    required this.estado,
    required this.horaSalida,
    this.vehiculoPlaca,
    this.vehiculoColor,
    this.lat,
    this.lng,
    this.origenLat,
    this.origenLng,
    this.destinoLat,
    this.destinoLng,
    this.esSimulacion = false,
    this.rutaGeojson = const [],
  });

  final String id;
  final String conductorNombre;
  final String conductorApellido;
  final String origenDireccion;
  final String destinoDireccion;
  final int asientosDisponibles;
  final String estado;
  final String horaSalida;
  final String? vehiculoPlaca;
  final String? vehiculoColor;
  final double? lat;
  final double? lng;
  final double? origenLat;
  final double? origenLng;
  final double? destinoLat;
  final double? destinoLng;
  final bool esSimulacion;

  /// Lista de [lng, lat] desde OSRM — representa la ruta por calles reales.
  final List<dynamic> rutaGeojson;

  String get conductorNombreCompleto => '$conductorNombre $conductorApellido';

  /// Convierte rutaGeojson en LatLng para flutter_map.
  /// OSRM devuelve [lng, lat], Leaflet/flutter_map usa LatLng(lat, lng).
  List<LatLng> get routePolyline {
    final List<LatLng> points = [];
    for (final point in rutaGeojson) {
      if (point is List && point.length >= 2) {
        final double lng = (point[0] as num).toDouble();
        final double lat = (point[1] as num).toDouble();
        points.add(LatLng(lat, lng));
      }
    }
    return points;
  }

  /// Posición actual del vehículo (si está en movimiento).
  LatLng? get currentPosition {
    if (lat != null && lng != null) {
      return LatLng(lat!, lng!);
    }
    if (origenLat != null && origenLng != null) {
      return LatLng(origenLat!, origenLng!);
    }
    if (routePolyline.isNotEmpty) return routePolyline.first;
    return null;
  }

  bool get hasPosition => currentPosition != null;
  bool get hasRoute => rutaGeojson.isNotEmpty;

  factory ActiveRouteModel.fromJson(Map<String, dynamic> json) {
    return ActiveRouteModel(
      id: json['id'] as String? ?? '',
      conductorNombre: json['conductor_nombre'] as String? ?? 'Conductor',
      conductorApellido: json['conductor_apellido'] as String? ?? '',
      origenDireccion: json['origen_direccion'] as String? ?? '',
      destinoDireccion: json['destino_direccion'] as String? ?? '',
      asientosDisponibles: json['asientos_disponibles'] as int? ?? 0,
      estado: json['estado'] as String? ?? '',
      horaSalida: json['hora_salida'] as String? ?? '',
      vehiculoPlaca: json['vehiculo_placa'] as String?,
      vehiculoColor: json['vehiculo_color'] as String?,
      lat: (json['lat'] as num?)?.toDouble(),
      lng: (json['lng'] as num?)?.toDouble(),
      origenLat: (json['origen_lat'] as num?)?.toDouble(),
      origenLng: (json['origen_lng'] as num?)?.toDouble(),
      destinoLat: (json['destino_lat'] as num?)?.toDouble(),
      destinoLng: (json['destino_lng'] as num?)?.toDouble(),
      esSimulacion: json['es_simulacion'] as bool? ?? false,
      rutaGeojson: json['ruta_geojson'] as List<dynamic>? ?? const [],
    );
  }

  ActiveRouteModel copyWith({
    double? lat,
    double? lng,
    List<dynamic>? rutaGeojson,
    int? asientosDisponibles,
    String? estado,
  }) {
    return ActiveRouteModel(
      id: id,
      conductorNombre: conductorNombre,
      conductorApellido: conductorApellido,
      origenDireccion: origenDireccion,
      destinoDireccion: destinoDireccion,
      asientosDisponibles: asientosDisponibles ?? this.asientosDisponibles,
      estado: estado ?? this.estado,
      horaSalida: horaSalida,
      vehiculoPlaca: vehiculoPlaca,
      vehiculoColor: vehiculoColor,
      lat: lat ?? this.lat,
      lng: lng ?? this.lng,
      origenLat: origenLat,
      origenLng: origenLng,
      destinoLat: destinoLat,
      destinoLng: destinoLng,
      esSimulacion: esSimulacion,
      rutaGeojson: rutaGeojson ?? this.rutaGeojson,
    );
  }

  Map<String, dynamic> toJson() => <String, dynamic>{
        'id': id,
        'conductor_nombre': conductorNombre,
        'conductor_apellido': conductorApellido,
        'origen_direccion': origenDireccion,
        'destino_direccion': destinoDireccion,
        'asientos_disponibles': asientosDisponibles,
        'estado': estado,
        'hora_salida': horaSalida,
        'vehiculo_placa': vehiculoPlaca,
        'vehiculo_color': vehiculoColor,
        'lat': lat,
        'lng': lng,
        'origen_lat': origenLat,
        'origen_lng': origenLng,
        'destino_lat': destinoLat,
        'destino_lng': destinoLng,
        'es_simulacion': esSimulacion,
        'ruta_geojson': rutaGeojson,
      };
}

/// Modelo de ruta publicada (para conductores al crear viaje).
class PublishedRouteModel {
  const PublishedRouteModel({
    required this.id,
    required this.origenDireccion,
    required this.destinoDireccion,
    required this.asientosDisponibles,
    required this.estado,
    required this.horaSalida,
    required this.costoCalculadoBs,
    this.distanciaTotalKm,
    this.duracionEstimadaMin,
  });

  final String id;
  final String origenDireccion;
  final String destinoDireccion;
  final int asientosDisponibles;
  final String estado;
  final String horaSalida;
  final double costoCalculadoBs;
  final double? distanciaTotalKm;
  final int? duracionEstimadaMin;

  factory PublishedRouteModel.fromJson(Map<String, dynamic> json) {
    return PublishedRouteModel(
      id: json['id'] as String? ?? '',
      origenDireccion: json['origen_direccion'] as String? ?? '',
      destinoDireccion: json['destino_direccion'] as String? ?? '',
      asientosDisponibles: json['asientos_disponibles'] as int? ?? 0,
      estado: json['estado'] as String? ?? '',
      horaSalida: json['hora_salida'] as String? ?? '',
      costoCalculadoBs: (json['costo_calculado_bs'] as num?)?.toDouble() ?? 0.0,
      distanciaTotalKm: (json['distancia_total_km'] as num?)?.toDouble(),
      duracionEstimadaMin: json['duracion_estimada_min'] as int?,
    );
  }

  PublishedRouteModel copyWith({
    int? asientosDisponibles,
    String? estado,
  }) =>
      PublishedRouteModel(
        id: id,
        origenDireccion: origenDireccion,
        destinoDireccion: destinoDireccion,
        asientosDisponibles: asientosDisponibles ?? this.asientosDisponibles,
        estado: estado ?? this.estado,
        horaSalida: horaSalida,
        costoCalculadoBs: costoCalculadoBs,
        distanciaTotalKm: distanciaTotalKm,
        duracionEstimadaMin: duracionEstimadaMin,
      );
}

/// Solicitud de viaje (pasajero pide unirse a ruta).
class RideRequestModel {
  const RideRequestModel({
    required this.id,
    required this.estado,
    required this.costoCalculadoBs,
    required this.metodoPago,
    this.pasajeroNombre,
    this.rutaId,
    this.conductorId,
    this.conductorNombre,
    this.origenDireccion,
    this.destinoDireccion,
  });

  final String id;
  final String estado; // pendiente | aceptado | rechazado | completado
  final double costoCalculadoBs;
  final String metodoPago;
  final String? pasajeroNombre;
  final String? rutaId;
  final String? conductorId;
  final String? conductorNombre;
  final String? origenDireccion;
  final String? destinoDireccion;

  factory RideRequestModel.fromJson(Map<String, dynamic> json) {
    return RideRequestModel(
      id: json['id'] as String? ?? '',
      estado: json['estado'] as String? ?? 'pendiente',
      costoCalculadoBs: (json['costo_calculado_bs'] as num?)?.toDouble() ?? 0.0,
      metodoPago: json['metodo_pago'] as String? ?? 'coins',
      pasajeroNombre: json['pasajero_nombre'] as String?,
      rutaId: json['ruta_publicada_id'] as String?,
      conductorId: json['conductor_id'] as String?,
      conductorNombre: json['conductor_nombre'] as String?,
      origenDireccion: json['origen_direccion'] as String?,
      destinoDireccion: json['destino_direccion'] as String?,
    );
  }

  Map<String, dynamic> toJson() => <String, dynamic>{
        'id': id,
        'estado': estado,
        'costo_calculado_bs': costoCalculadoBs,
        'metodo_pago': metodoPago,
        'pasajero_nombre': pasajeroNombre,
        'ruta_publicada_id': rutaId,
        'conductor_id': conductorId,
        'conductor_nombre': conductorNombre,
        'origen_direccion': origenDireccion,
        'destino_direccion': destinoDireccion,
      };
}

/// Modelo de pago / transacción.
class PaymentModel {
  const PaymentModel({
    required this.id,
    required this.montoBs,
    required this.estado,
    required this.metodo,
    required this.creadoEn,
  });

  final String id;
  final double montoBs;
  final String estado;
  final String metodo;
  final String creadoEn;

  factory PaymentModel.fromJson(Map<String, dynamic> json) {
    return PaymentModel(
      id: json['id'] as String? ?? '',
      montoBs: (json['monto_total_bs'] as num?)?.toDouble() ?? 0.0,
      estado: json['estado'] as String? ?? '',
      metodo: json['metodo'] as String? ?? 'coins',
      creadoEn: json['creado_en'] as String? ?? '',
    );
  }
}
