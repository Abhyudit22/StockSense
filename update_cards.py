import re

with open("frontend/src/routes/(marketing)/+page.svelte", "r", encoding="utf-8") as f:
    content = f.read()

# Add spotlight import
content = content.replace('import { intersect } from "$lib/actions/intersect";', 'import { intersect } from "$lib/actions/intersect";\n    import { spotlight } from "$lib/actions/spotlight";')

# Update the cards to use spotlight and neon glow
card_target = """<div class="bg-zinc-900/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm hover:border-emerald-500/30 transition-colors">"""
card_replacement = """<div class="spotlight-card group relative bg-zinc-900/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm transition-colors overflow-hidden" use:spotlight>
                <!-- Spotlight Hover Effect -->
                <div class="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition duration-300 group-hover:opacity-100" 
                     style="background: radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(16, 185, 129, 0.15), transparent 40%); z-index: 0;">
                </div>
                <div class="pointer-events-none absolute -inset-px rounded-2xl border border-emerald-500/50 opacity-0 transition duration-300 group-hover:opacity-100" 
                     style="mask-image: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), black, transparent); -webkit-mask-image: radial-gradient(300px circle at var(--mouse-x) var(--mouse-y), black, transparent); z-index: 0;">
                </div>
                <div class="relative z-10">"""

content = content.replace(card_target, card_replacement)
content = content.replace('</div>\n            </div>', '</div>\n                </div>\n            </div>') 

with open("frontend/src/routes/(marketing)/+page.svelte", "w", encoding="utf-8") as f:
    f.write(content)
