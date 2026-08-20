<script lang="ts">
    import type { PageData } from "./$types";
    import { goto } from "$app/navigation";
    import { onMount, onDestroy } from "svelte";
    import { invalidateAll } from "$app/navigation";

    let { data } = $props<{ data: PageData }>();

    let tickers = $derived(data.tickers ?? []);
    let news    = $derived(data.news ?? []);
    let indices = $derived(data.indices ?? []);

    let searchInput = $state("");
    let now = $state(new Date());
    let timer: number;

    onMount(() => { timer = setInterval(() => { now = new Date(); }, 1000); });
    onDestroy(() => clearInterval(timer));

    function handleSearch(e: Event) {
        e.preventDefault();
        if (searchInput.trim()) goto(`/ticker/${searchInput.trim().toUpperCase()}`);
    }

    // Categorise by sentiment score
    let bullish  = $derived(tickers.filter((t: any) => t.current_score > 0.1).sort((a: any, b: any) => b.current_score - a.current_score));
    let neutral  = $derived(tickers.filter((t: any) => t.current_score >= -0.1 && t.current_score <= 0.1));
    let bearish  = $derived(tickers.filter((t: any) => t.current_score < -0.1).sort((a: any, b: any) => a.current_score - b.current_score));

    function scoreColor(s: number) {
        if (s > 0.1)  return "text-emerald-400";
        if (s < -0.1) return "text-red-400";
        return "text-zinc-400";
    }
    function changeBg(c: number) {
        if (c > 0)  return "bg-emerald-950/60 text-emerald-400 border-emerald-800/40";
        if (c < 0)  return "bg-red-950/60 text-red-400 border-red-800/40";
        return "bg-zinc-800 text-zinc-400 border-zinc-700";
    }
    function sentimentLabel(s: number) {
        if (s > 0.5)  return "Very Bullish";
        if (s > 0.2)  return "Bullish";
        if (s > 0.05) return "Slightly Bullish";
        if (s < -0.5) return "Very Bearish";
        if (s < -0.2) return "Bearish";
        if (s < -0.05) return "Slightly Bearish";
        return "Neutral";
    }
    function sentimentBar(s: number) {
        const pct = Math.min(Math.abs(s) * 100, 100);
        if (s > 0.1)  return { width: pct + "%", color: "bg-emerald-500" };
        if (s < -0.1) return { width: pct + "%", color: "bg-red-500" };
        return { width: "50%", color: "bg-zinc-500" };
    }

    function timeAgo(dt: string) {
        const diff = (Date.now() - new Date(dt).getTime()) / 1000;
        if (diff < 60) return `${Math.floor(diff)}s ago`;
        if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
        return `${Math.floor(diff/3600)}h ago`;
    }

    function formatPrice(p: number) {
        return p >= 10000
            ? p.toLocaleString("en-IN", { maximumFractionDigits: 0 })
            : p.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    let marketTime = $derived(now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }));
    let marketDate = $derived(now.toLocaleDateString("en-IN", { weekday: "short", day: "2-digit", month: "short", year: "numeric" }));
</script>

