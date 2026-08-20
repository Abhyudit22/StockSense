<script lang="ts">
    import '../app.css';
    import favicon from '$lib/assets/favicon.svg';

    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
    <title>StockSense — India Market Intelligence</title>
</svelte:head>

<div class="min-h-screen bg-black">
    <nav class="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <a href="/" class="flex items-center gap-3 group">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <span class="material-symbols-outlined text-white text-base">candlestick_chart</span>
                </div>
                <div class="flex flex-col leading-none">
                    <span class="text-white font-bold tracking-wide text-base group-hover:text-blue-400 transition-colors">StockSense</span>
                    <span class="text-zinc-500 text-[10px] tracking-widest uppercase">India Market Intelligence</span>
                </div>
            </a>
            <div class="flex items-center gap-6">
                <a href="/" class="text-zinc-400 hover:text-white text-sm transition-colors flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-sm">dashboard</span>
                    Dashboard
                </a>
                <div class="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-1 rounded-full">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    Live
                </div>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {@render children()}
    </main>
</div>
