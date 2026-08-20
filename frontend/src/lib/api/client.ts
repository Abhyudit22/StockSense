let _base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
if (_base && !_base.endsWith('/api')) { _base = _base.replace(/\/$/, '') + '/api'; }
export const API_BASE = _base;

export async function getSentiment(symbol: string, customFetch: typeof fetch = fetch) {
    const res = await customFetch(`${API_BASE}/tickers/${symbol}/sentiment`);
    if (!res.ok) throw new Error("Failed to fetch sentiment");
    return res.json();
}

export async function getSources(symbol: string, page: number = 1, size: number = 20, customFetch: typeof fetch = fetch) {
    const res = await customFetch(`${API_BASE}/tickers/${symbol}/sources?page=${page}&size=${size}`);
    if (!res.ok) throw new Error("Failed to fetch sources");
    return res.json();
}

export async function getUpcomingIpos(customFetch: typeof fetch = fetch) {
    const res = await customFetch(`${API_BASE}/ipo/upcoming`);
    if (!res.ok) throw new Error("Failed to fetch IPOs");
    return res.json();
}

export async function getIpoReport(ticker: string, customFetch: typeof fetch = fetch) {
    const res = await customFetch(`${API_BASE}/ipo/${ticker}/report`);
    if (!res.ok) throw new Error("Failed to fetch IPO report");
    return res.json();
}

export async function getCorrelation(symbol: string, days: number = 30, customFetch: typeof fetch = fetch) {
    const res = await customFetch(`${API_BASE}/analytics/${symbol}/correlation?days=${days}`);
    if (!res.ok) throw new Error("Failed to fetch correlation data");
    return res.json();
}

export async function getIndices(customFetch: typeof fetch = fetch) {
    const res = await customFetch(`${API_BASE}/dashboard/indices`);
    if (!res.ok) return [];
    return res.json();
}
