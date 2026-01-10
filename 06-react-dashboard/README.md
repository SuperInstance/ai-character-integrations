# Example 6: React Dashboard with WebSocket Status

A real-time dashboard demonstrating the WebSocket status indicator component with auto-reconnection and live updates.

## What This Example Shows

- WebSocket connection management
- Auto-reconnection with exponential backoff
- Status indicators for different connection states
- Message handling and display
- Real-time data visualization

## Running the Example

```bash
# From the integration-examples directory
cd 06-react-dashboard

# Install dependencies
npm install

# Start the development server
npm run dev

# Or build for production
npm run build
npm run preview
```

## Features

### Connection States

| State | Icon | Description |
|-------|------|-------------|
| Connecting | Spinner | Initial connection attempt |
| Connected | WiFi | Successfully connected |
| Reconnecting | Spinner | Auto-reconnecting after disconnect |
| Disconnected | WiFi-off | Disconnected |
| Error | Error icon | Connection error |

### Auto-Reconnection

- Exponential backoff (1s → 2s → 4s → ... → 30s max)
- Configurable max attempts
- Random jitter to prevent thundering herd
- Manual reconnect option

### Mock WebSocket Server

The example includes a mock WebSocket server that:
- Simulates connection delays
- Sends periodic messages
- Simulates connection drops
- Provides echo functionality

## Component Usage

### Basic Status Display

```tsx
import { WebSocketStatus, useWebSocket } from '@ws-fabric/status-indicator';

function Dashboard() {
  const { state, isConnected, connect, disconnect } = useWebSocket({
    url: 'ws://localhost:8080',
  });

  return (
    <div>
      <WebSocketStatus state={state} />
      <button onClick={connect}>Connect</button>
      <button onClick={disconnect}>Disconnect</button>
    </div>
  );
}
```

### Provider Pattern

```tsx
import { WebSocketProvider, WebSocketStatusAuto } from '@ws-fabric/status-indicator';

function App() {
  return (
    <WebSocketProvider options={{ url: 'ws://localhost:8080' }}>
      <Header />
      <Content />
    </WebSocketProvider>
  );
}
```

### Conditional Rendering

```tsx
import {
  WebSocketStatusConnected,
  WebSocketStatusDisconnected,
} from '@ws-fabric/status-indicator';

function ChatApp() {
  return (
    <WebSocketProvider options={{ url: 'ws://localhost:8080' }}>
      <WebSocketStatusDisconnected>
        <div>Connection lost. Reconnecting...</div>
      </WebSocketStatusDisconnected>

      <WebSocketStatusConnected>
        <ChatInterface />
      </WebSocketStatusConnected>
    </WebSocketProvider>
  );
}
```

## Configuration

Edit `src/config.ts` to customize:
- WebSocket URL
- Reconnection settings
- Message handlers
