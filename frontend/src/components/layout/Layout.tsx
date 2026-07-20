import React from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-200">
      <Sidebar />
      <div className="pl-[260px]">
        <Header />
        <main className="pt-24 px-8 pb-12 min-h-screen">
          <div className="fade-in max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  )
}

export default Layout
