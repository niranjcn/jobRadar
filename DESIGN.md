# Design System — JobRadar

## Product Context
- **What this is:** JobRadar is a job discovery and alerting platform that continuously monitors company career pages, detects newly published jobs, deduplicates them, matches them against user preferences, and delivers alerts via Telegram and email.
- **Who it's for:** A single operator (early stage) — a job hunter who wants a personal radar over the market. Later: individual users of a dashboard.
- **Space/industry:** Job search / career intelligence tooling. Peers: job boards, ATS dashboards, aggregator tools.
- **Project type:** Web app / dashboard (Next.js + Tailwind + FastAPI backend).

## Aesthetic Direction
- **Direction:** Warm Editorial — heritage ink on warm parchment. White cards with 2px ink borders and offset shadows float over a warm `#FFFBF0` field with a subtle dot grain. Feels like a printed edition: tactile, precise, composed, quietly confident.
- **Decoration level:** Intentional — the ink border + offset shadow *is* the decoration; the dot grain adds tactility; nothing gratuitous.
- **Mood:** Calm, editorial, trustworthy. The UI should feel like a well-printed daily: every card is a neatly cut slip, every button is a pressed block, every stat is a headline numeral. Precise but human.
- **Memorable thing:** "This is the morning edition of the job market." The user should feel like an editor scanning a composed sheet, not a shopper on a job board.

## Typography
- **Display/Hero:** **Fraunces** — high-contrast editorial serif (700/800); used for headings, stat numerals, brand. Warm, authoritative, human.
- **Body:** **Inter** — clean, geometric, highly readable; used for paragraphs, sidebar, secondary text.
- **UI/Labels:** **IBM Plex Mono** — used for micro-labels, metadata, timestamps, run IDs, filter chips (400/500).
- **Data/Tables:** **IBM Plex Mono** / **JetBrains Mono** — tabular-nums, used for match scores, counts, timestamps. JetBrains kept as mono fallback.
- **Code:** IBM Plex Mono / JetBrains Mono.
- **Loading:** Google Fonts via `next/font/google` (Fraunces, Inter, IBM_Plex_Mono, JetBrains_Mono). No layout shift — use CSS `font-display: swap` and Tailwind CSS variables.
- **Scale:** Heading h1: 28px Fraunces 800 · h2: 18px Fraunces 700 · section kickers: 11px mono uppercase, letter-spaced · stat value: 26px Fraunces 800 · body: 14px · captions: 10px mono.

## Color
- **Approach:** Restrained — ink + vermillion on warm parchment. Everything serves legibility.
- **Base (warm):** `#FFFBF0` parchment. Dot grain `rgba(10,10,10,0.04)` at 14px.
- **Surface:** `#FFFFFF` white — cards, inputs, sidebar. Border `2px solid #0A0A0A`.
- **Primary:** `#FF3B30` vermillion — accents, active states, edition badge. Used sparingly.
- **Text:** ink `#0A0A0A`, secondary `#6B6B6B`, muted `#8A8A8A`.
- **Semantic:** success `#166534`, warning `#B45309`, error `#DC2626`.
- **Shadow:** offset `6px 6px 0 #0A0A0A` (hover `8px 8px 0`), small `4px 4px 0`. Press inverts to translate.
- **Dark legacy:** Dark tinted glass is preserved as `[data-theme="dark"]` for users who prefer it, but warm is the default.

## Spacing
- **Base unit:** 4px.
- **Density:** Comfortable (current layout density preserved — no visual regression).
- **Scale:** 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48) 3xl(64).

## Layout
- **Approach:** Grid-disciplined (app shell: fixed sidebar 224px + scrollable content column; content max-width ~`max-w-6xl`).
- **Grid:** Sidebar 224px with 2px right border; content uses existing responsive grids (2→4 for stats, 1→2 for job cards).
- **Max content width:** 1152px (`max-w-6xl`).
- **Border radius:** 12px for cards, 10px for inputs/buttons. Sharp enough to feel printed, soft enough to feel friendly. Ink border is the identity, not the radius.

## Motion
- **Approach:** Tactile — every card and stat has a physical entrance and a pressed response; motion is editorial, not flashy.
- **Entrance:** Stagger `rise` — `translateY(8px) → 0` + fade, 0.5s ease, 60ms stagger per item. Stats rise first, then cards.
- **Cards:** 150–200ms ease; hover → `translate(-1px,-1px)` + shadow `6px→8px`; active → `translate(1px,1px)` + shadow `4px`. Feels like a slip lifting off the page.
- **Buttons:** 150ms ease; same offset logic; primary inverts to vermillion on hover.
- **Line draw:** Section divider draws `scaleX(0→1)` 0.7s ease 0.3s.
- **Status pulse:** 1.6s blink for live dot.
- **Reduced motion:** All stagger disabled under `prefers-reduced-motion`.
- **Duration:** micro(50–100ms) short(150–250ms) medium(250–400ms).
- **Easing:** ease-out for enter/raise, ease-in for press.

## Implementation Status

Implemented in the Next.js frontend on 2026-08-28:

- **Tokens:** Warm parchment tokens (`--color-bg 255 251 240`, `--color-surface 255 255 255`, `--color-border 10 10 10`, `--color-primary 255 59 48`) centralized in `globals.css` as CSS variables, exposed via Tailwind `rgb(var(--...) / <alpha-value>)` and shadow utilities (`tailwind.config.ts`).
- **Typography:** Fraunces (display, 700/800), Inter (body), IBM Plex Mono (labels/data) loaded with `next/font/google` in `layout.tsx`; Tailwind `font-display` / `font-mono` / `font-fraunces` utilities.
- **Panels:** `.card` is white with `2px solid` ink border and `6px 6px 0` offset shadow; hover lifts to `8px`, press to `4px`. `.search-input` matches with mono font and offset shadow.
- **Buttons:** `.btn-primary` (ink → vermillion on hover) and `.btn-ghost` (white → parchment) use offset shadows and translate press, with disabled states.
- **Motion:** `rise` keyframes + `animate-rise-*` utilities with stagger delays; `draw-line` for dividers; `pulse-dot` for live indicators. Respects `prefers-reduced-motion`.
- **Theme:** Warm parchment is default (`data-theme="warm"`); dark glass preserved as `[data-theme="dark"]` opt-in, toggled from sidebar and persisted in `localStorage`.
- **Preview:** Live at `frontend/design-preview/index.html`; shotgun archives at `~/.gstack/projects/niranjcn-jobRadar/designs/`.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-08-16 | Adopt Neo-Glass Console direction (neomorphism + liquid glass) | Instrument-panel feel for radar identity. |
| 2026-08-16 | Chakra Petch / DM Sans / JetBrains Mono | Instrument character, readability, mono data. |
| 2026-08-16 | Cyan `#22D3EE` as primary identity | Radar glow as brand. |
| 2026-08-28 | Adopt Warm Editorial direction — ink on parchment (Fraunces / Inter / IBM Plex Mono, offset shadows) | Heritage print feel tested via shotgun (variant E family): tactile, calm, editorial. Chosen after 15-way exploration; warm is now the primary theme with dark as legacy. |
| 2026-08-28 | Fraunces 800 + IBM Plex Mono + offset shadow system | Editorial headlines + precise mono metadata + physical cut-slip shadow; distinguishes from flat SaaS while staying human and legible. |
| 2026-08-28 | Implement stagger rise + draw-line + offset hover across frontend | Entrance choreography and pressed offset make the sheet feel alive without decoration; respects reduced-motion. |