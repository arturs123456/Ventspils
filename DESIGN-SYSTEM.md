# Ventspils Social Media Reports — Design System & Brandbook

> Dizaina instrukcija prieksh AI tooliem (Claude Code, ChatGPT, u.c.), lai nakotne generetu vizuali identiskas atskaites un dashboardus.

---

## 1. Dizaina Filozofija

**Stils:** Premium dark-mode website (NE dashbords). Jasajutas ka moderna SaaS landing page, nevis korporativs parskats.

**Iedvesma:** Linear.app, Vercel.com, Stripe Dashboard — minimalistisks, elegants, ar dzilem foniem un subtiliem glow efektiem.

**Principi:**
- Lielaks ir labak neka mazaks (fonti, padding, spacing)
- Glass morphism kartinam (backdrop-filter blur)
- Subtili animeti gradienti fona
- Daudz whitespace starp sekcijam
- Dati ir galvenais — dizains tos izcels, nevis nomaskes
- Desktop-first (video prezentacijas formata)

---

## 2. Krasu Palete

### Pamata krāsas (CSS Variables)

```css
:root {
  /* === FONI === */
  --bg: #060911;              /* Galvenais fons — gandrīz melns ar zilu toņu */
  --surface-1: #131820;       /* Kartīšu fons (1. līmenis) */
  --surface-2: #1A2030;       /* Pogu/elementu fons (2. līmenis) */
  --surface-3: #232B3B;       /* Hover stāvoklis (3. līmenis) */

  /* === MALAS & BORDERS === */
  --border: rgba(255,255,255,0.05);         /* Kartīšu mala — gandrīz neredzama */
  --border-hover: rgba(255,255,255,0.12);   /* Hover mala */

  /* === TEKSTA KRĀSAS === */
  --text-1: #F0F2F5;          /* Primārais teksts — gandrīz balts */
  --text-2: #8B95A5;          /* Sekundārais teksts — pelēcīgi zils */
  --text-2b: #A8B2C1;         /* Apraksti — gaišāk pelēks */
  --text-3: #5A6577;          /* Labels, mazais teksts — kluss pelēks */

  /* === AKCENTU KRĀSAS === */
  --accent: #4F8CFF;          /* Galvenā akcenta krāsa — spilgti zila */
  --accent-hover: #6BA0FF;    /* Hover variant */
  --accent-dim: rgba(79,140,255,0.12);  /* Akcenta fons */

  /* === SEMANTISKĀS KRĀSAS === */
  --green: #34D399;            /* Pozitīvs / augšana */
  --green-dim: rgba(52,211,153,0.12);
  --red: #F87171;              /* Negatīvs / kritums */
  --red-dim: rgba(248,113,113,0.12);
  --orange: #FBBF24;           /* Brīdinājums / ieteikums */
  --orange-dim: rgba(251,191,36,0.12);
  --purple: #A78BFA;           /* Sekundārais akcents */
  --purple-dim: rgba(167,139,250,0.12);

  /* === GRAFIKI === */
  --chart-1: #4F8CFF;         /* Zilais */
  --chart-2: #34D399;         /* Zaļais */
  --chart-3: #FBBF24;         /* Dzeltenais */
  --chart-4: #F87171;         /* Sarkanais */
  --chart-grid: rgba(255,255,255,0.04);
}
```

### Fona Gradienti

Galvenais body fons NAV vienkārši melns — tam ir 3 radialie gradienti:
```css
body {
  background: #060911;
  background-image:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(79,140,255,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(167,139,250,0.05) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 50% 50%, rgba(52,211,153,0.03) 0%, transparent 60%);
  background-attachment: fixed;
}
```

### Noise Texture

Subtils troksna tekstura par visu lapu ar `opacity: 0.015` — dod premium "grain" efektu.

---

## 3. Tipografija

### Fontu Saime

| Loma | Fonts | Svars | Lietojums |
|------|-------|-------|-----------|
| **Pamatteksts** | Inter | 400, 500, 600, 700, 800 | Viss pamatteksts, dati, tabulas |
| **Virsraksti** | Space Grotesk | 500, 600, 700 | H1, H2, sekciju tituli, navigācija |

