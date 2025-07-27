"""
Liquidity Analyzer
Identifies buy-side and sell-side liquidity levels for Silver Bullet strategy
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LiquidityAnalyzer:
    """Analyzes liquidity levels in the market"""
    
    def __init__(self):
        self.liquidity_threshold = 0.001  # 10 pips threshold
        self.min_candles_for_analysis = 20
        self.lookback_periods = {
            'M1': 100,    # 100 minutes
            'M5': 50,     # 250 minutes
            'M15': 30,    # 450 minutes
            'H1': 24,     # 24 hours
            'H4': 12      # 48 hours
        }
    
    def find_liquidity_levels(self, candles: List[Dict], timeframe: str = 'H1') -> Dict:
        """
        Find buy-side and sell-side liquidity levels
        
        Args:
            candles: List of candlestick data
            timeframe: Analysis timeframe
        
        Returns:
            Dict with liquidity levels
        """
        if len(candles) < self.min_candles_for_analysis:
            return {
                'buy_side_liquidity': [],
                'sell_side_liquidity': [],
                'strongest_buy': None,
                'strongest_sell': None,
                'analysis_complete': False,
                'message': 'Insufficient data for analysis'
            }
        
        # Extract price data
        highs = [float(c['high']) for c in candles]
        lows = [float(c['low']) for c in candles]
        closes = [float(c['close']) for c in candles]
        
        # Find swing highs and lows
        swing_highs = self._find_swing_highs(highs, lows)
        swing_lows = self._find_swing_lows(highs, lows)
        
        # Identify liquidity levels
        buy_side_liquidity = self._identify_buy_side_liquidity(swing_lows, closes[-1])
        sell_side_liquidity = self._identify_sell_side_liquidity(swing_highs, closes[-1])
        
        # Find strongest levels
        strongest_buy = self._find_strongest_level(buy_side_liquidity, 'buy')
        strongest_sell = self._find_strongest_level(sell_side_liquidity, 'sell')
        
        return {
            'buy_side_liquidity': buy_side_liquidity,
            'sell_side_liquidity': sell_side_liquidity,
            'strongest_buy': strongest_buy,
            'strongest_sell': strongest_sell,
            'current_price': closes[-1],
            'analysis_complete': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _find_swing_highs(self, highs: List[float], lows: List[float]) -> List[Dict]:
        """Find swing high points"""
        swing_highs = []
        
        for i in range(2, len(highs) - 2):
            if (highs[i] > highs[i-1] and 
                highs[i] > highs[i-2] and 
                highs[i] > highs[i+1] and 
                highs[i] > highs[i+2]):
                
                # Calculate strength based on surrounding candles
                strength = self._calculate_level_strength(
                    highs[i], 
                    [highs[i-2], highs[i-1], highs[i+1], highs[i+2]]
                )
                
                swing_highs.append({
                    'price': highs[i],
                    'index': i,
                    'strength': strength,
                    'type': 'swing_high'
                })
        
        return swing_highs
    
    def _find_swing_lows(self, highs: List[float], lows: List[float]) -> List[Dict]:
        """Find swing low points"""
        swing_lows = []
        
        for i in range(2, len(lows) - 2):
            if (lows[i] < lows[i-1] and 
                lows[i] < lows[i-2] and 
                lows[i] < lows[i+1] and 
                lows[i] < lows[i+2]):
                
                # Calculate strength based on surrounding candles
                strength = self._calculate_level_strength(
                    lows[i], 
                    [lows[i-2], lows[i-1], lows[i+1], lows[i+2]]
                )
                
                swing_lows.append({
                    'price': lows[i],
                    'index': i,
                    'strength': strength,
                    'type': 'swing_low'
                })
        
        return swing_lows
    
    def _calculate_level_strength(self, level_price: float, surrounding_prices: List[float]) -> float:
        """Calculate the strength of a support/resistance level"""
        avg_surrounding = np.mean(surrounding_prices)
        distance = abs(level_price - avg_surrounding)
        
        # Normalize strength (0-1 scale)
        max_distance = 0.01  # 100 pips max
        strength = min(distance / max_distance, 1.0)
        
        return round(strength, 2)
    
    def _identify_buy_side_liquidity(self, swing_lows: List[Dict], current_price: float) -> List[Dict]:
        """Identify buy-side liquidity levels (below current price)"""
        buy_side = []
        
        for low in swing_lows:
            if low['price'] < current_price:
                # Calculate distance from current price
                distance = abs(current_price - low['price'])
                
                # Only include significant levels
                if distance > self.liquidity_threshold:
                    buy_side.append({
                        'price': low['price'],
                        'strength': low['strength'],
                        'distance': round(distance, 5),
                        'type': 'buy_liquidity',
                        'significance': 'high' if low['strength'] > 0.7 else 'medium'
                    })
        
        # Sort by strength (strongest first)
        buy_side.sort(key=lambda x: x['strength'], reverse=True)
        return buy_side[:5]  # Return top 5 levels
    
    def _identify_sell_side_liquidity(self, swing_highs: List[Dict], current_price: float) -> List[Dict]:
        """Identify sell-side liquidity levels (above current price)"""
        sell_side = []
        
        for high in swing_highs:
            if high['price'] > current_price:
                # Calculate distance from current price
                distance = abs(high['price'] - current_price)
                
                # Only include significant levels
                if distance > self.liquidity_threshold:
                    sell_side.append({
                        'price': high['price'],
                        'strength': high['strength'],
                        'distance': round(distance, 5),
                        'type': 'sell_liquidity',
                        'significance': 'high' if high['strength'] > 0.7 else 'medium'
                    })
        
        # Sort by strength (strongest first)
        sell_side.sort(key=lambda x: x['strength'], reverse=True)
        return sell_side[:5]  # Return top 5 levels
    
    def _find_strongest_level(self, levels: List[Dict], level_type: str) -> Optional[Dict]:
        """Find the strongest liquidity level"""
        if not levels:
            return None
        
        strongest = max(levels, key=lambda x: x['strength'])
        return {
            'price': strongest['price'],
            'strength': strongest['strength'],
            'distance': strongest['distance'],
            'type': level_type,
            'significance': strongest['significance']
        }
    
    def check_liquidity_sweep(self, candles: List[Dict], liquidity_levels: Dict) -> Dict:
        """Check if liquidity levels have been swept"""
        if not candles or not liquidity_levels['analysis_complete']:
            return {
                'sweep_detected': False,
                'swept_levels': [],
                'message': 'Insufficient data for sweep analysis'
            }
        
        current_price = float(candles[-1]['close'])
        swept_levels = []
        
        # Check buy-side liquidity sweeps
        for level in liquidity_levels['buy_side_liquidity']:
            if current_price < level['price']:
                swept_levels.append({
                    'level': level,
                    'sweep_type': 'buy_sweep',
                    'sweep_price': current_price,
                    'sweep_magnitude': abs(current_price - level['price'])
                })
        
        # Check sell-side liquidity sweeps
        for level in liquidity_levels['sell_side_liquidity']:
            if current_price > level['price']:
                swept_levels.append({
                    'level': level,
                    'sweep_type': 'sell_sweep',
                    'sweep_price': current_price,
                    'sweep_magnitude': abs(current_price - level['price'])
                })
        
        return {
            'sweep_detected': len(swept_levels) > 0,
            'swept_levels': swept_levels,
            'sweep_count': len(swept_levels),
            'timestamp': datetime.utcnow().isoformat()
        }

class LiquidityHeatmap:
    """Creates liquidity heatmap for visual analysis"""
    
    def __init__(self):
        self.price_granularity = 0.0001  # 1 pip granularity
    
    def generate_heatmap(self, candles: List[Dict], levels: Dict) -> Dict:
        """Generate liquidity heatmap data"""
        if not candles or not levels['analysis_complete']:
            return {'heatmap': [], 'message': 'Insufficient data'}
        
        current_price = float(candles[-1]['close'])
        
        # Create price ranges around current price
        price_range = 0.01  # 100 pips range
        min_price = current_price - price_range
        max_price = current_price + price_range
        
        heatmap = []
        
        # Generate heatmap points
        price_points = np.arange(min_price, max_price, self.price_granularity)
        
        for price in price_points:
            # Calculate liquidity density at this price
            buy_density = self._calculate_liquidity_density(
                price, levels['buy_side_liquidity'], 'buy'
            )
            sell_density = self._calculate_liquidity_density(
                price, levels['sell_side_liquidity'], 'sell'
            )
            
            heatmap.append({
                'price': round(price, 5),
                'buy_density': buy_density,
                'sell_density': sell_density,
                'total_density': buy_density + sell_density
            })
        
        return {
            'heatmap': heatmap,
            'current_price': current_price,
            'price_range': [min_price, max_price],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_liquidity_density(self, price: float, levels: List[Dict], level_type: str) -> float:
        """Calculate liquidity density at a specific price"""
        density = 0.0
        
        for level in levels:
            distance = abs(price - level['price'])
            if distance < 0.0005:  # Within 5 pips
                # Gaussian decay based on distance
                weight = level['strength'] * np.exp(-distance * 1000)
                density += weight
        
        return round(density, 3)
