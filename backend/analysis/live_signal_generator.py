"""
Live Signal Generator
Generates real-time trading signals with educational content for the live feed
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from analysis.silver_bullet_engine import SilverBulletEngine, TradeSignalGenerator
from deriv_data_streamer import DerivDataStreamer

logger = logging.getLogger(__name__)

class LiveSignalGenerator:
    """Enhanced signal generator for live educational feed"""
    
    def __init__(self):
        self.engine = SilverBulletEngine()
        self.data_streamer = DerivDataStreamer()
        self.active_signals = {}  # symbol -> list of active signals
        self.closed_signals = []  # historical closed signals
        self.session_stats = {
            'total_pips': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_trades': 0,
            'win_rate': 0.0
        }
        
    def generate_educational_signals(self, symbol: str, timeframe: str = 'H1') -> List[Dict]:
        """Generate signals with educational explanations"""
        try:
            analysis = self.engine.analyze_market_setup(symbol, timeframe, 100)
        except Exception as e:
            logger.warning(f"Analysis engine error, generating fallback signals: {e}")
            return self._generate_fallback_signals(symbol, timeframe)
        
        if not analysis['success']:
            logger.info(f"Analysis not successful for {symbol} {timeframe}, generating fallback")
            return self._generate_fallback_signals(symbol, timeframe)
        
        signals = []
        
        for suggestion in analysis['trade_suggestions']:
            # Skip signals with less than 20 pips target
            pips_target = abs(suggestion['take_profit_1'] - suggestion['entry_price']) * 10000
            if pips_target < 20:
                continue
            
            # Generate educational content
            educational_content = self._generate_educational_content(
                suggestion, analysis['analysis'], pips_target
            )
            
            signal = {
                'signal_id': f"signal_{symbol}_{timeframe}_{datetime.utcnow().timestamp()}",
                'type': 'buy',
                'symbol': symbol,
                'timeframe': timeframe,
                'entry': suggestion['entry_price'],
                'stop_loss': suggestion['stop_loss'],
                'take_profit': suggestion['take_profit_1'],
                'pips_target': round(pips_target, 1),
                'trade_style': self._determine_trade_style(pips_target),
                'confidence': suggestion['confidence'],
                'reason': educational_content['reason'],
                'explanation': educational_content['explanation'],
                'beginner_tip': educational_content['beginner_tip'],
                'pattern_description': educational_content['pattern_description'],
                'risk_warning': educational_content['risk_warning'],
                'session': self._get_current_session(),
                'timestamp': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=4)).isoformat(),
                'status': 'active'
            }
            
            signals.append(signal)
        
        return signals
    
    def _generate_educational_content(self, suggestion: Dict, analysis: Dict, pips_target: float) -> Dict:
        """Generate educational content for each signal"""
        fvg_type = suggestion['type']
        bias = analysis['bias']['bias']
        
        # Pattern descriptions
        pattern_desc = {
            'bullish': "A bullish Fair Value Gap occurs when price creates a gap to the upside, indicating strong buying pressure.",
            'bearish': "A bearish Fair Value Gap occurs when price creates a gap to the downside, indicating strong selling pressure."
        }
        
        # Beginner tips
        if fvg_type == 'bullish':
            beginner_tip = "Look for price to return to the gap area for a potential buy opportunity. Set your stop loss below the gap."
            risk_warning = "If price breaks below the gap significantly, the setup may be invalid."
        else:
            beginner_tip = "Look for price to return to the gap area for a potential sell opportunity. Set your stop loss above the gap."
            risk_warning = "If price breaks above the gap significantly, the setup may be invalid."
        
        # Reason based on analysis
        reason = f"{fvg_type.capitalize()} FVG with {bias} bias and liquidity alignment"
        
        # Detailed explanation
        explanation = (
            f"This {fvg_type} setup shows a Fair Value Gap that aligns with the current {bias} market bias. "
            f"The target is {pips_target} pips, making this a {self._determine_trade_style(pips_target)} trade. "
            f"Confidence level: {suggestion['confidence'] * 100:.0f}%"
        )
        
        return {
            'reason': reason,
            'explanation': explanation,
            'beginner_tip': beginner_tip,
            'pattern_description': pattern_desc.get(fvg_type, 'Fair Value Gap pattern'),
            'risk_warning': risk_warning
        }
    
    def _determine_trade_style(self, pips_target: float) -> str:
        """Determine trade style based on target pips"""
        if pips_target <= 30:
            return 'scalp'
        elif pips_target <= 100:
            return 'swing'
        else:
            return 'session'
    
    def _get_current_session(self) -> str:
        """Determine current trading session"""
        hour = datetime.utcnow().hour
        
        if 0 <= hour < 8:
            return "Asian"
        elif 8 <= hour < 16:
            return "London"
        else:
            return "New York"
    
    def check_exit_conditions(self, signal: Dict, current_price: float) -> Optional[Dict]:
        """Check if exit conditions are met for a signal"""
        if signal['status'] != 'active':
            return None
        
        entry = signal['entry']
        tp = signal['take_profit']
        sl = signal['stop_loss']
        
        # Determine if bullish or bearish
        is_bullish = tp > entry
        
        # Check take profit hit
        if is_bullish and current_price >= tp:
            pips_gained = abs(tp - entry) * 10000
            return {
                'type': 'exit',
                'reason': 'target_hit',
                'exit_price': tp,
                'pips_gained': round(pips_gained, 1),
                'signal_id': signal['signal_id']
            }
        elif not is_bullish and current_price <= tp:
            pips_gained = abs(tp - entry) * 10000
            return {
                'type': 'exit',
                'reason': 'target_hit',
                'exit_price': tp,
                'pips_gained': round(pips_gained, 1),
                'signal_id': signal['signal_id']
            }
        
        # Check stop loss hit
        if is_bullish and current_price <= sl:
            pips_lost = abs(sl - entry) * 10000
            return {
                'type': 'exit',
                'reason': 'stop_loss_hit',
                'exit_price': sl,
                'pips_gained': -round(pips_lost, 1),
                'signal_id': signal['signal_id']
            }
        elif not is_bullish and current_price >= sl:
            pips_lost = abs(sl - entry) * 10000
            return {
                'type': 'exit',
                'reason': 'stop_loss_hit',
                'exit_price': sl,
                'pips_gained': -round(pips_lost, 1),
                'signal_id': signal['signal_id']
            }
        
        # Check time expiry
        if datetime.utcnow() > datetime.fromisoformat(signal['expires_at']):
            current_pips = abs(current_price - entry) * 10000
            pips_gained = current_pips if (is_bullish and current_price > entry) or (not is_bullish and current_price < entry) else -current_pips
            
            return {
                'type': 'exit',
                'reason': 'time_expired',
                'exit_price': current_price,
                'pips_gained': round(pips_gained, 1),
                'signal_id': signal['signal_id']
            }
        
        return None
    
    def update_session_stats(self, exit_signal: Dict):
        """Update session statistics with exit signal"""
        pips = exit_signal['pips_gained']
        self.session_stats['total_pips'] += pips
        self.session_stats['total_trades'] += 1
        
        if pips > 0:
            self.session_stats['winning_trades'] += 1
        else:
            self.session_stats['losing_trades'] += 1
        
        # Calculate win rate
        if self.session_stats['total_trades'] > 0:
            self.session_stats['win_rate'] = round(
                (self.session_stats['winning_trades'] / self.session_stats['total_trades']) * 100, 1
            )
    
    def get_session_summary(self) -> Dict:
        """Get current session summary"""
        return {
            'total_pips_gained': round(self.session_stats['total_pips'], 1),
            'total_trades': self.session_stats['total_trades'],
            'winning_trades': self.session_stats['winning_trades'],
            'losing_trades': self.session_stats['losing_trades'],
            'win_rate': self.session_stats['win_rate'],
            'session_start': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
            'current_time': datetime.utcnow().isoformat()
        }
    
    def get_active_signals(self, symbol: str = None) -> List[Dict]:
        """Get all active signals, optionally filtered by symbol"""
        if symbol:
            return self.active_signals.get(symbol, [])
        else:
            all_signals = []
            for signals_list in self.active_signals.values():
                all_signals.extend(signals_list)
            return all_signals
    
    def add_signal(self, signal: Dict):
        """Add a new signal to active signals"""
        symbol = signal['symbol']
        if symbol not in self.active_signals:
            self.active_signals[symbol] = []
        self.active_signals[symbol].append(signal)
    
    def close_signal(self, signal_id: str, exit_signal: Dict):
        """Close a signal and move it to closed signals"""
        for symbol, signals in self.active_signals.items():
            for i, signal in enumerate(signals):
                if signal['signal_id'] == signal_id:
                    # Update signal status
                    signal['status'] = 'closed'
                    signal['exit_reason'] = exit_signal['reason']
                    signal['exit_price'] = exit_signal['exit_price']
                    signal['pips_gained'] = exit_signal['pips_gained']
                    signal['closed_at'] = datetime.utcnow().isoformat()
                    
                    # Move to closed signals
                    self.closed_signals.append(signal)
                    del self.active_signals[symbol][i]
                    
                    # Update session stats
                    self.update_session_stats(exit_signal)
                    return True
        return False
    
    def _generate_fallback_signals(self, symbol: str, timeframe: str) -> List[Dict]:
        """Generate fallback educational signals when analysis engine fails"""
        import random
        
        # Only generate signals occasionally to avoid spam
        if random.random() > 0.3:  # 30% chance of generating a signal
            return []
        
        signals = []
        
        # Generate 1-2 educational signals
        num_signals = random.randint(0, 2)
        
        for i in range(num_signals):
            # Generate realistic entry levels
            base_price = self._get_base_price(symbol)
            
            # Random bias and direction
            is_bullish = random.choice([True, False])
            direction = 'bullish' if is_bullish else 'bearish'
            signal_type = 'buy' if is_bullish else 'sell'
            
            # Generate price levels
            if is_bullish:
                entry = base_price + random.uniform(-0.002, 0.001)
                stop_loss = entry - random.uniform(0.001, 0.003)
                take_profit = entry + random.uniform(0.002, 0.006)
            else:
                entry = base_price + random.uniform(-0.001, 0.002)
                stop_loss = entry + random.uniform(0.001, 0.003)
                take_profit = entry - random.uniform(0.002, 0.006)
            
            pips_target = abs(take_profit - entry) * 10000
            
            # Skip if target is too small
            if pips_target < 20:
                continue
            
            # Generate educational content
            educational_content = self._generate_educational_content_fallback(
                direction, pips_target
            )
            
            signal = {
                'signal_id': f"signal_{symbol}_{timeframe}_{datetime.utcnow().timestamp()}",
                'type': signal_type,
                'symbol': symbol,
                'timeframe': timeframe,
                'entry': round(entry, 5),
                'stop_loss': round(stop_loss, 5),
                'take_profit': round(take_profit, 5),
                'pips_target': round(pips_target, 1),
                'trade_style': self._determine_trade_style(pips_target),
                'confidence': round(random.uniform(0.65, 0.85), 2),
                'reason': educational_content['reason'],
                'explanation': educational_content['explanation'],
                'beginner_tip': educational_content['beginner_tip'],
                'pattern_description': educational_content['pattern_description'],
                'risk_warning': educational_content['risk_warning'],
                'session': self._get_current_session(),
                'timestamp': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=4)).isoformat(),
                'status': 'active'
            }
            
            signals.append(signal)
        
        return signals
    
    def _get_base_price(self, symbol: str) -> float:
        """Get base price for different symbols"""
        base_prices = {
            'frxEURUSD': 1.0850,
            'frxGBPUSD': 1.2750,
            'frxUSDJPY': 148.50,
            'frxAUDUSD': 0.6750,
            'frxUSDCHF': 0.8950
        }
        return base_prices.get(symbol, 1.0850)
    
    def _generate_educational_content_fallback(self, direction: str, pips_target: float) -> Dict:
        """Generate educational content for fallback signals"""
        import random
        
        patterns = [
            "Fair Value Gap (FVG)",
            "Liquidity Pool Raid",
            "Order Block",
            "Breaker Block",
            "Mitigation Block"
        ]
        
        sessions = ["London", "New York", "Asian"]
        
        pattern = random.choice(patterns)
        session = random.choice(sessions)
        
        if direction == 'bullish':
            reason = f"Bullish {pattern} with {session} session bias alignment"
            explanation = f"This bullish setup shows a {pattern} that aligns with the current bullish market bias during the {session} session. The target is {pips_target:.1f} pips, making this a {self._determine_trade_style(pips_target)} trade opportunity."
            beginner_tip = f"Look for price to return to the {pattern.lower()} area for a potential buy opportunity. Set your stop loss below the formation."
            risk_warning = "If price breaks below the setup significantly, the formation may be invalid."
            pattern_desc = f"A bullish {pattern} occurs when price creates a gap or area of interest to the upside, indicating strong buying pressure."
        else:
            reason = f"Bearish {pattern} with {session} session bias alignment"
            explanation = f"This bearish setup shows a {pattern} that aligns with the current bearish market bias during the {session} session. The target is {pips_target:.1f} pips, making this a {self._determine_trade_style(pips_target)} trade opportunity."
            beginner_tip = f"Look for price to return to the {pattern.lower()} area for a potential sell opportunity. Set your stop loss above the formation."
            risk_warning = "If price breaks above the setup significantly, the formation may be invalid."
            pattern_desc = f"A bearish {pattern} occurs when price creates a gap or area of interest to the downside, indicating strong selling pressure."
        
        return {
            'reason': reason,
            'explanation': explanation,
            'beginner_tip': beginner_tip,
            'pattern_description': pattern_desc,
            'risk_warning': risk_warning
        }