**Google Fonts links:**
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
```

### Izmeru Skala

| Elements | Izmers | Svars | Fontu saime |
|----------|--------|-------|-------------|
| Hero H1 | 3.4em (~54px) | 700 | Space Grotesk |
| Hero H1 (individualie) | 2.4em (~38px) | 700 | Space Grotesk |
| Sekcijas virsraksts | 1.8em (~29px) | 700 | Space Grotesk |
| Sekcijas apraksts | 0.92em (~15px) | 400 | Inter |
| KPI vertiba | 2.2em (~35px) | 800 | Inter |
| KPI label | 0.72em (~12px) | 600 | Inter |
| KPI apaksteksts | 0.78em (~13px) | 400 | Inter |
| Tabulas teksts | 0.85em (~14px) | 400 | Inter |
| Tabulas header | 0.72em (~12px) | 600 | Inter |
| Pogas | 0.76em (~12px) | 500 | Inter |
| Badge | 0.76em (~12px) | 600 | Inter |
| Secinajumu virsraksts | 1.15em (~18px) | 700 | Inter |
| Secinajumu teksts | 0.92em (~15px) | 400 | Inter |
| Footer teksts | 0.75-0.8em | 400 | Inter |

### Letter Spacing

- Virsraksti: `-0.05em` lidz `-0.02em` (ciesak)
- Labels/uppercase: `1.5px` lidz `2px` (plataki)
- Pamatteksts: `0` (default)

### Line Height

- Pamatteksts: `1.6`
- Virsraksti: `1.1`
- Apraksti: `1.65`
- Secinajumu teksts: `1.7`

---

## 4. Kartinju Stils (Glass Morphism)

### Pamat kartina (.cs, .kpi, .con)
```css
{
  background: rgba(19,24,32,0.5);      /* Caurspidigs tumss */
  backdrop-filter: blur(12px);          /* Aizmugures blur */
  border-radius: 20px;                  /* Lieli noapalojumi */
  padding: 32px;                        /* Daudz vietas ieksa */
  border: 1px solid rgba(255,255,255,0.04);  /* Tikko redzama mala */
  box-shadow:
    0 2px 16px rgba(0,0,0,0.15),       /* Arpeja ena */
    inset 0 1px 0 rgba(255,255,255,0.02);  /* Iekshejs augshejais glow */
}
```

### Hover stavoklis
```css
:hover {
  border-color: rgba(255,255,255,0.08);
  box-shadow:
    0 8px 32px rgba(0,0,0,0.25),
    inset 0 1px 0 rgba(255,255,255,0.04);
  transform: translateY(-3px);           /* Pacelas uz augsu */
}
```

### KPI kartina papildus
```css
/* Augshejais gradient glow */
.kpi::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(79,140,255,0.2), transparent);
}
```

---

## 5. Izkartojums & Spacing

### Konteineru platums
- Maksimalais platums: `1280px`
- Sanu padding: `48px`
- Footer padding: `64px 48px 40px`

### Vertikalie atkapes

| Vieta | Vertiba |
|-------|---------|
| Hero augshejais padding | 100px |
| Hero apakshejais padding | 80px |
| KPI grid margin-bottom | 80px |
| Starp sekcijam (.section) | 100px |
| Sekcijas divider (.sd2) | 100px augsha, 60px apaksha |
| Starp kartinam (.con-grid gap) | 28px |
| Starp chart kartinu un naakosho | 100px |
| Footer margin-top | 120px |

### Grid Izkartojums

- **KPI grid:** `repeat(auto-fit, minmax(200px, 1fr))` ar `20px` gap
- **Divu kolonnu:** `1fr 1fr` ar `32px` gap
- **Secinajumu grid:** `1fr 1fr` ar `28px` gap

### Border Radius

| Elements | Radius |
|----------|--------|
| Kartinas | 20px |
| Pogas | 12px |
| Badges | 14px |
| Navigacijas pills | 16px |
| IG profila poga | 24px |
| Acc avatar | 50% (aplis) |

---

## 6. Animacijas & Efekti

### Scroll Reveal
```css
.section {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.9s cubic-bezier(0.16,1,0.3,1),
              transform 0.9s cubic-bezier(0.16,1,0.3,1);
}
.section.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### KPI Stagger Animation
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px) }
  to { opacity: 1; transform: translateY(0) }
}
.kpi { animation: fadeInUp 0.6s ease-out both }
.kpi:nth-child(1) { animation-delay: 0.05s }
.kpi:nth-child(2) { animation-delay: 0.1s }
/* ... utt, +0.05s katram */
```

### Hero Fona Glow
```css
@keyframes heroGlow {
  0% { opacity: 0.8; transform: translateX(-50%) scale(1) }
  100% { opacity: 1; transform: translateX(-50%) scale(1.15) }
}
/* 8s ease-in-out infinite alternate */
```

### Hover Transitions
- Kartinas: `0.5s cubic-bezier(0.16,1,0.3,1)`
- Pogas: `0.2s ease`
- Saites: `0.2s ease`

---

## 7. Grafiku Stils (Chart.js)

### Noklusejuma iestatijumi
```javascript
Chart.defaults.color = '#8B95A5';
Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
Chart.defaults.font.family = "'Inter',system-ui,sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.padding = 16;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = 'circle';
Chart.defaults.plugins.tooltip.backgroundColor = '#1A2030';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.08)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.cornerRadius = 10;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.elements.bar.borderRadius = 8;
Chart.defaults.elements.bar.borderSkipped = false;
Chart.defaults.elements.line.borderWidth = 2;
Chart.defaults.elements.point.radius = 3;
Chart.defaults.elements.point.hoverRadius = 6;
```

### Grafiku augstumi
- Standarta: `420px`
- Garais (.tall): `580px`
- Ipasi garais (.xtall): `740px`

### Grafiku krāsas
- Pirma: `#4F8CFF` (zils)
- Otra: `#34D399` (zals)
- Tresha: `#FBBF24` (dzeltens)
- Ceturta: `#F87171` (sarkans)
- Piektaa: `#A78BFA` (violets)
- Grid linijas: `rgba(255,255,255,0.04)`

