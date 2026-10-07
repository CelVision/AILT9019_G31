/**
 * WebSocket Protocol Client for ConnectFour Connect
 */

class GameSocketClient {
  constructor(options = {}) {
    this.url = options.url || this.getDefaultWsUrl();
    this.handlers = {};
    this.ws = null;
    this.isConnected = false;
  }

  getDefaultWsUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || '127.0.0.1:8000';
    return `${protocol}//${host}/ws/game`;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.emit('connected');
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.emit('disconnected');
      };

      this.ws.onerror = (err) => {
        this.emit('error', err);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && data.type) {
            this.emit(data.type, data.payload);
          }
        } catch (e) {
          console.error("Failed to parse incoming WS message:", e);
        }
      };
    } catch (e) {
      console.error("WebSocket connection failure:", e);
      this.emit('disconnected');
    }
  }

  send(type, payload = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    } else {
      console.warn("Cannot send message: WebSocket is not open.");
    }
  }

  on(event, handler) {
    if (!this.handlers[event]) this.handlers[event] = [];
    this.handlers[event].push(handler);
  }

  emit(event, payload) {
    if (this.handlers[event]) {
      this.handlers[event].forEach(fn => fn(payload));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
