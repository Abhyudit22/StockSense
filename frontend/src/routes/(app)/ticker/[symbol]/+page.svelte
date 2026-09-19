<script lang="ts">
    import type { PageData } from './$types';
    import SourceLedger from '$lib/components/SourceLedger.svelte';
    import AgentActivityPanel from '$lib/components/AgentActivityPanel.svelte';
    import CorrelationCard from '$lib/components/CorrelationCard.svelte';
    import TrendChart from '$lib/components/TrendChart.svelte';
    import { invalidateAll, goto } from '$app/navigation';
    import { onMount, onDestroy } from 'svelte';

    let { data } = $props<{ data: PageData }>();

    let sentiment = $derived(data.sentiment);
    let sources   = $derived(data.sources);
    let correlation = $derived(data.correlation);

    let displayScore = $state(0);
    let isPolling = $state(false);
    let timer: number;
    
    onMount(() => {
        displayScore = sentiment.current_score;
        
        // Auto-poll the API every 3s until today's data arrives
        if (sentiment.volume === 0) {
            isPolling = true;
            timer = setInterval(async () => {
                await invalidateAll();
                if (sentiment.volume > 0) {
                    isPolling = false;
                    displayScore = sentiment.current_score;
                    clearInterval(timer);
                }
            }, 3000);
        }

        // Load TradingView Widget
        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://s3.tradingview.com/tv.js';
        script.async = true;
        script.onload = () => {
            if (typeof (window as any).TradingView !== 'undefined') {
                new (window as any).TradingView.widget({
                    "autosize": true,
                    "symbol": `BSE:${sentiment.symbol}`, // Using BSE prefix as it's Indian stocks
                    "interval": "D",
                    "timezone": "Asia/Kolkata",
                    "theme": "dark",
                    "style": "1",
                    "locale": "in",
                    "enable_publishing": false,
                    "backgroundColor": "rgba(24, 24, 27, 1)",
                    "gridColor": "rgba(39, 39, 42, 1)",
                    "hide_top_toolbar": false,
                    "hide_legend": false,
                    "save_image": false,
                    "container_id": `tradingview_${sentiment.symbol}`,
                    "support_host": "https://www.tradingview.com"
                });
            }
        };
        document.getElementById(`tradingview_${sentiment.symbol}`)?.appendChild(script);
    });

    onDestroy(() => {
        if (timer) clearInterval(timer);
    });

    function scoreLabel(s: number) {
        if (s > 0.5) return 'Very Bullish';
        if (s > 0.2) return 'Bullish';
        if (s > 0.05) return 'Slightly Bullish';
        if (s < -0.5) return 'Very Bearish';
        if (s < -0.2) return 'Bearish';
        if (s < -0.05) return 'Slightly Bearish';
        return 'Neutral';
    }
</script>

