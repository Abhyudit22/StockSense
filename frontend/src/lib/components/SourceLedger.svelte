<script lang="ts">
    let { sources }: { sources: any } = $props();

    const platformColors: Record<string, string> = {
        mastodon:   'bg-zinc-800 text-zinc-300 border-zinc-700',
        news:       'bg-zinc-800 text-zinc-300 border-zinc-700',
        stocktwits: 'bg-zinc-800 text-zinc-300 border-zinc-700',
        forum:      'bg-zinc-800 text-zinc-300 border-zinc-700',
    };
    function badgeClass(platform: string) {
        return platformColors[platform] ?? 'bg-zinc-900 text-zinc-400 border-zinc-800';
    }
    function scoreClass(s: number) {
        if (s > 0.1) return 'text-green-500';
        if (s < -0.1) return 'text-red-500';
        return 'text-zinc-500';
    }
</script>

<div class="h-full bg-[#0a0a0a]">
    <div class="px-6 py-4 border-b border-zinc-800 flex items-center justify-between bg-black/50">
        <h2 class="text-sm font-medium text-white flex items-center gap-2">
            <span class="material-symbols-outlined text-sm text-zinc-400">receipt_long</span>
            Source Ledger
        </h2>
        <span class="text-xs text-zinc-500">{sources.total} Total Mentions</span>
    </div>

    <div class="divide-y divide-zinc-800/50">
        {#each sources.items as item}
            <div class="px-6 py-4 hover:bg-zinc-900/30 transition-colors">
                <div class="flex justify-between items-start mb-3">
                    <div class="flex items-center gap-3">
                        <span class="inline-flex items-center px-2 py-0.5 text-[10px] font-medium rounded border {badgeClass(item.platform)} capitalize">
                            {item.platform}
                        </span>
                        <span class="text-xs text-zinc-500">By {item.author || 'unknown'}</span>
                    </div>
                    <span class="text-sm font-medium {scoreClass(item.score)}">
                        {item.score > 0 ? '+' : ''}{item.score.toFixed(2)}
                    </span>
                </div>
                
                <p class="text-sm text-zinc-300 mb-3 leading-relaxed">{item.text}</p>
                
                <div class="flex justify-between items-center text-xs text-zinc-500">
                    <span>{new Date(item.collected_at).toLocaleString()}</span>
                    <a href={item.source_url} target="_blank" rel="noopener noreferrer"
                        class="hover:text-white transition-colors flex items-center gap-1">
                        Source <span class="material-symbols-outlined text-[12px]">open_in_new</span>
                    </a>
                </div>
            </div>
        {/each}

        {#if sources.items.length === 0}
            <div class="px-6 py-12 text-center">
                <p class="text-sm text-zinc-500">No sources found.</p>
            </div>
        {/if}
    </div>
</div>
