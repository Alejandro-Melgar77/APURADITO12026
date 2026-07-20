import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import KPICard from '../components/ui/KPICard'
import { SkeletonCard, SkeletonChart } from '../components/ui/SkeletonLoader'
import { Users, Calendar, MapPin, DollarSign } from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts'

interface DashboardData {
  usuarios_activos: number
  viajes_hoy: number
  kms_ahorrados: number
  comisiones_ganadas_bs: number
  grafico_viajes: { fecha: string; cantidad: number }[]
  grafico_usuarios: { fecha: string; cantidad: number }[]
}

const DashboardPage: React.FC = () => {
  const [periodo, setPeriodo] = useState('7dias')
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await api.get(`/api/v1/reportes/dashboard?periodo=${periodo}`)
        setData(response.data)
      } catch (error) {
        console.error('Error al cargar datos del dashboard:', error)
        setData(null)
        setError('No se pudieron cargar las estadísticas. Verifica la conexión e inténtalo nuevamente.')
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [periodo, refreshKey])

  return (
    <div className="flex flex-col gap-8">
      {/* Encabezado Dashboard */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Estadísticas de Uso
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Visión general del rendimiento de Apuradito.
          </p>
        </div>

        {/* Selector de Periodo */}
        <select
          value={periodo}
          onChange={(e) => setPeriodo(e.target.value)}
          className="px-4 py-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm font-semibold text-slate-700 dark:text-slate-300 focus:outline-none focus:border-violet-500 transition-all duration-200 cursor-pointer shadow-sm"
        >
          <option value="hoy">Hoy</option>
          <option value="7dias">Últimos 7 días</option>
          <option value="30dias">Últimos 30 días</option>
          <option value="año">Este año</option>
        </select>
      </div>

      {error && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-medium text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/20 dark:text-rose-300" role="alert">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span>{error}</span>
            <button type="button" className="btn btn-secondary !px-3 !py-1.5 text-xs" onClick={() => setRefreshKey((value) => value + 1)}>
              Reintentar
            </button>
          </div>
        </div>
      )}

      {/* Grid de KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading || !data ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <KPICard
              titulo="USUARIOS ACTIVOS"
              valor={data.usuarios_activos.toLocaleString()}
              icono={<Users size={22} />}
              subtitulo="total activos"
            />
            <KPICard
              titulo="VIAJES HOY / PERIODO"
              valor={data.viajes_hoy.toLocaleString()}
              icono={<Calendar size={22} />}
              subtitulo="en el periodo actual"
            />
            <KPICard
              titulo="KMS AHORRADOS"
              valor={`${data.kms_ahorrados.toLocaleString()} km`}
              icono={<MapPin size={22} />}
              subtitulo="en el periodo actual"
            />
            <KPICard
              titulo="AHORRO ESTIMADO"
              valor={`Bs. ${data.comisiones_ganadas_bs.toLocaleString('es-BO', { minimumFractionDigits: 2 })}`}
              icono={<DollarSign size={22} />}
              subtitulo="comisiones en el periodo"
            />
          </>
        )}
      </div>

      {/* Sección de Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {loading || !data ? (
          <>
            <SkeletonChart />
            <SkeletonChart />
          </>
        ) : (
          <>
            {/* Gráfico de Viajes */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-6">
              <div>
                <h3 className="font-extrabold text-slate-800 dark:text-white text-base leading-tight">
                  Viajes completados
                </h3>
                <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 mt-1 block">
                  Volumen diario de carpooling.
                </span>
              </div>
              <div className="h-[280px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.grafico_viajes}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                    <XAxis
                      dataKey="fecha"
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: '#94A3B8', fontSize: 10 }}
                    />
                    <YAxis
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: '#94A3B8', fontSize: 10 }}
                    />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }} />
                    <Line
                      type="monotone"
                      dataKey="cantidad"
                      name="Viajes"
                      stroke="#7C3AED"
                      strokeWidth={3}
                      dot={{ fill: '#7C3AED', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Gráfico de Usuarios */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-6">
              <div>
                <h3 className="font-extrabold text-slate-800 dark:text-white text-base leading-tight">
                  Nuevos Usuarios
                </h3>
                <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 mt-1 block">
                  Registros por día en la plataforma.
                </span>
              </div>
              <div className="h-[280px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.grafico_usuarios}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                    <XAxis
                      dataKey="fecha"
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: '#94A3B8', fontSize: 10 }}
                    />
                    <YAxis
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: '#94A3B8', fontSize: 10 }}
                    />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }} />
                    <Bar
                      dataKey="cantidad"
                      name="Nuevos"
                      fill="#3B82F6"
                      radius={[4, 4, 0, 0]}
                      barSize={24}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
