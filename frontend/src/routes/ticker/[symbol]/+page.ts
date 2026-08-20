import { error } from '@sveltejs/kit';
import { API_BASE } from '$lib/api/client';
import { getSources, getCorrelation } from '$lib/api/client';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
    const symbol = params.symbol.toUpperCase();
    
    // Fetch sentiment first so we can surface the backend error message clearly
    const sentimentRes = await fetch(`${API_BASE}/tickers/${symbol}/sentiment`);
    
    if (!sentimentRes.ok) {
        let detail = 'Stock not found. Please check the stock name and try again.';
        try {
            const body = await sentimentRes.json();
            if (body?.detail) detail = body.detail;
        } catch (_) {}
        throw error(sentimentRes.status, detail);
    }

    const sentiment = await sentimentRes.json();

    const [sources, correlation] = await Promise.all([
        getSources(symbol, 1, 20, fetch).catch(() => ({ items: [], total: 0, page: 1, size: 20 })),
        getCorrelation(symbol, 30, fetch).catch(() => null)
    ]);

    return { sentiment, sources, correlation };
};
