"""
Commission Manager for FVG Silver Bullet Trading Assistant
Handles markup commission calculations and tracking for monetization
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class CommissionManager:
    """Manages commission calculations and tracking for monetization"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.markup_rate = 0.03  # 3% markup on trades
        self._init_database()
    
    def _init_database(self):
        """Initialize commission tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create commission tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                trade_id TEXT,
                symbol TEXT,
                trade_amount REAL,
                commission_amount REAL,
                commission_rate REAL,
                trade_type TEXT,
                trade_timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create commission summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commission_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                total_commission REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create affiliate tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                affiliate_token TEXT,
                campaign_name TEXT,
                source TEXT,
                medium TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_commission(self, trade_amount: float) -> float:
        """Calculate commission amount based on trade size"""
        return round(trade_amount * self.markup_rate, 2)
    
    def record_commission(self, user_id: int, trade_data: Dict[str, Any]) -> bool:
        """Record commission for a trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            trade_amount = float(trade_data.get('amount', 0))
            commission_amount = self.calculate_commission(trade_amount)
            
            cursor.execute('''
                INSERT INTO commissions 
                (user_id, trade_id, symbol, trade_amount, commission_amount, 
                 commission_rate, trade_type, trade_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                trade_data.get('trade_id'),
                trade_data.get('symbol'),
                trade_amount,
                commission_amount,
                self.markup_rate,
                trade_data.get('trade_type'),
                trade_data.get('timestamp', datetime.utcnow())
            ))
            
            # Update commission summary
            cursor.execute('''
                INSERT OR REPLACE INTO commission_summary 
                (user_id, total_commission, total_trades, last_updated)
                SELECT 
                    user_id,
                    COALESCE((SELECT SUM(commission_amount) FROM commissions WHERE user_id = ?), 0),
                    COALESCE((SELECT COUNT(*) FROM commissions WHERE user_id = ?), 0),
                    ?
                WHERE user_id = ?
            ''', (user_id, user_id, datetime.utcnow(), user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Commission recorded: ${commission_amount} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording commission: {e}")
            return False
    
    def get_user_commissions(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get commission data for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get summary
        cursor.execute('''
            SELECT total_commission, total_trades 
            FROM commission_summary 
            WHERE user_id = ?
        ''', (user_id,))
        
        summary = cursor.fetchone()
        
        # Get recent commissions
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cursor.execute('''
            SELECT trade_id, symbol, trade_amount, commission_amount, 
                   trade_type, trade_timestamp
            FROM commissions 
            WHERE user_id = ? AND trade_timestamp >= ?
            ORDER BY trade_timestamp DESC
        ''', (user_id, cutoff_date))
        
        recent_commissions = cursor.fetchall()
        
        conn.close()
        
        return {
            'user_id': user_id,
            'total_commission': summary[0] if summary else 0,
            'total_trades': summary[1] if summary else 0,
            'recent_commissions': [
                {
                    'trade_id': row[0],
                    'symbol': row[1],
                    'trade_amount': row[2],
                    'commission_amount': row[3],
                    'trade_type': row[4],
                    'trade_timestamp': row[5]
                }
                for row in recent_commissions
            ],
            'markup_rate': self.markup_rate
        }
    
    def get_commission_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive commission dashboard data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get 7-day, 30-day, and all-time stats
        stats = {}
        
        for period in [7, 30, 365]:
            cutoff_date = datetime.utcnow() - timedelta(days=period)
            cursor.execute('''
                SELECT COUNT(*), SUM(commission_amount)
                FROM commissions 
                WHERE user_id = ? AND trade_timestamp >= ?
            ''', (user_id, cutoff_date))
            
            result = cursor.fetchone()
            stats[f'{period}d'] = {
                'trades': result[0] or 0,
                'commission': result[1] or 0
            }
        
        # Get all-time stats
        cursor.execute('''
            SELECT COUNT(*), SUM(commission_amount)
            FROM commissions 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        stats['all_time'] = {
            'trades': result[0] or 0,
            'commission': result[1] or 0
        }
        
        # Get top symbols by commission
        cursor.execute('''
            SELECT symbol, COUNT(*) as trade_count, SUM(commission_amount) as total_commission
            FROM commissions 
            WHERE user_id = ?
            GROUP BY symbol
            ORDER BY total_commission DESC
            LIMIT 5
        ''', (user_id,))
        
        top_symbols = cursor.fetchall()
        
        conn.close()
        
        return {
            'user_id': user_id,
            'markup_rate': self.markup_rate,
            'stats': stats,
            'top_symbols': [
                {
                    'symbol': row[0],
                    'trades': row[1],
                    'commission': row[2]
                }
                for row in top_symbols
            ]
        }
    
    def record_affiliate(self, user_id: int, affiliate_data: Dict[str, str]) -> bool:
        """Record affiliate information for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO affiliate_tracking 
                (user_id, affiliate_token, campaign_name, source, medium)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                affiliate_data.get('affiliate_token'),
                affiliate_data.get('campaign_name'),
                affiliate_data.get('source'),
                affiliate_data.get('medium')
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Affiliate recorded for user {user_id}: {affiliate_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording affiliate: {e}")
            return False
    
    def get_affiliate_stats(self, affiliate_token: str) -> Dict[str, Any]:
        """Get affiliate statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) as referred_users,
                   SUM(c.commission_amount) as total_commission
            FROM affiliate_tracking a
            LEFT JOIN commissions c ON a.user_id = c.user_id
            WHERE a.affiliate_token = ?
        ''', (affiliate_token,))
        
        result = cursor.fetchone()
        
        conn.close()
        
        return {
            'affiliate_token': affiliate_token,
            'referred_users': result[0] or 0,
            'total_commission': result[1] or 0,
            'markup_rate': self.markup_rate
        }
    
    def get_transparency_info(self, user_id: int) -> Dict[str, Any]:
        """Get transparency information for user display"""
        return {
            'markup_rate': self.markup_rate,
            'markup_percentage': f"{self.markup_rate * 100}%",
            'disclosure': "A 3% markup is applied to all trades to support the educational platform.",
            'transparency_note': "This markup is clearly disclosed and helps maintain the free educational tools.",
            'contact': "For questions about commissions, contact support@fvgsilverbullet.com"
        }
