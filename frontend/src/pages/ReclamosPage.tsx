import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import { SkeletonRow } from '../components/ui/SkeletonLoader'
import { AlertCircle, Eye, Search, Filter, MessageSquare, Clock, CheckCircle } from 'lucide-react'

interface Reclamo {
  id: string
  tipo: string
  asunto: string
  descripcion: string
  estado: string
  creado_en: string
  usuario_id: string
  solicitud_viaje_id: string | null
}

const ReclamosPage: React.FC = () => {
  const [reclamos, setReclamos] = useState<Reclamo[]>([])
  const [loading, setLoading] = useState(true)
  const [tipo, setTipo] = useState('')
  const [estado, setEstado] = useState('')
  const [pagina, setPagina] = useState(1)
  const [total, setTotal] = useState(0)

  const [selectedReclamo, setSelectedReclamo] = useState<Reclamo | null>(null)
  const [showDetailModal, setShowDetailModal] = useState(false)

  const fetchReclamos = async () => {
    setLoading(true)
    try {
      const response = await api.get('/api/v1/reclamos/', {
        params: {
          tipo: tipo || undefined,
          estado: estado || undefined,
          skip: (pagina - 1) * 10,
          limit: 10
        }
      })
      if (response.data.datos) {
        setReclamos(response.data.datos)
        setTotal(response.data.total)
      } else if (Array.isArray(response.data)) {
        setReclamos(response.data)
        setTotal(response.data.length)
      } else if (response.data.items) {
        setReclamos(response.data.items)
        setTotal(response.data.total)
      }
    } catch (error) {
      console.error('Error al cargar reclamos:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReclamos()
  }, [tipo, estado, pagina])

  const handleVerDetalles = (reclamo: Reclamo) => {
    setSelectedReclamo(reclamo)
    setShowDetailModal(true)
  }

  const handleCambiarEstado = async (id: string, nuevoEstado: string) => {
    try {
      await api.patch(`/api/v1/reclamos/${id}/estado`, { nuevo_estado: nuevoEstado })
      fetchReclamos()
      if (selectedReclamo && selectedReclamo.id === id) {
        setSelectedReclamo({ ...selectedReclamo, estado: nuevoEstado })
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error al cambiar estado')
    }
  }

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'abierto':
        return (
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-400 flex w-fit items-center gap-1">
            <AlertCircle size={12} /> Abierto
          </span>
        )
      case 'en_revision':
        return (
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-amber-100 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400 flex w-fit items-center gap-1">
            <Clock size={12} /> En Revisión
          </span>
        )
      case 'resuelto':
        return (
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400 flex w-fit items-center gap-1">
            <CheckCircle size={12} /> Resuelto
          </span>
        )
      default:
        return (
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 flex w-fit">
            {estado}
          </span>
        )
    }
  }

  const formatFecha = (isoString: string) => {
    return new Date(isoString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Reclamos y Denuncias
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Bandeja de entrada para procesar los reclamos de los usuarios.
          </p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm flex flex-wrap gap-4 items-center justify-start">
        <div className="flex flex-wrap gap-4 w-full md:w-auto">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 uppercase">Tipo:</span>
            <select
              value={tipo}
              onChange={(e) => {
                setTipo(e.target.value)
                setPagina(1)
              }}
              className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-300 focus:outline-none"
            >
              <option value="">Todos</option>
              <option value="conduccion_peligrosa">Conducción Peligrosa</option>
              <option value="cobro_incorrecto">Cobro Incorrecto</option>
              <option value="comportamiento">Comportamiento</option>
              <option value="ruta_incorrecta">Ruta Incorrecta</option>
              <option value="otro">Otro</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 uppercase">Estado:</span>
            <select
              value={estado}
              onChange={(e) => {
                setEstado(e.target.value)
                setPagina(1)
              }}
              className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-300 focus:outline-none"
            >
              <option value="">Todos</option>
              <option value="abierto">Abierto</option>
              <option value="en_revision">En Revisión</option>
              <option value="resuelto">Resuelto</option>
            </select>
          </div>
        </div>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Asunto</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Fecha</th>
              <th className="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <>
                <SkeletonRow />
                <SkeletonRow />
                <SkeletonRow />
              </>
            ) : reclamos.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-400 font-semibold">
                  No se encontraron reclamos registrados
                </td>
              </tr>
            ) : (
              reclamos.map((r) => (
                <tr key={r.id}>
                  <td>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-violet-100 dark:bg-violet-950 flex items-center justify-center font-bold text-violet-600 dark:text-violet-300 shadow-inner">
                        <MessageSquare size={16} />
                      </div>
                      <div className="flex flex-col">
                        <span className="font-semibold text-slate-800 dark:text-white line-clamp-1">
                          {r.asunto}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                      {r.tipo.replace('_', ' ')}
                    </span>
                  </td>
                  <td>{getEstadoBadge(r.estado)}</td>
                  <td>
                    <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      {formatFecha(r.creado_en)}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleVerDetalles(r)}
                        title="Ver detalles"
                        className="p-2 text-slate-400 hover:text-violet-600 hover:bg-violet-50 dark:hover:bg-slate-800 rounded-xl transition-colors duration-200"
                      >
                        <Eye size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-2">
        <span className="text-xs font-semibold text-slate-400">Mostrando página {pagina}</span>
        <div className="flex gap-2">
          <button
            disabled={pagina <= 1}
            onClick={() => setPagina(pagina - 1)}
            className="btn btn-secondary py-1.5 px-3 text-xs"
          >
            Anterior
          </button>
          <button
            disabled={reclamos.length < 10}
            onClick={() => setPagina(pagina + 1)}
            className="btn btn-secondary py-1.5 px-3 text-xs"
          >
            Siguiente
          </button>
        </div>
      </div>

      {showDetailModal && selectedReclamo && (
        <div className="fixed inset-0 bg-slate-950/45 flex items-center justify-center p-4 z-30 fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-[500px] shadow-2xl flex flex-col gap-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-extrabold text-slate-850 dark:text-white text-lg">
                  {selectedReclamo.asunto}
                </h3>
                <p className="text-xs font-semibold text-slate-400 mt-1">
                  Tipo: {selectedReclamo.tipo.replace('_', ' ').toUpperCase()}
                </p>
              </div>
              {getEstadoBadge(selectedReclamo.estado)}
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-slate-100 dark:border-slate-800">
              <p className="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-wrap">
                {selectedReclamo.descripcion}
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-slate-400">
                Cambiar estado del reclamo:
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleCambiarEstado(selectedReclamo.id, 'en_revision')}
                  className={`btn flex-1 text-xs py-2 ${selectedReclamo.estado === 'en_revision' ? 'bg-amber-100 text-amber-700 ring-2 ring-amber-500' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                >
                  <Clock size={14} className="mr-1" /> En Revisión
                </button>
                <button
                  onClick={() => handleCambiarEstado(selectedReclamo.id, 'resuelto')}
                  className={`btn flex-1 text-xs py-2 ${selectedReclamo.estado === 'resuelto' ? 'bg-emerald-100 text-emerald-700 ring-2 ring-emerald-500' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                >
                  <CheckCircle size={14} className="mr-1" /> Resuelto
                </button>
                <button
                  onClick={() => handleCambiarEstado(selectedReclamo.id, 'abierto')}
                  className={`btn flex-1 text-xs py-2 ${selectedReclamo.estado === 'abierto' ? 'bg-red-100 text-red-700 ring-2 ring-red-500' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                >
                  <AlertCircle size={14} className="mr-1" /> Abierto
                </button>
              </div>
            </div>

            <div className="flex justify-end mt-2">
              <button onClick={() => setShowDetailModal(false)} className="btn btn-secondary px-6">
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReclamosPage
