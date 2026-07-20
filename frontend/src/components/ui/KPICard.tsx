import React, { ReactNode } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface KPICardProps {
  titulo: string
  valor: string | number
  subtitulo?: string
  icono: ReactNode
  tendencia?: {
    valor: string
    tipo: 'sube' | 'baja'
  }
}

const KPICard: React.FC<KPICardProps> = ({ titulo, valor, subtitulo, icono, tendencia }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">{titulo}</span>
        <div className="w-12 h-12 rounded-xl bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400 flex items-center justify-center shadow-inner">
          {icono}
        </div>
      </div>

      <div className="mt-4 flex flex-col">
        <span className="text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight">
          {valor}
        </span>

        {subtitulo || tendencia ? (
          <div className="mt-2 flex items-center gap-2">
            {tendencia && (
              <span
                className={`flex items-center gap-1 text-xs font-bold px-1.5 py-0.5 rounded ${
                  tendencia.tipo === 'sube'
                    ? 'bg-emerald-100 dark:bg-emerald-950/20 text-emerald-600'
                    : 'bg-rose-100 dark:bg-rose-950/20 text-rose-600'
                }`}
              >
                {tendencia.tipo === 'sube' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {tendencia.valor}
              </span>
            )}
            {subtitulo && (
              <span className="text-xs font-medium text-slate-400 dark:text-slate-500">
                {subtitulo}
              </span>
            )}
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default KPICard
