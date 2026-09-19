import re

with open("frontend/src/routes/(marketing)/+page.svelte", "r", encoding="utf-8") as f:
    content = f.read()

# Change overflow-hidden to overflow-x-hidden
content = content.replace('overflow-hidden relative font-sans flex flex-col', 'overflow-x-hidden relative font-sans flex flex-col')

# Ensure script block gets the intersect action imported
script_insert = """    import { intersect } from "$lib/actions/intersect";
    
    let section1Visible = $state(false);
    let section2Visible = $state(false);
"""
content = content.replace('const stocks = [', script_insert + '\n    const stocks = [')

# Add marquee styles to style block
style_insert = """
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
"""
content = content.replace('</style>', style_insert + '\n</style>')

# Add new sections before the final </div>
sections = """
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
        <div class="text-center mb-16 fade-in-up" use:intersect on:enter={() => section1Visible = true} class:visible={section1Visible}>
            <h2 class="text-3xl lg:text-5xl font-bold mb-6">Smarter Analytics, Faster Decisions</h2>
            <p class="text-zinc-400 max-w-2xl mx-auto text-lg">
                Harness the power of AI to analyze thousands of news articles, tweets, and forum posts in seconds. 
                Visualized beautifully for the modern trader.
            </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 fade-in-up" use:intersect on:enter={() => section2Visible = true} class:visible={section2Visible}>
            <!-- Fake Graph Card 1 -->
            <div class="bg-zinc-900/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm hover:border-emerald-500/30 transition-colors">
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

            <!-- Fake Graph Card 2 -->
            <div class="bg-zinc-900/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm hover:border-emerald-500/30 transition-colors">
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
    </section>
"""
content = content.replace('</main>', '</main>\n' + sections)

with open("frontend/src/routes/(marketing)/+page.svelte", "w", encoding="utf-8") as f:
    f.write(content)
