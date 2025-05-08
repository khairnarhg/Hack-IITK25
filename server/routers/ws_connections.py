from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected: {websocket.client}")
        # Send a welcome message once connected.
        await websocket.send_text("WebSocket connection established")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket disconnected: {websocket.client}")

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
            print(f"Sent message to {websocket.client}: {message}")
        except Exception as e:
            print(f"Error sending message to {websocket.client}: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        print(f"Broadcasting message to {len(self.active_connections)} connection(s): {message}")
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
                print(f"Message sent to {connection.client}")
            except (RuntimeError, WebSocketDisconnect) as e:
                print(f"Error sending message to {connection.client}: {e}")
                self.disconnect(connection)
            except Exception as e:
                print(f"Unexpected error with {connection.client}: {e}")
                self.disconnect(connection)

# Separate managers for logs and alerts:
logs_manager = ConnectionManager()
alerts_manager = ConnectionManager()

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await logs_manager.connect(websocket)
    try:
        # Keep the connection open without waiting for client messages.
        while True:
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logs_manager.disconnect(websocket)

@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await alerts_manager.connect(websocket)
    try:
        # Keep the connection open without waiting for client messages.
        while True:
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        alerts_manager.disconnect(websocket)
