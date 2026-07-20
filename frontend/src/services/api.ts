import axios from 'axios'

const getBaseURL = () => {
  const env = localStorage.getItem('apuradito_env') || 'local'
  if (env === 'local') return 'http://localhost:8000'
  return (import.meta.env.VITE_API_URL_PROD || import.meta.env.VITE_API_URL || 'https://apuradito-backend.onrender.com').replace(/\/$/, '')
}

export const api = axios.create({
  baseURL: getBaseURL(),
  headers: { 'Content-Type': 'application/json' }
})

// Interceptores para inyectar automáticamente el token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('apuradito_access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor de respuesta para renovar el token si expira
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('apuradito_refresh_token')
        if (!refreshToken) throw new Error('No hay refresh token')

        const response = await axios.post(
          `${getBaseURL()}/api/v1/auth/refresh?refresh_token=${refreshToken}`
        )
        const { access_token, refresh_token: new_refresh_token } = response.data

        localStorage.setItem('apuradito_access_token', access_token)
        localStorage.setItem('apuradito_refresh_token', new_refresh_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (err) {
        // Redirigir al login si falla la renovación
        localStorage.removeItem('apuradito_access_token')
        localStorage.removeItem('apuradito_refresh_token')
        localStorage.removeItem('apuradito_usuario')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