<div class="space-y-6 relative">
    {#if isPolling}
        <div class="absolute inset-0 z-50 flex items-start justify-center pt-24 bg-black/80 backdrop-blur-sm rounded-lg">
            <div class="card p-8 flex flex-col items-center text-center max-w-sm w-full border-zinc-700 shadow-2xl">
                <span class="material-symbols-outlined text-4xl text-zinc-400 mb-4 animate-spin" style="animation-duration: 3s;">radar</span>
                <h3 class="text-lg font-semibold text-white mb-2">Analyzing {sentiment.symbol}</h3>
                <p class="text-sm text-zinc-400 mb-6">Booting up background agents to scrape social media, news, and forums...</p>
                
                <!-- Progress bar fake animation -->
                <div class="w-full h-1 bg-zinc-800 rounded-full overflow-hidden">
                    <div class="h-full bg-zinc-500 rounded-full animate-pulse w-full"></div>
                </div>
            </div>
        </div>
    {/if}

    <!-- Header -->
    <div class="flex items-center gap-4 mb-4 border-b border-zinc-800 pb-6 {isPolling ? 'opacity-20 pointer-events-none' : ''}">
        <button onclick={() => goto('/')} class="text-zinc-500 hover:text-white transition-colors flex items-center gap-1.5 text-sm">
            <span class="material-symbols-outlined text-sm">arrow_back</span>
            StockSense
        </button>
        <span class="text-zinc-700">/</span>
        <h1 class="text-xl font-semibold text-white tracking-tight">
            <span class="text-blue-400 font-mono">{sentiment.symbol}</span>
            <span class="text-zinc-400 font-normal text-base ml-1">— Sentiment Report</span>
        </h1>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 {isPolling ? 'opacity-20 pointer-events-none' : ''}">
        <!-- Main Content -->
        <div class="xl:col-span-2 space-y-6">
            
            <!-- AI Analysis Block -->
            {#if sentiment.ai_analysis}
                <div class="card p-6 border-l-2 border-l-white">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="material-symbols-outlined text-sm text-zinc-400">smart_toy</span>
                        <h3 class="text-sm font-medium text-white">AI Sentiment Overview</h3>
                    </div>
                    <p class="text-sm text-zinc-300 leading-relaxed">
                        {sentiment.ai_analysis}
                    </p>
                </div>
            {/if}

            <!-- Metrics -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="card p-5 flex flex-col justify-between">
                    <h3 class="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-4">Live Score</h3>
                    <div>
                        <div class="flex items-baseline gap-2">
                            <span class="text-3xl font-semibold {sentiment.current_score >= 0 ? 'text-green-500' : 'text-red-500'}">
                                {displayScore > 0 ? '+' : ''}{displayScore.toFixed(2)}
                            </span>
                        </div>
                        <p class="mt-2 text-xs text-zinc-400">{scoreLabel(sentiment.current_score)} (Conf: {(sentiment.confidence * 100).toFixed(0)}%)</p>
                    </div>
                </div>

                <div class="card p-5 flex flex-col justify-between">
                    <h3 class="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-4">Data Volume</h3>
                    <div>
                        <div class="text-3xl font-semibold text-white">{sentiment.volume}</div>
                        <p class="mt-2 text-xs text-zinc-400">Mentions Analyzed</p>
                    </div>
                </div>

                <div class="card p-5 flex flex-col justify-between">
                    <CorrelationCard correlationData={correlation} />
                </div>
            </div>

            <!-- TradingView Advanced Chart -->
            <div class="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden p-1 relative" style="height: 600px;">
                <!-- TradingView Widget BEGIN -->
                <div class="tradingview-widget-container" style="height:100%;width:100%">
                    <div id="tradingview_{sentiment.symbol}" style="height:calc(100% - 32px);width:100%"></div>
                    <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div>
                </div>
                <!-- TradingView Widget END -->
            </div>

            <!-- Source Ledger -->
            <div class="card overflow-hidden">
                <SourceLedger {sources} />
            </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
            <!-- Paper Trading Widget -->
            <div class="card p-5 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                <div class="flex items-center gap-2 mb-4">
                    <span class="material-symbols-outlined text-blue-400">account_balance_wallet</span>
                    <h3 class="text-sm font-bold text-white uppercase tracking-wider">Paper Trade Simulator</h3>
                </div>
                
                <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 mb-4 text-center">
                    <p class="text-xs text-zinc-500 mb-1">Current Mock Price</p>
                    <p class="text-2xl font-mono font-bold text-white">₹{sentiment.trend_30_days?.length ? sentiment.trend_30_days[sentiment.trend_30_days.length-1].score.toFixed(2) : '---'}</p>
                </div>
                
                <form class="space-y-4" onsubmit={async (e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target as HTMLFormElement);
                    const action = e.submitter?.getAttribute("value"); // BUY or SELL
                    const shares = parseInt(formData.get("shares") as string);
                    const price = sentiment.trend_30_days?.length ? sentiment.trend_30_days[sentiment.trend_30_days.length-1].score : 0;
                    
                    if (shares > 0 && price > 0 && action) {
                        try {
                            const res = await fetch('http://localhost:8000/api/portfolio/trade', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                                },
                                body: JSON.stringify({
                                    symbol: sentiment.symbol,
                                    shares,
                                    price,
                                    transaction_type: action
                                })
                            });
                            if (res.ok) alert(`Paper Trade: ${action} ${shares} shares successful!`);
                            else alert("Trade failed. Check balance or holding.");
                        } catch(err) {
                            alert("Network error.");
                        }
                    }
                }}>
                    <div>
                        <label for="shares" class="block text-xs font-semibold text-zinc-400 mb-1">Quantity (Shares)</label>
                        <input type="number" id="shares" name="shares" min="1" required class="w-full bg-zinc-900 border border-zinc-800 rounded-lg py-2 px-3 text-white focus:outline-none focus:border-blue-500" placeholder="10">
                    </div>
                    
                    <div class="grid grid-cols-2 gap-3">
                        <button type="submit" name="action" value="BUY" class="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 font-bold py-2 rounded-lg transition-colors">BUY</button>
                        <button type="submit" name="action" value="SELL" class="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 font-bold py-2 rounded-lg transition-colors">SELL</button>
                    </div>
                </form>
            </div>

            <!-- Agent Activity -->
            <div class="card overflow-hidden h-[400px]">
                <AgentActivityPanel targetTickerId={null} />
            </div>
        </div>
    </div>
</div>
