<script lang="ts">
    import { onMount } from 'svelte';

    type TrendPoint = { date: string; score: number; volume: number };
    let { data }: { data: TrendPoint[] } = $props();

    const W = 600;
    const H = 160;
    const PAD = { top: 16, right: 16, bottom: 28, left: 40 };
    const chartW = W - PAD.left - PAD.right;
    const chartH = H - PAD.top - PAD.bottom;

    let yMin = $derived(data.length > 0 ? Math.min(...data.map(d => d.score)) : -1);
    let yMax = $derived(data.length > 0 ? Math.max(...data.map(d => d.score)) : 1);

    function xPos(i: number, len: number) {
        return PAD.left + (i / Math.max(len - 1, 1)) * chartW;
    }
    function yPos(score: number) {
        if (yMax === yMin) return PAD.top + chartH / 2;
        // add 5% padding top and bottom to min max
        const range = yMax - yMin;
        const paddedMin = yMin - range * 0.05;
        const paddedMax = yMax + range * 0.05;
        return PAD.top + ((paddedMax - score) / (paddedMax - paddedMin)) * chartH;
    }
    function zeroY() { 
        if (yMax === yMin) return PAD.top + chartH / 2;
        const range = yMax - yMin;
        const paddedMin = yMin - range * 0.05;
        const paddedMax = yMax + range * 0.05;
        return PAD.top + ((paddedMax - Math.min(Math.max(0, paddedMin), paddedMax)) / (paddedMax - paddedMin)) * chartH;
    }

    function buildPath(pts: TrendPoint[]) {
        if (pts.length === 0) return '';
        if (pts.length === 1) return `M${PAD.left},${yPos(pts[0].score)} L${PAD.left + chartW},${yPos(pts[0].score)}`;
        return pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${xPos(i, pts.length)},${yPos(p.score)}`).join(' ');
    }

    function buildAreaPath(pts: TrendPoint[]) {
        if (pts.length === 0) return '';
        const z = zeroY();
        if (pts.length === 1) {
            return `M${PAD.left},${yPos(pts[0].score)} L${PAD.left + chartW},${yPos(pts[0].score)} L${PAD.left + chartW},${z} L${PAD.left},${z} Z`;
        }
        const line = buildPath(pts);
        const last = xPos(pts.length - 1, pts.length);
        const first = xPos(0, pts.length);
        return `${line} L${last},${z} L${first},${z} Z`;
    }

    let yTicks = $derived([
        yMin,
        yMin + (yMax - yMin) * 0.25,
        yMin + (yMax - yMin) * 0.5,
        yMin + (yMax - yMin) * 0.75,
        yMax
    ].map(v => Number(v.toFixed(2))));

    let hoveredIdx = $state<number | null>(null);
    let tooltipX = $state(0);
    let tooltipY = $state(0);
</script>

<div class="w-full overflow-x-auto">
    {#if data.length === 0}
        <div class="flex items-center justify-center h-32 text-xs text-zinc-600">
            No trend data available.
        </div>
    {:else}
        <svg
            viewBox="0 0 {W} {H}"
            class="w-full"
            style="height: {H}px"
            role="img"
        >
            <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#22c55e" stop-opacity="0.2"/>
                    <stop offset="50%" stop-color="#22c55e" stop-opacity="0.0"/>
                    <stop offset="50%" stop-color="#ef4444" stop-opacity="0.0"/>
                    <stop offset="100%" stop-color="#ef4444" stop-opacity="0.2"/>
                </linearGradient>
                <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#22c55e"/>
                    <stop offset="50%" stop-color="#22c55e"/>
                    <stop offset="50%" stop-color="#ef4444"/>
                    <stop offset="100%" stop-color="#ef4444"/>
                </linearGradient>
                <clipPath id="chart-clip">
                    <rect x={PAD.left} y={PAD.top} width={chartW} height={chartH}/>
                </clipPath>
            </defs>

            <!-- Y-axis grid lines -->
            {#each yTicks as tick}
                <line
                    x1={PAD.left} y1={yPos(tick)}
                    x2={PAD.left + chartW} y2={yPos(tick)}
                    stroke="#27272a"
                    stroke-width="1"
                    stroke-dasharray={tick === 0 ? '' : '2 2'}
                />
                <text x={PAD.left - 8} y={yPos(tick) + 3} text-anchor="end" fill="#52525b" font-size="10">
                    {tick}
                </text>
            {/each}

            <!-- X-axis labels -->
            {#each data as point, i}
                {#if i % 7 === 0 || i === data.length - 1}
                    <text
                        x={xPos(i, data.length)} y={H - 4}
                        text-anchor="middle" fill="#52525b" font-size="10"
                    >{point.date.slice(5)}</text>
                {/if}
            {/each}

            <g clip-path="url(#chart-clip)">
                <path d={buildAreaPath(data)} fill="url(#areaGrad)"/>
            </g>

            <!-- Simple solid line -->
            <path
                d={buildPath(data)}
                fill="none"
                stroke="url(#lineGrad)"
                stroke-width="2"
                stroke-linejoin="round"
                clip-path="url(#chart-clip)"
            />

            <!-- Hover dots -->
            {#each data as point, i}
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <circle
                    cx={xPos(i, data.length)} cy={yPos(point.score)} r="12"
                    fill="transparent"
                    role="button"
                    tabindex="-1"
                    onmouseenter={() => { hoveredIdx = i; tooltipX = xPos(i, data.length); tooltipY = yPos(point.score); }}
                    onmouseleave={() => hoveredIdx = null}
                    style="cursor: crosshair;"
                />
                {#if hoveredIdx === i}
                    <circle cx={xPos(i, data.length)} cy={yPos(point.score)} r="3" fill="#fff"/>
                    <g transform="translate({Math.min(tooltipX - 28, W - 80)}, {Math.max(tooltipY - 42, PAD.top)})">
                        <rect x="0" y="0" width="60" height="30" rx="4" fill="#18181b" stroke="#27272a" stroke-width="1"/>
                        <text x="30" y="12" text-anchor="middle" fill="#a1a1aa" font-size="9">{point.date}</text>
                        <text x="30" y="24" text-anchor="middle" fill="#fff" font-size="10" font-weight="600">
                            ₹{point.score.toFixed(2)}
                        </text>
                    </g>
                {/if}
            {/each}
        </svg>
    {/if}
</div>
