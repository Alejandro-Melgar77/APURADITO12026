import React, { useState } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useWebSocket } from '../hooks/useWebSocket'
import { Wifi, WifiOff, MapPin } from 'lucide-react'

interface RutaActiva {
  id: string
  conductor_nombre: string
  conductor_apellido: string
  vehiculo_placa: string
  vehiculo_color: string
  origen_direccion: string
  destino_direccion: string
  asientos_disponibles: number
  estado: string
  hora_salida: string
}

const ViajesPage: React.FC = () => {
  const [rutas, setRutas] = useState<RutaActiva[]>([])

  const wsBase = (import.meta.env.VITE_API_URL_PROD || 'http://localhost:8000').replace(/^http/, 'ws').replace(/\/$/, '')
  const { isConnected } = useWebSocket(`${wsBase}/ws/viajes`, {
    onMessage: (data) => {
      if (data.tipo === 'viajes_activos' && data.data) {
        setRutas(data.data)
      }
    }
  })

  return (
    <div className="flex flex-col gap-8 h-full min-h-[85vh]">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Supervisar Viajes (Mapa en Vivo)
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Monitoreo de carpooling activo con WebSockets.
          </p>
        </div>

        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold shadow-sm ${isConnected ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}
        >
          {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
          {isConnected ? 'Conectado a Live WS' : 'Desconectado'}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
        {/* Tabla / Lista de rutas */}
        <div className="lg:col-span-1 flex flex-col gap-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm overflow-y-auto custom-scrollbar">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
            <h3 className="font-extrabold text-slate-800 dark:text-white">Rutas Activas</h3>
            <span className="px-2.5 py-1 rounded-lg bg-violet-100 text-violet-700 font-bold text-xs">
              {rutas.length}
            </span>
          </div>

          <div className="flex flex-col gap-4 mt-2">
            {rutas.length === 0 ? (
              <div className="text-center py-10 text-slate-400 font-semibold text-sm">
                No hay rutas activas en este momento.
              </div>
            ) : (
              rutas.map((r) => (
                <div
                  key={r.id}
                  className="bg-slate-50 dark:bg-slate-850 p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex flex-col gap-2"
                >
                  <div className="flex justify-between items-start">
                    <span className="font-bold text-slate-800 dark:text-white">
                      {r.conductor_nombre} {r.conductor_apellido}
                    </span>
                    <span className="text-xs font-bold px-2 py-0.5 bg-blue-100 text-blue-700 rounded uppercase tracking-wider">
                      {r.vehiculo_placa}
                    </span>
                  </div>
                  <div className="flex items-start gap-2 mt-1">
                    <MapPin size={14} className="text-emerald-500 mt-0.5 shrink-0" />
                    <span className="text-xs text-slate-500 line-clamp-1">
                      {r.origen_direccion}
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <MapPin size={14} className="text-rose-500 mt-0.5 shrink-0" />
                    <span className="text-xs text-slate-500 line-clamp-1">
                      {r.destino_direccion}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-200 dark:border-slate-700">
                    <span className="text-xs font-semibold text-slate-400">
                      Asientos:{' '}
                      <b className="text-slate-700 dark:text-slate-300">{r.asientos_disponibles}</b>
                    </span>
                    <span className="text-xs font-semibold text-slate-400">
                      Estado: <b className="text-emerald-600 capitalize">{r.estado}</b>
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Mapa general */}
        <div className="lg:col-span-2 rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm relative z-0">
          <MapContainer
            center={[-17.783, -63.182]}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </MapContainer>
        </div>
      </div>
    </div>
  )
}

export default ViajesPage
