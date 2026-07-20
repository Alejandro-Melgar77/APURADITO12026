import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Map,
  Settings,
  LogOut,
  Play,
  FileBarChart2,
  FileText,
  AlertTriangle,
  Car
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

const Sidebar: React.FC = () => {
  const logout = useAuthStore((state) => state.logout)

  const menuItems = [
    { name: 'Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard size={20} /> },
    { name: 'Gestionar Usuarios', path: '/admin/usuarios', icon: <Users size={20} /> },
    { name: 'Supervisar Viajes', path: '/admin/viajes', icon: <Map size={20} /> },
    { name: 'Simulador', path: '/admin/simulacion', icon: <Play size={20} /> },
    { name: 'Reportes', path: '/admin/reportes', icon: <FileBarChart2 size={20} /> },
    { name: 'Configuración', path: '/admin/configuracion', icon: <Settings size={20} /> },
    { name: 'Políticas Legales', path: '/admin/politicas', icon: <FileText size={20} /> },
    { name: 'Reclamos', path: '/admin/reclamos', icon: <AlertTriangle size={20} /> }
  ]

  const activeStyle =
    'flex items-center gap-3 px-4 py-3 rounded-xl bg-violet-600 text-white font-medium shadow-md transition-all duration-200'
  const inactiveStyle =
    'flex items-center gap-3 px-4 py-3 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-white transition-all duration-200'

  return (
    <aside className="fixed left-0 top-0 h-full w-[260px] border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col justify-between p-6 z-20">
      <div className="flex flex-col gap-8">
        {/* LOGO */}
        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 bg-violet-600 rounded-xl flex items-center justify-center text-white shadow-md shadow-violet-500/20">
            <Car size={22} className="animate-pulse" />
          </div>
          <div>
            <h1 className="font-extrabold text-lg text-slate-800 dark:text-white leading-tight">
              Apuradito
            </h1>
            <span className="text-xs font-semibold text-violet-600 tracking-wider uppercase">
              Admin
            </span>
          </div>
        </div>

        {/* MENU */}
        <nav className="flex flex-col gap-1">
          <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mb-2 px-2">
            Menú Principal
          </span>
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => (isActive ? activeStyle : inactiveStyle)}
            >
              {item.icon}
              <span className="text-sm">{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* CERRAR SESION */}
      <button
        onClick={logout}
        className="flex items-center gap-3 px-4 py-3 rounded-xl text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 font-medium transition-all duration-200 w-full"
      >
        <LogOut size={20} />
        <span className="text-sm">Cerrar Sesión</span>
      </button>
    </aside>
  )
}

export default Sidebar
