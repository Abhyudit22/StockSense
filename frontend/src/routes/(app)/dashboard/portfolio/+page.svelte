<script lang="ts">
    import { onMount } from "svelte";
    import { API_BASE } from "$lib/api/client";

    let portfolio = $state<any>(null);
    let isLoading = $state(true);
    let errorMsg = $state("");

    onMount(async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE}/portfolio/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                portfolio = await res.json();
            } else {
                errorMsg = "Failed to load portfolio.";
            }
        } catch (e) {
            errorMsg = "Network error.";
        } finally {
            isLoading = false;
        }
    });

    let totalInvested = $derived(
        portfolio?.positions?.reduce((acc: number, pos: any) => acc + (pos.shares * pos.average_price), 0) || 0
    );
    let totalNetWorth = $derived((portfolio?.cash_balance || 0) + totalInvested);
</script>

<div class="space-y-6">
    <!-- Disclaimer Banner -->
    <div class="bg-blue-900/30 border border-blue-500/50 rounded-xl p-4 flex items-start gap-4">
        <span class="material-symbols-outlined text-blue-400 text-2xl mt-0.5">info</span>
        <div>
            <h3 class="font-bold text-blue-400">Paper Trading Simulator Active</h3>
            <p class="text-blue-200/70 text-sm mt-1">This section is completely separated from your real brokerage. All trades executed here use virtual money (₹1,000,000 starting balance) to safely test the AI's sentiment accuracy against live market prices.</p>
        </div>
    </div>

    {#if isLoading}
        <div class="text-center py-12 text-zinc-500">Loading your virtual portfolio...</div>
    {:else if errorMsg}
        <div class="text-center py-12 text-red-400">{errorMsg}</div>
    {:else}
        <!-- Top Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 class="text-sm font-medium text-zinc-500 uppercase tracking-widest mb-2">Net Worth</h3>
                <p class="text-3xl font-bold font-mono text-white">₹{totalNetWorth.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
            </div>
            <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 class="text-sm font-medium text-zinc-500 uppercase tracking-widest mb-2">Available Cash</h3>
                <p class="text-3xl font-bold font-mono text-emerald-400">₹{portfolio.cash_balance.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
            </div>
            <div class="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 class="text-sm font-medium text-zinc-500 uppercase tracking-widest mb-2">Total Invested</h3>
                <p class="text-3xl font-bold font-mono text-blue-400">₹{totalInvested.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
            </div>
        </div>

        <!-- Holdings Table -->
        <h3 class="text-xl font-bold text-white mt-8 mb-4">Current Holdings</h3>
        <div class="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
            <table class="w-full text-left text-sm text-zinc-400">
                <thead class="text-xs text-zinc-500 uppercase bg-zinc-950/50 border-b border-zinc-800">
                    <tr>
                        <th class="px-6 py-4">Symbol</th>
                        <th class="px-6 py-4 text-right">Shares</th>
                        <th class="px-6 py-4 text-right">Avg Price</th>
                        <th class="px-6 py-4 text-right">Total Cost</th>
                        <th class="px-6 py-4 text-center">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {#if portfolio.positions.length === 0}
                        <tr>
                            <td colspan="5" class="px-6 py-8 text-center text-zinc-500">
                                You have no open positions. Use the Search Hub or Screener to find a stock and execute a paper trade.
                            </td>
                        </tr>
                    {:else}
                        {#each portfolio.positions as pos}
                            <tr class="border-b border-zinc-800 hover:bg-zinc-800/50 transition-colors">
                                <td class="px-6 py-4 font-bold text-white">
                                    <a href="/ticker/{pos.symbol}" class="hover:text-emerald-400 transition-colors">{pos.symbol}</a>
                                </td>
                                <td class="px-6 py-4 text-right font-mono text-white">{pos.shares}</td>
                                <td class="px-6 py-4 text-right font-mono text-zinc-300">₹{pos.average_price.toFixed(2)}</td>
                                <td class="px-6 py-4 text-right font-mono text-white">₹{(pos.shares * pos.average_price).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                                <td class="px-6 py-4 text-center">
                                    <a href="/ticker/{pos.symbol}" class="text-xs bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 px-3 py-1.5 rounded-lg transition-colors font-medium">Trade</a>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>
    {/if}
</div>
