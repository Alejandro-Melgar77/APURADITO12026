import asyncio
import websockets
import json

async def test_ws():
    try:
        async with websockets.connect("ws://localhost:8000/ws/viajes") as ws:
            print("Connected to WS")
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                print("Received message type:", data.get("tipo"))
                if data.get("tipo") == "viajes_activos":
                    viajes = data.get("data", [])
                    print(f"Viajes count: {len(viajes)}")
                    if len(viajes) > 0:
                        print("Sample viaje:", viajes[0])
                    break
    except Exception as e:
        print("Error:", e)

asyncio.run(test_ws())
