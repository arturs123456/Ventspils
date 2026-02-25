# Ventspils Facebook 2025 — Pārskatu sistēma

## Projekta apraksts

Ventspils pašvaldības Facebook lapu analītikas pārskatu sistēma par 2025. gadu. Visas 32+ HTML lapas darbojas kā statiskas, pašpietiekamas single-file lapas (HTML + CSS + JS vienā failā), kas atver lokāli no failu sistēmas (`file:///`). Nav servera — viss darbojas pārlūkā.

---

## Failu struktūra

### 3 līmeņu hierarhija

| Līmenis | Fails | Apraksts |
|---------|-------|----------|
| **Kopējais** | `Facebook_apakšsvītra_visas_2025.html` | Visu 30+ lapu apkopojums — KPI, grafiki, Top lapas, secinājumi |
| **Grupas** (8 gab.) | `Facebook_parvalde_turisms_2025.html`, `Facebook_izglitiba_2025.html`, u.c. | Katras tematiskās grupas 2-5 lapu salīdzinājums |
| **Individuālās** (21+ gab.) | `visitventspils_2025.html`, `ventspilssp_2025.html`, u.c. | Katras atsevišķas Facebook lapas detalizēts pārskats |

### Palīgfaili

| Fails | Apraksts |
|-------|----------|
| `generate_facebook.py` | Ģenerē kopējo pārskatu no Excel datiem |
| `generate_fb_group.py` | Ģenerē grupu pārskatus |
| `generate_fb_page.py` | Ģenerē individuālo lapu pārskatus |
| `DESIGN-SYSTEM.md` | Dizaina sistēmas dokumentācija |

---

## Tehniskā arhitektūra

### Dizaina sistēma (vienota visās lapās)

