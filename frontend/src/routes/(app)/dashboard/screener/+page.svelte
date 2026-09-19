<script lang="ts">
    import { onMount } from "svelte";
    import { API_BASE } from "$lib/api/client";

    let tickers = $state<any[]>([]);
    let isLoading = $state(true);
    let sortColumn = $state("volume");
    let sortAsc = $state(false);
    
    // Advanced Filters
    let searchQuery = $state("");
    let minScore = $state<number>(-1);
    let minVolume = $state<number>(0);

    // Debounce timer for fetching
    let fetchTimer: number;

    async function fetchScreenerData() {
        isLoading = true;
        try {
            const token = localStorage.getItem('token');
            // Build query params
            const params = new URLSearchParams();
            if (searchQuery) params.append('query', searchQuery);
            if (minScore > -1) params.append('min_score', minScore.toString());
            if (minVolume > 0) params.append('min_volume', minVolume.toString());
            
            const res = await fetch(`${API_BASE}/screener/search?${params.toString()}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                tickers = await res.json();
            }
        } catch (e) {
            console.error("Failed to load screener data", e);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        fetchScreenerData();
    });

    function onFilterChange() {
        if (fetchTimer) clearTimeout(fetchTimer);
        fetchTimer = setTimeout(fetchScreenerData, 400); // Debounce API calls
    }

    let sortedTickers = $derived(() => {
        let result = [...tickers];
        result.sort((a, b) => {
            let valA = a[sortColumn];
            let valB = b[sortColumn];
            if (valA === null) valA = -Infinity;
            if (valB === null) valB = -Infinity;

            if (valA < valB) return sortAsc ? -1 : 1;
            if (valA > valB) return sortAsc ? 1 : -1;
            return 0;
        });
        return result;
    });

    function toggleSort(col: string) {
        if (sortColumn === col) {
            sortAsc = !sortAsc;
        } else {
            sortColumn = col;
            sortAsc = false;
        }
    }

    function sentimentLabel(s: number) {
        if (s > 0.1) return "Bullish";
        if (s < -0.1) return "Bearish";
        return "Neutral";
    }
</script>

<div class="space-y-6">
    <div class="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-6 bg-zinc-900 border border-zinc-800 p-6 rounded-xl">
        <h2 class="text-2xl font-bold text-white flex items-center gap-2 shrink-0">
            <span class="material-symbols-outlined text-emerald-500 text-3xl">list_alt</span>
            Advanced Screener
        </h2>
        
        <div class="flex flex-col sm:flex-row items-center gap-6 w-full">
            <!-- Search -->
            <div class="relative w-full sm:w-64 shrink-0">
                <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 text-sm">search</span>
                <input 
                    type="text" 
                    bind:value={searchQuery}
                    oninput={onFilterChange}
                    placeholder="Search symbol..." 
                    class="w-full bg-zinc-950 border border-zinc-800 rounded-lg py-2 pl-9 pr-4 text-sm text-white focus:border-emerald-500 focus:outline-none transition-colors uppercase"
                />
            </div>
            
            <!-- Filters -->
            <div class="flex-1 flex flex-col sm:flex-row items-center gap-6 w-full">
                <div class="w-full">
                    <div class="flex justify-between text-xs text-zinc-400 mb-2">
                        <span>Min Sentiment: {minScore.toFixed(1)}</span>
                    </div>
                    <input type="range" min="-1" max="1" step="0.1" bind:value={minScore} onchange={onFilterChange} class="w-full accent-emerald-500" />
                </div>
                
                <div class="w-full">
                    <div class="flex justify-between text-xs text-zinc-400 mb-2">
                        <span>Min Mentions: {minVolume}</span>
                    </div>
                    <input type="range" min="0" max="500" step="10" bind:value={minVolume} onchange={onFilterChange} class="w-full accent-emerald-500" />
                </div>
            </div>
        </div>
    </div>

    <div class="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-zinc-400">
                <thead class="text-xs text-zinc-500 uppercase bg-zinc-950/50 border-b border-zinc-800">
                    <tr>
                        <th class="px-6 py-4 cursor-pointer hover:text-white" onclick={() => toggleSort('symbol')}>
                            Symbol {sortColumn === 'symbol' ? (sortAsc ? '↑' : '↓') : ''}
                        </th>
                        <th class="px-6 py-4 cursor-pointer hover:text-white" onclick={() => toggleSort('price')}>
                            Price {sortColumn === 'price' ? (sortAsc ? '↑' : '↓') : ''}
                        </th>
                        <th class="px-6 py-4 cursor-pointer hover:text-white" onclick={() => toggleSort('change_percent')}>
                            Change {sortColumn === 'change_percent' ? (sortAsc ? '↑' : '↓') : ''}
                        </th>
                        <th class="px-6 py-4 cursor-pointer hover:text-white" onclick={() => toggleSort('volume')}>
                            Mentions {sortColumn === 'volume' ? (sortAsc ? '↑' : '↓') : ''}
                        </th>
                        <th class="px-6 py-4 cursor-pointer hover:text-white" onclick={() => toggleSort('current_score')}>
                            AI Sentiment {sortColumn === 'current_score' ? (sortAsc ? '↑' : '↓') : ''}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {#if isLoading}
                        <tr><td colspan="5" class="px-6 py-8 text-center text-zinc-500">Loading market data...</td></tr>
                    {:else if sortedTickers.length === 0}
                        <tr><td colspan="5" class="px-6 py-8 text-center text-zinc-500">No stocks match your search.</td></tr>
                    {:else}
                        {#each sortedTickers as t}
                            <tr class="border-b border-zinc-800 hover:bg-zinc-800/50 transition-colors cursor-pointer" onclick={() => window.location.href = `/ticker/${t.symbol}`}>
                                <td class="px-6 py-4 font-bold text-white">
                                    {t.symbol}
                                </td>
                                <td class="px-6 py-4 font-mono text-white">
                                    {t.price ? `₹${t.price.toFixed(2)}` : 'N/A'}
                                </td>
                                <td class="px-6 py-4 font-mono font-medium {t.change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}">
                                    {t.change_percent ? `${t.change_percent > 0 ? '+' : ''}${t.change_percent.toFixed(2)}%` : '-'}
                                </td>
                                <td class="px-6 py-4 text-zinc-300">
                                    {t.volume}
                                </td>
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-2">
                                        <div class="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                            <div class="h-full {t.current_score > 0.1 ? 'bg-emerald-500' : (t.current_score < -0.1 ? 'bg-red-500' : 'bg-zinc-500')} rounded-full" 
                                                 style="width:{Math.min(Math.abs(t.current_score) * 100, 100)}%"></div>
                                        </div>
                                        <span class="text-xs font-mono {t.current_score > 0.1 ? 'text-emerald-400' : (t.current_score < -0.1 ? 'text-red-400' : 'text-zinc-500')}">
                                            {t.current_score.toFixed(2)}
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>
    </div>
</div>
