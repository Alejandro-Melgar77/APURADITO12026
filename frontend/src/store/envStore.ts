import { create } from 'zustand'
import { api } from '../services/api'

interface EnvState {
  env: 'local' | 'online'
  toggleEnv: () => void
}

export const useEnvStore = create<EnvState>((set) => {
  const savedEnv = (localStorage.getItem('apuradito_env') as 'local' | 'online') || 'local'

  return {
    env: savedEnv,
    toggleEnv: () => {
      set((state) => {
        const nextEnv = state.env === 'local' ? 'online' : 'local'
        localStorage.setItem('apuradito_env', nextEnv)

        // Actualizar la baseURL del cliente axios directamente al cambiar el switch
        if (nextEnv === 'local') {
          api.defaults.baseURL = 'http://localhost:8000'
        } else {
          api.defaults.baseURL =
            (import.meta.env.VITE_API_URL_PROD || import.meta.env.VITE_API_URL || 'https://apuradito-backend.onrender.com').replace(/\/$/, '')
        }

        return { env: nextEnv }
      })
    }
  }
})
