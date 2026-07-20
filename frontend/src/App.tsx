import React, { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import { useAuthStore } from './store/authStore'

const LoginPage = lazy(() => import('./pages/LoginPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const UsuariosPage = lazy(() => import('./pages/UsuariosPage'))
const ViajesPage = lazy(() => import('./pages/ViajesPage'))
const SimulacionPage = lazy(() => import('./pages/SimulacionPage'))
const ReportesPage = lazy(() => import('./pages/ReportesPage'))
const ConfiguracionPage = lazy(() => import('./pages/ConfiguracionPage'))
const PoliticasPage = lazy(() => import('./pages/PoliticasPage'))
const ReclamosPage = lazy(() => import('./pages/ReclamosPage'))

const PageLoader = () => (
  <div className="grid min-h-[240px] place-items-center" role="status" aria-live="polite">
    <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Cargando contenido...</span>
  </div>
)

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const usuario = useAuthStore((state) => state.usuario)

  if (!isAuthenticated || usuario?.rol !== 'admin') return <Navigate to="/login" replace />

  return <>{children}</>
}

const App: React.FC = () => (
  <BrowserRouter>
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
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
        <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
      </Routes>
    </Suspense>
  </BrowserRouter>
)

export default App
