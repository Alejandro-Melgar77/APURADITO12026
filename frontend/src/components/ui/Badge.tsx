import React from 'react'

type EstadoUsuario = 'activo' | 'pendiente' | 'suspendido' | 'eliminado'

interface BadgeProps {
  estado: EstadoUsuario | string
  texto?: string
}

const Badge: React.FC<BadgeProps> = ({ estado, texto }) => {
  const label = texto || estado.charAt(0).toUpperCase() + estado.slice(1)

  let styles = 'bg-slate-100 text-slate-800'

  switch (estado) {
    case 'activo':
      styles =
        'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900/30'
      break
    case 'pendiente':
      styles =
        'bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-900/30'
      break
    case 'suspendido':
      styles =
        'bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900/30'
      break
    case 'eliminado':
      styles =
        'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50'
      break
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${styles}`}
    >
      {label}
    </span>
  )
}

export default Badge
