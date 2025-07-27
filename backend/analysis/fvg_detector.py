"""
FVG (Fair Value Gap) Detector
Identifies Fair Value Gaps for Silver Bullet strategy
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime

# Simple statistics functions to replace numpy functionality
def _mean(values: List[float]) -> float:
    """Calculate mean of a list of values"""
    if not values:
        return 0.0
    return sum(values) / len(values)

logger = logging.getLogger(__name__)

class FVGDetector:
    """Detects Fair Value Gaps in candlestick data"""
    
    def __init__(self):
        self.min_gap_size = 0.0002  # 2 pips minimum gap
        self.lookback_periods = 3   # Look back 3 candles for gap formation
        self.confirmation_candles = 2  # Candles to confirm gap
    
    def detect_fvgs(self, candles: List[Dict], timeframe: str = 'H1') -> Dict:
        """
        Detect Fair Value Gaps in candlestick data
        
        Args:
            candles: List of candlestick data
            timeframe: Analysis timeframe
        
        Returns:
            Dict with FVG analysis
        """
        if len(candles) < 5:
            return {
                'fvgs': [],
                'active_fvgs': [],
                'filled_fvgs': [],
                'analysis_complete': False,
                'message': 'Insufficient data for FVG analysis'
            }
        
        fvgs = []
        
        # Analyze candles for FVG formation
        for i in range(2, len(candles) - 1):
            fvg = self._analyze_single_fvg(candles, i)
            if fvg:
                fvgs.append(fvg)
        
        # Categorize FVGs
        active_fvgs = [fvg for fvg in fvgs if fvg['status'] == 'active']
        filled_fvgs = [fvg for fvg in fvgs if fvg['status'] == 'filled']
        
        return {
            'fvgs': fvgs,
            'active_fvgs': active_fvgs,
            'filled_fvgs': filled_fvgs,
            'total_count': len(fvgs),
            'active_count': len(active_fvgs),
            'filled_count': len(filled_fvgs),
            'analysis_complete': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _analyze_single_fvg(self, candles: List[Dict], index: int) -> Optional[Dict]:
        """Analyze a single potential FVG formation"""
        if index < 2 or index >= len(candles) - 1:
            return None
        
        # Get the three candles involved
        candle1 = candles[index - 2]  # First candle
        candle2 = candles[index - 1]  # Middle candle (imbalance)
        candle3 = candles[index]      # Third candle
        
        # Extract prices
        high1, low1 = float(candle1['high']), float(candle1['low'])
        high2, low2 = float(candle2['high']), float(candle2['low'])
        high3, low3 = float(candle3['high']), float(candle3['low'])
        
        # Check for bullish FVG (gap down)
        bullish_fvg = self._check_bullish_fvg(high1, low1, high2, low2, high3, low3)
        if bullish_fvg:
            return self._create_fvg_record(
                candles, index, bullish_fvg, 'bullish', candle1, candle2, candle3
            )
        
        # Check for bearish FVG (gap up)
        bearish_fvg = self._check_bearish_fvg(high1, low1, high2, low2, high3, low3)
        if bearish_fvg:
            return self._create_fvg_record(
                candles, index, bearish_fvg, 'bearish', candle1, candle2, candle3
            )
        
        return None
    
    def _check_bullish_fvg(self, high1: float, low1: float, high2: float, low2: float, 
                          high3: float, low3: float) -> Optional[Dict]:
        """Check for bullish FVG formation"""
        # Bullish FVG: gap between candle1 low and candle3 high
        if low1 > high3:
            gap_size = low1 - high3
            
            if gap_size >= self.min_gap_size:
                return {
                    'type': 'bullish',
                    'gap_top': high3,
                    'gap_bottom': low1,
                    'gap_size': gap_size,
                    'formation_index': 2  # Index of the middle candle
                }
        
        return None
    
    def _check_bearish_fvg(self, high1: float, low1: float, high2: float, low2: float,
                          high3: float, low3: float) -> Optional[Dict]:
        """Check for bearish FVG formation"""
        # Bearish FVG: gap between candle1 high and candle3 low
        if high1 < low3:
            gap_size = low3 - high1
            
            if gap_size >= self.min_gap_size:
                return {
                    'type': 'bearish',
                    'gap_top': low3,
                    'gap_bottom': high1,
                    'gap_size': gap_size,
                    'formation_index': 2  # Index of the middle candle
                }
        
        return None
    
    def _create_fvg_record(self, candles: List[Dict], index: int, fvg_data: Dict, 
                          fvg_type: str, candle1: Dict, candle2: Dict, candle3: Dict) -> Dict:
        """Create a complete FVG record"""
        formation_time = datetime.fromtimestamp(int(candle2['timestamp']))
        
        # Check if FVG is filled
        status = self._check_fvg_status(candles, index, fvg_data)
        
        # Calculate target levels
        target_levels = self._calculate_fvg_targets(fvg_data, fvg_type)
        
        return {
            'id': f"fvg_{index}_{fvg_type}",
            'type': fvg_type,
            'formation_time': formation_time.isoformat(),
            'formation_index': index - 1,
            'gap_top': fvg_data['gap_top'],
            'gap_bottom': fvg_data['gap_bottom'],
            'gap_size': round(fvg_data['gap_size'], 5),
            'status': status['status'],
            'fill_price': status['fill_price'],
            'fill_time': status['fill_time'],
            'fill_index': status['fill_index'],
            'target_levels': target_levels,
            'confidence': self._calculate_fvg_confidence(fvg_data, candles, index),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_fvg_status(self, candles: List[Dict], formation_index: int, fvg_data: Dict) -> Dict:
        """Check if FVG has been filled"""
        gap_top = fvg_data['gap_top']
        gap_bottom = fvg_data['gap_bottom']
        
        # Check subsequent candles for fill
        for i in range(formation_index + 1, len(candles)):
            candle = candles[i]
            high = float(candle['high'])
            low = float(candle['low'])
            
            # Check if price has entered the gap
            if fvg_data['type'] == 'bullish':
                # Bullish FVG filled when price goes into gap from below
                if high >= gap_bottom:
                    return {
                        'status': 'filled',
                        'fill_price': gap_bottom,
                        'fill_time': datetime.fromtimestamp(int(candle['timestamp'])).isoformat(),
                        'fill_index': i
                    }
            else:  # bearish
                # Bearish FVG filled when price goes into gap from above
                if low <= gap_top:
                    return {
                        'status': 'filled',
                        'fill_price': gap_top,
                        'fill_time': datetime.fromtimestamp(int(candle['timestamp'])).isoformat(),
                        'fill_index': i
                    }
        
        return {
            'status': 'active',
            'fill_price': None,
            'fill_time': None,
            'fill_index': None
        }
    
    def _calculate_fvg_targets(self, fvg_data: Dict, fvg_type: str) -> Dict:
        """Calculate target levels for FVG trading"""
        gap_top = fvg_data['gap_top']
        gap_bottom = fvg_data['gap_bottom']
        gap_size = fvg_data['gap_size']
        
        if fvg_type == 'bullish':
            # Bullish FVG targets
            entry = gap_bottom
            stop_loss = gap_bottom - (gap_size * 0.5)  # 50% of gap size
            take_profit_1 = gap_top
            take_profit_2 = gap_top + (gap_size * 1.0)  # 100% extension
            
            return {
                'entry': round(entry, 5),
                'stop_loss': round(stop_loss, 5),
                'take_profit_1': round(take_profit_1, 5),
                'take_profit_2': round(take_profit_2, 5),
                'risk_reward_1': round((take_profit_1 - entry) / (entry - stop_loss), 2),
                'risk_reward_2': round((take_profit_2 - entry) / (entry - stop_loss), 2)
            }
        else:  # bearish
            # Bearish FVG targets
            entry = gap_top
            stop_loss = gap_top + (gap_size * 0.5)  # 50% of gap size
            take_profit_1 = gap_bottom
            take_profit_2 = gap_bottom - (gap_size * 1.0)  # 100% extension
            
            return {
                'entry': round(entry, 5),
                'stop_loss': round(stop_loss, 5),
                'take_profit_1': round(take_profit_1, 5),
                'take_profit_2': round(take_profit_2, 5),
                'risk_reward_1': round((entry - take_profit_1) / (stop_loss - entry), 2),
                'risk_reward_2': round((entry - take_profit_2) / (stop_loss - entry), 2)
            }
    
    def _calculate_fvg_confidence(self, fvg_data: Dict, candles: List[Dict], formation_index: int) -> float:
        """Calculate confidence score for FVG"""
        gap_size = fvg_data['gap_size']
        
        # Base confidence on gap size
        size_confidence = min(gap_size / 0.001, 1.0)  # Normalize to 0-1
        
        # Check market context
        recent_volatility = self._calculate_recent_volatility(candles, formation_index)
        volatility_factor = min(recent_volatility / 0.002, 1.0)
        
        # Combine factors
        confidence = (size_confidence * 0.6) + (volatility_factor * 0.4)
        
        return round(min(confidence, 1.0), 2)
    
    def _calculate_recent_volatility(self, candles: List[Dict], index: int) -> float:
        """Calculate recent market volatility"""
        start_idx = max(0, index - 10)
        recent_candles = candles[start_idx:index]
        
        if len(recent_candles) < 5:
            return 0.001
        
        highs = [float(c['high']) for c in recent_candles]
        lows = [float(c['low']) for c in recent_candles]
        
        # Calculate average true range
        atr_values = []
        for i in range(1, len(recent_candles)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - float(recent_candles[i-1]['close'])),
                abs(lows[i] - float(recent_candles[i-1]['close']))
            )
            atr_values.append(tr)
        
        return _mean(atr_values) if atr_values else 0.001
    
    def get_silver_bullet_setups(self, candles: List[Dict], liquidity_levels: Dict, 
                               bias_data: Dict) -> Dict:
        """
        Identify Silver Bullet setups combining FVG, liquidity, and bias
        
        Args:
            candles: Candlestick data
            liquidity_levels: Liquidity analysis data
            bias_data: Market bias data
        
        Returns:
            Dict with Silver Bullet setups
        """
        fvg_data = self.detect_fvgs(candles)
        
        if not fvg_data['analysis_complete']:
            return {
                'setups': [],
                'message': 'Insufficient data for Silver Bullet analysis'
            }
        
        setups = []
        
        for fvg in fvg_data['active_fvgs']:
            setup = self._evaluate_silver_bullet_setup(fvg, liquidity_levels, bias_data)
            if setup:
                setups.append(setup)
        
        return {
            'setups': setups,
            'setup_count': len(setups),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _evaluate_silver_bullet_setup(self, fvg: Dict, liquidity_levels: Dict, 
                                    bias_data: Dict) -> Optional[Dict]:
        """Evaluate if FVG forms a valid Silver Bullet setup"""
        # Check alignment with bias
        bias_alignment = self._check_bias_alignment(fvg, bias_data)
        if not bias_alignment['aligned']:
            return None
        
        # Check liquidity proximity
        liquidity_proximity = self._check_liquidity_proximity(fvg, liquidity_levels)
        if not liquidity_proximity['valid']:
            return None
        
        # Calculate setup quality
        quality_score = self._calculate_setup_quality(fvg, liquidity_levels, bias_data)
        
        return {
            'fvg': fvg,
            'bias_alignment': bias_alignment,
            'liquidity_proximity': liquidity_proximity,
            'quality_score': quality_score,
            'setup_type': 'silver_bullet',
            'confidence': quality_score,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_bias_alignment(self, fvg: Dict, bias_data: Dict) -> Dict:
        """Check if FVG aligns with market bias"""
        bias = bias_data.get('bias', 'neutral')
        
        if fvg['type'] == 'bullish' and bias == 'bullish':
            return {'aligned': True, 'reason': 'Bullish FVG in bullish bias'}
        elif fvg['type'] == 'bearish' and bias == 'bearish':
            return {'aligned': True, 'reason': 'Bearish FVG in bearish bias'}
        else:
            return {'aligned': False, 'reason': 'FVG type conflicts with bias'}
    
    def _check_liquidity_proximity(self, fvg: Dict, liquidity_levels: Dict) -> Dict:
        """Check if FVG is near significant liquidity levels"""
        if not liquidity_levels['analysis_complete']:
            return {'valid': False, 'reason': 'No liquidity data'}
        
        # Check proximity to liquidity levels
        fvg_price = fvg['gap_bottom'] if fvg['type'] == 'bullish' else fvg['gap_top']
        
        # Check buy-side liquidity for bullish setups
        if fvg['type'] == 'bullish':
            relevant_liquidity = liquidity_levels.get('buy_side_liquidity', [])
        else:
            relevant_liquidity = liquidity_levels.get('sell_side_liquidity', [])
        
        # Find nearest liquidity level
        nearest_distance = float('inf')
        nearest_level = None
        
        for level in relevant_liquidity:
            distance = abs(fvg_price - level['price'])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_level = level
        
        if nearest_distance < 0.002:  # Within 20 pips
            return {
                'valid': True,
                'nearest_level': nearest_level,
                'distance': nearest_distance,
                'reason': 'FVG near significant liquidity'
            }
        
        return {'valid': False, 'reason': 'No significant liquidity nearby'}
    
    def _calculate_setup_quality(self, fvg: Dict, liquidity_levels: Dict, bias_data: Dict) -> float:
        """Calculate overall setup quality score"""
        quality_factors = []
        
        # FVG confidence
        quality_factors.append(fvg['confidence'] * 0.4)
        
        # Gap size factor
        gap_size_factor = min(fvg['gap_size'] / 0.001, 1.0)
        quality_factors.append(gap_size_factor * 0.3)
        
        # Bias confidence
        bias_confidence = bias_data.get('confidence', 0.5)
        quality_factors.append(bias_confidence * 0.2)
        
        # Liquidity strength
        liquidity_strength = 0.5  # Default
        if liquidity_levels['analysis_complete']:
            if fvg['type'] == 'bullish' and liquidity_levels['strongest_buy']:
                liquidity_strength = liquidity_levels['strongest_buy']['strength']
            elif fvg['type'] == 'bearish' and liquidity_levels['strongest_sell']:
                liquidity_strength = liquidity_levels['strongest_sell']['strength']
        
        quality_factors.append(liquidity_strength * 0.1)
        
        return round(sum(quality_factors), 2)
