const formatters = {
    formatPrice(price) {
        if (typeof price !== 'number') return price;
        return price.toFixed(5);
    },

    formatTimestamp(timestamp) {
        if (!timestamp) return 'N/A';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays}d ago`;
    },

    formatPercentage(value) {
        if (typeof value !== 'number') return value;
        const sign = value >= 0 ? '+' : '';
        return `${sign}${value.toFixed(2)}%`;
    },

    formatVolume(volume) {
        if (typeof volume !== 'number') return volume;
        
        if (volume >= 1000000) {
            return `${(volume / 1000000).toFixed(1)}M`;
        } else if (volume >= 1000) {
            return `${(volume / 1000).toFixed(1)}K`;
        }
        return volume.toString();
    },

    formatSignalType(type) {
        const types = {
            'BUY': { text: 'BUY', class: 'buy' },
            'SELL': { text: 'SELL', class: 'sell' },
            'HOLD': { text: 'HOLD', class: 'hold' },
            'STRONG_BUY': { text: 'STRONG BUY', class: 'buy' },
            'STRONG_SELL': { text: 'STRONG SELL', class: 'sell' }
        };
        
        return types[type] || { text: type, class: 'neutral' };
    },

    formatConfidence(confidence) {
        if (typeof confidence !== 'number') return confidence;
        
        if (confidence >= 80) return { text: 'High', class: 'high' };
        if (confidence >= 60) return { text: 'Medium', class: 'medium' };
        return { text: 'Low', class: 'low' };
    },

    formatTimeframe(timeframe) {
        const timeframes = {
            '1m': '1 Minute',
            '5m': '5 Minutes',
            '15m': '15 Minutes',
            '1h': '1 Hour',
            '4h': '4 Hours',
            '1d': '1 Day'
        };
        
        return timeframes[timeframe] || timeframe;
    },

    formatCurrency(value, currency = 'USD') {
        if (typeof value !== 'number') return value;
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    },

    formatSignalStrength(strength) {
        if (typeof strength !== 'number') return strength;
        
        if (strength >= 0.8) return { text: 'Strong', class: 'strong', color: '#10b981' };
        if (strength >= 0.6) return { text: 'Moderate', class: 'moderate', color: '#f59e0b' };
        if (strength >= 0.4) return { text: 'Weak', class: 'weak', color: '#ef4444' };
        return { text: 'Very Weak', class: 'very-weak', color: '#6b7280' };
    },

    getTimeAgo(timestamp) {
        if (!timestamp) return 'N/A';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        
        const seconds = Math.floor(diffMs / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return `${seconds} second${seconds !== 1 ? 's' : ''} ago`;
    },

    truncateText(text, maxLength = 50) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    formatNumber(num, decimals = 2) {
        if (typeof num !== 'number') return num;
        return num.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }
};

// Make formatters available globally
window.formatters = formatters;
