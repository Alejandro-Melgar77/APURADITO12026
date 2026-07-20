import { Zap, Globe } from 'lucide-react'
import { useEnvStore } from '../../store/envStore'
import './EnvToggle.css'

export default function EnvToggle() {
  const { env, toggleEnv } = useEnvStore()
  const isLocal = env === 'local'

  return (
    <button
      className={`env-toggle ${isLocal ? 'env-local' : 'env-online'}`}
      onClick={toggleEnv}
      title={isLocal ? 'Cambiar a entorno de producción' : 'Cambiar a entorno local'}
    >
      {isLocal ? <Zap size={14} /> : <Globe size={14} />}
      <span>{isLocal ? 'Local' : 'En línea'}</span>
    </button>
  )
}
