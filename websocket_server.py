"""
WebSocket Server for Real-Time Updates
=======================================
Run this separately: python websocket_server.py
"""

import asyncio
import websockets
import json

# Store all connected clients
connected_clients = set()


async def handler(websocket):
    """Handle WebSocket connections (new API - no path parameter)"""
    # Register new client
    connected_clients.add(websocket)
    print(f"✅ Client connected. Total clients: {len(connected_clients)}")
    
    try:
        async for message in websocket:
            # Parse incoming message
            data = json.loads(message)
            print(f"📨 Received: {data}")
            
            # Broadcast to ALL connected clients (including sender)
            await broadcast(data)
            
    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected")
    finally:
        # Remove client on disconnect
        connected_clients.discard(websocket)
        print(f"📊 Remaining clients: {len(connected_clients)}")


async def broadcast(message):
    """Send message to all connected clients"""
    if connected_clients:
        message_json = json.dumps(message)
        # Send to all clients
        await asyncio.gather(
            *[client.send(message_json) for client in connected_clients],
            return_exceptions=True
        )
        print(f"📢 Broadcasted to {len(connected_clients)} client(s)")


async def main():
    """Start the WebSocket server"""
    async with websockets.serve(handler, "localhost", 8765):
        print("🚀 WebSocket Server started on ws://localhost:8765")
        print("   Waiting for connections...")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())