/**
 * Mock WebSocket Server for Development
 *
 * Simulates a WebSocket server for development and testing.
 */

export type MockWebSocketMessage = {
  type: 'data' | 'status' | 'error' | 'ping';
  payload: any;
  timestamp: number;
};

export class MockWebSocketServer {
  private messageInterval: number | null = null;
  private dropInterval: number | null = null;
  private connections: Set<MockWebSocket> = new Set();

  constructor(
    private config: {
      messageInterval: number;
      connectionDropChance: number;
      connectionDropInterval: number;
    }
  ) {}

  createConnection(): MockWebSocket {
    const ws = new MockWebSocket(this);
    this.connections.add(ws);
    return ws;
  }

  removeConnection(ws: MockWebSocket): void {
    this.connections.delete(ws);
  }

  broadcast(message: MockWebSocketMessage): void {
    this.connections.forEach((ws) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.triggerMessage(JSON.stringify(message));
      }
    });
  }

  startMessages(): void {
    if (this.messageInterval) return;

    this.messageInterval = window.setInterval(() => {
      const message: MockWebSocketMessage = {
        type: 'data',
        payload: {
          value: Math.random(),
          timestamp: Date.now(),
          message: this.getRandomMessage(),
        },
        timestamp: Date.now(),
      };
      this.broadcast(message);
    }, this.config.messageInterval);

    // Randomly drop connections
    this.dropInterval = window.setInterval(() => {
      if (Math.random() < this.config.connectionDropChance) {
        const connections = Array.from(this.connections);
        if (connections.length > 0) {
          const victim = connections[Math.floor(Math.random() * connections.length)];
          victim.simulateDrop();
        }
      }
    }, this.config.connectionDropInterval);
  }

  stopMessages(): void {
    if (this.messageInterval) {
      clearInterval(this.messageInterval);
      this.messageInterval = null;
    }
    if (this.dropInterval) {
      clearInterval(this.dropInterval);
      this.dropInterval = null;
    }
  }

  private getRandomMessage(): string {
    const messages = [
      'Processing request...',
      'Data updated successfully',
      'New event detected',
      'Status check: OK',
      'Cache refreshed',
      'Background task completed',
      'Metrics collected',
      'Sync complete',
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  }
}

export class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  private _readyState: number = MockWebSocket.CONNECTING;
  private url: string;
  private server: MockWebSocketServer;
  private protocols?: string | string[];
  private messageHandlers: Set<(event: MessageEvent) => void> = new Set();
  private openHandlers: Set<() => void> = new Set();
  private closeHandlers: Set<(event: CloseEvent) => void> = new Set();
  private errorHandlers: Set<(event: Event) => void> = new Set();
  private connectionDelay: number;

  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(
    server: MockWebSocketServer,
    url: string = 'ws://localhost:8080',
    protocols?: string | string[]
  ) {
    this.server = server;
    this.url = url;
    this.protocols = protocols;
    this.connectionDelay = Math.random() * 500 + 100; // 100-600ms

    // Simulate connection delay
    setTimeout(() => {
      this._readyState = MockWebSocket.OPEN;
      this.triggerOpen();
    }, this.connectionDelay);
  }

  get readyState(): number {
    return this._readyState;
  }

  send(data: string): void {
    if (this._readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }

    // Echo back after delay
    setTimeout(() => {
      const parsed = JSON.parse(data);
      const response = {
        type: 'echo',
        payload: parsed,
        timestamp: Date.now(),
      };
      this.triggerMessage(JSON.stringify(response));
    }, 50);
  }

  close(code?: number, reason?: string): void {
    this._readyState = MockWebSocket.CLOSING;
    setTimeout(() => {
      this._readyState = MockWebSocket.CLOSED;
      this.triggerClose({ code: code || 1000, reason: reason || '' });
      this.server.removeConnection(this);
    }, 50);
  }

  simulateDrop(): void {
    this._readyState = MockWebSocket.CLOSING;
    setTimeout(() => {
      this._readyState = MockWebSocket.CLOSED;
      this.triggerClose({ code: 1006, reason: 'Connection dropped' });
      this.server.removeConnection(this);
    }, 50);
  }

  addEventListener(
    type: 'open' | 'message' | 'close' | 'error',
    handler: any
  ): void {
    switch (type) {
      case 'open':
        this.openHandlers.add(handler);
        break;
      case 'message':
        this.messageHandlers.add(handler);
        break;
      case 'close':
        this.closeHandlers.add(handler);
        break;
      case 'error':
        this.errorHandlers.add(handler);
        break;
    }
  }

  removeEventListener(
    type: 'open' | 'message' | 'close' | 'error',
    handler: any
  ): void {
    switch (type) {
      case 'open':
        this.openHandlers.delete(handler);
        break;
      case 'message':
        this.messageHandlers.delete(handler);
        break;
      case 'close':
        this.closeHandlers.delete(handler);
        break;
      case 'error':
        this.errorHandlers.delete(handler);
        break;
    }
  }

  triggerOpen(): void {
    const event = new Event('open');
    this.openHandlers.forEach((h) => h());
    if (this.onopen) this.onopen(event);
  }

  triggerMessage(data: string): void {
    const event = new MessageEvent('message', { data });
    this.messageHandlers.forEach((h) => h(event));
    if (this.onmessage) this.onmessage(event);
  }

  triggerClose(detail: { code: number; reason: string }): void {
    const event = new CloseEvent('close', detail);
    this.closeHandlers.forEach((h) => h(event));
    if (this.onclose) this.onclose(event);
  }

  triggerError(): void {
    const event = new Event('error');
    this.errorHandlers.forEach((h) => h(event));
    if (this.onerror) this.onerror(event);
  }
}

// Singleton instance
let mockServer: MockWebSocketServer | null = null;

export function getMockWebSocketServer(config: {
  messageInterval: number;
  connectionDropChance: number;
  connectionDropInterval: number;
}): MockWebSocketServer {
  if (!mockServer) {
    mockServer = new MockWebSocketServer(config);
  }
  return mockServer;
}

// Patch global WebSocket if in development mode
export function installMockWebSocket(): void {
  (window as any).MockWebSocket = MockWebSocket;
}
