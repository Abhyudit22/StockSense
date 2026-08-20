<script lang="ts">
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";

    let searchInput = $state("");
    let errorMessage = $derived($page.error?.message ?? "Stock not found. Please check the stock name and try again.");
    let symbol = $derived($page.url?.pathname?.split("/").pop()?.toUpperCase() ?? "");

    function handleSearch(e: Event) {
        e.preventDefault();
        if (searchInput.trim()) {
            goto(`/ticker/${searchInput.trim().toUpperCase()}`);
        }
    }
</script>

<div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-xl space-y-6">

        <!-- Top badge -->
        <div class="flex justify-center">
            <span class="inline-flex items-center gap-2 text-xs font-medium text-red-400 bg-red-950/50 border border-red-800/40 px-3 py-1 rounded-full">
                <span class="material-symbols-outlined text-sm">error</span>
                Symbol Not Recognised
            </span>
        </div>

        <!-- Main card -->
        <div class="relative bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl">

            <!-- Gradient top accent -->
            <div class="h-1 w-full bg-gradient-to-r from-red-600 via-orange-500 to-amber-500"></div>

            <div class="p-8 space-y-6">

                <!-- Icon + heading -->
                <div class="text-center space-y-3">
                    <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-red-950/60 border border-red-800/30 mx-auto">
                        <span class="material-symbols-outlined text-3xl text-red-400">manage_search</span>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold text-white">Stock Not Found</h1>
                        {#if symbol}
                            <p class="text-zinc-400 text-sm mt-1">
                                <span class="text-red-400 font-mono font-semibold bg-red-950/40 px-2 py-0.5 rounded">{symbol}</span>
                                is not a valid NSE symbol or may be delisted.
                            </p>
                        {:else}
                            <p class="text-zinc-400 text-sm mt-1">{errorMessage}</p>
                        {/if}
                    </div>
                </div>

                <!-- Search again -->
                <form onsubmit={handleSearch} class="space-y-2">
                    <label class="text-xs text-zinc-500 font-medium uppercase tracking-widest">Try another symbol</label>
                    <div class="flex gap-2">
                        <input
                            bind:value={searchInput}
                            type="text"
                            placeholder="e.g. INFY, SBIN, TCS..."
                            class="flex-1 bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all uppercase font-mono tracking-wider"
                        />
                        <button
                            type="submit"
                            class="px-5 py-3 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors flex items-center gap-2 whitespace-nowrap"
                        >
                            <span class="material-symbols-outlined text-sm">search</span>
                            Analyse
                        </button>
                    </div>
                </form>

                <!-- Tips -->
                <div class="bg-zinc-800/50 border border-zinc-700/50 rounded-xl p-4 space-y-3">
                    <p class="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-sm text-amber-400">tips_and_updates</span>
                        Tips to find the correct symbol
                    </p>
                    <div class="grid grid-cols-1 gap-2">
                        <div class="flex items-start gap-2.5 text-xs text-zinc-400">
                            <span class="material-symbols-outlined text-[14px] text-blue-400 mt-0.5 shrink-0">check_circle</span>
                            Use the official <strong class="text-zinc-200">NSE ticker</strong>, e.g.
                            <code class="text-amber-300 bg-amber-950/40 px-1 rounded">RELIANCE</code>
                            <code class="text-amber-300 bg-amber-950/40 px-1 rounded">HDFCBANK</code>
                            <code class="text-amber-300 bg-amber-950/40 px-1 rounded">TCS</code>
                        </div>
                        <div class="flex items-start gap-2.5 text-xs text-zinc-400">
                            <span class="material-symbols-outlined text-[14px] text-blue-400 mt-0.5 shrink-0">check_circle</span>
                            SBI is listed as <code class="text-amber-300 bg-amber-950/40 px-1 rounded">SBIN</code>, Bajaj Finance as <code class="text-amber-300 bg-amber-950/40 px-1 rounded">BAJFINANCE</code>
                        </div>
                        <div class="flex items-start gap-2.5 text-xs text-zinc-400">
                            <span class="material-symbols-outlined text-[14px] text-orange-400 mt-0.5 shrink-0">warning</span>
                            <code class="text-red-400 bg-red-950/40 px-1 rounded">HDFC</code> was delisted — use
                            <code class="text-amber-300 bg-amber-950/40 px-1 rounded">HDFCBANK</code> instead
                        </div>
                    </div>
                </div>

                <!-- Popular stocks quicklinks -->
                <div class="space-y-2">
                    <p class="text-xs text-zinc-500 uppercase tracking-widest font-medium">Popular stocks</p>
                    <div class="flex flex-wrap gap-2">
                        {#each ["RELIANCE","TCS","INFY","HDFCBANK","TATASTEEL","SBIN","WIPRO","ITC","ADANIENT","BAJFINANCE"] as s}
                            <button
                                onclick={() => goto(`/ticker/${s}`)}
                                class="text-xs font-mono font-semibold px-2.5 py-1 rounded-lg bg-zinc-800 hover:bg-blue-900/50 border border-zinc-700 hover:border-blue-600 text-zinc-300 hover:text-blue-300 transition-all"
                            >
                                {s}
                            </button>
                        {/each}
                    </div>
                </div>
            </div>
        </div>

        <!-- Back link -->
        <div class="text-center">
            <button
                onclick={() => goto("/")}
                class="inline-flex items-center gap-2 text-xs text-zinc-500 hover:text-white transition-colors"
            >
                <span class="material-symbols-outlined text-sm">arrow_back</span>
                Back to StockSense Dashboard
            </button>
        </div>
    </div>
</div>
