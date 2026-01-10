import { useState, useEffect } from 'react';
import { CONFIG } from './config';
import { getMockWebSocketServer, installMockWebSocket, MockWebSocket } from './mockWebSocket';
import { useWebSocket, WebSocketStatus, WebSocketProvider, WebSocketStatusAuto, WebSocketStatusConnected, WebSocketStatusDisconnected } from '@ws-fabric/status-indicator';
import type { ConnectionState } from '@ws-fabric/status-indicator';

// Install mock WebSocket
installMockWebSocket();

// --- Components ---

function StatusCard({ state, stats }: { state: ConnectionState; stats: any }) {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Connection Status</h2>
      <WebSocketStatus
        state={state}
        useDot
        size={1.2}
        labels={{
          connected: 'Connected',
          connecting: 'Connecting...',
          reconnecting: 'Reconnecting...',
          disconnected: 'Disconnected',
          error: 'Connection Error',
        }}
        colors={{
          connected: '#22c55e',
          connecting: '#f59e0b',
          reconnecting: '#f59e0b',
          disconnected: '#64748b',
          error: '#ef4444',
        }}
      />

      {state === 'reconnecting' && stats.reconnectionAttempt > 0 && (
        <p className="mt-3 text-sm text-slate-400">
          Reconnect attempt: {stats.reconnectionAttempt}
        </p>
      )}
    </div>
  );
}

function ConnectionStats({ stats }: { stats: any }) {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Statistics</h2>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Connections:</span>
          <span>{stats.connections}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Reconnect Attempts:</span>
          <span>{stats.reconnectionAttempts}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Messages Received:</span>
          <span>{stats.messagesReceived}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Messages Sent:</span>
          <span>{stats.messagesSent}</span>
        </div>
        {stats.uptime > 0 && (
          <div className="flex justify-between">
            <span className="text-slate-400">Uptime:</span>
            <span>{Math.floor(stats.uptime / 1000)}s</span>
          </div>
        )}
      </div>
    </div>
  );
}

function MessageList({ messages }: { messages: Array<{ type: string; data: any; timestamp: number }> }) {
  return (
    <div className="card flex-1 overflow-hidden flex flex-col">
      <h2 className="text-lg font-semibold mb-4">Messages</h2>
      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.length === 0 ? (
          <p className="text-slate-500 text-sm">No messages yet...</p>
        ) : (
          messages.slice(-50).map((msg, i) => (
            <div
              key={i}
              className={`message ${msg.type === 'sent' ? 'message-sent' : 'message-received'}`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs opacity-70">
                  {msg.type === 'sent' ? 'Sent' : 'Received'}
                </span>
                <span className="text-xs opacity-50">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(msg.data, null, 2)}
              </pre>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function ControlPanel({ isConnected, connect, disconnect, send, clear }: {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  send: (message: string) => void;
  clear: () => void;
}) {
  const [message, setMessage] = useState('{"type": "ping"}');

  const handleSend = () => {
    if (message.trim()) {
      send(message);
    }
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Controls</h2>
      <div className="space-y-3">
        <div className="flex gap-2">
          {!isConnected ? (
            <button onClick={connect} className="button button-primary flex-1">
              Connect
            </button>
          ) : (
            <button onClick={disconnect} className="button button-danger flex-1">
              Disconnect
            </button>
          )}
          <button onClick={clear} className="button bg-slate-600 text-white flex-1">
            Clear Messages
          </button>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">Send Message:</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="flex-1 bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm"
              placeholder='{"type": "ping"}'
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button
              onClick={handleSend}
              disabled={!isConnected}
              className="button button-primary"
            >
              Send
            </button>
          </div>
        </div>

        <div className="text-xs text-slate-500">
          <p>Try: {"{"}"type": "ping"}{"}"}</p>
          <p>Or: {"{"}"action": "test"}{"}"}</p>
        </div>
      </div>
    </div>
  );
}

function DashboardContent() {
  const [messages, setMessages] = useState<Array<{ type: string; data: any; timestamp: number }>>([]);

  const { state, isConnected, stats, send, connect, disconnect, resetReconnection } = useWebSocket({
    url: CONFIG.wsUrl,
    reconnection: CONFIG.reconnection,
    immediate: true,
    onMessage: (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prev) => [...prev, { type: 'received', data, timestamp: Date.now() }]);
      } catch {
        setMessages((prev) => [...prev, { type: 'received', data: event.data, timestamp: Date.now() }]);
      }
    },
  });

  const handleSend = (message: string) => {
    try {
      const data = JSON.parse(message);
      send(message);
      setMessages((prev) => [...prev, { type: 'sent', data, timestamp: Date.now() }]);
    } catch (err) {
      alert('Invalid JSON');
    }
  };

  const handleClear = () => {
    setMessages([]);
  };

  // Start mock server messages when connected
  useEffect(() => {
    if (isConnected) {
      const server = getMockWebSocketServer(CONFIG.mockServer);
      server.startMessages();
      return () => server.stopMessages();
    }
  }, [isConnected]);

  return (
    <div className="p-6 space-y-4">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">WebSocket Dashboard</h1>
        <p className="text-slate-400">
          Real-time connection status with auto-reconnection
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatusCard state={state} stats={stats} />
        <ConnectionStats stats={stats} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" style={{ gridTemplateColumns: '2fr 1fr' }}>
        <MessageList messages={messages} />
        <div className="space-y-4">
          <ControlPanel
            isConnected={isConnected}
            connect={connect}
            disconnect={disconnect}
            send={handleSend}
            clear={handleClear}
          />
        </div>
      </div>
    </div>
  );
}