---

## 8. Tabulu Stils

```css
table { font-size: 0.85em; }
th {
  font-size: 0.72em;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--text-3);
  border-bottom: 2px solid rgba(79,140,255,0.1);
}
td {
  color: var(--text-2b);
  padding: 14px 16px;
}
tr:hover td {
  background: rgba(79,140,255,0.03);
}
```

---

## 9. Secinajumu Kartinas

### Tipi un Krasas

| Tips | Kreisā mala | Virsraksta krāsa | Lietojums |
|------|-------------|-------------------|-----------|
| `.good` | `var(--green)` | Zaļš | Pozitīvi rezultāti |
| `.bad` | `var(--red)` | Sarkans | Problemzones |
| `.tip` | `var(--orange)` | Dzeltens | Ieteikumi/padomi |
| (default) | `var(--accent)` | Zils | Neitrāla info |

Kartina pamats: `border-left: 4px solid [krasa]`

---

## 10. Navigacijas Footer

Katrai lapai apaksa ir vienots footer ar visam 22 lapa saitēm:
- Izcelts "Kopejais parskats" ar gradient fonu
- Aktivā lapa iezīmēta zilā ar `pointer-events: none`
- Krāsaini apļa avatāri katram kontam
- Glass morphism stils: `backdrop-filter: blur(8px)`

---

## 11. Scrollbar

```css
::-webkit-scrollbar { width: 8px }
::-webkit-scrollbar-thumb {
  background: rgba(79,140,255,0.15);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(79,140,255,0.3);
}
```

---

## 12. Selection

```css
::selection {
  background: rgba(79,140,255,0.25);
  color: var(--text-1);
}
```

---

## 13. Atkiribas: Kopejais vs Individualie Parskati

| Ipasiba | Kopejais (summary) | Individualais (account) |
|---------|---------------------|-------------------------|
| Hero H1 | 3.4em "Ventspils Instagram 2025" | 2.4em "@kontanosaukums Analize" |
| Navigacija augsa | Nav (tikai acc-bar) | Sticky nav ar prev/next |
| Acc bar | Ir (21 konts) | Nav |
| KPI grid | 6 kartinas ar Top1 info | 6 kartinas ar badge (+/-%) |
| Datu filtri | Ir (Visi/Bez Top2/Bez Bibl.) | Nav |
| Hashtag/Word clouds | Ir | Nav |
| Container platums | 1280px (CSS), 1400px (con-grid) | 1200px |

---

## 14. Tehnoloģiju Steks

- **HTML5** ar embedded CSS un JavaScript
- **Chart.js v4.4.1** no CDN
- **Google Fonts:** Inter + Space Grotesk
- **Nav build tools** — katrs fails ir self-contained
- **IntersectionObserver** scroll animacijām
- **CSS Custom Properties** visam krasam/spacing

---

## 15. Atslēgas Frāzes AI Promptiem

Lai reproducētu šo dizainu, izmanto šādas frāzes:

> "Dark premium website design, NOT a dashboard. Glass morphism cards with backdrop-filter blur. Background: near-black (#060911) with subtle radial gradient orbs in blue and purple. Fonts: Inter for body, Space Grotesk for headings. Large typography, generous whitespace. Cards have rgba backgrounds, 20px border-radius, subtle 1px borders, inset glow. Hover: cards lift with translateY(-3px) and deeper shadow. Colors: accent blue #4F8CFF, green #34D399, red #F87171, orange #FBBF24, purple #A78BFA. Chart.js with dark theme. Scroll animations with IntersectionObserver. Noise texture overlay at 1.5% opacity. Hero section with animated gradient glow."