- **Fonts**: Inter (teksts) + Space Grotesk (virsraksti)
- **Tēma**: Tumšā (--bg: #060911, virsmas: #131820 → #232B3B)
- **Krāsas**: Accent #1877F2 (zils), Green #34D399, Red #F87171, Orange #FBBF24, Purple #A78BFA
- **Chart.js 4.4.1** — grafiku bibliotēka
- **Animācijas**: fadeInUp, scroll-triggered visibility (IntersectionObserver)

### Datu glabāšana

Katrs HTML fails satur pilnu datu objektu inline JavaScript:

```javascript
// Kopējais fails:
const D = {
  kpi: {...},          // Kopējie KPI
  monthly: [...],      // Mēneša dati
  all_pages: [...],    // Visu lapu tabula
  top_posts: [...],    // Top publikācijas
  word_cloud: [...],   // Tagu mākoņa dati
  // ... vēl ~15 datu masīvi
};

// Grupu fails:
const D = {
  pages: {
    "Ventspils": { kpi: {...}, monthly: [...], contest: {...}, bigrams: [...], ... },
    "VisitVentspils": { kpi: {...}, monthly: [...], contest: {...}, bigrams: [...], ... }
  },
  group_kpi: {...},
  research: {...},
  top_posts: [...],
  worst_posts: [...]
};

// Individuālais fails:
const D = {
  kpi: {...},
  monthly: [...],
  type: {...},          // Formātu sadalījums
  weekday: [...],
  hour: [...],
  caption: [...],
  emoji_binary: {...},
  hashtag_binary: {...},
  top_posts: [...],
  worst_posts: [...],
  collab_partners: [...],
  top_hashtags: [...]
};
```

### Grafiku sistēma

**Kopējais fails** izmanto CFG pattern:
```javascript
var CFG = {};
var CH = {};  // Chart instances

CFG.monthC = function(chartType) {
  return {
    cid: 'monthC',  // canvas ID
    cfg: { type: chartType || 'bar', data: {...}, options: {...} }
  };
};

function rc(id) {
  if(CH[id]) CH[id].destroy();
  var c = CFG[id](CT[id] || 'bar');
  CH[id] = new Chart(document.getElementById(c.cid), c.cfg);
}

// Renderē visus:
Object.keys(CFG).forEach(function(id) { rc(id) });
```

**Grupu un individuālie faili** izmanto vienkāršāku pieeju:
```javascript
function makeChart(canvasId, config) {
  new Chart(document.getElementById(canvasId), config);
}
```

### Trīs Y-asu pattern (kopējais fails)

Daudzi grafiki kopējā failā izmanto 3 Y-asis:
- **y** (kreisā): Galvenais rādītājs (stabiņi)
- **y1** (labā): Vidējā iesaiste (līnija, pārtraukta)
- **y2** (slēpta): Iesaiste kopā (līnija, afterFit width=0 paslēpj asi)

```javascript
y2: {
  position: 'right',
  afterFit: function(a) { a.width = 0 },  // Paslēpj asi
  grid: { display: false }
}
```

---

## Kas jau izdarīts (izmaiņas, kas atšķiras no ģenerētā)

### Kopējais fails (`Facebook_apakšsvītra_visas_2025.html`)

1. **Latviskās diakritiskās zīmes** — visi virsraksti, apraksti, secinājumi laboti no ASCII uz pareizām garumzīmēm/mīkstinājumiem
2. **"Iesaiste kopā" 3. Y-ass** — pievienota 11 grafikiem kā rozā līnija (`#ec4899`), ieskaitot:
   - Mēneša dati, Formāts, Orientācija, Teksts uz bildes, Teksta garums
   - Publicēšanas dienas, Stundas, Darba/brīvdienas, Laika slots
   - H1 vs H2, Konkursi vs Parastie, Iesaistes sadalījums
3. **Bilžu krāsas** — stabiņu grafiks ar TOP 10 + Bar/Pie pārslēgšanas pogas (`switchColor()`)
4. **Tagu mākonis** — jauna sekcija (Nr. 20) ar vārdu mākoni, fontu izmērs graduēti no 14px līdz 48px. **⚠️ DATI IR APTUVENI** — vajag reālas vārdu frekvences no postu tekstiem
5. **Top 10 publikācijas** — pievienota "Saite" kolonna ar Facebook saitēm (🔗)
6. **Visu lapu pārskats** — šķirojama tabula (klikšķis uz galvenes)
7. **3 jauni secinājumi**: VisitVentspils Nr.2, Jūras Vārti komentāru līderis, Komunālā pārvalde ar maziem sekotājiem
8. **Nav links labots** — `apakšvītra` → `apakšsvītra` visās 9 failos

### Grupu fails (`Facebook_parvalde_turisms_2025.html`)

1. **Kopējā karstuma karte** — trešais heatmap "Kopā (abu lapu apvienojums)" zem individuālajiem
2. **Kopējie biežākie vārdu pāri** — trešais bigram bloks ar apvienotajiem datiem
3. **Zemākā iesaiste** — ja visi posti ir ar 0, rāda statistiku par mazās iesaistes postiem (<50)
4. **Secinājumi uzlaboti**:
   - Labākā diena: vispirms kopējais labākais, tad pa lapām
   - Efektīvākais formāts: vispirms kopējais, tad pa lapām (vecais vienkāršais teksts noņemts)
   - Labākais teksta garums: vispirms kopējais, tad pa lapām
   - Konkursu efekts: pievienots konkursu skaits katrai lapai
5. **Nav links labots**

---

## Kas vēl jādara

### 🔴 Prioritāte 1 — Kopējais fails

- **Tagu mākoņa reālie dati**: Lietotājam ir fails ar visiem postiem un tekstiem. Vajag:
  1. Nolasīt visus postu tekstus
  2. Saskaitīt vārdu frekvences (vārdi ar 4+ zīmēm)
  3. Filtrēt stop-vārdus (un, vai, bet, par, kas, tas, šis, arī, ...)
  4. Atjaunot `D.word_cloud` ar reālajiem TOP 20-25 vārdiem

### 🟡 Prioritāte 2 — Grupu faili (7 atlikušie)

Pārvalde+Tūrisms jau ir uzlabots. **Tās pašas izmaiņas jāpiemēro pārējiem 7 grupu failiem**:
- `Facebook_izglitiba_2025.html`
- `Facebook_komunalie_2025.html`
- `Facebook_kultura_2025.html`
- `Facebook_sports_2025.html`
- `Facebook_socialais_veseliba_2025.html`
- `Facebook_partneri_2025.html`
- `Facebook_citi_2025.html`

Izmaiņas:
1. ✅ Kopējā karstuma karte (trešais heatmap)
2. ✅ Kopējie biežākie vārdu pāri (apvienotais bloks)
3. ✅ Zemākā iesaiste — ja visi 0, rāda statistiku
4. ✅ Secinājumi — kopējais labākais + pa lapām (dienas, formāts, teksta garums)
5. ✅ Konkursu skaits secinājumos

### 🟢 Prioritāte 3 — Individuālie faili

- **Latviskās diakritiskās zīmes** — sekciju virsrakstos nav garumzīmju (piem. "Iesaiste pa menesiem" → "Iesaiste pa mēnešiem")
- **Nav links** — daudzi links norāda uz neeksistējošiem failiem ar `Facebook_` prefiksu (piem. `Facebook_visitventspils_2025.html`), bet faktiski fails ir `visitventspils_2025.html`. Vajag vai nu labot links, vai pārsaukt failus.

### 🔵 Bonus idejas

- Konkursu analīze pa lapām (ja pieejami postu līmeņa dati ar tekstu)
- Iesaistes kopā pievienošana arī grupu failiem (3. Y-ass kā kopējā failā)
- Responive dizaina uzlabojumi mobilajiem
- Eksporta funkcija (PDF vai attēls no grafikiem)

---

## Salauzto linku kopsavilkums

### Nav links uz kopējo failu (SALABOTS)
9 failos bija `Facebook_apakšvītra_visas_2025.html` → labots uz `Facebook_apakšsvītra_visas_2025.html`

### Individuālo lapu saites (NAV SALABOTS)
`Facebook_ventspils_2025.html` un citi faili satur ~50 saites uz failiem ar nosaukumu formātu `Facebook_[lapas_nosaukums]_2025.html`, bet faktiskie faili ir nosaukti bez `Facebook_` prefiksa. Piemēri:

| Saite failā | Faktiskais fails |
|---|---|
| `Facebook_visitventspils_2025.html` | `visitventspils_2025.html` |
| `Facebook_ventspils_biblioteka_2025.html` | `ventspils_biblioteka_2025.html` |
| `Facebook_ventspils_tehnikums_2025.html` | `ventspilstehnikums_2025.html` |

**Risinājums**: Vai nu masveida pārsaukšana failu nosaukumiem, vai saišu labošana HTML.

---

## Koda piemēri atkārtojamiem uzdevumiem

### Kā pievienot kopējo heatmap grupas failā

```javascript
// HTML — pievienot zem esošajiem heatmap diviem:
<div style="margin-top:28px">
  <h4 style="color:var(--text-2b);...;text-align:center">Kopā (abu lapu apvienojums)</h4>
  <div class="hm-grid" id="hmCombined"></div>
</div>

// JS — pievienot pēc individuālo heatmap izsaukumiem:
(function(){
  var combined=[];
  for(var d=0;d<7;d++){for(var h=0;h<24;h++){
    var totalEng=0,totalPosts=0;
    PAGES.forEach(function(p){
      var cell=D.pages[p].heatmap.find(function(x){return x.day===d&&x.hour===h});
      if(cell){totalEng+=cell.avg_eng*cell.posts;totalPosts+=cell.posts}
    });
    combined.push({day:d,hour:h,posts:totalPosts,
      avg_eng:totalPosts>0?Math.round(totalEng/totalPosts*10)/10:0});
  }}
  buildHeatmap(combined,'hmCombined');
})();
```

### Kā pievienot kopējos bigramus

```javascript
// HTML — pievienot zem bg-wrap diva:
<div style="margin-top:28px">
  <h4 style="...;text-align:center">Kopā (abu lapu apvienojums)</h4>
  <div id="bgCombined"></div>
</div>

// JS — pievienot buildBigrams() funkcijā:
(function(){
  var combined={};
  PAGES.forEach(function(p){
    D.pages[p].bigrams.forEach(function(b){
      if(!combined[b.phrase])combined[b.phrase]=0;
      combined[b.phrase]+=b.count;
    });
  });
  var sorted=Object.keys(combined).map(function(k){
    return {phrase:k,count:combined[k]}
  }).sort(function(a,b){return b.count-a.count}).slice(0,10);
  // ... render table to #bgCombined
})();
```

### Kā uzlabot secinājumus ar kopējo labāko

```javascript
// Labākā diena kopumā (nevis katrai lapai atsevišķi):
var allDays={};
PAGES.forEach(function(p){D.pages[p].weekday.forEach(function(d){
  if(!allDays[d.name])allDays[d.name]={name:d.name,totalEng:0,totalPosts:0};
  allDays[d.name].totalEng+=d.avg_eng*d.posts;
  allDays[d.name].totalPosts+=d.posts;
})});
var dayArr=Object.keys(allDays).map(function(k){
  var d=allDays[k];
  return {name:d.name,avg:d.totalPosts>0?Math.round(d.totalEng/d.totalPosts*10)/10:0}
});
var bestDayAll=dayArr.reduce(function(a,b){return a.avg>b.avg?a:b});
// Tāds pats pattern formātam un teksta garumam
```

---

## Piezīmes AI asistentam

1. **Visi faili ir self-contained** — katrs HTML ir pilnīga lapa ar CSS, JS un datiem. Nav ārējo atkarību izņemot Google Fonts un Chart.js CDN.
2. **Neizmantot ES6+ sintaksi** — faili rakstīti ar `var`, `function(){}`, `.forEach()`. Neizmantot arrow functions, let/const (izņemot `const D`), template literals.
3. **HTML entītijas** — Latviskās zīmes bieži ir kā HTML entītijas (`&#257;` = ā, `&#275;` = ē, `&#299;` = ī, `&#363;` = ū, `&#353;` = š, `&#382;` = ž, `&#311;` = ķ, `&#316;` = ļ, `&#326;` = ņ, `&#291;` = ģ). Teksts var būt jaukts — daļa ar entītijām, daļa ar Unicode.
4. **Python skripti labojumiem** — ieteicams rakstīt Python skriptus, kas meklē un aizstāj noteiktas HTML/JS daļas, nevis rediģēt failus manuāli.
5. **Sekciju numerācija** — ja pievieno jaunu sekciju, jāpārnumurē visi `<span class="num">XX</span>`.
6. **Chart.js instances** — kopējā failā instances glabājas `CH` objektā. Ja iznīcina un pārbūvē grafiku, jāiznīcina ar `CH[id].destroy()`.
