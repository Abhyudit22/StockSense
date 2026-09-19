<script lang="ts">
    import '../../app.css';
    import favicon from '$lib/assets/favicon.svg';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { onMount, onDestroy } from 'svelte';

    import Toast from '$lib/components/Toast.svelte';
    import { API_BASE } from '$lib/api/client';

    let { children } = $props();
    
    let isMobileMenuOpen = $state(false);
    let isProfileDropdownOpen = $state(false);
    
    let toastMessage = $state("");
    let toastType = $state<'info'|'alert'|'success'>("info");
    let showToast = $state(false);

    let ws: WebSocket;

    onMount(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            goto('/login', { replaceState: true });
        } else {
            // Connect to WebSocket for live alerts
            const wsUrl = API_BASE.replace('http', 'ws');
            ws = new WebSocket(`${wsUrl}/ws`);
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'alert') {
                        toastMessage = data.message;
                        toastType = data.level || 'info';
                        showToast = true;
                    }
                } catch(e){}
            };
        }
    });

    onDestroy(() => {
        if (ws) ws.close();
    });

    function logout() {
        localStorage.removeItem('token');
        goto('/', { replaceState: true });
    }

    const navItems = [
        { href: "/dashboard", icon: "dashboard", label: "Overview" },
        { href: "/dashboard/screener", icon: "list_alt", label: "Screener" },
        { href: "/dashboard/intelligence", icon: "bolt", label: "Intelligence" },
        { href: "/dashboard/portfolio", icon: "account_balance_wallet", label: "Paper Trading" },
        { href: "/dashboard/watchlist", icon: "star", label: "Watchlist" }
    ];
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
    <title>StockSense | Terminal</title>
</svelte:head>

<div class="min-h-screen bg-black flex overflow-hidden">
    <!-- Sidebar for Desktop -->
    <aside class="hidden md:flex flex-col w-64 border-r border-zinc-800 bg-zinc-950 h-screen sticky top-0 shrink-0 z-50">
        <div class="h-16 flex items-center px-6 border-b border-zinc-800 shrink-0">
            <a href="/" class="flex items-center gap-3 group">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                    <span class="material-symbols-outlined text-white text-base">query_stats</span>
                </div>
                <span class="text-white font-bold tracking-wide text-base group-hover:text-emerald-400 transition-colors">StockSense</span>
            </a>
        </div>
        
        <nav class="flex-1 overflow-y-auto py-6 px-4 space-y-1 custom-scrollbar">
            <div class="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4 px-2">Menu</div>
            {#each navItems as item}
                {@const active = $page.url.pathname === item.href}
                <a 
                    href={item.href} 
                    class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all font-medium text-sm
                           {active ? 'bg-emerald-500/10 text-emerald-400' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'}"
                >
                    <span class="material-symbols-outlined {active ? 'text-emerald-400' : 'text-zinc-500'} text-[20px]">{item.icon}</span>
                    {item.label}
                </a>
            {/each}
        </nav>
        
        <div class="p-4 border-t border-zinc-800 shrink-0 relative">
            <button 
                onclick={() => isProfileDropdownOpen = !isProfileDropdownOpen}
                class="flex items-center justify-between w-full p-2 rounded-xl hover:bg-zinc-900 transition-colors"
            >
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 text-white">
                        <span class="material-symbols-outlined text-sm">person</span>
                    </div>
                    <div class="text-left">
                        <p class="font-bold text-sm text-white leading-tight">Trader</p>
                        <p class="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">Pro Plan</p>
                    </div>
                </div>
                <span class="material-symbols-outlined text-zinc-500 text-sm transition-transform {isProfileDropdownOpen ? 'rotate-180' : ''}">expand_more</span>
            </button>

            {#if isProfileDropdownOpen}
                <!-- Dropdown Menu -->
                <div class="absolute bottom-[72px] left-4 right-4 bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl py-2 z-50 overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-200">
                    <a href="/dashboard/settings" onclick={() => isProfileDropdownOpen = false} class="flex items-center gap-3 px-4 py-2.5 text-sm text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors">
                        <span class="material-symbols-outlined text-[18px]">settings</span>
                        Settings
                    </a>
                    <a href="javascript:void(0)" class="flex items-center gap-3 px-4 py-2.5 text-sm text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors">
                        <span class="material-symbols-outlined text-[18px]">help</span>
                        Support
                    </a>
                    <div class="h-px bg-zinc-800 my-1"></div>
                    <button onclick={logout} class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors text-left">
                        <span class="material-symbols-outlined text-[18px]">logout</span>
                        Log Out
                    </button>
                </div>
            {/if}
        </div>
    </aside>

    <!-- Mobile Header -->
    <div class="md:hidden fixed top-0 left-0 right-0 h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md z-50 flex items-center justify-between px-4">
        <a href="/" class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-emerald-600 flex items-center justify-center">
                <span class="material-symbols-outlined text-white text-sm">query_stats</span>
            </div>
            <span class="text-white font-bold text-sm">StockSense</span>
        </a>
        <button onclick={() => isMobileMenuOpen = !isMobileMenuOpen} class="text-zinc-400 hover:text-white">
            <span class="material-symbols-outlined">{isMobileMenuOpen ? 'close' : 'menu'}</span>
        </button>
    </div>

    <!-- Mobile Menu Overlay -->
    {#if isMobileMenuOpen}
        <div class="md:hidden fixed inset-0 top-16 bg-zinc-950 z-40 border-t border-zinc-800">
            <nav class="p-4 space-y-2">
                {#each navItems as item}
                    {@const active = $page.url.pathname === item.href}
                    <a 
                        href={item.href} 
                        onclick={() => isMobileMenuOpen = false}
                        class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm
                               {active ? 'bg-emerald-500/10 text-emerald-400' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'}"
                    >
                        <span class="material-symbols-outlined {active ? 'text-emerald-400' : 'text-zinc-500'} text-xl">{item.icon}</span>
                        {item.label}
                    </a>
                {/each}
            </nav>
        </div>
    {/if}

    <!-- Main Content -->
    <main class="flex-1 h-screen overflow-y-auto bg-black pt-16 md:pt-0">
        <div class="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
            <!-- Global Dashboard Header (optional depending on page, but nice to have) -->
            <div class="flex items-center justify-between mb-8">
                <h1 class="text-2xl font-bold text-white capitalize">
                    {$page.url.pathname.split('/').pop() || 'Overview'}
                </h1>
                <div class="flex items-center gap-3">
                    <div class="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-3 py-1.5 rounded-full">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        Market Live
                    </div>
                </div>
            </div>
            
            {@render children()}
        </div>
    </main>
</div>

{#if showToast}
    <Toast message={toastMessage} type={toastType} onClose={() => showToast = false} />
{/if}

<style>
    .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        background-color: #27272a;
        border-radius: 20px;
    }
</style>
