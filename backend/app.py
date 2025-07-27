"""
Main Flask Application Entry Point
Initializes Flask, registers blueprints, and can optionally start the websocket server.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from api.analysis_routes import analysis_bp
from api.data_routes import data_bp

# If you implement auth_routes.py, import here:
try:
    from api.auth_routes import auth_bp
except ImportError:
    auth_bp = None

# Import engine and data_streamer for use in aliases
from analysis.silver_bullet_engine import SilverBulletEngine
from deriv_data_streamer import DerivDataStreamer

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(data_bp)
    if auth_bp:
        app.register_blueprint(auth_bp)

    # --- MARKET OVERVIEW ---
    @app.route('/api/market/overview', methods=['GET'])
    def api_market_overview():
        symbol = request.args.get('symbol', 'frxEURUSD')
        engine = SilverBulletEngine()
        summary = engine.get_market_summary(symbol)
        # Get H1 analysis for more relevant stats
        multi = summary.get('multi_timeframe', {})
        h1 = multi.get('H1', {})
        # Map actual values
        volatility = int((h1.get("confidence") or 0) * 100)
        active_pairs = h1.get("setup_count", 0)
        signal_strength = int((h1.get("setup_count") or 0) * 10)
        return jsonify({
            "volatility": volatility,
            "activePairs": active_pairs,
            "signalStrength": signal_strength
        })
    
    # --- MARKET PAIRS ---
    @app.route('/api/market/pairs', methods=['GET'])
    def api_market_pairs():
        streamer = DerivDataStreamer()
        pairs = streamer.get_active_symbols()
        return jsonify({"pairs": [
            {"symbol": s["symbol"], "display_name": s.get("display_name", s["symbol"])}
            for s in pairs if s.get("market") == "forex"
        ]})
    
    # --- MARKET DATA FOR SYMBOL ---
    @app.route('/api/market/data/<symbol>', methods=['GET'])
    def api_market_data(symbol):
        streamer = DerivDataStreamer()
        candles = streamer.get_historical_candles(symbol, 60, 20)
        if not candles:
            return jsonify({"error": "No data"}), 404
        last = candles[-1]
        return jsonify({
            "symbol": symbol,
            "price": last["close"],
            "timestamp": last["timestamp"],
            "candles": candles
        })
    
    # --- SIGNALS HISTORY (stubbed as recent signals) ---
    @app.route('/api/signals/history', methods=['GET'])
    def api_signals_history():
        symbol = request.args.get('symbol', 'frxEURUSD')
        timeframe = request.args.get('timeframe', 'H1')
        limit = int(request.args.get('limit', 20))
        from analysis.silver_bullet_engine import TradeSignalGenerator
        engine = SilverBulletEngine()
        gen = TradeSignalGenerator(engine)
        signals = gen.generate_signals(symbol, timeframe)
        return jsonify({"signals": signals[:limit]})

    # --- SYSTEM STATUS (stub) ---
    @app.route('/api/system/status', methods=['GET'])
    def api_system_status():
        return jsonify({"status": "ok", "uptime": 12345, "message": "System operational"})

    # --- TRADING BALANCE (stub/demo data) ---
    @app.route('/api/trading/balance', methods=['GET'])
    def api_trading_balance():
        # Demo balance structure as per docs
        return jsonify({
            "success": True,
            "balance": {
                "currency": "USD",
                "balance": 10000.0,
                "available": 9500.0,
                "used": 500.0
            }
        })

    # --- TRADING CONFIG (stub/demo data) ---
    @app.route('/api/trading/config', methods=['GET'])
    def api_trading_config():
        return jsonify({
            "max_trade_amount": 10000,
            "min_trade_amount": 1,
            "supported_contract_types": ["CALL", "PUT"],
            "supported_durations": [1, 5, 15, 30, 60]
        })

    # --- HOME ROUTE ---
    @app.route('/')
    def home():
        return jsonify({
            'message': 'FVG Silver Bullet Trading Assistant API',
            'version': '1.0.0',
            'endpoints': {
                'analysis': '/api/analysis',
                'data': '/api/data',
                'auth': '/api/auth',
                'market': '/api/market',
                'trading': '/api/trading',
                'signals': '/api/signals'
            }
        })

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
