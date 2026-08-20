import type { PageLoad } from './$types';
import { API_BASE } from '$lib/api/client';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const [tickersRes, newsRes, indicesRes] = await Promise.all([
            fetch(`${API_BASE}/dashboard/tickers`),
            fetch(`${API_BASE}/dashboard/news?limit=15`),
            fetch(`${API_BASE}/dashboard/indices`)
        ]);

        return {
            tickers: tickersRes.ok ? await tickersRes.json() : [],
            news: newsRes.ok ? await newsRes.json() : [],
            indices: indicesRes.ok ? await indicesRes.json() : []
        };
    } catch (e) {
        console.error("Dashboard load error:", e);
        return { tickers: [], news: [], indices: [] };
    }
};
