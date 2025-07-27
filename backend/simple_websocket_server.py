#!/usr/bin/env python3
"""
Simple WebSocket Server
A robust WebSocket server for real-time data streaming
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWebSocketServer:
    """Simple WebSocket server for real-time data streaming"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.is_running = False
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        try:
            welcome_message = {
                'type': 'welcome',
                'message': 'Connected to Simple WebSocket Server',
                'timestamp': datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(welcome_message))
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
        
    async def unregister_client(self, websocket):
        """Unregister a client connection"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def send_to_client(self, websocket, message):
        """Send message to a specific client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
            await self.unregister_client(websocket)
    
    async def handle_client(self, websocket, path="/"):
        """Handle individual client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError:
                    await self.send_to_client(websocket, {
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    })
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await self.send_to_client(websocket, {
                        'type': 'error',
                        'message': str(e)
                    })
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def handle_message(self, websocket, data):
        """Handle incoming WebSocket messages"""
        message_type = data.get('type')
        logger.info(f"Received message type: {message_type}")
        
        if message_type == 'subscribe_ticks':
            await self.handle_subscribe_ticks(websocket, data)
        elif message_type == 'subscribe_candles':
            await self.handle_subscribe_candles(websocket, data)
        elif message_type == 'ping':
            await self.send_to_client(websocket, {
                'type': 'pong',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })
    
    async def handle_subscribe_ticks(self, websocket, data):
        """Handle tick subscription requests"""
        symbol = data.get('symbol', 'R_100')
        
        # Send confirmation immediately
        await self.send_to_client(websocket, {
            'type': 'subscription_confirmed',
            'symbol': symbol,
            'message': f'Subscribed to ticks for {symbol}'
        })
        
        # Send sample tick data
        sample_tick = {
            'type': 'tick',
            'symbol': symbol,
            'data': {
                'quote': 1125.50 + (random.random() - 0.5) * 10,
                'timestamp': datetime.utcnow().isoformat()
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.send_to_client(websocket, sample_tick)
        
        logger.info(f"Sent sample tick data for {symbol}")
    
    async def handle_subscribe_candles(self, websocket, data):
        """Handle candle subscription requests"""
        symbol = data.get('symbol', 'R_100')
        timeframe = int(data.get('timeframe', 60))  # Default 1 minute
        
        # Send confirmation immediately
        await self.send_to_client(websocket, {
            'type': 'subscription_confirmed',
            'symbol': symbol,
            'timeframe': timeframe,
            'message': f'Subscribed to candles for {symbol} with timeframe {timeframe}'
        })
        
        # Generate sample candle data
        sample_candles = []
        now = datetime.utcnow()
        base_price = 1125.50
        
        for i in range(20):
            candle_time = now - timedelta(minutes=i*5)
            price_change = (random.random() - 0.5) * 2
            open_price = base_price + price_change
            close_price = open_price + (random.random() - 0.5) * 1
            high_price = max(open_price, close_price) + random.random() * 0.5
            low_price = min(open_price, close_price) - random.random() * 0.5
            
            sample_candles.append({
                'timestamp': int(candle_time.timestamp()),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2)
            })
        
        message = {
            'type': 'candles',
            'symbol': symbol,
            'timeframe': timeframe,
            'data': sample_candles,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.send_to_client(websocket, message)
        
        logger.info(f"Sent {len(sample_candles)} sample candles for {symbol}")
    
    async def broadcast_sample_data(self):
        """Broadcast sample data to all clients"""
        while self.is_running:
            try:
                if self.clients:
                    # Send sample market update
                    sample_update = {
                        'type': 'market_update',
                        'symbol': 'R_100',
                        'data': {
                            'bias': 'bullish',
                            'trend': 'uptrend',
                            'strength': 'strong',
                            'price': 1125.50 + (random.random() - 0.5) * 5
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    # Send to all clients
                    for client in self.clients.copy():
                        await self.send_to_client(client, sample_update)
                    
                    logger.info(f"Broadcasted sample data to {len(self.clients)} clients")
                
                # Wait 10 seconds before next broadcast
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error broadcasting sample data: {e}")
                await asyncio.sleep(10)
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.is_running = True
        
        # Start the broadcast task
        broadcast_task = asyncio.create_task(self.broadcast_sample_data())
        
        # Start the WebSocket server with error handling
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        try:
            # Create a wrapper to handle the connection properly
            async def connection_handler(websocket):
                await self.handle_client(websocket, None)
                
            server = await websockets.serve(
                connection_handler,
                self.host,
                self.port
            )
            
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            
            try:
                await server.wait_closed()
            except KeyboardInterrupt:
                logger.info("WebSocket server shutting down...")
            finally:
                self.is_running = False
                broadcast_task.cancel()
                try:
                    await broadcast_task
                except asyncio.CancelledError:
                    pass
        except OSError as e:
            if "Address already in use" in str(e) or "only one usage of each socket address" in str(e):
                logger.warning(f"Port {self.port} is already in use. WebSocket server not started.")
                self.is_running = False
                broadcast_task.cancel()
                try:
                    await broadcast_task
                except asyncio.CancelledError:
                    pass
            else:
                raise e

class SimpleWebSocketManager:
    """Manager for simple WebSocket server"""
    
    def __init__(self):
        self.server = SimpleWebSocketServer()
        self.is_running = False
    
    async def start(self):
        """Start the WebSocket server"""
        if not self.is_running:
            self.is_running = True
            await self.server.start_server()
    
    def stop(self):
        """Stop the WebSocket server"""
        self.is_running = False
    
    def get_status(self):
        """Get WebSocket server status"""
        return {
            'is_running': self.is_running,
            'connected_clients': len(self.server.clients),
            'server_address': f"ws://{self.server.host}:{self.server.port}"
        }

# Example usage
if __name__ == "__main__":
    async def main():
        manager = SimpleWebSocketManager()
        await manager.start()
    
    asyncio.run(main()) 