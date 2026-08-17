# Design System — JobRadar

## Product Context
- **What this is:** JobRadar is a job discovery and alerting platform that continuously monitors company career pages, detects newly published jobs, deduplicates them, matches them against user preferences, and delivers alerts via Telegram and email.
- **Who it's for:** A single operator (early stage) — a job hunter who wants a personal radar over the market. Later: individual users of a dashboard.
- **Space/industry:** Job search / career intelligence tooling. Peers: job boards, ATS dashboards, aggregator tools.
- **Project type:** Web app / dashboard (Next.js + Tailwind + FastAPI backend).

## Aesthetic Direction
- **Direction:** Neo-Glass Console ("Mission-Control Glass") — neomorphic soft-depth surfaces floating on frosted liquid-glass panels over a dark indigo radar backdrop.
- **Decoration level:** Intentional — the radar grid, aurora glow, and specular sheen carry the decoration; there is no gratuitous ornament.
- **Mood:** The product literally is a *radar*. The UI should feel like its instrument panel: physical, glowing, precise, alive. Buttons rise and depress like hardware. Data reads like cockpit gauges. The radar sweep is the identity.
- **Memorable thing:** "This is a mission-control console for the job market." The user should feel like an operator scanning a radar, not a shopper on a job board.

## Typography
- **Display/Hero:** **Chakra Petch** — angular, instrument-panel character; used for headings, navigation brand, stat readout numerals.
- **Body:** **DM Sans** — clean, geometric, highly readable; used for paragraphs, buttons, table cell content.
- **UI/Labels:** Same as body (DM Sans), with JetBrains Mono reserved for micro-labels and metadata.
- **Data/Tables:** **JetBrains Mono** — tabular-nums, used for match scores, counts, timestamps, run IDs, source status.
- **Code:** JetBrains Mono.
- **Loading:** Google Fonts via `next/font/google` (Chakra_Petch, DM_Sans, JetBrains_Mono). No layout shift — use CSS `font-display: swap` and Tailwind CSS variables.
- **Scale:** Heading h1: clamp(28px–40px) · h2: 24px · section kickers: 12px mono uppercase, letter-spaced · stat value: 32px display · body: 14–15px · captions: 11px mono.

## Color
- **Approach:** Restrained — a small set of meaningful accents on a tinted-glass neutral base. Cyan is the radar identity; everything else serves it.
- **Base (dark):** `#060C18 → #0E1B33` gradient (radar field). Grid line `rgba(148,190,255,0.05)`.
- **Primary:** `#22D3EE` cyan — radar glow, primary CTA, active nav. Glow `rgba(34,211,238,0.35)`.
- **Secondary:** `#60A5FA` blue — secondary buttons, links, secondary highlights.
- **Surface:** `rgba(148,190,255,0.06)` glass, strong `0.10`, border `rgba(148,190,255,0.14)`. Specular highlight `rgba(255,255,255,0.10)`.
- **Neutrals (dark):** text `#EAF3FF`, secondary `#9FB3D1`, muted `#5C7299`.
- **Semantic:** success `#34D399`, warning `#FBBF24`, error `#F87171`, info = primary cyan.
- **Dark mode:** Dark tinted glass is the primary theme (this app is inherently a dark radar console). A light frosted-ice theme exists as an opt-in (`[data-theme="light"]`) — soft `#DBE7F6 → #ECF4FD`, white-glass surfaces, deeper text `#12233F`, same accent roles desaturated for contrast.
- **Neomorphic shadow tokens:** raised `7px 7px 18px rgba(2,6,18,0.60), -7px -7px 18px rgba(120,160,255,0.07), inset 0 1px 0 rgba(255,255,255,0.08)`; pressed = inset version; hover = enlarged version.

## Spacing
- **Base unit:** 4px.
- **Density:** Comfortable (current layout density is preserved — no visual regression in information architecture).
- **Scale:** 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48) 3xl(64).

## Layout
- **Approach:** Grid-disciplined (app shell: fixed glass sidebar + scrollable content column; content max-width ~`max-w-6xl`).
- **Grid:** Sidebar 224px; content uses existing responsive grid patterns (1 col → 2 → 4 for stats, 1→2 for job cards).
- **Max content width:** 1152px (`max-w-6xl`).
- **Border radius:** sm 10px · md 14px · lg 20px · full 9999px. Squared, not bubbly — mission control isn't a bubble. (Deliberate: avoids the "AI slop uniform pill radius" trap while staying soft enough for glass.)

## Motion
- **Approach:** Intentional — every interactive element has a physical response; nothing decorative.
- **Buttons/cards/inputs:** 200ms ease-out; hover → shadow enlarges (element "rises"); active → shadow inverts (element "depresses", translateY 1px).
- **Radar sweep:** continuous 3.5–4s linear rotation (identity motif — sidebar mark, loading state, landing hero).
- **Status pulse:** 1.6s blink for live indicators.
- **Duration:** micro(50–100ms) short(150–250ms) medium(250–400ms).
- **Easing:** ease-out for enter/raise, ease-in for depress.

## Implementation Status

Implemented in the Next.js frontend on 2026-08-17:

- **Tokens:** All design tokens (colors, glass, neomorphic shadows, grid/aurora) are centralized as CSS variables in `globals.css` and exposed to Tailwind via `rgb(var(--...) / <alpha-value>)` and `var(--shadow-neo-*)` shadow utilities (`tailwind.config.ts`).
- **Typography:** Chakra Petch (display), DM Sans (body), JetBrains Mono (data/labels) loaded with `next/font/google` in `layout.tsx`; Tailwind `font-display` / `font-mono` utilities.
- **Glass panels:** `.card` and `.search-input` are frosted glass (backdrop-blur, gradient glass, specular highlight) with raised/pressed neomorphic shadow states.
- **Buttons:** `.btn-primary` / `.btn-ghost` get raised/pressed/hover neomorphic shadows, a physical press (translateY + inset shadow), and disabled states.
- **Radar field:** Fixed aurora-glow + faint grid backdrop on `body`; radar sweep runs at 3.5s, status pulse at 1.6s.
- **Theme:** Dark tinted glass is primary; an opt-in light frosted-ice theme is driven by `[data-theme="light"]`, toggled from the sidebar and persisted in `localStorage`.
- **Preview:** A static design preview is at `frontend/design-preview/index.html`.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-08-16 | Adopt Neo-Glass Console direction (neomorphism + liquid glass) | Product is literally a radar; instrument-panel feel is the memorable identity. Approved via design preview. |
| 2026-08-16 | Chakra Petch / DM Sans / JetBrains Mono | Instrument character (display), readability (body), tabular data (mono). Replaces Inter. |
| 2026-08-16 | Cyan `#22D3EE` as primary identity | It was already the radar accent; elevation to primary makes the glow the brand. |
| 2026-08-16 | Dark tinted glass primary theme, light as opt-in | Radar consoles are dark; light theme preserved for accessibility/preference. |
| 2026-08-16 | Physical depth as state (raised/pressed shadows) | Distinguishes JobRadar from flat dark SaaS; reinforces "hardware instrument" feel. |
| 2026-08-17 | Implement Neo-Glass Console across the live frontend | The approved direction is now the shipped UI; tokens centralized as CSS variables so theming stays consistent. |