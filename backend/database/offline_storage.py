"""
Offline Storage Module
Handles storage of profitable sessions and learning data
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class OfflineStorage:
    """Manages offline storage of trading sessions and learning data"""
    
    def __init__(self, db_path: str = "data/trading_sessions.db"):
        self.db_path = db_path
        self.data_dir = os.path.dirname(db_path)
        
        # Create data directory if it doesn't exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                initial_balance REAL,
                final_balance REAL,
                profit_loss REAL,
                profit_percentage REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                max_drawdown REAL,
                strategy_used TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                trade_id TEXT UNIQUE,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                entry_time DATETIME NOT NULL,
                exit_time DATETIME,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                stop_loss REAL,
                take_profit REAL,
                position_size REAL,
                profit_loss REAL,
                profit_percentage REAL,
                risk_reward_ratio REAL,
                setup_quality REAL,
                confidence REAL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES trading_sessions (session_id)
            )
        ''')
        
        # Create market_conditions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                bias TEXT,
                bias_confidence REAL,
                liquidity_levels TEXT,
                fvgs TEXT,
                silver_bullet_setups TEXT,
                market_volatility REAL,
                trend_strength TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create learning_insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                symbol TEXT,
                timeframe TEXT,
                data TEXT,
                confidence REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def save_session(self, session_data: Dict) -> bool:
        """Save a trading session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trading_sessions (
                    session_id, symbol, timeframe, start_time, end_time,
                    initial_balance, final_balance, profit_loss, profit_percentage,
                    total_trades, winning_trades, losing_trades, max_drawdown,
                    strategy_used, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_data['session_id'],
                session_data['symbol'],
                session_data['timeframe'],
                session_data['start_time'],
                session_data.get('end_time'),
                session_data['initial_balance'],
                session_data.get('final_balance'),
                session_data.get('profit_loss', 0),
                session_data.get('profit_percentage', 0),
                session_data.get('total_trades', 0),
                session_data.get('winning_trades', 0),
                session_data.get('losing_trades', 0),
                session_data.get('max_drawdown', 0),
                session_data.get('strategy_used', 'Silver Bullet'),
                session_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Session saved: {session_data['session_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def save_trade(self, trade_data: Dict) -> bool:
        """Save a trade to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trades (
                    session_id, trade_id, symbol, timeframe, entry_time, exit_time,
                    direction, entry_price, exit_price, stop_loss, take_profit,
                    position_size, profit_loss, profit_percentage, risk_reward_ratio,
                    setup_quality, confidence, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data['session_id'],
                trade_data['trade_id'],
                trade_data['symbol'],
                trade_data['timeframe'],
                trade_data['entry_time'],
                trade_data.get('exit_time'),
                trade_data['direction'],
                trade_data['entry_price'],
                trade_data.get('exit_price'),
                trade_data.get('stop_loss'),
                trade_data.get('take_profit'),
                trade_data.get('position_size'),
                trade_data.get('profit_loss', 0),
                trade_data.get('profit_percentage', 0),
                trade_data.get('risk_reward_ratio', 0),
                trade_data.get('setup_quality', 0),
                trade_data.get('confidence', 0),
                trade_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Trade saved: {trade_data['trade_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
            return False
    
    def save_market_condition(self, condition_data: Dict) -> bool:
        """Save market condition snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO market_conditions (
                    symbol, timeframe, timestamp, bias, bias_confidence,
                    liquidity_levels, fvgs, silver_bullet_setups, market_volatility,
                    trend_strength
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                condition_data['symbol'],
                condition_data['timeframe'],
                condition_data['timestamp'],
                condition_data.get('bias'),
                condition_data.get('bias_confidence'),
                json.dumps(condition_data.get('liquidity_levels', {})),
                json.dumps(condition_data.get('fvgs', {})),
                json.dumps(condition_data.get('silver_bullet_setups', {})),
                condition_data.get('market_volatility'),
                condition_data.get('trend_strength')
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Market condition saved for {condition_data['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving market condition: {e}")
            return False
    
    def save_learning_insight(self, insight_data: Dict) -> bool:
        """Save a learning insight"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_insights (
                    insight_type, title, description, symbol, timeframe, data, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight_data['insight_type'],
                insight_data['title'],
                insight_data.get('description', ''),
                insight_data.get('symbol'),
                insight_data.get('timeframe'),
                json.dumps(insight_data.get('data', {})),
                insight_data.get('confidence', 0)
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Learning insight saved: {insight_data['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving learning insight: {e}")
            return False
    
    def get_profitable_sessions(self, limit: int = 50) -> List[Dict]:
        """Get profitable trading sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trading_sessions 
                WHERE profit_loss > 0 
                ORDER BY profit_percentage DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            sessions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting profitable sessions: {e}")
            return []
    
    def get_session_trades(self, session_id: str) -> List[Dict]:
        """Get all trades for a specific session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades 
                WHERE session_id = ? 
                ORDER BY entry_time
            ''', (session_id,))
            
            columns = [description[0] for description in cursor.description]
            trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return trades
            
        except Exception as e:
            logger.error(f"Error getting session trades: {e}")
            return []
    
    def get_learning_insights(self, insight_type: str = None, limit: int = 20) -> List[Dict]:
        """Get learning insights"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if insight_type:
                cursor.execute('''
                    SELECT * FROM learning_insights 
                    WHERE insight_type = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (insight_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM learning_insights 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            insights = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Parse JSON data
            for insight in insights:
                if insight['data']:
                    insight['data'] = json.loads(insight['data'])
            
            conn.close()
            return insights
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return []
    
    def get_performance_summary(self, days: int = 30) -> Dict:
        """Get performance summary for the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(profit_loss) as total_profit,
                    AVG(profit_percentage) as avg_profit_percentage,
                    SUM(total_trades) as total_trades,
                    SUM(winning_trades) as total_wins,
                    SUM(losing_trades) as total_losses,
                    AVG(max_drawdown) as avg_max_drawdown
                FROM trading_sessions
                WHERE start_time >= ?
            ''', (cutoff_date.isoformat(),))
            
            result = cursor.fetchone()
            summary = {
                'total_sessions': result[0] or 0,
                'total_profit': result[1] or 0,
                'avg_profit_percentage': result[2] or 0,
                'total_trades': result[3] or 0,
                'total_wins': result[4] or 0,
                'total_losses': result[5] or 0,
                'avg_max_drawdown': result[6] or 0,
                'win_rate': (result[4] / max(result[3], 1)) * 100 if result[3] else 0
            }
            
            conn.close()
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    def export_data(self, format: str = 'json') -> str:
        """Export all data to JSON format"""
        try:
            data = {
                'sessions': self.get_profitable_sessions(1000),
                'learning_insights': self.get_learning_insights(limit=1000),
                'performance_summary': self.get_performance_summary(days=365)
            }
            
            filename = f"trading_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Data exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return ""
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data beyond specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM trading_sessions 
                WHERE start_time < ?
            ''', (cutoff_date.isoformat(),))
            
            cursor.execute('''
                DELETE FROM trades 
                WHERE entry_time < ?
            ''', (cutoff_date.isoformat(),))
            
            cursor.execute('''
                DELETE FROM market_conditions 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

# Example usage
if __name__ == "__main__":
    storage = OfflineStorage()
    
    # Example session data
    session_data = {
        'session_id': 'session_001',
        'symbol': 'frxEURUSD',
        'timeframe': 'H1',
        'start_time': datetime.now().isoformat(),
        'initial_balance': 10000,
        'final_balance': 10500,
        'profit_loss': 500,
        'profit_percentage': 5.0,
        'total_trades': 10,
        'winning_trades': 7,
        'losing_trades': 3,
        'max_drawdown': 2.5,
        'strategy_used': 'Silver Bullet',
        'notes': 'Good session with strong FVG setups'
    }
    
    storage.save_session(session_data)
    
    # Get profitable sessions
    sessions = storage.get_profitable_sessions()
    print(f"Found {len(sessions)} profitable sessions")
