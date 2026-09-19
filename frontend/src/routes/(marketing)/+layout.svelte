<script lang="ts">
    import '../../app.css';
    import favicon from '$lib/assets/favicon.svg';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let { children } = $props();

    onMount(() => {
        const token = localStorage.getItem('token');
        if (token) {
            goto('/dashboard', { replaceState: true });
        }
    });
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
