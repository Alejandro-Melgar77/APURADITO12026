import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
} from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { api } from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'
import { Play, Square, Settings, Wifi, WifiOff, Car, Navigation } from 'lucide-react'
import L from 'leaflet'

// ─── Icono Apuradito (SVG inline como DivIcon) ──────────────────────────────
const createApuraditoCarIcon = () =>
  L.divIcon({
    className: '',
    html: `<div style="
      width:36px;height:36px;
      background:linear-gradient(135deg,#7c3aed,#6d28d9);
      border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);
      border:2px solid white;
      box-shadow:0 2px 8px rgba(109,40,217,0.5);
      display:flex;align-items:center;justify-content:center;
    ">
      <svg style="transform:rotate(45deg)" width="18" height="18" viewBox="0 0 24 24" fill="white">
        <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
      </svg>
    </div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36],
  })

// ─── Icono Origen (verde) ────────────────────────────────────────────────────
const originIcon = L.divIcon({
  className: '',
  html: `<div style="
    width:16px;height:16px;
    background:#10b981;
    border-radius:50%;
    border:3px solid white;
    box-shadow:0 0 0 2px #10b981;
  "></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
})

// ─── Icono Destino (rojo) ────────────────────────────────────────────────────
const destIcon = L.divIcon({
  className: '',
  html: `<div style="
    width:16px;height:16px;
    background:#ef4444;
    border-radius:50%;
    border:3px solid white;
    box-shadow:0 0 0 2px #ef4444;
  "></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
})

// ─── Tipos ───────────────────────────────────────────────────────────────────
interface LatLng {
  lat: number
  lng: number
}

interface ViajeWS {
  id: string
  conductor_nombre: string
  conductor_apellido: string
  lat?: number
  lng?: number
  es_simulacion?: boolean
  velocidad?: number
  ruta_geojson?: [number, number][] // [lng, lat] pairs from OSRM
}

// ─── MapClickHandler ─────────────────────────────────────────────────────────
const MapClickHandler: React.FC<{ onMapClick: (latlng: LatLng) => void }> = ({
  onMapClick,
}) => {
  const onClickRef = useRef(onMapClick)
  useEffect(() => {
    onClickRef.current = onMapClick
  }, [onMapClick])

  useMapEvents({
    click(e) {
      onClickRef.current(e.latlng)
    },
  })
  return null
}

// ─── VehiculoLayer: Marca + polilínea de la ruta morada ─────────────────────
const VehiculoLayer: React.FC<{ viaje: ViajeWS }> = ({ viaje }) => {
  const carIcon = createApuraditoCarIcon()

  if (viaje.lat === undefined || viaje.lng === undefined) return null

  // Convertir ruta_geojson de [lng,lat] a [lat,lng] para Leaflet
  const routePositions: [number, number][] = (viaje.ruta_geojson ?? []).map(
    ([lng, lat]) => [lat, lng]
  )

  return (
    <>
      {routePositions.length > 1 && (
        <Polyline
          positions={routePositions}
          pathOptions={{
            color: '#7c3aed',
            weight: 5,
            opacity: 0.85,
            dashArray: undefined,
          }}
        />
      )}
      <Marker position={[viaje.lat, viaje.lng]} icon={carIcon}>
        <Popup>
          <div style={{ fontFamily: 'Inter, sans-serif', minWidth: 160 }}>
            <div style={{ fontWeight: 700, fontSize: 13, color: '#7c3aed', marginBottom: 4 }}>
              🚗 {viaje.conductor_nombre} {viaje.conductor_apellido}
            </div>
            <div style={{ fontSize: 11, color: '#64748b' }}>
              Simulación en tiempo real
            </div>
            <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
              Pos: {viaje.lat.toFixed(5)}, {viaje.lng.toFixed(5)}
            </div>
          </div>
        </Popup>
      </Marker>
    </>
  )
}

// ─── Componente principal ────────────────────────────────────────────────────
const SimulacionPage: React.FC = () => {
  const [activo, setActivo] = useState(false)
  const [numVehiculos, setNumVehiculos] = useState(3)
  const [velocidadKmh, setVelocidadKmh] = useState(40)

  const [origen, setOrigen] = useState<LatLng | null>(null)
  const [destino, setDestino] = useState<LatLng | null>(null)
  const [modoSeleccion, setModoSeleccion] = useState<'origen' | 'destino' | null>(null)

  const [viajes, setViajes] = useState<ViajeWS[]>([])
  const [error, setError] = useState<string | null>(null)

  // Sincronizar estado inicial
  useEffect(() => {
    const fetchEstado = async () => {
      try {
        const res = await api.get('/api/v1/simulacion/estado')
        setActivo(res.data.activo ?? false)
        if (res.data.num_vehiculos) setNumVehiculos(res.data.num_vehiculos)
      } catch {
        // server might not be up yet
      }
    }
    fetchEstado()
  }, [])

  // WebSocket unificado de viajes
  const wsBase = (import.meta.env.VITE_API_URL_PROD || 'http://localhost:8000').replace(/^http/, 'ws').replace(/\/$/, '')
  const { isConnected } = useWebSocket(`${wsBase}/ws/viajes`, {
    onMessage: (data) => {
      if (data.tipo === 'viajes_activos' || data.tipo === 'update_simulacion') {
        if (Array.isArray(data.data)) {
          setViajes(data.data as ViajeWS[])
        }
      }
    },
  })

  const handleMapClick = useCallback(
    (latlng: LatLng) => {
      if (activo || numVehiculos > 1) return
      if (modoSeleccion === 'origen') {
        setOrigen(latlng)
        setModoSeleccion('destino')
      } else if (modoSeleccion === 'destino') {
        setDestino(latlng)
        setModoSeleccion(null)
      }
    },
    [activo, numVehiculos, modoSeleccion]
  )

  const handleIniciar = async () => {
    setError(null)
    if (numVehiculos === 1 && (!origen || !destino)) {
      setError('Para 1 vehículo, debes seleccionar Origen y Destino en el mapa.')
      return
    }
    try {
      await api.post('/api/v1/simulacion/iniciar', {
        num_vehiculos: numVehiculos,
        num_pasajeros: 0,
        velocidad_promedio: velocidadKmh,
        origen_lat: origen?.lat,
        origen_lng: origen?.lng,
        destino_lat: destino?.lat,
        destino_lng: destino?.lng,
      })
      setActivo(true)
    } catch (e) {
      setError('Error al iniciar la simulación. Verifica que el backend esté activo.')
      console.error(e)
    }
  }

  const handleDetener = async () => {
    try {
      await api.post('/api/v1/simulacion/detener')
      setActivo(false)
      setViajes([])
      setOrigen(null)
      setDestino(null)
      setModoSeleccion(null)
    } catch (e) {
      console.error(e)
    }
  }

  const handleVelocidadChange = async (nuevaVel: number) => {
    setVelocidadKmh(nuevaVel)
    if (activo) {
      try {
        await api.patch('/api/v1/simulacion/velocidad', { velocidad_kmh: nuevaVel })
      } catch {
        // silencioso si falla
      }
    }
  }

  const vehiculosSimulados = viajes.filter(
    (v) => v.es_simulacion !== false && v.lat !== undefined
  )

  return (
    <div className="flex flex-col gap-6 h-full min-h-[85vh]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Motor de Simulación
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Rutas reales por calles de Santa Cruz · Tracking WebSocket en tiempo real
          </p>
        </div>
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold shadow-sm ${
            isConnected ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
          }`}
        >
          {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
          {isConnected ? 'WebSocket Activo' : 'Desconectado'}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[640px]">
        {/* Panel de Control */}
        <div className="lg:col-span-1 flex flex-col gap-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm overflow-y-auto custom-scrollbar">
          {/* Título */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <h3 className="font-extrabold text-slate-800 dark:text-white flex items-center gap-2">
              <Settings size={16} className="text-violet-500" /> Controles
            </h3>
            <span
              className={`px-2.5 py-1 rounded-lg font-bold text-xs uppercase ${
                activo
                  ? 'bg-emerald-100 text-emerald-700'
                  : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
              }`}
            >
              {activo ? '● Activo' : '○ Detenido'}
            </span>
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-100 dark:border-red-800/30 text-xs text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          {/* N° Vehículos */}
          <div>
            <label className="label">Nº Vehículos</label>
            <input
              id="sim-num-vehiculos"
              type="number"
              min={1}
              max={20}
              value={numVehiculos}
              onChange={(e) => {
                const val = Math.max(1, parseInt(e.target.value) || 1)
                setNumVehiculos(val)
                if (val > 1) {
                  setOrigen(null)
                  setDestino(null)
                  setModoSeleccion(null)
                }
              }}
              className="input"
              disabled={activo}
            />
          </div>

          {/* Selector manual de ruta (solo si numVehiculos === 1) */}
          {numVehiculos === 1 && !activo && (
            <div className="flex flex-col gap-2">
              <p className="text-xs text-violet-600 dark:text-violet-400 font-medium">
                Selecciona la ruta manualmente en el mapa:
              </p>
              <div className="flex gap-2">
                <button
                  id="sim-btn-origen"
                  onClick={() => setModoSeleccion('origen')}
                  className={`flex-1 text-xs py-2 px-3 rounded-xl font-bold border transition-all ${
                    modoSeleccion === 'origen'
                      ? 'bg-emerald-500 text-white border-emerald-500'
                      : origen
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : 'bg-slate-50 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                  }`}
                >
                  {origen ? '✓ Origen' : '⊕ Origen'}
                </button>
                <button
                  id="sim-btn-destino"
                  onClick={() => setModoSeleccion('destino')}
                  className={`flex-1 text-xs py-2 px-3 rounded-xl font-bold border transition-all ${
                    modoSeleccion === 'destino'
                      ? 'bg-red-500 text-white border-red-500'
                      : destino
                        ? 'bg-red-50 text-red-700 border-red-200'
                        : 'bg-slate-50 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                  }`}
                  disabled={!origen}
                >
                  {destino ? '✓ Destino' : '⊕ Destino'}
                </button>
              </div>
              {modoSeleccion && (
                <p className="text-[11px] text-slate-400 text-center animate-pulse">
                  {modoSeleccion === 'origen' ? '🟢 Haz clic en el mapa para el origen' : '🔴 Haz clic en el mapa para el destino'}
                </p>
              )}
            </div>
          )}

          {/* Velocidad km/h — editable en tiempo real */}
          <div>
            <label className="label">
              Velocidad (km/h)
              {activo && (
                <span className="ml-2 text-[10px] text-emerald-600 font-bold">
                  ↻ Tiempo real
                </span>
              )}
            </label>
            <input
              id="sim-velocidad"
              type="number"
              min={5}
              max={120}
              step={5}
              value={velocidadKmh}
              onChange={(e) =>
                handleVelocidadChange(Math.max(5, parseFloat(e.target.value) || 40))
              }
              className="input"
            />
            <p className="text-[10px] text-slate-400 mt-1">
              {velocidadKmh} km/h ≈ {((velocidadKmh / 3600) * 5 * 1000).toFixed(0)} m cada 5 seg
            </p>
          </div>

          {/* Botones Iniciar / Detener */}
          <div className="flex gap-2">
            {!activo ? (
              <button
                id="sim-btn-iniciar"
                onClick={handleIniciar}
                className="btn btn-primary flex-1 bg-emerald-500 hover:bg-emerald-600 focus:ring-emerald-500 text-sm"
              >
                <Play size={14} /> Iniciar
              </button>
            ) : (
              <button
                id="sim-btn-detener"
                onClick={handleDetener}
                className="btn btn-primary flex-1 bg-rose-500 hover:bg-rose-600 focus:ring-rose-500 text-sm"
              >
                <Square size={14} /> Detener
              </button>
            )}
          </div>

          {/* Lista de vehículos simulados */}
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Car size={12} className="text-violet-500" /> En Ruta ({vehiculosSimulados.length})
            </span>
            {vehiculosSimulados.length === 0 ? (
              <p className="text-xs text-slate-400 mt-2">Sin vehículos activos.</p>
            ) : (
              <div className="flex flex-col gap-1.5 mt-2 max-h-[180px] overflow-y-auto custom-scrollbar pr-1">
                {vehiculosSimulados.map((v) => (
                  <div
                    key={v.id}
                    className="bg-violet-50 dark:bg-violet-900/20 p-2.5 rounded-xl border border-violet-100 dark:border-violet-800/30 flex justify-between items-center"
                  >
                    <div className="flex items-center gap-2">
                      <Navigation size={12} className="text-violet-500" />
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                        {v.conductor_nombre}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-violet-500">
                      {v.lat?.toFixed(4)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Mapa */}
        <div className="lg:col-span-3 rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm relative z-0">
          <MapContainer
            center={[-17.783, -63.182]}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <MapClickHandler onMapClick={handleMapClick} />

            {/* Marcadores de origen y destino (modo selección manual) */}
            {origen && (
              <Marker position={[origen.lat, origen.lng]} icon={originIcon}>
                <Popup>📍 Origen seleccionado</Popup>
              </Marker>
            )}
            {destino && (
              <Marker position={[destino.lat, destino.lng]} icon={destIcon}>
                <Popup>🏁 Destino seleccionado</Popup>
              </Marker>
            )}

            {/* Vehículos simulados con sus rutas */}
            {vehiculosSimulados.map((v) => (
              <VehiculoLayer key={v.id} viaje={v} />
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}

export default SimulacionPage
