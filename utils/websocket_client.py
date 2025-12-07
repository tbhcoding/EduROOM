"""
WebSocket Client for Real-Time Updates
======================================
Connects to the WebSocket server and handles real-time messages
"""

import asyncio
import websockets
import json
import threading


class RealtimeClient:
    """WebSocket client for real-time updates"""
    
    def __init__(self, url="ws://localhost:8765"):
        self.url = url
        self.websocket = None
        self.connected = False
        self.callbacks = {}  # Event type -> callback function
        self.loop = None
        self.thread = None
    
    def on(self, event_type, callback):
        """Register a callback for an event type"""
        self.callbacks[event_type] = callback
    
    def connect(self):
        """Connect to WebSocket server in background thread"""
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def _run_loop(self):
        """Run the async event loop in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect_and_listen())
    
    async def _connect_and_listen(self):
        """Connect and listen for messages"""
        try:
            async with websockets.connect(self.url) as websocket:
                self.websocket = websocket
                self.connected = True
                print(f"✅ Connected to WebSocket server: {self.url}")
                
                # Listen for messages
                async for message in websocket:
                    await self._handle_message(message)
                    
        except ConnectionRefusedError:
            print("❌ Could not connect to WebSocket server. Is it running?")
            self.connected = False
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            self.connected = False
    
    async def _handle_message(self, message):
        """Handle incoming message"""
        try:
            data = json.loads(message)
            event_type = data.get("type", "unknown")
            
            # Call the registered callback
            if event_type in self.callbacks:
                self.callbacks[event_type](data)
            
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
    
    def send(self, event_type, payload=None):
        """Send a message to the server"""
        if self.connected and self.loop:
            message = {
                "type": event_type,
                "payload": payload or {}
            }
            asyncio.run_coroutine_threadsafe(
                self._send_async(json.dumps(message)),
                self.loop
            )
    
    async def _send_async(self, message):
        """Async send"""
        if self.websocket:
            await self.websocket.send(message)
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)


# Global client instance
realtime = RealtimeClient()