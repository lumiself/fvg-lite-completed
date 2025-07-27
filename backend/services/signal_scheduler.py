"""
Signal Scheduler Service
Background service for real-time signal generation and broadcasting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import websockets
from analysis.live_signal_generator import LiveSignalGenerator
from deriv_data_streamer import DerivDataStreamer

logger = logging.getLogger(__name__)

class SignalSchedulerService:
    """Background service for real-time signal generation"""
    
    def __init__(self, websocket_server=None):
        self.generator = LiveSignalGenerator()
        self.data_streamer = DerivDataStreamer()
        self.websocket_server = websocket_server
        self.is_running = False
        self.monitored_symbols = [
            'frxEURUSD',
            'frxGBPUSD', 
            'frxUSDJPY',
            'frxAUDUSD',
            'frxUSDCHF'
        ]
        self.monitored_timeframes = ['M15', 'H1', 'H4']
        self.check_interval = 30  # seconds
        
    async def start(self):
        """Start the signal scheduler service"""
        self.is_running = True
        logger.info("Starting Signal Scheduler Service...")
        
        # Connect to data streamer
        try:
            if await self.data_streamer.connect():
                logger.info("Connected to Deriv API for signal generation")
            else:
                logger.warning("Using demo data for signal generation")
        except Exception as e:
            logger.error(f"Error connecting to Deriv API: {e}")
            logger.warning("Using demo data for signal generation")
        
        # Start the main loop
        await self._run_signal_loop()
    
    async def stop(self):
        """Stop the signal scheduler service"""
        self.is_running = False
        logger.info("Stopping Signal Scheduler Service...")
        try:
            await self.data_streamer.disconnect()
        except:
            pass
    
    async def _run_signal_loop(self):
        """Main loop for signal generation and broadcasting"""
        while self.is_running:
            try:
                await self._process_all_symbols()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in signal loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _process_all_symbols(self):
        """Process all monitored symbols and timeframes"""
        for symbol in self.monitored_symbols:
            for timeframe in self.monitored_timeframes:
                try:
                    await self._process_symbol_timeframe(symbol, timeframe)
                except Exception as e:
                    logger.error(f"Error processing {symbol} {timeframe}: {e}")
    
    async def _process_symbol_timeframe(self, symbol: str, timeframe: str):
        """Process a single symbol/timeframe combination"""
        # Get current price for exit checking
        try:
            current_price = await self._get_current_price(symbol)
            if current_price is None:
                return
        except:
            # Use demo price if API fails
            current_price = 1.0850  # Demo price for EUR/USD
    
        # Check existing signals for exit conditions
        await self._check_exit_conditions(symbol, current_price)
        
        # Generate new signals
        new_signals = self.generator.generate_educational_signals(symbol, timeframe)
        
        # Filter out duplicates and add new signals
        for signal in new_signals:
            if not self._is_duplicate_signal(signal):
                self.generator.add_signal(signal)
                await self._broadcast_signal(signal)
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        try:
            # Try to get real-time price
            ticks = await self.data_streamer.get_latest_ticks(symbol, 1)
            if ticks:
                return float(ticks[0]['quote'])
            
            # Fallback to historical data (sync, do NOT await)
            candles = self.data_streamer.get_historical_candles(
                symbol, 60, 1  # 1 minute timeframe, 1 candle
            )
            if candles:
                return float(candles[0]['close'])
                
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
        
        return None
    
    async def _check_exit_conditions(self, symbol: str, current_price: float):
        """Check all active signals for exit conditions"""
        active_signals = self.generator.get_active_signals(symbol)
        
        for signal in active_signals:
            exit_condition = self.generator.check_exit_conditions(signal, current_price)
            if exit_condition:
                # Close the signal
                success = self.generator.close_signal(
                    exit_condition['signal_id'], 
                    exit_condition
                )
                
                if success:
                    # Create exit signal for broadcasting
                    exit_signal = {
                        'type': 'signal_feed',
                        'signal_type': 'exit',
                        'symbol': signal['symbol'],
                        'timeframe': signal['timeframe'],
                        'signal_id': signal['signal_id'],
                        'exit_price': exit_condition['exit_price'],
                        'pips_gained': exit_condition['pips_gained'],
                        'exit_reason': exit_condition['reason'],
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    await self._broadcast_signal(exit_signal)
    
    def _is_duplicate_signal(self, new_signal: Dict) -> bool:
        """Check if this signal is a duplicate of an existing one"""
        symbol = new_signal['symbol']
        timeframe = new_signal['timeframe']
        
        active_signals = self.generator.get_active_signals(symbol)
        
        for existing_signal in active_signals:
            if (existing_signal['timeframe'] == timeframe and
                abs(existing_signal['entry'] - new_signal['entry']) < 0.001 and
                existing_signal['status'] == 'active'):
                return True
        
        return False
    
    async def _broadcast_signal(self, signal: Dict):
        """Broadcast signal to all connected WebSocket clients"""
        if self.websocket_server:
            try:
                await self.websocket_server.send_to_all_clients(signal)
                logger.info(f"Broadcasted signal: {signal.get('type', 'signal_feed')} for {signal.get('symbol', 'unknown')}")
            except Exception as e:
                logger.error(f"Error broadcasting signal: {e}")
    
    def get_service_status(self) -> Dict:
        """Get current service status"""
        return {
            'is_running': self.is_running,
            'monitored_symbols': self.monitored_symbols,
            'monitored_timeframes': self.monitored_timeframes,
            'check_interval': self.check_interval,
            'active_signals_count': len(self.generator.get_active_signals()),
            'closed_signals_count': len(self.generator.closed_signals),
            'session_summary': self.generator.get_session_summary()
        }
    
    async def get_session_summary(self) -> Dict:
        """Get current session summary"""
        return self.generator.get_session_summary()

# Global instance
signal_scheduler = SignalSchedulerService()

async def start_signal_service(websocket_server=None):
    """Start the signal scheduler service"""
    if websocket_server:
        signal_scheduler.websocket_server = websocket_server
    await signal_scheduler.start()

async def stop_signal_service():
    """Stop the signal scheduler service"""
    await signal_scheduler.stop()

def get_signal_service_status():
    """Get signal service status"""
    return signal_scheduler.get_service_status()

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        await start
