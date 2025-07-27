"""
Market Bias Analyzer
Analyzes market direction using EMA-based bias determination
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketBiasAnalyzer:
    """Analyzes market bias using EMA indicators"""
    
    def __init__(self):
        self.default_ema_periods = {
            'H1': 200,   # 200-period EMA on 1H
            'H4': 50,    # 50-period EMA on 4H
            'D1': 20     # 20-period EMA on Daily
        }
        
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
            
        prices_array = np.array(prices)
        multiplier = 2 / (period + 1)
        
        ema = prices_array[0]
        for price in prices_array[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            
        return float(ema)
    
    def determine_bias(self, candles: List[Dict], timeframe: str = 'H1') -> Dict:
        """
        Determine market bias based on EMA analysis
        
        Args:
            candles: List of candlestick data
            timeframe: Analysis timeframe ('H1', 'H4', 'D1')
        
        Returns:
            Dict with bias information
        """
        if not candles:
            return {
                'bias': 'neutral',
                'confidence': 0.0,
                'ema_value': 0.0,
                'current_price': 0.0,
                'timeframe': timeframe,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Extract closing prices
        closes = [float(candle['close']) for candle in candles]
        current_price = closes[-1]
        
        # Get EMA period for timeframe
        ema_period = self.default_ema_periods.get(timeframe, 200)
        
        # Calculate EMA
        ema_value = self.calculate_ema(closes, ema_period)
        
        # Determine bias
        price_vs_ema = current_price - ema_value
        bias_threshold = 0.0005  # 5 pips threshold
        
        if abs(price_vs_ema) < bias_threshold:
            bias = 'neutral'
            confidence = 0.3
        elif price_vs_ema > 0:
            bias = 'bullish'
            confidence = min(abs(price_vs_ema) / 0.002, 1.0)  # Cap at 1.0
        else:
            bias = 'bearish'
            confidence = min(abs(price_vs_ema) / 0.002, 1.0)
        
        return {
            'bias': bias,
            'confidence': round(confidence, 2),
            'ema_value': round(ema_value, 5),
            'current_price': round(current_price, 5),
            'price_vs_ema': round(price_vs_ema, 5),
            'timeframe': timeframe,
            'ema_period': ema_period,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_multi_timeframe_bias(self, candles_by_tf: Dict[str, List[Dict]]) -> Dict:
        """
        Get bias across multiple timeframes
        
        Args:
            candles_by_tf: Dict mapping timeframe to candle data
        
        Returns:
            Dict with multi-timeframe bias analysis
        """
        results = {}
        overall_bias = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        total_confidence = 0
        
        for timeframe, candles in candles_by_tf.items():
            bias_data = self.determine_bias(candles, timeframe)
            results[timeframe] = bias_data
            
            # Count bias for overall determination
            overall_bias[bias_data['bias']] += 1
            total_confidence += bias_data['confidence']
        
        # Determine overall bias
        max_count = max(overall_bias.values())
        if max_count == overall_bias['bullish']:
            overall = 'bullish'
        elif max_count == overall_bias['bearish']:
            overall = 'bearish'
        else:
            overall = 'neutral'
        
        avg_confidence = total_confidence / len(candles_by_tf) if candles_by_tf else 0
        
        return {
            'overall_bias': overall,
            'overall_confidence': round(avg_confidence, 2),
            'timeframe_analysis': results,
            'bias_distribution': overall_bias,
            'timestamp': datetime.utcnow().isoformat()
        }

class TrendStrengthAnalyzer:
    """Analyzes trend strength using additional indicators"""
    
    def __init__(self):
        self.atr_period = 14
    
    def calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range for volatility"""
        if len(candles) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = float(candles[i]['high'])
            low = float(candles[i]['low'])
            prev_close = float(candles[i-1]['close'])
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        if len(true_ranges) < period:
            return 0.0
            
        return float(np.mean(true_ranges[-period:]))
    
    def analyze_trend_strength(self, candles: List[Dict]) -> Dict:
        """Analyze trend strength using multiple indicators"""
        if len(candles) < 20:
            return {
                'trend_strength': 'weak',
                'volatility': 0.0,
                'momentum': 0.0,
                'support_resistance': []
            }
        
        closes = [float(c['close']) for candle in candles]
        
        # Calculate momentum
        momentum = (closes[-1] - closes[-10]) / closes[-10] * 100
        
        # Calculate volatility
        volatility = self.calculate_atr(candles)
        
        # Determine trend strength
        if abs(momentum) > 2.0:
            trend_strength = 'strong'
        elif abs(momentum) > 1.0:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
        
        # Find support/resistance levels
        recent_high = max([float(c['high']) for c in candles[-10:]])
        recent_low = min([float(c['low']) for c in candles[-10:]])
        
        return {
            'trend_strength': trend_strength,
            'momentum': round(momentum, 2),
            'volatility': round(volatility, 5),
            'recent_high': recent_high,
            'recent_low': recent_low,
            'support_level': recent_low,
            'resistance_level': recent_high,
            'timestamp': datetime.utcnow().isoformat()
        }
