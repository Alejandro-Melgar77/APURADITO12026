import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  AlertTriangle,
  FileBarChart2,
  FileText,
  LayoutDashboard,
  LogOut,
  Map,
  Play,
  Settings,
  Users
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const menuItems = [
  { name: 'Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard size={20} /> },
  { name: 'Gestionar usuarios', path: '/admin/usuarios', icon: <Users size={20} /> },
  { name: 'Supervisar viajes', path: '/admin/viajes', icon: <Map size={20} /> },
  { name: 'Simulador', path: '/admin/simulacion', icon: <Play size={20} /> },
  { name: 'Reportes', path: '/admin/reportes', icon: <FileBarChart2 size={20} /> },
  { name: 'Configuracion', path: '/admin/configuracion', icon: <Settings size={20} /> },
  { name: 'Politicas legales', path: '/admin/politicas', icon: <FileText size={20} /> },
  { name: 'Reclamos', path: '/admin/reclamos', icon: <AlertTriangle size={20} /> }
]

const activeStyle =
  'flex items-center gap-3 rounded-xl bg-violet-600 px-4 py-3 font-medium text-white shadow-md transition-all duration-200'
const inactiveStyle =
  'flex items-center gap-3 rounded-xl px-4 py-3 text-slate-500 transition-all duration-200 hover:bg-slate-100 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white'

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const logout = useAuthStore((state) => state.logout)

  return (
    <>
      {isOpen && (
        <button
          type="button"
          className="fixed inset-0 z-20 bg-slate-950/40 lg:hidden"
          aria-label="Cerrar menú"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed left-0 top-0 z-30 flex h-full w-[260px] -translate-x-full flex-col justify-between border-r border-slate-200 bg-white p-6 transition-transform duration-200 dark:border-slate-800 dark:bg-slate-900 lg:z-20 lg:translate-x-0 ${isOpen ? 'translate-x-0' : ''}`}
      >
        <div className="flex flex-col gap-8">
          <div className="flex items-center gap-3 px-2">
            <div className="h-11 w-11 overflow-hidden rounded-2xl shadow-md shadow-violet-500/30 ring-1 ring-violet-200 dark:ring-violet-400/30">
              <img src="/logo.png" alt="Apuradito" className="h-full w-full object-cover" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold leading-tight text-slate-800 dark:text-white">Apuradito</h1>
              <span className="text-xs font-semibold uppercase tracking-wider text-violet-600">Admin</span>
            </div>
          </div>

          <nav className="flex flex-col gap-1" aria-label="Navegación principal">
            <span className="mb-2 px-2 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500">
              Menú principal
            </span>
            {menuItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) => (isActive ? activeStyle : inactiveStyle)}
              >
                {item.icon}
                <span className="text-sm">{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-xl px-4 py-3 font-medium text-red-500 transition-all duration-200 hover:bg-red-50 dark:hover:bg-red-950/20"
        >
          <LogOut size={20} />
          <span className="text-sm">Cerrar sesión</span>
        </button>
      </aside>
    </>
  )
}

export default Sidebar
