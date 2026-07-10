export type CampaignWebSocketEvent = {
  type: string;
  data: Record<string, unknown>;
};

type CampaignWebSocketOptions = {
  campaignId: number;
  token: string;
  onMessage: (event: CampaignWebSocketEvent) => void;
  onOpen?: () => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
};

type CampaignWebSocketConnection = {
  close: () => void;
  send: (payload: unknown) => void;
  readyState: () => number;
};

function buildCampaignWebSocketUrl(campaignId: number, token: string) {
  const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
  const url = new URL(`/ws/campaigns/${campaignId}`, baseUrl);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  url.searchParams.set('token', token);
  return url.toString();
}

export function connectCampaignWebSocket({
  campaignId,
  token,
  onMessage,
  onOpen,
  onClose,
  onError,
}: CampaignWebSocketOptions): CampaignWebSocketConnection {
  let websocket: WebSocket | null = null;
  let reconnectTimer: number | null = null;
  let manuallyClosed = false;
  let reconnectDelayMs = 1000;

  const clearReconnectTimer = () => {
    if (reconnectTimer !== null) {
      window.clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  const shouldReconnect = (event: CloseEvent) => !manuallyClosed && event.code !== 1000 && event.code !== 1008;

  const scheduleReconnect = () => {
    if (manuallyClosed) {
      return;
    }

    clearReconnectTimer();

    reconnectTimer = window.setTimeout(() => {
      reconnectDelayMs = Math.min(reconnectDelayMs * 2, 10000);
      connect();
    }, reconnectDelayMs);
  };

  function connect() {
    if (manuallyClosed) {
      return;
    }

    websocket = new WebSocket(buildCampaignWebSocketUrl(campaignId, token));

    websocket.onopen = () => {
      reconnectDelayMs = 1000;
      onOpen?.();
    };

    websocket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data as string) as Partial<CampaignWebSocketEvent>;

        if (typeof parsed.type === 'string' && parsed.data && typeof parsed.data === 'object') {
          onMessage({
            type: parsed.type,
            data: parsed.data as Record<string, unknown>,
          });
        }
      } catch {
        // Ignore malformed payloads and keep the connection alive.
      }
    };

    websocket.onerror = (event) => {
      onError?.(event);
    };

    websocket.onclose = (event) => {
      onClose?.(event);

      if (shouldReconnect(event)) {
        scheduleReconnect();
      }
    };
  }

  connect();

  return {
    close() {
      manuallyClosed = true;
      clearReconnectTimer();
      websocket?.close(1000, 'Client closed connection');
      websocket = null;
    },
    send(payload: unknown) {
      if (websocket?.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(payload));
      }
    },
    readyState() {
      return websocket?.readyState ?? WebSocket.CLOSED;
    },
  };
}
