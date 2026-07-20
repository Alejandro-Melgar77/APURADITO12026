import { create } from 'zustand'
import { api, getApiBaseURL } from '../services/api'

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
        api.defaults.baseURL = getApiBaseURL()

        return { env: nextEnv }
      })
    }
  }
})
