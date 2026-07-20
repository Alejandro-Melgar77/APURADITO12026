export interface Usuario {
  id: string
  email: string
  nombre: string
  apellido: string
  ci_carnet?: string
  fecha_nacimiento?: string
  telefono?: string
  foto_perfil_url?: string
  foto_facial_verificacion_url?: string
  rol: 'conductor' | 'pasajero' | 'ambos' | 'admin'
  estado: 'pendiente' | 'activo' | 'suspendido' | 'eliminado'
  verificado_facial: boolean
  google_uid?: string
  saldo_coins: number
  creado_en: string
  actualizado_en: string
}

export interface Conductor {
  conductor_id: string
  nombre: string
  email: string
  ci_carnet: string
  calificacion_promedio: number
  total_viajes: number
  km_totales: number
  comisiones_pendientes_bs: number
  cuenta_congelada: boolean
  congelado_manualmente: boolean
  verificado_facial: boolean
  estado_usuario: string
}

export interface Vehiculo {
  id: string
  conductor_id: string
  placa: string
  marca: string
  modelo: string
  color: string
  anio: number
  tipo: 'automovil' | 'moto'
  combustible: 'gasolina' | 'diesel' | 'gas'
  asientos_totales: number
  placa_verificada: boolean
  activo: boolean
}

export interface RutaPublicada {
  id: string
  conductor_id: string
  vehiculo_id?: string
  origen_direccion: string
  destino_direccion: string
  distancia_total_km: number
  duracion_estimada_min: number
  asientos_disponibles: number
  estado: 'programada' | 'en_curso' | 'completada' | 'cancelada'
  hora_salida: string
  es_simulacion: boolean
  creado_en: string
}

export interface SolicitarViaje {
  id: string
  pasajero_id: string
  ruta_publicada_id: string
  distancia_viaje_km: number
  costo_calculado_bs: number
  estado: 'pendiente' | 'aceptada' | 'rechazada' | 'cancelada' | 'completada'
  metodo_pago: 'coins' | 'efectivo' | 'nfc'
  creado_en: string
}

export interface Configuracion {
  valor: number | string
  tipo: 'float' | 'int' | 'string' | 'json'
  descripcion: string
}

export interface PaginatedResponse<T> {
  datos: T[]
  total: number
  pagina: number
  por_pagina: number
}