<div class="space-y-6">

    <!-- ═══════ MARKET INDICES BAR ═══════ -->
    <div class="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div>
                <h1 class="text-2xl font-bold text-white">StockSense</h1>
                <p class="text-zinc-500 text-xs mt-0.5">India Market Intelligence · NSE/BSE · {marketDate}</p>
            </div>
            <div class="flex items-center gap-3">
                <span class="font-mono text-zinc-300 text-sm">{marketTime} IST</span>
                <form onsubmit={handleSearch} class="relative">
                    <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 text-sm">search</span>
                    <input
                        type="text"
                        bind:value={searchInput}
                        placeholder="Search NSE symbol..."
                        class="bg-zinc-800 border border-zinc-700 rounded-xl py-2 pl-9 pr-4 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all uppercase w-52"
                    />
                </form>
            </div>
        </div>

        <!-- Index cards -->
        {#if indices.length > 0}
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {#each indices as idx}
                    {@const up = idx.change_percent >= 0}
                    <div class="relative overflow-hidden bg-zinc-800/60 border {up ? 'border-emerald-800/30' : 'border-red-800/30'} rounded-xl p-4">
                        <div class="absolute top-0 left-0 right-0 h-0.5 {up ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : 'bg-gradient-to-r from-red-500 to-orange-400'}"></div>
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="text-xs text-zinc-500 font-medium uppercase tracking-widest">{idx.name}</p>
                                <p class="text-xl font-bold text-white mt-0.5 font-mono">{formatPrice(idx.price)}</p>
                            </div>
                            <div class="text-right">
                                <span class="inline-flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-lg border {changeBg(idx.change_percent)}">
                                    <span class="material-symbols-outlined text-xs">{up ? 'arrow_drop_up' : 'arrow_drop_down'}</span>
                                    {Math.abs(idx.change_percent).toFixed(2)}%
                                </span>
                                <p class="text-xs text-zinc-500 mt-1 font-mono">{up ? '+' : ''}{idx.change.toFixed(1)}</p>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        {:else}
            <div class="grid grid-cols-3 gap-3">
                {#each ["NIFTY 50","BANK NIFTY","SENSEX"] as name}
                    <div class="bg-zinc-800/40 border border-zinc-700/50 rounded-xl p-4 animate-pulse">
                        <p class="text-xs text-zinc-600 uppercase tracking-widest">{name}</p>
                        <div class="h-6 bg-zinc-700/60 rounded mt-2 w-24"></div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>

    <!-- ═══════ MARKET SUMMARY STATS ═══════ -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-center">
            <p class="text-3xl font-bold text-white">{tickers.length}</p>
            <p class="text-xs text-zinc-500 mt-1 uppercase tracking-widest">Stocks Tracked</p>
        </div>
        <div class="bg-emerald-950/40 border border-emerald-800/30 rounded-xl p-4 text-center">
            <p class="text-3xl font-bold text-emerald-400">{bullish.length}</p>
            <p class="text-xs text-emerald-600 mt-1 uppercase tracking-widest">Bullish</p>
        </div>
        <div class="bg-zinc-900 border border-zinc-700/40 rounded-xl p-4 text-center">
            <p class="text-3xl font-bold text-zinc-400">{neutral.length}</p>
            <p class="text-xs text-zinc-600 mt-1 uppercase tracking-widest">Neutral</p>
        </div>
        <div class="bg-red-950/40 border border-red-800/30 rounded-xl p-4 text-center">
            <p class="text-3xl font-bold text-red-400">{bearish.length}</p>
            <p class="text-xs text-red-600 mt-1 uppercase tracking-widest">Bearish</p>
        </div>
    </div>

    <!-- ═══════ MAIN CONTENT ═══════ -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">

        <!-- Stock lists -->
        <div class="xl:col-span-2 space-y-6">

            <!-- BULLISH -->
            {#if bullish.length > 0}
                <section>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                        <h2 class="text-sm font-semibold text-emerald-400 uppercase tracking-widest">Bullish Stocks</h2>
                        <span class="ml-auto text-xs text-zinc-600">{bullish.length} stocks</span>
                    </div>
                    <div class="space-y-2">
                        {#each bullish as t}
                            {@const bar = sentimentBar(t.current_score)}
                            <button
                                onclick={() => goto(`/ticker/${t.symbol}`)}
                                class="w-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-emerald-800/50 rounded-xl p-4 text-left transition-all group"
                            >
                                <div class="flex items-center justify-between gap-4">
                                    <div class="flex items-center gap-3 min-w-0">
                                        <div class="w-9 h-9 rounded-lg bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center shrink-0">
                                            <span class="text-emerald-400 text-xs font-bold">{t.symbol.slice(0,2)}</span>
                                        </div>
                                        <div class="min-w-0">
                                            <p class="font-semibold text-white text-sm truncate">{t.symbol}</p>
                                            <p class="text-xs text-zinc-500">{t.volume} mentions</p>
                                        </div>
                                    </div>

                                    <!-- Sentiment bar -->
                                    <div class="flex-1 hidden sm:block max-w-[120px]">
                                        <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                            <div class="h-full {bar.color} rounded-full transition-all" style="width:{bar.width}"></div>
                                        </div>
                                        <p class="text-[10px] text-zinc-500 mt-1">{sentimentLabel(t.current_score)}</p>
                                    </div>

                                    <div class="text-right shrink-0">
                                        {#if t.price}
                                            <p class="text-sm font-bold text-white font-mono">₹{formatPrice(t.price)}</p>
                                            {#if t.change_percent !== null}
                                                <p class="text-xs font-medium {t.change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}">
                                                    {t.change_percent > 0 ? '+' : ''}{t.change_percent.toFixed(2)}%
                                                </p>
                                            {/if}
                                        {:else}
                                            <p class="text-xs text-zinc-600">No price</p>
                                        {/if}
                                        <p class="{scoreColor(t.current_score)} text-xs font-mono font-semibold">
                                            {t.current_score > 0 ? '+' : ''}{t.current_score.toFixed(3)}
                                        </p>
                                    </div>

                                    <span class="material-symbols-outlined text-zinc-700 group-hover:text-emerald-500 transition-colors text-sm shrink-0">arrow_forward</span>
                                </div>
                            </button>
                        {/each}
                    </div>
                </section>
            {/if}

            <!-- NEUTRAL -->
            {#if neutral.length > 0}
                <section>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="w-2 h-2 rounded-full bg-zinc-500"></span>
                        <h2 class="text-sm font-semibold text-zinc-400 uppercase tracking-widest">Neutral Stocks</h2>
                        <span class="ml-auto text-xs text-zinc-600">{neutral.length} stocks</span>
                    </div>
                    <div class="space-y-2">
                        {#each neutral as t}
                            <button
                                onclick={() => goto(`/ticker/${t.symbol}`)}
                                class="w-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-600 rounded-xl p-4 text-left transition-all group"
                            >
                                <div class="flex items-center justify-between gap-4">
                                    <div class="flex items-center gap-3 min-w-0">
                                        <div class="w-9 h-9 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center shrink-0">
                                            <span class="text-zinc-400 text-xs font-bold">{t.symbol.slice(0,2)}</span>
                                        </div>
                                        <div class="min-w-0">
                                            <p class="font-semibold text-white text-sm truncate">{t.symbol}</p>
                                            <p class="text-xs text-zinc-500">{t.volume} mentions</p>
                                        </div>
                                    </div>
                                    <div class="flex-1 hidden sm:block max-w-[120px]">
                                        <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                            <div class="h-full bg-zinc-500 rounded-full w-1/2"></div>
                                        </div>
                                        <p class="text-[10px] text-zinc-500 mt-1">Neutral</p>
                                    </div>
                                    <div class="text-right shrink-0">
                                        {#if t.price}
                                            <p class="text-sm font-bold text-white font-mono">₹{formatPrice(t.price)}</p>
                                            {#if t.change_percent !== null}
                                                <p class="text-xs font-medium {t.change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}">
                                                    {t.change_percent > 0 ? '+' : ''}{t.change_percent.toFixed(2)}%
                                                </p>
                                            {/if}
                                        {:else}
                                            <p class="text-xs text-zinc-600">No price</p>
                                        {/if}
                                        <p class="text-zinc-500 text-xs font-mono">{t.current_score.toFixed(3)}</p>
                                    </div>
                                    <span class="material-symbols-outlined text-zinc-700 group-hover:text-zinc-400 transition-colors text-sm shrink-0">arrow_forward</span>
                                </div>
                            </button>
                        {/each}
                    </div>
                </section>
            {/if}

            <!-- BEARISH -->
            {#if bearish.length > 0}
                <section>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="w-2 h-2 rounded-full bg-red-400"></span>
                        <h2 class="text-sm font-semibold text-red-400 uppercase tracking-widest">Bearish Stocks</h2>
                        <span class="ml-auto text-xs text-zinc-600">{bearish.length} stocks</span>
                    </div>
                    <div class="space-y-2">
                        {#each bearish as t}
                            {@const bar = sentimentBar(t.current_score)}
                            <button
                                onclick={() => goto(`/ticker/${t.symbol}`)}
                                class="w-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-red-800/50 rounded-xl p-4 text-left transition-all group"
                            >
                                <div class="flex items-center justify-between gap-4">
                                    <div class="flex items-center gap-3 min-w-0">
                                        <div class="w-9 h-9 rounded-lg bg-red-950/60 border border-red-800/40 flex items-center justify-center shrink-0">
                                            <span class="text-red-400 text-xs font-bold">{t.symbol.slice(0,2)}</span>
                                        </div>
                                        <div class="min-w-0">
                                            <p class="font-semibold text-white text-sm truncate">{t.symbol}</p>
                                            <p class="text-xs text-zinc-500">{t.volume} mentions</p>
                                        </div>
                                    </div>
                                    <div class="flex-1 hidden sm:block max-w-[120px]">
                                        <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                            <div class="h-full {bar.color} rounded-full transition-all" style="width:{bar.width}"></div>
                                        </div>
                                        <p class="text-[10px] text-zinc-500 mt-1">{sentimentLabel(t.current_score)}</p>
                                    </div>
                                    <div class="text-right shrink-0">
                                        {#if t.price}
                                            <p class="text-sm font-bold text-white font-mono">₹{formatPrice(t.price)}</p>
                                            {#if t.change_percent !== null}
                                                <p class="text-xs font-medium {t.change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}">
                                                    {t.change_percent > 0 ? '+' : ''}{t.change_percent.toFixed(2)}%
                                                </p>
                                            {/if}
                                        {:else}
                                            <p class="text-xs text-zinc-600">No price</p>
                                        {/if}
                                        <p class="{scoreColor(t.current_score)} text-xs font-mono font-semibold">
                                            {t.current_score.toFixed(3)}
                                        </p>
                                    </div>
                                    <span class="material-symbols-outlined text-zinc-700 group-hover:text-red-500 transition-colors text-sm shrink-0">arrow_forward</span>
                                </div>
                            </button>
                        {/each}
                    </div>
                </section>
            {/if}

            {#if tickers.length === 0}
                <div class="text-center py-16 text-zinc-600">
                    <span class="material-symbols-outlined text-4xl mb-2 block">monitoring</span>
                    <p>Loading tracked stocks...</p>
                </div>
            {/if}
        </div>

        <!-- ═══════ RIGHT PANEL: Live Intelligence ═══════ -->
        <div class="space-y-4">
            <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-zinc-400 text-sm">bolt</span>
                <h2 class="text-sm font-semibold text-white uppercase tracking-widest">Live Intelligence</h2>
                <span class="ml-auto flex items-center gap-1.5 text-xs text-emerald-400">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    Live
                </span>
            </div>

            <div class="space-y-2 max-h-[780px] overflow-y-auto pr-1 custom-scrollbar">
                {#each news as item}
                    {@const positive = item.score > 0.1}
                    {@const negative = item.score < -0.1}
                    <a
                        href={item.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        class="block bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 rounded-xl p-3.5 transition-all group"
                    >
                        <div class="flex items-start justify-between gap-2 mb-2">
                            <button
                                onclick={(e) => { e.preventDefault(); e.stopPropagation(); goto(`/ticker/${item.symbol}`); }}
                                class="text-[10px] font-bold px-2 py-0.5 rounded-md {positive ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40' : negative ? 'bg-red-950/60 text-red-400 border border-red-800/40' : 'bg-zinc-800 text-zinc-400 border border-zinc-700'} font-mono hover:opacity-80"
                            >
                                {item.symbol}
                            </button>
                            <span class="text-xs font-bold font-mono {positive ? 'text-emerald-400' : negative ? 'text-red-400' : 'text-zinc-500'}">
                                {item.score > 0 ? '+' : ''}{item.score.toFixed(2)}
                            </span>
                        </div>
                        <p class="text-xs text-zinc-300 group-hover:text-white line-clamp-2 leading-relaxed transition-colors">{item.text}</p>
                        <div class="flex items-center justify-between mt-2">
                            <span class="text-[10px] text-zinc-600 capitalize">{item.platform}</span>
                            <span class="text-[10px] text-zinc-600">{timeAgo(item.collected_at)}</span>
                        </div>
                    </a>
                {/each}

                {#if news.length === 0}
                    <div class="text-center py-8 text-zinc-600 text-sm">
                        <span class="material-symbols-outlined block text-3xl mb-2">newspaper</span>
                        Collecting news...
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>
