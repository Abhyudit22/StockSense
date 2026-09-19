<script lang="ts">
    import { onMount } from "svelte";
    import { API_BASE } from "$lib/api/client";

    let news = $state<any[]>([]);
    let isLoading = $state(true);

    onMount(async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE}/dashboard/news?limit=50`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                news = await res.json();
            }
        } catch (e) {
            console.error("Failed to load news", e);
        } finally {
            isLoading = false;
        }
    });

    function timeAgo(dt: string) {
        const diff = (Date.now() - new Date(dt).getTime()) / 1000;
        if (diff < 60) return `${Math.floor(diff)}s ago`;
        if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
        return `${Math.floor(diff/86400)}d ago`;
    }
</script>

<div class="space-y-6 max-w-4xl mx-auto">
    <div class="bg-gradient-to-r from-emerald-900/40 to-blue-900/40 border border-emerald-800/30 rounded-2xl p-8">
        <h2 class="text-2xl font-bold text-white flex items-center gap-2 mb-2">
            <span class="material-symbols-outlined text-emerald-400 text-3xl">bolt</span>
            Live Intelligence
        </h2>
        <p class="text-zinc-400 text-sm">Real-time aggregated market sentiment, news, and AI insights from global financial sources.</p>
    </div>

    <div class="space-y-4">
        {#if isLoading}
            <div class="text-center py-12 text-zinc-500">
                <span class="material-symbols-outlined text-4xl mb-2 animate-spin">refresh</span>
                <p>Aggregating global intelligence...</p>
            </div>
        {:else if news.length === 0}
            <div class="text-center py-12 text-zinc-500">
                No recent intelligence gathered.
            </div>
        {:else}
            {#each news as item}
                {@const positive = item.score > 0.1}
                {@const negative = item.score < -0.1}
                <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="block bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 rounded-xl p-5 transition-all group"
                >
                    <div class="flex items-start justify-between gap-4 mb-3">
                        <div class="flex items-center gap-3">
                            <span class="text-xs font-bold px-2 py-1 rounded-md {positive ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40' : negative ? 'bg-red-950/60 text-red-400 border border-red-800/40' : 'bg-zinc-800 text-zinc-400 border border-zinc-700'} font-mono uppercase">
                                {item.symbol}
                            </span>
                            <span class="text-xs text-zinc-500 capitalize flex items-center gap-1">
                                <span class="material-symbols-outlined text-[14px]">public</span>
                                {item.platform}
                            </span>
                        </div>
                        <span class="text-sm font-bold font-mono {positive ? 'text-emerald-400' : negative ? 'text-red-400' : 'text-zinc-500'}">
                            {item.score > 0 ? '+' : ''}{item.score.toFixed(2)}
                        </span>
                    </div>
                    
                    <p class="text-sm text-zinc-300 group-hover:text-white leading-relaxed transition-colors mb-3">
                        {item.text}
                    </p>
                    
                    <div class="flex items-center justify-between text-xs text-zinc-500">
                        <span>{item.author || 'Anonymous Analyst'}</span>
                        <span>{timeAgo(item.collected_at)}</span>
                    </div>
                </a>
            {/each}
        {/if}
    </div>
</div>
