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

            <!-- Trend Chart -->
            <div class="card p-5">
                <h3 class="text-sm font-medium text-white mb-6">30-Day Stock Price Trend</h3>
                <TrendChart data={sentiment.trend_30_days} />
            </div>

            <!-- Source Ledger -->
            <div class="card overflow-hidden">
                <SourceLedger {sources} />
            </div>
        </div>

        <!-- Sidebar -->
        <div class="card overflow-hidden h-[600px] xl:sticky xl:top-20">
            <AgentActivityPanel targetTickerId={null} />
        </div>
    </div>
</div>
