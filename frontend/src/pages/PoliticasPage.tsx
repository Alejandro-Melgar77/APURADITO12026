import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import { SkeletonCard } from '../components/ui/SkeletonLoader'
import { FileText, Plus, CheckCircle, XCircle } from 'lucide-react'

interface Politica {
  id: string
  titulo: string
  contenido: string
  version: string
  activa: boolean
  creado_en: string
}

const PoliticasPage: React.FC = () => {
  const [politicas, setPoliticas] = useState<Politica[]>([])
  const [loading, setLoading] = useState(true)

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedPolitica, setSelectedPolitica] = useState<Politica | null>(null)

  // Nuevos datos
  const [nuevoTitulo, setNuevoTitulo] = useState('')
  const [nuevoContenido, setNuevoContenido] = useState('')
  const [nuevaVersion, setNuevaVersion] = useState('')

  const fetchPoliticas = async () => {
    setLoading(true)
    try {
      const response = await api.get('/api/v1/politicas/')
      setPoliticas(response.data)
    } catch (error) {
      console.error('Error al cargar politicas:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPoliticas()
  }, [])

  const handleCrearPolitica = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/api/v1/politicas/', {
        titulo: nuevoTitulo,
        contenido: nuevoContenido,
        version: nuevaVersion
      })
      setShowCreateModal(false)
      setNuevoTitulo('')
      setNuevoContenido('')
      setNuevaVersion('')
      fetchPoliticas()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error al crear política')
    }
  }

  const handleVerDetalles = (politica: Politica) => {
    setSelectedPolitica(politica)
    setShowDetailModal(true)
  }

  const formatFecha = (isoString: string) => {
    return new Date(isoString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Encabezado */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Políticas Legales
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Gestión de términos, condiciones y privacidad de la plataforma.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary shadow-sm hover:scale-[1.02] active:scale-[0.98]"
        >
          <Plus size={18} />
          Nueva Política
        </button>
      </div>

      {/* Lista de Políticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : politicas.length === 0 ? (
          <div className="col-span-full text-center py-8 text-slate-400 font-semibold">
            No se encontraron políticas registradas
          </div>
        ) : (
          politicas.map((p) => (
            <div
              key={p.id}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col gap-4"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-violet-100 dark:bg-violet-950 flex items-center justify-center text-violet-600 dark:text-violet-400">
                    <FileText size={20} />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-slate-800 dark:text-white">{p.titulo}</h3>
                    <span className="text-xs font-semibold text-slate-400">
                      Versión {p.version} • {formatFecha(p.creado_en)}
                    </span>
                  </div>
                </div>
                {p.activa ? (
                  <span className="text-emerald-500" title="Activa">
                    <CheckCircle size={20} />
                  </span>
                ) : (
                  <span className="text-slate-300 dark:text-slate-600" title="Inactiva">
                    <XCircle size={20} />
                  </span>
                )}
              </div>
              <div className="text-sm text-slate-500 dark:text-slate-400 line-clamp-3 bg-slate-50 dark:bg-slate-850 p-3 rounded-xl">
                {p.contenido}
              </div>
              <button
                onClick={() => handleVerDetalles(p)}
                className="mt-auto pt-2 text-sm font-bold text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300 flex items-center"
              >
                Ver completa
              </button>
            </div>
          ))
        )}
      </div>

      {/* Modal de Detalle */}
      {showDetailModal && selectedPolitica && (
        <div className="fixed inset-0 bg-slate-950/45 flex items-center justify-center p-4 z-30 fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 w-full max-w-[800px] max-h-[90vh] shadow-2xl flex flex-col gap-6 overflow-hidden">
            <div className="flex justify-between items-start shrink-0">
              <div>
                <h3 className="font-extrabold text-slate-850 dark:text-white text-2xl">
                  {selectedPolitica.titulo}
                </h3>
                <p className="text-sm font-semibold text-slate-400 mt-1">
                  Versión {selectedPolitica.version} • {formatFecha(selectedPolitica.creado_en)}
                  {selectedPolitica.activa && (
                    <span className="ml-3 px-2 py-0.5 bg-emerald-100 text-emerald-600 rounded-md text-xs">
                      ACTIVA
                    </span>
                  )}
                </p>
              </div>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <XCircle size={24} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar text-slate-600 dark:text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">
              {selectedPolitica.contenido}
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-100 dark:border-slate-800 shrink-0">
              <button onClick={() => setShowDetailModal(false)} className="btn btn-primary px-8">
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Creación */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-950/45 flex items-center justify-center p-4 z-30 fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-[600px] shadow-2xl flex flex-col gap-6">
            <div>
              <h3 className="font-extrabold text-slate-850 dark:text-white text-lg">
                Nueva Política
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Al crear una nueva política, la versión anterior se desactiva automáticamente.
              </p>
            </div>

            <form onSubmit={handleCrearPolitica} className="flex flex-col gap-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="label">Título</label>
                  <input
                    type="text"
                    required
                    value={nuevoTitulo}
                    onChange={(e) => setNuevoTitulo(e.target.value)}
                    placeholder="Ej: Términos de Servicio"
                    className="input"
                  />
                </div>
                <div className="w-32">
                  <label className="label">Versión</label>
                  <input
                    type="text"
                    required
                    value={nuevaVersion}
                    onChange={(e) => setNuevaVersion(e.target.value)}
                    placeholder="Ej: 1.0"
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="label">Contenido Legal</label>
                <textarea
                  required
                  value={nuevoContenido}
                  onChange={(e) => setNuevoContenido(e.target.value)}
                  className="input min-h-[250px] resize-y py-3"
                  placeholder="Redacta el contenido de la política aquí..."
                ></textarea>
              </div>

              <div className="flex gap-4 mt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn btn-secondary flex-1"
                >
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary flex-1">
                  Publicar Política
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default PoliticasPage
