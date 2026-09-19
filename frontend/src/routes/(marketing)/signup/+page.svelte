<script lang="ts">
    import { goto } from "$app/navigation";
    import { API_BASE } from "$lib/api/client";

    let fname = $state("");
    let lname = $state("");
    let email = $state("");
    let password = $state("");
    let errorMsg = $state("");
    let isLoading = $state(false);

    async function handleSignup(e: Event) {
        e.preventDefault();
        errorMsg = "";
        isLoading = true;
        try {
            const res = await fetch(`${API_BASE}/auth/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ first_name: fname, last_name: lname, email, password })
            });
            const data = await res.json();
            if (res.ok) {
                localStorage.setItem("token", data.access_token);
                goto("/dashboard");
            } else {
                errorMsg = data.detail || "Signup failed";
                if (res.status === 429) {
                    errorMsg = "Too many requests. Please try again in a minute.";
                }
            }
        } catch (err) {
            errorMsg = "Network error. Is the backend running?";
        } finally {
            isLoading = false;
        }
    }
</script>

<svelte:head>
    <title>Sign Up | StockSense</title>
</svelte:head>

<div class="min-h-screen bg-zinc-950 text-white flex items-center justify-center p-6 relative overflow-hidden">
    <!-- Ambient backgrounds -->
    <div class="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 blur-[120px] rounded-full"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/10 blur-[120px] rounded-full"></div>

    <div class="w-full max-w-md bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl relative z-10">
        <div class="text-center mb-8">
            <a href="/" class="inline-flex items-center gap-2 mb-6 hover:opacity-80 transition-opacity">
                <span class="material-symbols-outlined text-emerald-400 text-3xl">query_stats</span>
                <span class="text-xl font-bold tracking-tight">StockSense</span>
            </a>
            <h1 class="text-2xl font-bold mb-2">Create your account</h1>
            <p class="text-sm text-zinc-400">Join thousands of traders mastering the market</p>
        </div>

        <form class="space-y-4" onsubmit={handleSignup}>
            {#if errorMsg}
                <div class="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-xl mb-4">
                    {errorMsg}
                </div>
            {/if}
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label for="fname" class="block text-sm font-medium text-zinc-400 mb-1.5">First name</label>
                    <input type="text" id="fname" bind:value={fname} required class="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors" />
                </div>
                <div>
                    <label for="lname" class="block text-sm font-medium text-zinc-400 mb-1.5">Last name</label>
                    <input type="text" id="lname" bind:value={lname} required class="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors" />
                </div>
            </div>
            <div>
                <label for="email" class="block text-sm font-medium text-zinc-400 mb-1.5">Email address</label>
                <input type="email" id="email" bind:value={email} required class="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors" placeholder="you@example.com" />
            </div>
            <div>
                <label for="password" class="block text-sm font-medium text-zinc-400 mb-1.5">Password</label>
                <input type="password" id="password" bind:value={password} required minlength="6" class="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors" placeholder="••••••••" />
            </div>

            <button type="submit" disabled={isLoading} class="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-zinc-950 font-semibold py-2.5 rounded-xl transition-all shadow-[0_0_15px_rgba(16,185,129,0.2)] hover:shadow-[0_0_20px_rgba(16,185,129,0.4)] mt-4">
                {isLoading ? "Creating..." : "Create Account"}
            </button>
        </form>

        <div class="mt-6 text-center text-sm text-zinc-400">
            Already have an account? 
            <a href="/login" class="text-emerald-400 hover:text-emerald-300 font-medium ml-1">Log in</a>
        </div>
    </div>
</div>
