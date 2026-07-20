import React, { useEffect, useState } from 'react'
import { api } from '../services/api'
import { Usuario } from '../types'
import { SkeletonRow } from '../components/ui/SkeletonLoader'
import Badge from '../components/ui/Badge'
import { Search, Plus, Filter, Edit, Trash2, Eye, ShieldAlert, Star } from 'lucide-react'

const UsuariosPage: React.FC = () => {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [rol, setRol] = useState('')
  const [estado, setEstado] = useState('')
  const [pagina, setPagina] = useState(1)
  const [total, setTotal] = useState(0)

  // Modales
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Datos del nuevo usuario
  const [nuevoNombre, setNuevoNombre] = useState('')
  const [nuevoApellido, setNuevoApellido] = useState('')
  const [nuevoEmail, setNuevoEmail] = useState('')
  const [nuevoPassword, setNuevoPassword] = useState('')
  const [nuevoRol, setNuevoRol] = useState('pasajero')

  // Modal Detalles
  const [selectedUsuario, setSelectedUsuario] = useState<Usuario | null>(null)
  const [showDetailModal, setShowDetailModal] = useState(false)

  const fetchUsuarios = async () => {
    setLoading(true)
    try {
      const response = await api.get('/api/v1/usuarios/', {
        params: {
          rol: rol || undefined,
          estado: estado || undefined,
          busqueda: busqueda || undefined,
          pagina,
          por_pagina: 10
        }
      })
      setUsuarios(response.data.datos)
      setTotal(response.data.total)
    } catch (error) {
      console.error('Error al cargar usuarios:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsuarios()
  }, [rol, estado, busqueda, pagina])

  const handleCrearUsuario = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/api/v1/usuarios/', {
        email: nuevoEmail,
        password: nuevoPassword,
        nombre: nuevoNombre,
        apellido: nuevoApellido,
        rol: nuevoRol,
        estado: 'activo'
      })
      setShowCreateModal(false)
      // Reset
      setNuevoNombre('')
      setNuevoApellido('')
      setNuevoEmail('')
      setNuevoPassword('')
      fetchUsuarios()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error al crear usuario')
    }
  }

  const handleCambiarEstado = async (id: string, nuevoEstado: string) => {
    if (window.confirm(`¿Está seguro de cambiar el estado de este usuario a ${nuevoEstado}?`)) {
      try {
        await api.patch(`/api/v1/usuarios/${id}/estado?estado=${nuevoEstado}`)
        fetchUsuarios()
      } catch (error) {
        console.error(error)
      }
    }
  }

  const handleEliminar = async (id: string) => {
    if (window.confirm('¿Está seguro de eliminar lógicamente a este usuario?')) {
      try {
        await api.delete(`/api/v1/usuarios/${id}`)
        fetchUsuarios()
      } catch (error) {
        console.error(error)
      }
    }
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Encabezado */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
            Gestionar Usuarios
          </h2>
          <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-1">
            Directorio de pasajeros y conductores de la plataforma.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary shadow-sm hover:scale-[1.02] active:scale-[0.98]"
        >
          <Plus size={18} />
          Nuevo Usuario
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm flex flex-wrap gap-4 items-center justify-between">
        {/* Buscador */}
        <div className="relative w-full md:w-72">
          <span className="absolute inset-y-0 left-3 flex items-center text-slate-400">
            <Search size={18} />
          </span>
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar por nombre o correo..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 focus:outline-none focus:border-violet-500 text-sm"
          />
        </div>

        {/* Combos de Filtro */}
        <div className="flex flex-wrap gap-4 w-full md:w-auto">
          {/* Rol */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 uppercase">Rol:</span>
            <select
              value={rol}
              onChange={(e) => {
                setRol(e.target.value)
                setPagina(1)
              }}
              className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-300 focus:outline-none"
            >
              <option value="">Todos</option>
              <option value="conductor">Conductor</option>
              <option value="pasajero">Pasajero</option>
              <option value="admin">Administrador</option>
            </select>
          </div>

          {/* Estado */}
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
              <option value="activo">Activo</option>
              <option value="pendiente">Pendiente</option>
              <option value="suspendido">Suspendido</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabla */}
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Rating</th>
              <th>Monedas (Coins)</th>
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
            ) : usuarios.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-slate-400 font-semibold">
                  No se encontraron usuarios registrados
                </td>
              </tr>
            ) : (
              usuarios.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-violet-100 dark:bg-violet-950 flex items-center justify-center font-bold text-violet-600 dark:text-violet-300 shadow-inner">
                        {u.nombre.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex flex-col">
                        <span className="font-semibold text-slate-800 dark:text-white">
                          {u.nombre} {u.apellido}
                        </span>
                        <span className="text-xs text-slate-400">{u.email}</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                      {u.rol}
                    </span>
                  </td>
                  <td>
                    <Badge estado={u.estado} />
                  </td>
                  <td>
                    <div className="flex items-center gap-1 text-amber-500 font-semibold text-sm">
                      <Star size={14} fill="currentColor" />
                      {u.verificado_facial ? '4.9' : 'N/A'}
                    </div>
                  </td>
                  <td>
                    <span className="font-bold text-slate-700 dark:text-slate-300">
                      {parseFloat((u.saldo_coins as any) || 0).toFixed(1)} Coins
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setSelectedUsuario(u)
                          setShowDetailModal(true)
                        }}
                        title="Ver detalles"
                        className="p-2 text-slate-400 hover:text-violet-600 hover:bg-violet-50 dark:hover:bg-slate-800 rounded-xl transition-colors duration-200"
                      >
                        <Eye size={18} />
                      </button>

                      {u.estado === 'suspendido' ? (
                        <button
                          onClick={() => handleCambiarEstado(u.id, 'activo')}
                          title="Habilitar Cuenta"
                          className="p-2 text-emerald-500 hover:bg-emerald-50 dark:hover:bg-slate-800 rounded-xl transition-colors duration-200"
                        >
                          <ShieldAlert size={18} />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleCambiarEstado(u.id, 'suspendido')}
                          title="Suspender Cuenta"
                          className="p-2 text-amber-500 hover:bg-amber-50 dark:hover:bg-slate-800 rounded-xl transition-colors duration-200"
                        >
                          <ShieldAlert size={18} />
                        </button>
                      )}

                      <button
                        onClick={() => handleEliminar(u.id)}
                        title="Eliminar lógicamente"
                        className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-slate-800 rounded-xl transition-colors duration-200"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs font-semibold text-slate-400">
          Mostrando {usuarios.length} de {total} usuarios
        </span>
        <div className="flex gap-2">
          <button
            disabled={pagina <= 1}
            onClick={() => setPagina(pagina - 1)}
            className="btn btn-secondary py-1.5 px-3 text-xs"
          >
            Anterior
          </button>
          <button
            disabled={usuarios.length < 10}
            onClick={() => setPagina(pagina + 1)}
            className="btn btn-secondary py-1.5 px-3 text-xs"
          >
            Siguiente
          </button>
        </div>
      </div>

      {/* Modal de Creación */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-950/45 flex items-center justify-center p-4 z-30 fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-[420px] shadow-2xl flex flex-col gap-6">
            <div>
              <h3 className="font-extrabold text-slate-850 dark:text-white text-lg">
                Registrar Nuevo Usuario
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Creación manual de cuentas desde el panel de control.
              </p>
            </div>

            <form onSubmit={handleCrearUsuario} className="flex flex-col gap-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="label">Nombre</label>
                  <input
                    type="text"
                    required
                    value={nuevoNombre}
                    onChange={(e) => setNuevoNombre(e.target.value)}
                    className="input"
                  />
                </div>
                <div className="flex-1">
                  <label className="label">Apellido</label>
                  <input
                    type="text"
                    required
                    value={nuevoApellido}
                    onChange={(e) => setNuevoApellido(e.target.value)}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="label">Correo Electrónico</label>
                <input
                  type="email"
                  required
                  value={nuevoEmail}
                  onChange={(e) => setNuevoEmail(e.target.value)}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Contraseña</label>
                <input
                  type="password"
                  required
                  value={nuevoPassword}
                  onChange={(e) => setNuevoPassword(e.target.value)}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Rol Inicial</label>
                <select
                  value={nuevoRol}
                  onChange={(e) => setNuevoRol(e.target.value)}
                  className="select"
                >
                  <option value="pasajero">Pasajero</option>
                  <option value="conductor">Conductor</option>
                  <option value="admin">Administrador</option>
                </select>
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
                  Crear Usuario
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Detalles */}
      {showDetailModal && selectedUsuario && (
        <div className="fixed inset-0 bg-slate-950/45 flex items-center justify-center p-4 z-30 fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-[500px] shadow-2xl flex flex-col gap-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-extrabold text-slate-850 dark:text-white text-lg">
                  Detalles del Usuario
                </h3>
                <p className="text-xs font-semibold text-slate-400 mt-1">
                  ID: {selectedUsuario.id}
                </p>
              </div>
              <Badge estado={selectedUsuario.estado} />
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-slate-100 dark:border-slate-800 flex flex-col gap-3">
              <p className="text-sm text-slate-600 dark:text-slate-300">
                <strong>Nombre Completo:</strong> {selectedUsuario.nombre}{' '}
                {selectedUsuario.apellido}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                <strong>Correo:</strong> {selectedUsuario.email}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                <strong>Rol:</strong> {selectedUsuario.rol.toUpperCase()}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                <strong>Coins:</strong>{' '}
                {parseFloat((selectedUsuario.saldo_coins as any) || 0).toFixed(1)}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                <strong>Verificado Facial:</strong>{' '}
                {selectedUsuario.verificado_facial ? 'Sí' : 'No'}
              </p>
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

export default UsuariosPage
