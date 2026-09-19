<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    
    let { 
        message, 
        type = 'info', 
        onClose 
    } = $props<{ 
        message: string; 
        type?: 'info' | 'success' | 'alert'; 
        onClose: () => void; 
    }>();

    let timer: number;

    onMount(() => {
        timer = setTimeout(() => {
            onClose();
        }, 5000);
    });

    onDestroy(() => {
        if (timer) clearTimeout(timer);
    });
</script>

<div class="fixed bottom-4 right-4 max-w-sm w-full bg-zinc-900 border 
    {type === 'alert' ? 'border-red-500/50 shadow-red-500/20' : 
     type === 'success' ? 'border-emerald-500/50 shadow-emerald-500/20' : 
     'border-blue-500/50 shadow-blue-500/20'} 
    shadow-xl rounded-xl p-4 flex gap-4 animate-in slide-in-from-right-8 fade-in duration-300 z-[100]"
>
    <div class="shrink-0 mt-0.5">
        <span class="material-symbols-outlined 
            {type === 'alert' ? 'text-red-400' : 
             type === 'success' ? 'text-emerald-400' : 
             'text-blue-400'}">
            {type === 'alert' ? 'warning' : type === 'success' ? 'check_circle' : 'notifications_active'}
        </span>
    </div>
    <div class="flex-1">
        <h3 class="text-sm font-bold text-white mb-1">Live Alert</h3>
        <p class="text-sm text-zinc-300">{message}</p>
    </div>
    <button onclick={onClose} class="shrink-0 text-zinc-500 hover:text-white transition-colors">
        <span class="material-symbols-outlined text-sm">close</span>
    </button>
</div>
