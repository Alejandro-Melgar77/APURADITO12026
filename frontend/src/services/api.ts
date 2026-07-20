import axios from 'axios'

const normalizeRemoteBaseURL = (value: string) => {
  const trimmed = value.trim().replace(/\/$/, '')
  if (/^https?:\/\//i.test(trimmed)) return trimmed
  if (trimmed.startsWith('//')) return `https:${trimmed}`
  return `https://${trimmed}`
}

export const getApiBaseURL = (selectedEnv?: string) => {
  const env = selectedEnv || localStorage.getItem('apuradito_env') || 'local'
  if (env === 'local') return 'http://localhost:8000'
  const remoteHost =
    import.meta.env.VITE_API_URL_PROD ||
    import.meta.env.VITE_API_URL ||
    'https://apuradito-backend.onrender.com'
  return normalizeRemoteBaseURL(remoteHost)
}

export const getWebSocketBaseURL = (selectedEnv?: string) =>
  getApiBaseURL(selectedEnv).replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')

export const api = axios.create({
  baseURL: getApiBaseURL(),
  headers: { 'Content-Type': 'application/json' }
})

// Interceptores para inyectar automáticamente el token JWT
api.interceptors.request.use(
  (config) => {
    // El entorno puede cambiar sin recargar la aplicación; resuélvelo antes de cada solicitud.
    config.baseURL = getApiBaseURL()
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
          `${getApiBaseURL()}/api/v1/auth/refresh`,
          null,
          { params: { refresh_token: refreshToken } }
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
