<script lang="ts">
    import { onMount, onDestroy } from "svelte";

    // Fake ticker data for the landing page
        import { intersect } from "$lib/actions/intersect";
    import { spotlight } from "$lib/actions/spotlight";
    
    let section1Visible = $state(false);
    let section2Visible = $state(false);

    const stocks = [
        { symbol: "RELIANCE", price: 2984.50, change: 1.2 },
        { symbol: "HDFCBANK", price: 1642.10, change: -0.5 },
        { symbol: "INFY", price: 1420.30, change: 0.8 },
    ];

    let mouseX = $state(0);
    let mouseY = $state(0);
    let time = $state(0);

    let animationFrame: number;

    function handleMouseMove(event: MouseEvent) {
        // Normalize mouse coordinates to -1 to 1
        mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    function loop() {
        time += 0.01;
        animationFrame = requestAnimationFrame(loop);
    }

    onMount(() => {
        window.addEventListener("mousemove", handleMouseMove);
        loop();
    });

    onDestroy(() => {
        if (typeof window !== "undefined") {
            window.removeEventListener("mousemove", handleMouseMove);
            cancelAnimationFrame(animationFrame);
        }
    });

    // We add base rotation to make the 3D scene look like it's viewed from an angle
    let rotationX = $derived(20 + mouseY * 15);
    let rotationY = $derived(-30 + mouseX * 25);
</script>

<svelte:head>
    <title>StockSense | Next-Gen Market Intelligence</title>
</svelte:head>

<div class="min-h-screen bg-zinc-950 text-white overflow-x-hidden relative font-sans flex flex-col">
    <!-- Ambient animated background blobs -->
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-600/20 blur-[120px] rounded-full animate-blob"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-600/20 blur-[120px] rounded-full animate-blob" style="animation-delay: 2s"></div>
    <div class="absolute top-[40%] left-[60%] w-[30%] h-[30%] bg-purple-600/20 blur-[120px] rounded-full animate-blob" style="animation-delay: 4s"></div>

    <!-- Navbar -->
    <header class="relative z-20 p-6 flex items-center justify-between border-b border-white/5 bg-zinc-950/50 backdrop-blur-md">
        <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-emerald-400 text-3xl">query_stats</span>
            <span class="text-xl font-bold tracking-tight">StockSense</span>
        </div>
        <div class="flex items-center gap-4">
            <a href="/login" class="text-sm font-medium text-zinc-300 hover:text-white transition-colors">Log In</a>
            <a href="/signup" class="text-sm font-medium bg-emerald-500 hover:bg-emerald-400 text-zinc-950 px-4 py-2 rounded-full transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] hover:shadow-[0_0_25px_rgba(16,185,129,0.5)]">
                Sign Up Free
            </a>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 relative z-10 container mx-auto px-6 flex flex-col lg:flex-row items-center justify-center gap-12 pt-12 lg:pt-0 h-[calc(100vh-80px)]">
        
        <!-- Left: Copy -->
        <div class="flex-1 max-w-2xl text-center lg:text-left z-20 pointer-events-none">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-6 backdrop-blur-sm pointer-events-auto">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="text-xs font-medium text-emerald-400 uppercase tracking-widest">Live Market Intelligence</span>
            </div>
            
            <h1 class="text-5xl lg:text-7xl font-bold tracking-tight mb-6 leading-tight pointer-events-auto">
                Master the <br/>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">
                    Indian Markets
                </span>
            </h1>
            
            <p class="text-lg lg:text-xl text-zinc-400 mb-8 max-w-lg mx-auto lg:mx-0 leading-relaxed pointer-events-auto">
                Experience real-time stock tracking, advanced sentiment analysis, and interactive 3D visualizations built for the modern trader.
            </p>
            
            <div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pointer-events-auto">
                <a href="/signup" class="w-full sm:w-auto text-center font-semibold bg-emerald-500 hover:bg-emerald-400 text-zinc-950 px-8 py-3.5 rounded-full transition-all shadow-[0_0_20px_rgba(16,185,129,0.4)] hover:shadow-[0_0_30px_rgba(16,185,129,0.6)]">
                    Get Started
                </a>
                <a href="/dashboard" class="w-full sm:w-auto text-center font-medium bg-white/5 hover:bg-white/10 border border-white/10 text-white px-8 py-3.5 rounded-full transition-all backdrop-blur-sm">
                    View Demo Dashboard
                </a>
            </div>
        </div>

        <!-- Right: Complex 3D Visualization Area -->
        <div class="flex-1 w-full absolute inset-0 lg:relative lg:inset-auto h-full lg:h-[600px] flex items-center justify-center perspective-container overflow-visible z-10 pointer-events-none">
            
            <div class="scene-3d w-full h-full absolute lg:relative" style="transform: rotateX({rotationX}deg) rotateY({rotationY}deg);">
                
                <!-- Connecting Strings (SVG overlay inside 3D space) -->
                <!-- Note: True 3D lines in CSS are hard, but we can simulate them by placing rotated thin divs -->
                <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-0 h-0 element-3d">
                    {#each Array(5) as _, i}
                        <div class="absolute bg-emerald-500/30 origin-left"
                             style="
                                width: {150 + Math.random() * 100}px;
                                height: 1px;
                                transform: 
                                    rotateX({Math.sin(time + i) * 360}deg) 
                                    rotateY({Math.cos(time + i) * 360}deg) 
                                    rotateZ({time * 20 + i * 72}deg);
                                box-shadow: 0 0 8px rgba(16,185,129,0.5);
                             ">
                        </div>
                    {/each}
                </div>

                <!-- 3D Grid Plane -->
                <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] element-3d border border-emerald-900/30"
                     style="
                        transform: rotateX(90deg) translateZ(-150px);
                        background-image: 
                            linear-gradient(to right, rgba(16,185,129,0.1) 1px, transparent 1px),
                            linear-gradient(to bottom, rgba(16,185,129,0.1) 1px, transparent 1px);
                        background-size: 50px 50px;
                     ">
                    
                    <!-- 3D Bar Graphs growing from the plane -->
                    {#each Array(16) as _, i}
                        {@const row = Math.floor(i / 4)}
                        {@const col = i % 4}
                        {@const height = 50 + (Math.sin(time * 2 + i) * 0.5 + 0.5) * 150}
                        <div class="absolute w-8 element-3d transition-all duration-75"
                             style="
                                left: {col * 100 + 200}px;
                                top: {row * 100 + 200}px;
                                height: {height}px;
                                transform-origin: bottom;
                                transform: rotateX(-90deg) translateZ(0);
                                background: linear-gradient(to top, rgba(16,185,129,0.2), rgba(16,185,129,0.8));
                                border: 1px solid rgba(16,185,129,0.5);
                                box-shadow: 0 0 20px rgba(16,185,129,0.2);
                             ">
                             <!-- Top cap of the bar -->
                             <div class="absolute top-0 left-0 w-full h-8 bg-emerald-400/80 element-3d border border-emerald-300"
                                  style="transform: rotateX(90deg) translateZ(16px); transform-origin: top;"></div>
                        </div>
                    {/each}
                </div>

                <!-- Floating Stock Cards -->
                {#each stocks as stock, i}
                    {@const up = stock.change >= 0}
                    <div 
                        class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 element-3d"
                        style="
                            transform: translate3d(
                                {Math.sin(time + i * 2.1) * 180}px, 
                                {Math.cos(time + i * 1.5) * 100 - 50}px, 
                                {Math.sin(time * 0.8 + i) * 150}px
                            );
                        "
                    >
                        <div class="bg-zinc-900/80 backdrop-blur-md border border-white/10 p-4 rounded-xl shadow-2xl w-48 
                                    {up ? 'shadow-emerald-500/20' : 'shadow-red-500/20'} pointer-events-auto cursor-pointer hover:scale-110 transition-transform">
                            <div class="flex justify-between items-start mb-3">
                                <div class="font-bold text-white text-sm">{stock.symbol}</div>
                                <div class="text-xs font-mono font-medium px-1.5 py-0.5 rounded 
                                            {up ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
                                    {up ? '+' : ''}{stock.change}%
                                </div>
                            </div>
                            <div class="text-xl font-mono text-white">₹{stock.price.toFixed(2)}</div>
                        </div>
                    </div>
                {/each}
                
                <!-- Floating Money Symbols -->
                {#each ['₹', '$', '₹', '€', '₹'] as symbol, i}
                    <div 
                        class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 element-3d text-4xl font-bold text-emerald-400/60 drop-shadow-[0_0_15px_rgba(16,185,129,0.8)]"
                        style="
                            transform: translate3d(
                                {Math.cos(time * 1.2 + i * 3) * 250}px, 
                                {Math.sin(time * 0.9 + i * 2) * 200}px, 
                                {Math.cos(time * 0.5 + i) * 200}px
                            ) rotateY({time * 100 + i * 50}deg);
                        "
                    >
                        {symbol}
                    </div>
                {/each}

                <!-- Central glowing orb -->
                <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-emerald-500/20 rounded-full blur-3xl animate-pulse element-3d" style="transform: translateZ(-50px);"></div>
                </div>
            </div>
        </div>

    </main>

    <!-- Marquee Ticker Section -->
    <div class="w-full bg-zinc-900/50 border-y border-white/5 py-4 overflow-hidden relative z-20 pointer-events-auto">
        <div class="animate-marquee flex gap-8 items-center">
            {#each [...stocks, ...stocks, ...stocks, ...stocks, ...stocks, ...stocks] as stock, i}
                {@const up = stock.change >= 0}
                <div class="flex items-center gap-3 shrink-0 mx-8">
                    <span class="font-bold text-zinc-300">{stock.symbol}</span>
                    <span class="font-mono text-sm {up ? 'text-emerald-400' : 'text-red-400'}">
                        ₹{stock.price.toFixed(2)}
                    </span>
                    <span class="text-xs {up ? 'text-emerald-500/70' : 'text-red-500/70'}">
                        {up ? '▲' : '▼'} {Math.abs(stock.change)}%
                    </span>
                </div>
            {/each}
        </div>
    </div>

    <!-- Features & Graphs Section -->
    <section class="w-full max-w-7xl mx-auto px-6 py-24 relative z-20 pointer-events-auto">
        <div class="text-center mb-16 fade-in-up" use:intersect={{ onEnter: () => section1Visible = true }} class:visible={section1Visible}>
            <h2 class="text-3xl lg:text-5xl font-bold mb-6">Smarter Analytics, Faster Decisions</h2>
            <p class="text-zinc-400 max-w-2xl mx-auto text-lg">
                Harness the power of AI to analyze thousands of news articles, tweets, and forum posts in seconds. 
                Visualized beautifully for the modern trader.
            </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 fade-in-up" use:intersect={{ onEnter: () => section2Visible = true }} class:visible={section2Visible}>
            <!-- Fake Graph Card 1 -->
            <div class="spotlight-card group relative bg-zinc-900/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm transition-colors overflow-hidden" use:spotlight>
                <!-- Spotlight Hover Effect -->
                <div class="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition duration-300 group-hover:opacity-100" 
                     style="background: radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(16, 185, 129, 0.15), transparent 40%); z-index: 0;">
                </div>
                <div class="pointer-events-none absolute -inset-px rounded-2xl border border-emerald-500/50 opacity-0 transition duration-300 group-hover:opacity-100" 
                     style="mask-image: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), black, transparent); -webkit-mask-image: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), black, transparent); z-index: 0;">
                </div>
                <div class="relative z-10">
                <h3 class="text-xl font-bold mb-2">Live Sentiment Index</h3>
                <p class="text-sm text-zinc-500 mb-6">Real-time bullish/bearish divergence across multiple timeframes.</p>
                <div class="h-48 flex items-end gap-2">
                    {#each Array(20) as _, i}
                        <div class="flex-1 bg-gradient-to-t from-emerald-900/50 to-emerald-500 rounded-t-sm" 
                             style="height: {30 + Math.random() * 70}%; opacity: {0.3 + (i/20) * 0.7}">
                        </div>
                    {/each}
                </div>
                </div>
            </div>

            <!-- Fake Graph Card 2 -->
            <div class="spotlight-card group relative bg-zinc-900/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm transition-colors overflow-hidden" use:spotlight>
                <!-- Spotlight Hover Effect -->
                <div class="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition duration-300 group-hover:opacity-100" 
                     style="background: radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(16, 185, 129, 0.15), transparent 40%); z-index: 0;">
                </div>
                <div class="pointer-events-none absolute -inset-px rounded-2xl border border-emerald-500/50 opacity-0 transition duration-300 group-hover:opacity-100" 
                     style="mask-image: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), black, transparent); -webkit-mask-image: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), black, transparent); z-index: 0;">
                </div>
                <div class="relative z-10">
                <h3 class="text-xl font-bold mb-2">Volume Analysis</h3>
                <p class="text-sm text-zinc-500 mb-6">Identify institutional accumulation phases before retail breakdown.</p>
                <div class="h-48 relative overflow-hidden flex flex-col justify-end gap-2">
                    <!-- Lines simulation -->
                    <svg class="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                        <path d="M0,100 C50,80 150,120 200,60 S300,100 400,20 L500,200 L0,200 Z" fill="rgba(16,185,129,0.1)" stroke="rgba(16,185,129,0.5)" stroke-width="2"/>
                    </svg>
                    {#each Array(15) as _, i}
                        <div class="w-full bg-zinc-800/50 h-px"></div>
                    {/each}
                </div>
                </div>
            </div>
        </div>
    </section>

</div>

<style>
    :global(body) {
        margin: 0;
        background-color: #09090b;
    }

    .perspective-container {
        perspective: 1000px;
    }

    .scene-3d {
        transform-style: preserve-3d;
        transition: transform 0.1s ease-out;
    }

    .element-3d {
        transform-style: preserve-3d;
    }

    @keyframes blob {
        0% { transform: translate(0px, 0px) scale(1); }
        33% { transform: translate(30px, -50px) scale(1.1); }
        66% { transform: translate(-20px, 20px) scale(0.9); }
        100% { transform: translate(0px, 0px) scale(1); }
    }
    
    .animate-blob {
        animation: blob 10s infinite alternate ease-in-out;
    }

    @keyframes marquee {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
    .animate-marquee {
        animation: marquee 20s linear infinite;
        display: flex;
        width: 200%;
    }
    
    .fade-in-up {
        opacity: 0;
        transform: translateY(30px);
        transition: opacity 0.8s ease-out, transform 0.8s ease-out;
    }
    .fade-in-up.visible {
        opacity: 1;
        transform: translateY(0);
    }

</style>
