"""
Configuration file for Deriv API settings and other application configurations.
"""

class DerivConfig:
    DERIV_APP_ID = '1'  # Deriv's official public app ID for testing
    DERIV_API_TOKEN = '1Do9SNoDFIl6uiT'

    @staticmethod
    def get_ws_url():
        return f"wss://ws.derivws.com/websockets/v3?app_id={DerivConfig.DERIV_APP_ID}"

    @staticmethod
    def validate_config():
        issues = []
        if not DerivConfig.DERIV_APP_ID or DerivConfig.DERIV_APP_ID == 'your_app_id_here':
            issues.append('App ID not configured')
        if not DerivConfig.DERIV_API_TOKEN or DerivConfig.DERIV_API_TOKEN == 'your_api_token_here':
            issues.append('API token not configured')
        return {'is_valid': len(issues) == 0, 'issues': issues}
