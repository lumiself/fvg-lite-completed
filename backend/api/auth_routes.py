"""
Auth API Routes
Implements user registration, login, logout, session validation, and Deriv OAuth URL endpoints.
"""

from flask import Blueprint, request, jsonify
from auth_manager import AuthManager

auth_bp = Blueprint('auth', __name__)
auth_manager = AuthManager()

# --- User Registration ---
@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # For demo, store user in SQLite users table
    import sqlite3
    conn = sqlite3.connect(auth_manager.db_path)
    cursor = conn.cursor()

    # Check uniqueness
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Username already exists"}), 400

    cursor.execute("INSERT INTO users (username, email, access_token) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "User registered successfully"})

# --- User Login ---
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    import sqlite3
    conn = sqlite3.connect(auth_manager.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, username FROM users WHERE username = ? AND access_token = ?", (username, password))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    user_id, email, username = row
    # Create a session
    session_token = auth_manager.create_session(user_id)
    user = {
        "id": user_id,
        "username": username,
        "email": email,
    }
    conn.close()
    return jsonify({"success": True, "session_token": session_token, "user": user})

# --- User Logout ---
@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        session_token = auth_header.split()[1]
        auth_manager.logout_user(session_token)
    return jsonify({"success": True, "message": "Logged out successfully"})

# --- Session Validation ---
@auth_bp.route('/api/auth/validate', methods=['GET'])
def validate():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "error": "Missing token"}), 401
    session_token = auth_header.split()[1]
    user_id = auth_manager.validate_session(session_token)
    if not user_id:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    user = auth_manager.get_user_info(user_id)
    return jsonify({"success": True, "user": user})

# --- Deriv OAuth URL (Mock) ---
@auth_bp.route('/api/auth/deriv/oauth-url', methods=['GET'])
def get_deriv_oauth_url():
    # In production, generate a real OAuth URL
    import secrets
    state = auth_manager.generate_oauth_state()
    oauth_url = f"https://oauth.deriv.com/oauth2/authorize?client_id=demo_client_id&redirect_uri=http://localhost:5000/oauth/callback&state={state}"
    return jsonify({'oauth_url': oauth_url})

# --- Deriv OAuth Callback (Mock) ---
@auth_bp.route('/api/auth/deriv/callback', methods=['POST'])
def deriv_oauth_callback():
    data = request.get_json() or {}
    code = data.get('code')
    state = data.get('state')
    if not code or not state:
        return jsonify({'success': False, 'error': 'Missing code or state'}), 400
    try:
        token_data = auth_manager.exchange_code_for_token(code, state)
        session_token = auth_manager.create_session(token_data['user_id'])
        user = auth_manager.get_user_info(token_data['user_id'])
        return jsonify({'success': True, 'session_token': session_token, 'user': user})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
