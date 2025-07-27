# FVG Silver Bullet Lite

A lightweight, standalone version of the FVG Silver Bullet Trading Assistant frontend. This version provides essential trading signal functionality with minimal dependencies and a simple architecture.

## Features

- **Real-time Signal Feed**: Live trading signals via WebSocket
- **Market Overview**: Key market metrics and volatility indicators
- **Lightweight Design**: Minimal dependencies, fast loading
- **Responsive UI**: Works on desktop and mobile devices
- **Dark/Light Theme**: Toggle between themes
- **Sound Notifications**: Optional audio alerts for new signals
- **Signal Export**: Download signal history as JSON
- **Customizable Settings**: Configure WebSocket URL and preferences

## Quick Start

### Prerequisites
- Node.js (for development server)
- Backend services running:
  - Flask API: `http://localhost:5000`
  - WebSocket Server: `ws://localhost:8765`

### Installation

1. Navigate to the lite frontend directory:
```bash
cd frontend-lite
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:3001`

### Production Deployment

For production, simply serve the static files:

```bash
npm run start
```

Or use any static file server:
```bash
npx http-server . -p 3001
```

## Architecture

### File Structure
```
frontend-lite/
├── index.html              # Main HTML file
├── styles.css              # CSS styles
├── app.js                  # Main application controller
├── package.json            # Dependencies and scripts
├── src/
│   ├── services/
│   │   ├── websocket.js    # WebSocket service
│   │   └── api.js          # REST API service
│   ├── utils/
│   │   └── formatters.js   # Data formatting utilities
│   └── components/
│       └── signal-renderer.js  # Signal display component
└── public/                 # Static assets
```

### Technology Stack
- **Pure HTML/CSS/JavaScript**: No frameworks
- **Font Awesome**: Icons
- **Web Audio API**: Sound notifications
- **Local Storage**: Settings persistence
- **Fetch API**: HTTP requests
- **WebSocket API**: Real-time data

## Configuration

### Environment Variables
The application uses default URLs:
- WebSocket: `ws://localhost:8765`
- REST API: `http://localhost:5000`

These can be changed in the settings modal.

### Settings
Settings are automatically saved to browser local storage:
- Sound notifications (on/off)
- Auto-scroll (on/off)
- WebSocket URL
- Theme preference

## API Endpoints Used

- `GET /api/market/overview` - Market overview data
- `GET /api/signals/history?limit=N` - Historical signals
- `GET /api/system/status` - System health check
- `GET /api/market/pairs` - Available trading pairs
- `GET /api/market/data/{symbol}` - Specific market data

## WebSocket Messages

Expected message format:
```json
{
  "symbol": "EURUSD",
  "type": "BUY",
  "price": 1.08543,
  "confidence": 85,
  "timestamp": "2024-01-15T10:30:00Z",
  "stop_loss": 1.08400,
  "take_profit": 1.08700,
  "volume": 1000
}
```

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Development

### Adding New Features

1. **New Services**: Add to `src/services/`
2. **New Components**: Add to `src/components/`
3. **New Utilities**: Add to `src/utils/`
4. **Styling**: Modify `styles.css`

### Building for Production

No build step required - the application is ready to serve as static files.

## Performance

- **Bundle Size**: ~50KB total
- **Load Time**: <1 second on fast connections
- **Memory Usage**: Minimal, suitable for long-running tabs
- **CPU Usage**: Low, efficient DOM updates

## Troubleshooting

### Connection Issues
1. Check if backend services are running
2. Verify WebSocket URL in settings
3. Check browser console for errors

### No Signals Appearing
1. Ensure WebSocket server is sending data
2. Check network tab for WebSocket messages
3. Verify signal format matches expected structure

### Sound Not Working
1. Check browser audio permissions
2. Ensure sound is enabled in settings
3. Some browsers require user interaction first

## License

MIT License - See LICENSE file for details
