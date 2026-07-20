import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { api } from '../services/api'
import { Lock, Mail, Eye, EyeOff, ArrowRight } from 'lucide-react'

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loginStore = useAuthStore((state) => state.login)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await api.post('/api/v1/auth/login', { email, password })
      const { usuario, access_token, refresh_token } = response.data

      if (usuario.rol !== 'admin') {
        throw new Error('Acceso restringido. Solo cuentas de administrador autorizadas.')
      }

      loginStore(usuario, access_token, refresh_token)
      navigate('/admin/dashboard')
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Error de conexión. Verifique que el backend esté en ejecución.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen bg-slate-950 flex items-center justify-center p-4 transition-colors duration-200 bg-cover bg-center"
      style={{ backgroundImage: "linear-gradient(90deg, rgba(12, 7, 42, 0.94), rgba(37, 17, 89, 0.70)), url('/brand-routes.png')" }}
    >
      <div className="w-full max-w-[400px] bg-white/95 dark:bg-slate-950/90 backdrop-blur-xl border border-white/20 dark:border-violet-400/20 rounded-3xl p-8 shadow-2xl flex flex-col items-center">
        {/* LOGO DE APURADITO */}
        <div className="w-20 h-20 rounded-3xl overflow-hidden shadow-lg shadow-violet-500/35 mb-5 ring-1 ring-white/50">
          <img src="/logo.png" alt="Apuradito" className="w-full h-full object-cover" />
        </div>

        <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-tight">
          Bienvenido a Apuradito
        </h2>
        <p className="text-sm font-medium text-slate-400 dark:text-slate-500 mt-2 mb-8">
          Panel de administración y control operativo
        </p>

        {error && (
          <div className="w-full p-4 rounded-xl bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900/30 text-xs font-semibold mb-4 text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
          {/* EMAIL */}
          <div className="relative">
            <span className="absolute inset-y-0 left-4 flex items-center text-slate-400">
              <Mail size={18} />
            </span>
            <input
              type="email"
              placeholder="Correo electrónico"
              aria-label="Correo electrónico"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-2xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 focus:border-violet-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none text-sm transition-all duration-200 text-slate-800 dark:text-white"
            />
          </div>

          {/* PASSWORD */}
          <div className="relative">
            <span className="absolute inset-y-0 left-4 flex items-center text-slate-400">
              <Lock size={18} />
            </span>
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Contraseña"
              aria-label="Contraseña"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-12 pr-12 py-3 rounded-2xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 focus:border-violet-500 focus:bg-white dark:focus:bg-slate-900 focus:outline-none text-sm transition-all duration-200 text-slate-800 dark:text-white"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              aria-pressed={showPassword}
              className="absolute inset-y-0 right-4 flex items-center text-slate-400 hover:text-slate-600"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {/* BOTON DE ACCESO */}
          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3.5 rounded-2xl bg-violet-600 text-white font-semibold text-sm flex items-center justify-center gap-2 hover:bg-violet-700 shadow-md shadow-violet-500/20 active:scale-95 transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Ingresando...' : 'Ingresar al panel'}
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="w-full flex items-center justify-center my-6 gap-3">
          <div className="h-[1px] bg-slate-200 dark:bg-slate-800 flex-1"></div>
          <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 tracking-wider uppercase">
            o
          </span>
          <div className="h-[1px] bg-slate-200 dark:bg-slate-800 flex-1"></div>
        </div>

        {/* GOOGLE SIGN IN (SIMULADO EN ADMIN) */}
        <button
          onClick={() =>
            setError(
              'El acceso por Google de Firebase está restringido a la App Móvil en esta versión.'
            )
          }
          className="w-full py-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-200"
        >
          <img
            src="https://docs.kodular.io/guides/component-examples/google-sign-in/google.png"
            alt="Google logo"
            className="w-4 h-4 object-contain"
          />
          Continuar con Google
        </button>

        <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 mt-8">
          Acceso exclusivo para personal autorizado
        </span>
      </div>
    </div>
  )
}

export default LoginPage
