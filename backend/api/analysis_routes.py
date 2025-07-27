"""
Analysis API Routes
REST API endpoints for Silver Bullet strategy analysis
"""

from flask import Blueprint, jsonify, request
import logging
from analysis.silver_bullet_engine import SilverBulletEngine
from deriv_data_streamer import DerivDataStreamer

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

# Initialize engines
engine = SilverBulletEngine()
data_streamer = DerivDataStreamer()

@analysis_bp.route('/api/analysis/market_summary', methods=['GET'])
def get_market_summary():
    """Get comprehensive market summary for a symbol"""
    try:
        symbol = request.args.get('symbol', 'frxEURUSD')
        
        summary = engine.get_market_summary(symbol)
        
        return jsonify({
            'success': True,
            'data': summary,
            'timestamp': summary['analysis_time']
        })
        
    except Exception as e:
        logger.error(f"Error getting market summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/bias', methods=['GET'])
def get_market_bias():
    """Get market bias analysis"""
    try:
        symbol = request.args.get('symbol', 'frxEURUSD')
        timeframe = request.args.get('timeframe', 'H1')
        lookback = int(request.args.get('lookback', 50))
        
        analysis = engine.analyze_market_setup(symbol, timeframe, lookback)
        
        if not analysis['success']:
            return jsonify({
                'success': False,
                'error': analysis['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'bias': analysis['analysis']['bias'],
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting market bias: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/liquidity', methods=['GET'])
def get_liquidity_levels():
    """Get liquidity level analysis"""
    try:
        symbol = request.args.get('symbol', 'frxEURUSD')
        timeframe = request.args.get('timeframe', 'H1')
        lookback = int(request.args.get('lookback', 50))
        
        # Get data and analyze
        candles = data_streamer.get_historical_candles(
            symbol, 
            engine._timeframe_to_minutes(timeframe), 
            lookback
        )
        
        if not candles:
            return jsonify({
                'success': False,
                'error': 'No data available'
            }), 500
        
        from analysis.liquidity_analyzer import LiquidityAnalyzer
        liquidity_analyzer = LiquidityAnalyzer()
        liquidity_data = liquidity_analyzer.find_liquidity_levels(candles, timeframe)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'liquidity': liquidity_data,
                'timestamp': liquidity_data['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting liquidity levels: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/fvgs', methods=['GET'])
def get_fvgs():
    """Get Fair Value Gap analysis"""
    try:
        symbol = request.args.get('symbol', 'frxEURUSD')
        timeframe = request.args.get('timeframe', 'H1')
        lookback = int(request.args.get('lookback', 50))
        
        # Get data and analyze
        candles = data_streamer.get_historical_candles(
            symbol, 
            engine._timeframe_to_minutes(timeframe), 
            lookback
        )
        
        if not candles:
            return jsonify({
                'success': False,
                'error': 'No data available'
            }), 500
        
        from analysis.fvg_detector import FVGDetector
        fvg_detector = FVGDetector()
        fvg_data = fvg_detector.detect_fvgs(candles, timeframe)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'fvgs': fvg_data,
                'timestamp': fvg_data['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting FVG analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/silver_bullet', methods=['GET'])
def get_silver_bullet_setups():
    """Get Silver Bullet strategy setups"""
    try:
        symbol = request.args.get('symbol', 'frxEURUSD')
        timeframe = request.args.get('timeframe', 'H1')
        lookback = int(request.args.get('lookback', 100))
        
        analysis = engine.analyze_market_setup(symbol, timeframe, lookback)
        
        if not analysis['success']:
            return jsonify({
                'success': False,
                'error': analysis['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'analysis': analysis['analysis'],
                'trade_suggestions': analysis['trade_suggestions'],
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting Silver Bullet setups: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/validate_setup', methods=['POST'])
def validate_setup():
    """Validate a trade setup against current market conditions"""
    try:
        data = request.json
        setup = data.get('setup')
        
        if not setup:
            return jsonify({
                'success': False,
                'error': 'No setup provided'
            }), 400
        
        validation = engine.validate_setup(setup)
        
        return jsonify({
            'success': True,
            'data': validation
        })
        
    except Exception as e:
        logger.error(f"Error validating setup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/signals', methods=['GET'])
def get_trade_signals():
    """Get current trade signals"""
    try:
        symbol = request.args.get('symbol', 'frxEURUSD')
        timeframe = request.args.get('timeframe', 'H1')
        
        from analysis.silver_bullet_engine import TradeSignalGenerator
        signal_generator = TradeSignalGenerator(engine)
        signals = signal_generator.generate_signals(symbol, timeframe)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'signals': signals,
                'count': len(signals),
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting trade signals: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/supported_symbols', methods=['GET'])
def get_supported_symbols():
    """Get list of supported trading symbols"""
    try:
        symbols = data_streamer.get_active_symbols()
        
        # Filter for forex symbols
        forex_symbols = [
            {
                'symbol': s['symbol'],
                'display_name': s['display_name'],
                'market': s['market'],
                'submarket': s['submarket']
            }
            for s in symbols 
            if s.get('market') == 'forex'
        ]
        
        return jsonify({
            'success': True,
            'data': forex_symbols,
            'count': len(forex_symbols)
        })
        
    except Exception as e:
        logger.error(f"Error getting supported symbols: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/api/analysis/timeframes', methods=['GET'])
def get_supported_timeframes():
    """Get supported analysis timeframes"""
    timeframes = {
        'M1': {'name': '1 Minute', 'minutes': 60},
        'M5': {'name': '5 Minutes', 'minutes': 300},
        'M15': {'name': '15 Minutes', 'minutes': 900},
        'M30': {'name': '30 Minutes', 'minutes': 1800},
        'H1': {'name': '1 Hour', 'minutes': 3600},
        'H4': {'name': '4 Hours', 'minutes': 14400},
        'D1': {'name': 'Daily', 'minutes': 86400}
    }
    
    return jsonify({
        'success': True,
        'data': timeframes
    })

# Error handlers for analysis routes
@analysis_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Analysis endpoint not found'
    }), 404

@analysis_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Analysis route error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
