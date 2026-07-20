import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/layout/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UsuariosPage from './pages/UsuariosPage'
import ConfiguracionPage from './pages/ConfiguracionPage'
import ReportesPage from './pages/ReportesPage'
import ReclamosPage from './pages/ReclamosPage'
import PoliticasPage from './pages/PoliticasPage'
import ViajesPage from './pages/ViajesPage'
import SimulacionPage from './pages/SimulacionPage'

// ProtectedRoute para verificar token JWT del Administrador
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const usuario = useAuthStore((state) => state.usuario)

  if (!isAuthenticated || usuario?.rol !== 'admin') {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Placeholder estético para páginas en desarrollo de las fases 2, 3 y 4
const PagePlaceholder: React.FC<{ title: string; desc: string }> = ({ title, desc }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 shadow-sm flex flex-col items-center justify-center min-h-[450px] text-center gap-4">
      <div className="w-16 h-16 rounded-2xl bg-violet-50 dark:bg-violet-950/30 text-violet-600 dark:text-violet-400 flex items-center justify-center text-2xl font-bold animate-bounce">
        🚀
      </div>
      <h3 className="text-xl font-extrabold text-slate-800 dark:text-white leading-tight">
        {title}
      </h3>
      <p className="text-sm font-medium text-slate-400 dark:text-slate-500 max-w-md">{desc}</p>
      <div className="mt-4 px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400">
        Próxima fase de implementación
      </div>
    </div>
  )
}

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* RUTA PUBLICA */}
        <Route path="/login" element={<LoginPage />} />

        {/* RUTAS PROTEGIDAS DEL ADMIN */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="dashboard" element={<DashboardPage />} />
                  <Route path="usuarios" element={<UsuariosPage />} />
                  <Route path="viajes" element={<ViajesPage />} />
                  <Route path="simulacion" element={<SimulacionPage />} />
                  <Route path="reportes" element={<ReportesPage />} />
                  <Route path="configuracion" element={<ConfiguracionPage />} />
                  <Route path="politicas" element={<PoliticasPage />} />
                  <Route path="reclamos" element={<ReclamosPage />} />
                  <Route path="*" element={<Navigate to="dashboard" replace />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* REDIRECCION POR DEFECTO */}
        <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
