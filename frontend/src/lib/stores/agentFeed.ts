import { writable } from 'svelte/store';

export type AgentEvent = {
    id: number;
    job_id: string;
    ticker_id: number;
    step_name: string;
    message: string;
    timestamp: string;
};

function createAgentFeed() {
    const { subscribe, update, set } = writable<AgentEvent[]>([]);
    let ws: WebSocket | null = null;

    return {
        subscribe,
        connect: () => {
            if (typeof window === 'undefined') return;
            if (ws) return;
            
            // Adjust port if deployed differently
            const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/agent-feed';
            ws = new WebSocket(wsUrl);
            
            ws.onmessage = (event) => {
                try {
                    const data: AgentEvent = JSON.parse(event.data);
                    // Prepend new event and keep last 50
                    update(events => [data, ...events].slice(0, 50));
                } catch (e) {
                    console.error("Error parsing WS message:", e);
                }
            };
            
            ws.onerror = (err) => console.error("AgentFeed WS Error:", err);
            ws.onclose = () => { ws = null; };
        },
        disconnect: () => {
            if (ws) {
                ws.close();
                ws = null;
            }
        },
        reset: () => set([])
    };
}

export const agentFeed = createAgentFeed();
