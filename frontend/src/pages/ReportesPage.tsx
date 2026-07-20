import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import KPICard from '../components/ui/KPICard'
import { SkeletonCard } from '../components/ui/SkeletonLoader'
import { AlertTriangle, DollarSign, Download, Loader2 } from 'lucide-react'

interface Moroso {
  conductor_id: string
  nombre: string
  email: string
  telefono: string
  comisiones_pendientes_bs: number
  fecha_inicio_deuda: string | null
  dias_deuda: number
  cuenta_congelada: boolean
}

const ReportesPage: React.FC = () => {
  const [periodo, setPeriodo] = useState('7dias')
  const [morosos, setMorosos] = useState<Moroso[]>([])
  const [loadingMorosos, setLoadingMorosos] = useState(true)
  const [errorMorosos, setErrorMorosos] = useState<string | null>(null)
  const [exportando, setExportando] = useState(false)

  // ── Carga de conductores morosos ────────────────────────────────────────
  useEffect(() => {
    const fetchMorosos = async () => {
      setLoadingMorosos(true)
      setErrorMorosos(null)
      try {
        const response = await api.get('/api/v1/reportes/morosos')
        setMorosos(response.data)
      } catch (err) {
        console.error('Error al cargar morosos:', err)
        setErrorMorosos('No se pudo cargar la lista de conductores morosos. Intenta de nuevo.')
      } finally {
        setLoadingMorosos(false)
      }
    }
    fetchMorosos()
  }, [])

  // ── KPIs derivados ──────────────────────────────────────────────────────
  const totalMorosos = morosos.length
  const deudaTotal = morosos.reduce((acc, m) => acc + m.comisiones_pendientes_bs, 0)

  // ── Exportar Excel ──────────────────────────────────────────────────────
  const handleExportarExcel = async () => {
    setExportando(true)
    try {
      const response = await api.get('/api/v1/reportes/exportar-excel', {
        params: { periodo },
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'reporte_apuradito.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Error al exportar Excel:', err)
    } finally {
      setExportando(false)
    }
  }

  return (
    <div className="flex flex-col gap-8">
      {/* ── Encabezado ─────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Reportes y Exportaciones
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Balances financieros, conductores morosos y exportación de datos.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Selector de periodo */}
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

          {/* Botón Exportar Excel */}
          <button
            onClick={handleExportarExcel}
            disabled={exportando}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:bg-violet-400 text-white text-sm font-bold shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
          >
            {exportando ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
            {exportando ? 'Exportando…' : 'Exportar Excel'}
          </button>
        </div>
      </div>

      {/* ── KPI Cards ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {loadingMorosos ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <KPICard
              titulo="CONDUCTORES MOROSOS"
              valor={totalMorosos.toLocaleString()}
              icono={<AlertTriangle size={22} />}
              subtitulo="conductores con deuda activa"
            />
            <KPICard
              titulo="DEUDA TOTAL PENDIENTE"
              valor={`Bs. ${deudaTotal.toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              icono={<DollarSign size={22} />}
              subtitulo="suma de comisiones pendientes"
            />
          </>
        )}
      </div>

      {/* ── Tabla de Conductores Morosos ────────────────────────────────── */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-red-50 dark:bg-red-950/30 text-red-500 flex items-center justify-center">
            <AlertTriangle size={16} />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 dark:text-white text-base leading-tight">
              Conductores Morosos
            </h3>
            <span className="text-xs font-semibold text-slate-400 dark:text-slate-500">
              Conductores con comisiones pendientes de pago
            </span>
          </div>
        </div>

        {/* Error */}
        {errorMorosos && (
          <div className="mx-6 my-4 px-4 py-3 rounded-xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 text-sm font-semibold text-red-600 dark:text-red-400 flex items-center gap-2">
            <AlertTriangle size={15} />
            {errorMorosos}
          </div>
        )}

        {/* Skeleton de tabla */}
        {loadingMorosos && !errorMorosos && (
          <div className="p-6 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="h-10 rounded-xl bg-slate-100 dark:bg-slate-800 animate-pulse"
              />
            ))}
          </div>
        )}

        {/* Tabla */}
        {!loadingMorosos && !errorMorosos && (
          <>
            {morosos.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 gap-3">
                <div className="w-14 h-14 rounded-2xl bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 flex items-center justify-center text-2xl">
                  ✅
                </div>
                <p className="text-base font-bold text-slate-700 dark:text-slate-300">
                  No hay conductores con deuda pendiente
                </p>
                <p className="text-sm text-slate-400 dark:text-slate-500">
                  Todos los conductores están al día con sus comisiones.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-100 dark:border-slate-800">
                      <th className="text-left px-6 py-3 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        Nombre
                      </th>
                      <th className="text-left px-6 py-3 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="text-right px-6 py-3 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        Deuda (Bs.)
                      </th>
                      <th className="text-center px-6 py-3 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        Cuenta Congelada
                      </th>
                      <th className="text-right px-6 py-3 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        Días de Deuda
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {morosos.map((m) => (
                      <tr
                        key={m.conductor_id}
                        className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors duration-150"
                      >
                        {/* Nombre */}
                        <td className="px-6 py-4">
                          <span className="text-sm font-semibold text-slate-800 dark:text-white">
                            {m.nombre}
                          </span>
                        </td>

                        {/* Email */}
                        <td className="px-6 py-4">
                          <span className="text-sm text-slate-500 dark:text-slate-400">
                            {m.email}
                          </span>
                        </td>

                        {/* Deuda */}
                        <td className="px-6 py-4 text-right">
                          <span className="text-sm font-bold text-red-600 dark:text-red-400">
                            {m.comisiones_pendientes_bs.toLocaleString('es-BO', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            })}
                          </span>
                        </td>

                        {/* Cuenta Congelada */}
                        <td className="px-6 py-4 text-center">
                          {m.cuenta_congelada ? (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-red-100 dark:bg-red-950/40 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900">
                              Congelada
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900">
                              Activa
                            </span>
                          )}
                        </td>

                        {/* Días de Deuda */}
                        <td className="px-6 py-4 text-right">
                          <span
                            className={`text-sm font-bold ${
                              m.dias_deuda > 30
                                ? 'text-red-600 dark:text-red-400'
                                : m.dias_deuda > 7
                                  ? 'text-amber-600 dark:text-amber-400'
                                  : 'text-slate-600 dark:text-slate-400'
                            }`}
                          >
                            {m.dias_deuda} días
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Footer con conteo */}
                <div className="px-6 py-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 dark:text-slate-500">
                    {totalMorosos} conductor{totalMorosos !== 1 ? 'es' : ''} con deuda
                  </span>
                  <span className="text-xs font-bold text-red-500">
                    Total: Bs.{' '}
                    {deudaTotal.toLocaleString('es-BO', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </span>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default ReportesPage
