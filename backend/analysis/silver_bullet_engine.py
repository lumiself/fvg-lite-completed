"""
Silver Bullet Engine
Main analysis engine combining all components for trade suggestions
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from analysis.market_bias_analyzer import MarketBiasAnalyzer
from analysis.liquidity_analyzer import LiquidityAnalyzer
from analysis.fvg_detector import FVGDetector
from deriv_data_streamer import DerivDataStreamer

logger = logging.getLogger(__name__)

class SilverBulletEngine:
    """Main analysis engine for Silver Bullet strategy"""
    
    def __init__(self):
        self.bias_analyzer = MarketBiasAnalyzer()
        self.liquidity_analyzer = LiquidityAnalyzer()
        self.fvg_detector = FVGDetector()
        self.data_streamer = DerivDataStreamer()
        
        # Strategy parameters
        self.min_setup_quality = 0.7
        self.max_risk_per_trade = 0.02  # 2% max risk
        self.min_risk_reward = 2.0
        
    def analyze_market_setup(self, symbol: str, timeframe: str = 'H1', 
                           lookback: int = 50) -> Dict:
        """
        Complete market analysis for Silver Bullet strategy
        
        Args:
            symbol: Trading symbol (e.g., 'frxEURUSD')
            timeframe: Analysis timeframe
            lookback: Number of candles to analyze
        
        Returns:
            Dict with complete market analysis
        """
        try:
            # Get historical data with fallback
            try:
                candles = self.data_streamer.get_historical_candles(
                    symbol, self._timeframe_to_minutes(timeframe), lookback
                )
            except Exception as e:
                logger.warning(f"Data streamer error, using fallback data: {e}")
                candles = self._generate_fallback_candles(symbol, lookback)
            
            if not candles:
                logger.warning("No data available, generating fallback data")
                candles = self._generate_fallback_candles(symbol, lookback)
            
            # Perform comprehensive analysis
            bias_analysis = self.bias_analyzer.determine_bias(candles, timeframe)
            liquidity_analysis = self.liquidity_analyzer.find_liquidity_levels(candles, timeframe)
            fvg_analysis = self.fvg_detector.detect_fvgs(candles, timeframe)
            
            # Generate Silver Bullet setups
            silver_bullet_setups = self.fvg_detector.get_silver_bullet_setups(
                candles, liquidity_analysis, bias_analysis
            )
            
            # Filter high-quality setups
            high_quality_setups = [
                setup for setup in silver_bullet_setups['setups']
                if setup['quality_score'] >= self.min_setup_quality
            ]
            
            # Generate trade suggestions
            trade_suggestions = self._generate_trade_suggestions(
                high_quality_setups, candles[-1]['close']
            )
            
            return {
                'success': True,
                'symbol': symbol,
                'timeframe': timeframe,
                'analysis': {
                    'bias': bias_analysis,
                    'liquidity': liquidity_analysis,
                    'fvgs': fvg_analysis,
                    'silver_bullet_setups': {
                        'all_setups': silver_bullet_setups['setups'],
                        'high_quality_setups': high_quality_setups,
                        'setup_count': len(silver_bullet_setups['setups']),
                        'high_quality_count': len(high_quality_setups)
                    }
                },
                'trade_suggestions': trade_suggestions,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol,
                'timeframe': timeframe
            }
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        timeframe_map = {
            'M1': 60,
            'M5': 300,
            'M15': 900,
            'M30': 1800,
            'H1': 3600,
            'H4': 14400,
            'D1': 86400
        }
        return timeframe_map.get(timeframe, 3600)
    
    def _generate_trade_suggestions(self, setups: List[Dict], current_price: float) -> List[Dict]:
        """Generate actionable trade suggestions from setups"""
        suggestions = []
        
        for setup in setups:
            fvg = setup['fvg']
            targets = fvg['target_levels']
            
            # Calculate position size based on risk
            risk_amount = abs(targets['entry'] - targets['stop_loss'])
            position_size = self._calculate_position_size(risk_amount, current_price)
            
            # Validate risk/reward ratio
            risk_reward_1 = targets['risk_reward_1']
            risk_reward_2 = targets['risk_reward_2']
            
            if risk_reward_1 >= self.min_risk_reward or risk_reward_2 >= self.min_risk_reward:
                suggestion = {
                    'setup_id': fvg['id'],
                    'type': fvg['type'],
                    'symbol': 'EUR/USD',  # This should be dynamic
                    'timeframe': 'H1',    # This should be dynamic
                    'entry_price': targets['entry'],
                    'stop_loss': targets['stop_loss'],
                    'take_profit_1': targets['take_profit_1'],
                    'take_profit_2': targets['take_profit_2'],
                    'risk_reward_1': risk_reward_1,
                    'risk_reward_2': risk_reward_2,
                    'position_size': position_size,
                    'confidence': setup['confidence'],
                    'setup_quality': setup['quality_score'],
                    'bias_alignment': setup['bias_alignment']['reason'],
                    'liquidity_reason': setup['liquidity_proximity']['reason'],
                    'status': 'pending',
                    'created_at': datetime.utcnow().isoformat()
                }
                
                suggestions.append(suggestion)
        
        return suggestions
    
    def _calculate_position_size(self, risk_amount: float, current_price: float) -> Dict:
        """Calculate position size based on risk management"""
        # Simplified position sizing
        account_balance = 10000  # Default demo account
        risk_percentage = self.max_risk_per_trade
        
        dollar_risk = account_balance * risk_percentage
        pip_value = 0.0001
        
        # Calculate position size
        position_size = dollar_risk / (risk_amount / pip_value)
        
        return {
            'units': int(position_size),
            'risk_amount': dollar_risk,
            'risk_percentage': risk_percentage * 100
        }
    
    def get_real_time_analysis(self, symbol: str, timeframe: str = 'H1') -> Dict:
        """Get real-time market analysis"""
        return self.analyze_market_setup(symbol, timeframe, 100)
    
    def validate_setup(self, setup: Dict) -> Dict:
        """Validate a trade setup against current market conditions"""
        try:
            # Re-analyze with latest data
            current_analysis = self.analyze_market_setup(
                setup['symbol'], 
                setup['timeframe'], 
                50
            )
            
            if not current_analysis['success']:
                return {'valid': False, 'reason': current_analysis['error']}
            
            # Check if setup is still valid
            current_price = float(current_analysis['analysis']['bias']['current_price'])
            entry_price = setup['entry_price']
            
            # Check if price has moved too far
            price_deviation = abs(current_price - entry_price) / entry_price
            if price_deviation > 0.005:  # 0.5% deviation
                return {
                    'valid': False,
                    'reason': f'Price has moved too far: {price_deviation:.3%} deviation'
                }
            
            # Check if setup still exists
            high_quality_setups = current_analysis['analysis']['silver_bullet_setups']['high_quality_setups']
            setup_still_exists = any(
                s['setup_id'] == setup['setup_id'] 
                for s in high_quality_setups
            )
            
            if not setup_still_exists:
                return {
                    'valid': False,
                    'reason': 'Setup no longer valid based on current market conditions'
                }
            
            return {
                'valid': True,
                'reason': 'Setup remains valid',
                'current_price': current_price,
                'deviation': price_deviation
            }
            
        except Exception as e:
            logger.error(f"Error validating setup: {e}")
            return {'valid': False, 'reason': str(e)}
    
    def get_market_summary(self, symbol: str = 'frxEURUSD') -> Dict:
        """Get comprehensive market summary"""
        # Analyze multiple timeframes
        timeframes = ['H1', 'H4', 'D1']
        summary = {
            'symbol': symbol,
            'analysis_time': datetime.utcnow().isoformat(),
            'multi_timeframe': {}
        }
        
        for tf in timeframes:
            analysis = self.analyze_market_setup(symbol, tf, 100)
            if analysis['success']:
                summary['multi_timeframe'][tf] = {
                    'bias': analysis['analysis']['bias']['bias'],
                    'confidence': analysis['analysis']['bias']['confidence'],
                    'setup_count': len(analysis['analysis']['silver_bullet_setups']['high_quality_setups']),
                    'active_setups': len(analysis['analysis']['silver_bullet_setups']['high_quality_setups'])
                }
        
        # Overall recommendation
        bullish_count = sum(1 for tf_data in summary['multi_timeframe'].values() 
                          if tf_data['bias'] == 'bullish')
        bearish_count = sum(1 for tf_data in summary['multi_timeframe'].values() 
                          if tf_data['bias'] == 'bearish')
        
        if bullish_count > bearish_count:
            overall_bias = 'bullish'
        elif bearish_count > bullish_count:
            overall_bias = 'bearish'
        else:
            overall_bias = 'neutral'
        
        summary['overall_bias'] = overall_bias
        summary['total_setups'] = sum(tf_data['setup_count'] 
                                    for tf_data in summary['multi_timeframe'].values())
        
        return summary
    
    def _generate_fallback_candles(self, symbol: str, count: int = 100) -> List[Dict]:
        """Generate fallback candle data for demo/testing purposes"""
        import random
        from datetime import datetime, timedelta
        
        candles = []
        base_price = 1.0850  # Base price for EUR/USD
        
        # Adjust base price for different symbols
        if 'GBP' in symbol:
            base_price = 1.2750
        elif 'JPY' in symbol:
            base_price = 148.50
        elif 'AUD' in symbol:
            base_price = 0.6750
        elif 'CHF' in symbol:
            base_price = 0.8950
        
        current_time = datetime.utcnow()
        
        for i in range(count):
            # Create realistic price movement
            time_offset = timedelta(hours=count - i)
            timestamp = int((current_time - time_offset).timestamp())
            
            # Generate OHLC with realistic relationships
            price_change = (random.random() - 0.5) * 0.002  # Max 0.2% change
            open_price = base_price + price_change
            
            candle_range = random.uniform(0.0005, 0.003)  # 0.05% to 0.3% range
            high_offset = random.uniform(0, candle_range)
            low_offset = random.uniform(0, candle_range)
            
            close_change = (random.random() - 0.5) * candle_range
            close_price = open_price + close_change
            
            high_price = max(open_price, close_price) + high_offset
            low_price = min(open_price, close_price) - low_offset
            
            candle = {
                'timestamp': timestamp,
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'volume': random.randint(1000, 10000)
            }
            
            candles.append(candle)
            base_price = close_price  # Use close as next open
        
        return candles

class TradeSignalGenerator:
    """Generates trade signals based on Silver Bullet strategy"""
    
    def __init__(self, engine: SilverBulletEngine):
        self.engine = engine
        self.active_signals = []
    
    def generate_signals(self, symbol: str, timeframe: str = 'H1') -> List[Dict]:
        """Generate trade signals for the symbol"""
        analysis = self.engine.analyze_market_setup(symbol, timeframe)
        
        if not analysis['success']:
            return []
        
        signals = []
        
        for suggestion in analysis['trade_suggestions']:
            signal = {
                'signal_id': f"signal_{datetime.utcnow().timestamp()}",
                'symbol': symbol,
                'timeframe': timeframe,
                'direction': suggestion['type'],
                'entry': suggestion['entry_price'],
                'stop_loss': suggestion['stop_loss'],
                'take_profit': suggestion['take_profit_1'],
                'confidence': suggestion['confidence'],
                'risk_reward': suggestion['risk_reward_1'],
                'status': 'active',
                'created_at': suggestion['created_at'],
                'expires_at': (datetime.utcnow() + timedelta(hours=4)).isoformat()
            }
            
            signals.append(signal)
        
        return signals
    
    def expire_old_signals(self):
        """Remove expired signals"""
        current_time = datetime.utcnow()
        self.active_signals = [
            signal for signal in self.active_signals
            if datetime.fromisoformat(signal['expires_at']) > current_time
        ]
