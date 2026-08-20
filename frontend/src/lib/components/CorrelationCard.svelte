<script lang="ts">
    let { correlationData }: { correlationData: any } = $props();

    let score = $derived(correlationData?.correlation_forward_return ?? correlationData?.correlation_price);

    function getLabel(s: number | null) {
        if (s === null || s === undefined) return 'N/A';
        if (s > 0.5) return 'Strong Positive';
        if (s > 0.2) return 'Weak Positive';
        if (s < -0.5) return 'Strong Negative';
        if (s < -0.2) return 'Weak Negative';
        return 'No Correlation';
    }
    
    function getColor(s: number | null) {
        if (!s) return 'text-zinc-500';
        if (s > 0.2) return 'text-green-500';
        if (s < -0.2) return 'text-red-500';
        return 'text-zinc-300';
    }
</script>

<div class="h-full flex flex-col justify-between">
    <h3 class="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-4">Predictive Edge</h3>

    {#if correlationData && score !== null && score !== undefined}
        <div>
            <div class="flex items-baseline gap-2 mb-2">
                <span class="text-3xl font-semibold {getColor(score)}">
                    {score > 0 ? '+' : ''}{score.toFixed(2)}
                </span>
                <span class="text-xs text-zinc-500">Pearson r</span>
            </div>
            <span class="inline-block text-xs font-medium text-zinc-300 mb-2">
                {getLabel(score)}
            </span>
            <p class="text-xs text-zinc-500 mt-1">
                {correlationData.data_points} overlapping points.
            </p>
        </div>
    {:else}
        <div class="flex-1 flex items-center text-xs text-zinc-600">
            {correlationData?.message || 'Not enough data available.'}
        </div>
    {/if}
</div>
