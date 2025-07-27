"""
WebSocket Server
Real-time WebSocket server for live data streaming and signal broadcasting
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
import websockets
from deriv_data_streamer import DerivDataStreamer
from analysis.silver_bullet_engine import SilverBulletEngine
from services.signal_scheduler import SignalSchedulerService

logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket server for real-time data and analysis"""
    
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.data_streamer = DerivDataStreamer()
        self.engine = SilverBulletEngine()
        self.signal_scheduler = None
        self.is_running = False
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        try:
            welcome_message = {
                'type': 'welcome',
                'message': 'Connected to FVG Silver Bullet Trading Assistant',
                'timestamp': datetime.utcnow().isoformat(),
                'server_version': '1.0.0'
            }
            await websocket.send(json.dumps(welcome_message))
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
        
    async def unregister_client(self, websocket):
        """Unregister a client connection"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def send_to_all_clients(self, message):
        """Send message to all connected clients"""
        if self.clients:
            # Create a list of send coroutines with better error handling
            disconnected_clients = []
            for client in self.clients.copy():
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.append(client)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.clients.discard(client)
        
    async def handle_client(self, websocket, path=None):
        """Handle individual client connection"""
        # Handle both old (websocket, path) and new (connection) signatures
        await self.register_client(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    try:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': str(e)
                        }))
                    except websockets.exceptions.ConnectionClosed:
                        logger.info("Client disconnected during error handling")
                    except Exception as send_error:
                        logger.error(f"Error sending error message: {send_error}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        finally:
            await self.unregister_client(websocket)
    
    async def handle_message(self, websocket, data):
        """Handle incoming WebSocket messages"""
        message_type = data.get('type')
        
        if message_type == 'subscribe_ticks':
            await self.handle_subscribe_ticks(websocket, data)
        elif message_type == 'subscribe_candles':
            await self.handle_subscribe_candles(websocket, data)
        elif message_type == 'get_analysis':
            await self.handle_get_analysis(websocket, data)
        elif message_type == 'ping':
            await websocket.send(json.dumps({'type': 'pong', 'timestamp': datetime.utcnow().isoformat()}))
        else:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            }))
    
    async def handle_subscribe_ticks(self, websocket, data):
        """Handle tick subscription requests"""
        symbol = data.get('symbol', 'frxEURUSD')
        
        # Send confirmation immediately
        await websocket.send(json.dumps({
            'type': 'subscription_confirmed',
            'symbol': symbol,
            'message': f'Subscribed to ticks for {symbol}'
        }))
        
        # Try to subscribe to real data if connected
        if self.data_streamer.is_connected:
            async def tick_handler(tick):
                message = {
                    'type': 'tick',
                    'symbol': symbol,
                    'data': tick,
                    'timestamp': datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(message))
            
            await self.data_streamer.subscribe_to_ticks(symbol, tick_handler)
        else:
            # Send sample data if not connected to real API
            logger.info(f"Data streamer not connected, sending sample tick data for {symbol}")
            sample_tick = {
                'type': 'tick',
                'symbol': symbol,
                'data': {
                    'quote': 1125.50 + (random.random() - 0.5) * 10,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(sample_tick))
    
    async def handle_subscribe_candles(self, websocket, data):
        """Handle candle subscription requests"""
        symbol = data.get('symbol', 'frxEURUSD')
        timeframe = int(data.get('timeframe', 3600))  # Default 1 hour
        
        # Send confirmation immediately
        await websocket.send(json.dumps({
            'type': 'subscription_confirmed',
            'symbol': symbol,
            'timeframe': timeframe,
            'message': f'Subscribed to candles for {symbol} with timeframe {timeframe}'
        }))
        
        # Try to subscribe to real data if connected
        if self.data_streamer.is_connected:
            async def candle_handler(candles):
                message = {
                    'type': 'candles',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'data': candles,
                    'timestamp': datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(message))
            
            await self.data_streamer.subscribe_to_candles(symbol, timeframe, candle_handler)
        else:
            # Send sample data if not connected to real API
            logger.info(f"Data streamer not connected, sending sample candle data for {symbol}")
            sample_candles = []
            now = datetime.utcnow()
            for i in range(10):
                candle_time = now - timedelta(minutes=i*5)
                sample_candles.append({
                    'timestamp': candle_time.isoformat(),
                    'open': 1125.50 + (i * 0.1),
                    'high': 1125.50 + (i * 0.1) + 0.5,
                    'low': 1125.50 + (i * 0.1) - 0.3,
                    'close': 1125.50 + (i * 0.1) + 0.2
                })
            
            message = {
                'type': 'candles',
                'symbol': symbol,
                'timeframe': timeframe,
                'data': sample_candles,
                'timestamp': datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(message))
    
    async def handle_get_analysis(self, websocket, data):
        """Handle analysis requests"""
        symbol = data.get('symbol', 'frxEURUSD')
        timeframe = data.get('timeframe', 'H1')
        
        try:
            analysis = self.engine.analyze_market_setup(symbol, timeframe, 100)
            
            message = {
                'type': 'analysis',
                'symbol': symbol,
                'timeframe': timeframe,
                'data': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(message))
            
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Analysis error: {str(e)}'
            }))
    
    async def broadcast_analysis_updates(self):
        """Broadcast periodic analysis updates to all clients"""
        while self.is_running:
            try:
                # Get analysis for common symbols
                symbols = ['frxEURUSD', 'frxGBPUSD', 'frxUSDJPY']
                
                for symbol in symbols:
                    analysis = self.engine.get_market_summary(symbol)
                    
                    message = {
                        'type': 'market_update',
                        'symbol': symbol,
                        'data': analysis,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    await self.send_to_all_clients(message)
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error broadcasting updates: {e}")
                await asyncio.sleep(30)
    
    async def start_server(self):
        """Start the WebSocket server with integrated signal service"""
        self.is_running = True
        
        # Initialize signal scheduler
        self.signal_scheduler = SignalSchedulerService(self)
        
        # Try to connect to Deriv API (but don't fail if it doesn't work)
        try:
            if await self.data_streamer.connect():
                logger.info("Connected to Deriv API successfully")
            else:
                logger.warning("Failed to connect to Deriv API, but continuing with WebSocket server")
        except Exception as e:
            logger.error(f"Error connecting to Deriv API: {e}")
        
        # Start the signal scheduler
        try:
            asyncio.create_task(self.signal_scheduler.start())
            logger.info("Signal scheduler started successfully")
        except Exception as e:
            logger.error(f"Error starting signal scheduler: {e}")
        
        # Start the broadcast task
        broadcast_task = asyncio.create_task(self.broadcast_analysis_updates())
        
        # Start the WebSocket server with proper handler
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
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
            if self.signal_scheduler:
                await self.signal_scheduler.stop()
            try:
                await self.data_streamer.disconnect()
            except:
                pass

class WebSocketManager:
    """Manager for WebSocket connections and data streaming"""
    
    def __init__(self):
        self.server = WebSocketServer()
        self.is_running = False
    
    async def start(self):
        """Start the WebSocket server with integrated signal service"""
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
            'server_address': f"ws://{self.server.host}:{self.server.port}",
            'signal_scheduler_running': self.server.signal_scheduler is not None and self.server.signal_scheduler.is_running
        }

# WebSocket endpoints for the main Flask app
async def websocket_handler(websocket, path):
    """Handler for WebSocket connections from Flask"""
    server = WebSocketServer()
    await server.handle_client(websocket, path)

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Start WebSocket server with integrated signal service
    manager = WebSocketManager()
    asyncio.run(manager.start())
