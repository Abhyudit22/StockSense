<script lang="ts">
    import { onMount } from "svelte";
    import { API_BASE } from "$lib/api/client";

    let watchlist = $state<string[]>([]);
    let stockData = $state<Record<string, any>>({});
    let newSymbol = $state("");
    let isAdding = $state(false);

    onMount(() => {
        const saved = localStorage.getItem("watchlist");
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                watchlist = Array.isArray(parsed) ? parsed : [];
                watchlist.forEach(fetchStockData);
            } catch (e) {}
        } else {
            // Default demo list
            watchlist = ["RELIANCE", "INFY", "TCS"];
            saveWatchlist();
            watchlist.forEach(fetchStockData);
        }
    });

    function saveWatchlist() {
        localStorage.setItem("watchlist", JSON.stringify(watchlist));
    }

    async function fetchStockData(symbol: string) {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE}/tickers/${symbol}/sentiment`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                stockData[symbol] = await res.json();
            } else {
                stockData[symbol] = { error: "Failed to load data" };
            }
        } catch (e) {
            stockData[symbol] = { error: "Network error" };
        }
    }

    async function addSymbol(e: Event) {
        e.preventDefault();
        const sym = newSymbol.trim().toUpperCase();
        if (!sym || watchlist.includes(sym)) return;
        
        isAdding = true;
        try {
            const token = localStorage.getItem('token');
            // Check if it exists/fetch it
            const res = await fetch(`${API_BASE}/tickers/${sym}/sentiment`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                stockData[sym] = await res.json();
                watchlist = [...watchlist, sym];
                saveWatchlist();
                newSymbol = "";
            } else {
                alert(`Could not find symbol: ${sym}`);
            }
        } finally {
            isAdding = false;
        }
    }

    function removeSymbol(sym: string) {
        watchlist = watchlist.filter(s => s !== sym);
        const newData = { ...stockData };
        delete newData[sym];
        stockData = newData;
        saveWatchlist();
    }
</script>

<div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h2 class="text-2xl font-bold text-white flex items-center gap-2">
                <span class="material-symbols-outlined text-amber-400">star</span>
                Personal Watchlist
            </h2>
            <p class="text-zinc-500 text-sm mt-1">Track your favorite stocks closely.</p>
        </div>

        <form onsubmit={addSymbol} class="flex items-center gap-2 w-full sm:w-auto">
            <input 
                type="text" 
                bind:value={newSymbol}
                placeholder="Enter symbol (e.g. HDFCBANK)"
                class="bg-zinc-900 border border-zinc-800 rounded-lg py-2 px-4 text-sm text-white focus:outline-none focus:border-amber-500 transition-colors uppercase w-full sm:w-64"
                required
            />
            <button type="submit" disabled={isAdding} class="bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-zinc-950 px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">add</span>
                Add
            </button>
        </form>
    </div>

    {#if watchlist.length === 0}
        <div class="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-12 text-center">
            <span class="material-symbols-outlined text-5xl text-zinc-700 mb-4 block">monitoring</span>
            <p class="text-zinc-400">Your watchlist is empty.</p>
            <p class="text-zinc-500 text-sm mt-1">Add stocks above to start tracking their sentiment securely.</p>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each watchlist as sym}
                {@const data = stockData[sym]}
                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-5 relative group">
                    <button 
                        onclick={() => removeSymbol(sym)}
                        class="absolute top-4 right-4 text-zinc-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Remove from watchlist"
                    >
                        <span class="material-symbols-outlined text-sm">close</span>
                    </button>

                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-10 h-10 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                            <span class="text-white font-bold">{sym.slice(0, 2)}</span>
                        </div>
                        <div>
                            <h3 class="text-lg font-bold text-white">{sym}</h3>
                        </div>
                    </div>

                    {#if !data}
                        <div class="animate-pulse space-y-2">
                            <div class="h-4 bg-zinc-800 rounded w-1/2"></div>
                            <div class="h-4 bg-zinc-800 rounded w-3/4"></div>
                        </div>
                    {:else if data.error}
                        <p class="text-red-400 text-sm">{data.error}</p>
                    {:else}
                        <div class="space-y-4">
                            <div class="flex justify-between items-end">
                                <div>
                                    <p class="text-xs text-zinc-500 uppercase tracking-widest">Sentiment</p>
                                    <p class="text-xl font-bold font-mono {data.current_score > 0.1 ? 'text-emerald-400' : (data.current_score < -0.1 ? 'text-red-400' : 'text-zinc-400')}">
                                        {data.current_score > 0 ? '+' : ''}{data.current_score.toFixed(2)}
                                    </p>
                                </div>
                                <div class="text-right">
                                    <p class="text-xs text-zinc-500 uppercase tracking-widest">Mentions</p>
                                    <p class="text-lg font-medium text-white">{data.volume}</p>
                                </div>
                            </div>

                            {#if data.ai_analysis}
                                <div class="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
                                    <p class="text-xs text-zinc-400 leading-relaxed line-clamp-3">
                                        <span class="text-emerald-400 font-semibold mr-1">AI Insight:</span>
                                        {data.ai_analysis}
                                    </p>
                                </div>
                            {/if}
                            
                            <a href={`/ticker/${sym}`} class="block text-center text-sm text-zinc-400 hover:text-white bg-zinc-800/50 hover:bg-zinc-800 py-2 rounded-lg transition-colors">
                                View Full Details
                            </a>
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    {/if}
</div>
