<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { agentFeed } from '$lib/stores/agentFeed';

    let { targetTickerId = null }: { targetTickerId?: number | null } = $props();

    onMount(() => { agentFeed.connect(); });
    onDestroy(() => { agentFeed.disconnect(); });

    let filteredEvents = $derived(
        targetTickerId
            ? $agentFeed.filter(e => e.ticker_id === targetTickerId)
            : $agentFeed
    );
</script>

<div class="flex flex-col h-full bg-[#0a0a0a]">
    <div class="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
        <h2 class="text-sm font-medium text-white flex items-center gap-2">
            <span class="material-symbols-outlined text-sm text-zinc-400">terminal</span>
            Live Pipeline Logs
        </h2>
        <div class="flex items-center gap-2">
            <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span class="text-xs text-zinc-500">Active</span>
        </div>
    </div>

    <div class="p-4 flex-1 overflow-y-auto flex flex-col-reverse gap-3 max-h-[500px]">
        {#each filteredEvents as event (event.id)}
            <div class="border-l border-zinc-800 pl-3 py-1 hover:border-zinc-600 transition-colors">
                <div class="text-[10px] text-zinc-500 mb-1 flex items-center gap-2 font-mono">
                    <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
                    <span class="text-zinc-300 font-medium">{event.step_name}</span>
                </div>
                <div class="text-xs text-zinc-400 break-words leading-relaxed font-mono">{event.message}</div>
            </div>
        {/each}

        {#if filteredEvents.length === 0}
            <div class="flex flex-col items-center justify-center h-full text-zinc-600 text-xs py-10">
                Listening for events...
            </div>
        {/if}
    </div>
</div>
