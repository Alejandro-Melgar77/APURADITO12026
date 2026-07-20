import React, { useEffect, useState, useRef } from 'react'
import { Bell, Sun, Moon, Search, Laptop, Monitor } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useEnvStore } from '../../store/envStore'
import { api } from '../../services/api'

const Header: React.FC = () => {
  const usuario = useAuthStore((state) => state.usuario)
  const { env, toggleEnv } = useEnvStore()

  // Estado local para el tema
  const [theme, setTheme] = useState<'light' | 'dark'>(
    (localStorage.getItem('apuradito_theme') as 'light' | 'dark') || 'light'
  )

  const [notificaciones, setNotificaciones] = useState<any[]>([])
  const [showNotif, setShowNotif] = useState(false)
  const notifRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchNotif = async () => {
      try {
        const res = await api.get('/api/v1/notificaciones/')
        setNotificaciones(res.data.slice(0, 5))
      } catch (e) {
        console.error(e)
      }
    }
    fetchNotif()

    const interval = setInterval(fetchNotif, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotif(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark')
    } else {
      root.removeAttribute('data-theme')
    }
    localStorage.setItem('apuradito_theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  return (
    <header className="fixed top-0 right-0 h-16 left-[260px] bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-8 z-10 transition-colors duration-200">
      {/* Buscador */}
      <div className="relative w-72">
        <span className="absolute inset-y-0 left-3 flex items-center text-slate-400">
          <Search size={18} />
        </span>
        <input
          type="text"
          placeholder="Buscar usuarios, viajes..."
          className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border border-transparent focus:border-violet-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none text-sm transition-all duration-200 text-slate-800 dark:text-white"
        />
      </div>

      {/* Controles de barra superior */}
      <div className="flex items-center gap-6">
        {/* Toggle de Entorno (Local / En línea) */}
        <button
          onClick={toggleEnv}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
            env === 'local'
              ? 'bg-amber-100 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-900/50'
              : 'bg-emerald-100 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-900/50'
          }`}
        >
          {env === 'local' ? '⚡ Local' : '🌐 En línea'}
        </button>

        {/* Toggle Claro/Oscuro */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-violet-600 transition-colors duration-200"
          title="Cambiar tema claro/oscuro"
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        {/* Campanita Notificaciones */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setShowNotif(!showNotif)}
            className="relative cursor-pointer p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-violet-600 transition-colors duration-200"
          >
            <Bell size={18} />
            {notificaciones.some((n) => !n.leida) && (
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border border-white dark:border-slate-900"></span>
            )}
          </button>

          {showNotif && (
            <div className="absolute top-12 right-0 w-80 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl z-50 overflow-hidden">
              <div className="p-3 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
                <span className="font-bold text-sm text-slate-800 dark:text-white">
                  Notificaciones
                </span>
                <span className="text-xs text-slate-400">
                  {notificaciones.filter((n) => !n.leida).length} nuevas
                </span>
              </div>
              <div className="max-h-64 overflow-y-auto">
                {notificaciones.length === 0 ? (
                  <div className="p-4 text-center text-xs text-slate-400">
                    No hay notificaciones
                  </div>
                ) : (
                  notificaciones.map((n) => (
                    <div
                      key={n.id}
                      className={`p-3 border-b border-slate-100 dark:border-slate-800 text-xs ${!n.leida ? 'bg-violet-50 dark:bg-violet-900/20' : ''}`}
                    >
                      <p className="font-semibold text-slate-700 dark:text-slate-300">{n.titulo}</p>
                      <p className="text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                        {n.mensaje}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Perfil Admin */}
        <div className="flex items-center gap-3 pl-4 border-l border-slate-200 dark:border-slate-800">
          <div className="w-9 h-9 rounded-full bg-violet-100 dark:bg-violet-950 flex items-center justify-center text-violet-600 dark:text-violet-300 font-bold overflow-hidden shadow-inner">
            {usuario?.foto_perfil_url ? (
              <img
                src={usuario.foto_perfil_url}
                alt="Admin avatar"
                className="w-full h-full object-cover"
              />
            ) : (
              usuario?.nombre.substring(0, 1).toUpperCase() || 'A'
            )}
          </div>
          <div className="hidden md:flex flex-col text-left">
            <span className="text-sm font-semibold text-slate-800 dark:text-white leading-tight">
              {usuario ? `${usuario.nombre} ${usuario.apellido}` : 'Admin'}
            </span>
            <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-0.5">
              {usuario?.rol === 'admin' ? 'Superadmin' : 'Administrador'}
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
