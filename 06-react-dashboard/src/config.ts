/**
 * Configuration for the React Dashboard example
 */

export const CONFIG = {
  // WebSocket server URL
  wsUrl: 'ws://localhost:8080',

  // Reconnection settings
  reconnection: {
    enabled: true,
    maxAttempts: -1, // -1 = infinite
    initialDelay: 1000,
    maxDelay: 30000,
    backoffMultiplier: 2,
    jitter: true,
  },

  // Mock server settings
  mockServer: {
    enabled: true,
    messageInterval: 3000, // ms between mock messages
    connectionDropChance: 0.05, // 5% chance to drop connection
    connectionDropInterval: 15000, // check every 15s
  },

  // UI settings
  ui: {
    maxMessages: 50,
    showTimestamps: true,
    showConnectionStats: true,
  },
};
