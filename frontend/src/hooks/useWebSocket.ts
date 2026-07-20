import { useEffect, useRef, useState, useCallback } from 'react'

interface UseWebSocketOptions {
  onMessage?: (data: any) => void
  onConnect?: () => void
  onDisconnect?: () => void
  reconnectInterval?: number
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const { onMessage, onConnect, onDisconnect, reconnectInterval = 3000 } = options

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          onMessage?.(data)
        } catch {
          setLastMessage(event.data)
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        onDisconnect?.()
        setTimeout(connect, reconnectInterval)
      }

      ws.onerror = () => {
        ws.close()
      }
    } catch {
      setTimeout(connect, reconnectInterval)
    }
  }, [url, onMessage, onConnect, onDisconnect, reconnectInterval])

  useEffect(() => {
    connect()
    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null // Prevents reconnect timeout loop on unmount
        wsRef.current.close()
      }
    }
  }, [connect])

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }, [])

  return { isConnected, lastMessage, send }
}
