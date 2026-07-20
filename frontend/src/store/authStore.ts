import { create } from 'zustand'
import { Usuario } from '../types'

interface AuthState {
  usuario: Usuario | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (usuario: Usuario, access: string, refresh: string) => void
  logout: () => void
  actualizarUsuario: (usuario: Usuario) => void
}

export const useAuthStore = create<AuthState>((set) => {
  // Inicialización desde localStorage para persistencia
  const savedUser = localStorage.getItem('apuradito_usuario')
  const savedAccess = localStorage.getItem('apuradito_access_token')
  const savedRefresh = localStorage.getItem('apuradito_refresh_token')

  return {
    usuario: savedUser ? JSON.parse(savedUser) : null,
    accessToken: savedAccess || null,
    refreshToken: savedRefresh || null,
    isAuthenticated: !!savedAccess,
    login: (usuario, access, refresh) => {
      localStorage.setItem('apuradito_usuario', JSON.stringify(usuario))
      localStorage.setItem('apuradito_access_token', access)
      localStorage.setItem('apuradito_refresh_token', refresh)
      set({ usuario, accessToken: access, refreshToken: refresh, isAuthenticated: true })
    },
    logout: () => {
      localStorage.removeItem('apuradito_usuario')
      localStorage.removeItem('apuradito_access_token')
      localStorage.removeItem('apuradito_refresh_token')
      set({ usuario: null, accessToken: null, refreshToken: null, isAuthenticated: false })
      window.location.href = '/login'
    },
    actualizarUsuario: (usuario) => {
      localStorage.setItem('apuradito_usuario', JSON.stringify(usuario))
      set({ usuario })
    }
  }
})
