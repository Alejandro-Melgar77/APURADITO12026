import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'
import './Pagination.css'

interface PaginationProps {
  paginaActual: number
  totalPaginas: number
  onCambiarPagina: (pagina: number) => void
  porPagina?: number
  total?: number
}

export default function Pagination({
  paginaActual,
  totalPaginas,
  onCambiarPagina,
  porPagina,
  total
}: PaginationProps) {
  if (totalPaginas <= 1) return null

  const getPageNumbers = () => {
    const pages: (number | '...')[] = []
    const delta = 2

    if (totalPaginas <= 7) {
      for (let i = 1; i <= totalPaginas; i++) pages.push(i)
    } else {
      pages.push(1)
      if (paginaActual - delta > 2) pages.push('...')
      for (
        let i = Math.max(2, paginaActual - delta);
        i <= Math.min(totalPaginas - 1, paginaActual + delta);
        i++
      ) {
        pages.push(i)
      }
      if (paginaActual + delta < totalPaginas - 1) pages.push('...')
      pages.push(totalPaginas)
    }

    return pages
  }

  const inicio = porPagina && total ? (paginaActual - 1) * porPagina + 1 : null
  const fin = porPagina && total ? Math.min(paginaActual * porPagina, total) : null

  return (
    <div className="pagination-wrapper">
      {inicio !== null && fin !== null && total !== undefined && (
        <span className="pagination-info">
          Mostrando {inicio}–{fin} de {total} registros
        </span>
      )}
      <div className="pagination">
        <button
          className="page-btn"
          onClick={() => onCambiarPagina(1)}
          disabled={paginaActual === 1}
          title="Primera página"
        >
          <ChevronsLeft size={16} />
        </button>
        <button
          className="page-btn"
          onClick={() => onCambiarPagina(paginaActual - 1)}
          disabled={paginaActual === 1}
          title="Página anterior"
        >
          <ChevronLeft size={16} />
        </button>

        {getPageNumbers().map((page, idx) =>
          page === '...' ? (
            <span key={`dots-${idx}`} className="page-dots">
              …
            </span>
          ) : (
            <button
              key={page}
              className={`page-btn ${paginaActual === page ? 'active' : ''}`}
              onClick={() => onCambiarPagina(page as number)}
            >
              {page}
            </button>
          )
        )}

        <button
          className="page-btn"
          onClick={() => onCambiarPagina(paginaActual + 1)}
          disabled={paginaActual === totalPaginas}
          title="Página siguiente"
        >
          <ChevronRight size={16} />
        </button>
        <button
          className="page-btn"
          onClick={() => onCambiarPagina(totalPaginas)}
          disabled={paginaActual === totalPaginas}
          title="Última página"
        >
          <ChevronsRight size={16} />
        </button>
      </div>
    </div>
  )
}