// --- Demo Components ---

function MinimalDemo() {
  const { state, isConnected, connect, disconnect } = useWebSocket({
    url: CONFIG.wsUrl,
    reconnection: CONFIG.reconnection,
  });

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Minimal Example</h2>
      <div className="card space-y-4">
        <WebSocketStatus state={state} useDot size={1.5} />
        <div className="flex gap-2">
          {!isConnected ? (
            <button onClick={connect} className="button button-primary">
              Connect
            </button>
          ) : (
            <button onClick={disconnect} className="button button-danger">
              Disconnect
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function ConditionalDemo() {
  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Conditional Rendering Demo</h2>
      <WebSocketStatusDisconnected>
        <div className="card bg-yellow-900/30 border-yellow-700">
          <p className="text-yellow-300">
            Connection lost. Please wait while we reconnect...
          </p>
        </div>
      </WebSocketStatusDisconnected>

      <WebSocketStatusConnected>
        <div className="card bg-green-900/30 border-green-700">
          <p className="text-green-300">
            Connected! Real-time features are now available.
          </p>
        </div>
      </WebSocketStatusConnected>

      <div className="card mt-4">
        <WebSocketStatusAuto useDot />
      </div>
    </div>
  );
}

// --- Main App ---

type Tab = 'dashboard' | 'minimal' | 'conditional';

function App() {
  const [tab, setTab] = useState<Tab>('dashboard');

  // Create mock WebSocket connection
  useEffect(() => {
    const server = getMockWebSocketServer(CONFIG.mockServer);

    // Override native WebSocket with mock
    const originalWebSocket = (window as any).WebSocket;
    (window as any).WebSocket = function(url: string, protocols?: string | string[]) {
      return server.createConnection();
    };

    return () => {
      (window as any).WebSocket = originalWebSocket;
    };
  }, []);

  return (
    <WebSocketProvider options={{ url: CONFIG.wsUrl, reconnection: CONFIG.reconnection }}>
      <div className="min-h-screen">
        {/* Tab Navigation */}
        <nav className="border-b border-slate-700 bg-slate-900/50">
          <div className="max-w-6xl mx-auto px-4">
            <div className="flex gap-1">
              {[
                { id: 'dashboard', label: 'Dashboard' },
                { id: 'minimal', label: 'Minimal' },
                { id: 'conditional', label: 'Conditional' },
              ].map(({ id, label }) => (
                <button
                  key={id}
                  onClick={() => setTab(id as Tab)}
                  className={`px-4 py-3 text-sm font-medium transition-colors ${
                    tab === id
                      ? 'text-blue-400 border-b-2 border-blue-400'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Tab Content */}
        {tab === 'dashboard' && <DashboardContent />}
        {tab === 'minimal' && <MinimalDemo />}
        {tab === 'conditional' && <ConditionalDemo />}
      </div>
    </WebSocketProvider>
  );
}

export default App;
