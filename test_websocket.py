"""Quick test for WebSocket"""
import asyncio
import websockets

async def test():
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            await websocket.send('{"type": "test", "payload": {"msg": "Hello!"}}')
            print("✅ Message sent!")
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"✅ Received: {response}")
    except ConnectionRefusedError:
        print("❌ Server not running!")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test())
