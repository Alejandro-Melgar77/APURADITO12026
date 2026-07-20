import React from 'react'

export const SkeletonCard: React.FC = () => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm animate-pulse flex flex-col justify-between h-[140px]">
      <div className="flex items-center justify-between">
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-24"></div>
        <div className="w-12 h-12 rounded-xl bg-slate-200 dark:bg-slate-800"></div>
      </div>
      <div className="mt-4 flex flex-col gap-2">
        <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded w-32"></div>
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-20"></div>
      </div>
    </div>
  )
}

export const SkeletonRow: React.FC = () => {
  return (
    <tr className="animate-pulse">
      <td className="p-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-32"></div>
      </td>
      <td className="p-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-24"></div>
      </td>
      <td className="p-4">
        <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded-full w-20"></div>
      </td>
      <td className="p-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-16"></div>
      </td>
      <td className="p-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-12"></div>
      </td>
      <td className="p-4">
        <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded w-16"></div>
      </td>
    </tr>
  )
}

export const SkeletonChart: React.FC = () => {
  return (
    <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm animate-pulse h-[350px] flex flex-col gap-4">
      <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded w-48"></div>
      <div className="flex-1 bg-slate-100 dark:bg-slate-800/50 rounded-xl"></div>
    </div>
  )
}
