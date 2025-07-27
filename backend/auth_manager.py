"""
Authentication Manager (Simplified for Testing)
Handles OAuth token storage and management for Deriv API
"""

import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import sqlite3
import requests
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages OAuth authentication and token storage (simplified version)"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for user storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deriv_user_id TEXT UNIQUE,
                email TEXT,
                username TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create oauth_states table for CSRF protection
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS oauth_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT UNIQUE,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_oauth_state(self, user_id: Optional[int] = None) -> str:
        """Generate a secure OAuth state parameter"""
        state = secrets.token_urlsafe(32)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store state with expiration (10 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        cursor.execute('''
            INSERT INTO oauth_states (state, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (state, user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        return state
    
    def verify_oauth_state(self, state: str) -> bool:
        """Verify OAuth state parameter and clean up"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if state exists and is not expired
        cursor.execute('''
            SELECT id FROM oauth_states 
            WHERE state = ? AND expires_at > ?
        ''', (state, datetime.utcnow()))
        
        result = cursor.fetchone()
        
        if result:
            # Clean up used state
            cursor.execute('DELETE FROM oauth_states WHERE state = ?', (state,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        from config.deriv_config import DerivConfig
        
        # Verify state parameter
        if not self.verify_oauth_state(state):
            raise ValueError("Invalid or expired OAuth state")
        
        # For testing purposes, create a mock token response
        # In production, this would make a real API call to Deriv
        mock_user_info = {
            'authorize': {
                'loginid': '12345678',
                'email': 'test@example.com',
                'username': 'testuser'
            }
        }
        
        mock_token_data = {
            'access_token': f'test_token_{secrets.token_urlsafe(16)}',
            'refresh_token': f'test_refresh_{secrets.token_urlsafe(16)}',
            'expires_in': 3600
        }
        
        # Store user and tokens
        user_id = self._store_user_tokens(mock_user_info, mock_token_data)
        
        return {
            'user_id': user_id,
            'user_info': mock_user_info,
            'access_token': mock_token_data['access_token'],
            'refresh_token': mock_token_data['refresh_token'],
            'expires_in': mock_token_data['expires_in']
        }
    
    def _store_user_tokens(self, user_info: Dict[str, Any], token_data: Dict[str, Any]) -> int:
        """Store user tokens in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate token expiration
        expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600))
        
        # Insert or update user
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (deriv_user_id, email, username, access_token, refresh_token, token_expires_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_info.get('authorize', {}).get('loginid'),
            user_info.get('authorize', {}).get('email'),
            user_info.get('authorize', {}).get('username'),
            token_data['access_token'],
            token_data.get('refresh_token'),
            expires_at,
            datetime.utcnow()
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    
    def refresh_access_token(self, user_id: int) -> Optional[str]:
        """Refresh expired access token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user's refresh token
        cursor.execute('''
            SELECT refresh_token FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            conn.close()
            return None
        
        refresh_token = result[0]
        
        # For testing, generate a new mock token
        new_access_token = f'test_token_{secrets.token_urlsafe(16)}'
        
        # Update stored tokens
        expires_at = datetime.utcnow() + timedelta(seconds=3600)
        
        cursor.execute('''
            UPDATE users 
            SET access_token = ?, token_expires_at = ?, updated_at = ?
            WHERE id = ?
        ''', (new_access_token, expires_at, datetime.utcnow(), user_id))
        
        conn.commit()
        conn.close()
        
        return new_access_token
    
    def get_valid_access_token(self, user_id: int) -> Optional[str]:
        """Get valid access token for user, refreshing if necessary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT access_token, token_expires_at FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        access_token, expires_at = result
        
        # Check if token is expired
        if datetime.fromisoformat(expires_at) <= datetime.utcnow():
            # Token expired, try to refresh
            return self.refresh_access_token(user_id)
        
        # Return token
        return access_token
    
    def create_session(self, user_id: int) -> str:
        """Create a new user session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hour session
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[int]:
        """Validate session and return user_id if valid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM sessions 
            WHERE session_id = ? AND expires_at > ?
        ''', (session_id, datetime.utcnow()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def logout_user(self, session_id: str):
        """Logout user by removing session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT deriv_user_id, email, username, created_at 
            FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            'user_id': user_id,
            'deriv_user_id': result[0],
            'email': result[1],
            'username': result[2],
            'created_at': result[3]
        } 