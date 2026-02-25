#!/usr/bin/env python3
"""Generate comprehensive Facebook analytics report for all Ventspils pages."""
import openpyxl
import json
import os
from datetime import datetime
from collections import defaultdict, Counter

DIR = os.path.dirname(os.path.abspath(__file__))
XLSX = '/Users/arturs25/Downloads/facebook_posts-2026-02-24.xlsx'
CSV_DIR = '/Users/arturs25/Downloads/Facebook Research - Visas'
OUTPUT = os.path.join(DIR, 'Facebook_apakšsvītra_visas_2025.html')

def read_csv(name):
    import csv
    path = os.path.join(CSV_DIR, name)
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.reader(f))

def load_all_data():
    """Load and compute all data from Excel + CSVs."""
    print("Loading Excel...")
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb['Worksheet']

    posts = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        ts = row[12]
        hour = None
        if ts and isinstance(ts, (int, float)):
            try:
                hour = datetime.fromtimestamp(ts).hour
            except:
                pass

        teksts = str(row[3]) if row[3] else ''
        t_lower = teksts.lower()
        is_contest = any(k in t_lower for k in ['konkurs', 'laimē', 'izlozē', 'loterij', 'izloze', 'laimēt', 'piedalies un laimē'])

        posts.append({
            'id': row[0],
            'lapa': row[1] or '',
            'type': row[2] or 'Other',
            'teksts': teksts,
            't_zimes': row[4] or 0,
            'a_zimes': row[7] or 0,
            'a_prop': row[8] or '',
            'a_krasa': row[9] or '',
            'date': str(row[11]) if row[11] else '',
            'hour': hour,
            'day': row[13] or 0,
            'shares': row[14] or 0,
            'likes': row[15] or 0,
            'comments': row[16] or 0,
            'slc': row[17] or 0,
            'video_len': row[18] or 0,
            'views': row[19] or 0,
            'is_contest': is_contest,
        })

    wb.close()
    print(f"Loaded {len(posts)} posts from {len(set(p['lapa'] for p in posts))} pages")
    return posts


def compute_data(posts):
    """Compute all analytics from posts."""
    D = {}

    total_posts = len(posts)
    total_likes = sum(p['likes'] for p in posts)
    total_shares = sum(p['shares'] for p in posts)
    total_comments = sum(p['comments'] for p in posts)
    total_slc = sum(p['slc'] for p in posts)
    unique_pages = len(set(p['lapa'] for p in posts))

    # === KPI ===
    D['kpi'] = {
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_shares': total_shares,
        'total_comments': total_comments,
        'total_engagement': total_slc,
        'unique_pages': unique_pages,
        'avg_eng_per_post': round(total_slc / total_posts, 1) if total_posts else 0,
        'avg_posts_per_day': round(total_posts / 365, 1),
        'avg_likes_per_post': round(total_likes / total_posts, 1) if total_posts else 0,
        'avg_shares_per_post': round(total_shares / total_posts, 1) if total_posts else 0,
        'avg_comments_per_post': round(total_comments / total_posts, 1) if total_posts else 0,
    }

    # === MONTHLY ===
    monthly = defaultdict(lambda: {'posts': 0, 'likes': 0, 'shares': 0, 'comments': 0, 'slc': 0})
    month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mai',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Okt',11:'Nov',12:'Dec'}
    for p in posts:
        if p['date'] and '-' in p['date']:
            m = int(p['date'].split('-')[1])
            monthly[m]['posts'] += 1
            monthly[m]['likes'] += p['likes']
            monthly[m]['shares'] += p['shares']
            monthly[m]['comments'] += p['comments']
            monthly[m]['slc'] += p['slc']

    D['monthly'] = []
    for m in range(1, 13):
        d = monthly[m]
        D['monthly'].append({
            'month': m,
            'name': month_names[m],
            'posts': d['posts'],
            'likes': d['likes'],
            'shares': d['shares'],
            'comments': d['comments'],
            'engagement': d['slc'],
            'avg_eng': round(d['slc'] / d['posts'], 1) if d['posts'] else 0,
        })

    # === WEEKDAY ===
    day_names = {1:'Pirmdiena',2:'Otrdiena',3:'Tresdiena',4:'Ceturtdiena',5:'Piektdiena',6:'Sestdiena',7:'Svetdiena'}
    weekday = defaultdict(lambda: {'posts': 0, 'likes': 0, 'shares': 0, 'comments': 0, 'slc': 0})
    for p in posts:
        if p['day']:
            weekday[p['day']]['posts'] += 1
            weekday[p['day']]['likes'] += p['likes']
            weekday[p['day']]['shares'] += p['shares']
            weekday[p['day']]['comments'] += p['comments']
            weekday[p['day']]['slc'] += p['slc']

    D['weekday'] = []
    for d in range(1, 8):
        data = weekday[d]
        D['weekday'].append({
            'day': d,
            'name': day_names[d],
            'posts': data['posts'],
            'engagement': data['slc'],
            'avg_eng': round(data['slc'] / data['posts'], 1) if data['posts'] else 0,
            'likes': data['likes'],
            'shares': data['shares'],
            'comments': data['comments'],
        })

    # === HOURLY ===
    hourly = defaultdict(lambda: {'posts': 0, 'slc': 0, 'likes': 0})
    for p in posts:
        if p['hour'] is not None:
            hourly[p['hour']]['posts'] += 1
            hourly[p['hour']]['slc'] += p['slc']
            hourly[p['hour']]['likes'] += p['likes']

    D['hourly'] = []
    for h in range(24):
        d = hourly[h]
        D['hourly'].append({
            'hour': f'{h:02d}:00',
            'posts': d['posts'],
            'avg_eng': round(d['slc'] / d['posts'], 1) if d['posts'] else 0,
        })

    # === CONTENT FORMAT ===
    format_data = defaultdict(lambda: {'count': 0, 'slc': 0, 'likes': 0, 'shares': 0, 'comments': 0})
    for p in posts:
        t = p['type'] if p['type'] else 'Other'
        format_data[t]['count'] += 1
        format_data[t]['slc'] += p['slc']
        format_data[t]['likes'] += p['likes']
        format_data[t]['shares'] += p['shares']
        format_data[t]['comments'] += p['comments']

    D['formats'] = []
    for t in ['Photo', 'Reel', 'Video', 'Link']:
        d = format_data.get(t, {'count':0,'slc':0,'likes':0,'shares':0,'comments':0})
        D['formats'].append({
            'type': t,
            'count': d['count'],
            'pct': round(d['count'] / total_posts * 100, 1) if total_posts else 0,
            'avg_eng': round(d['slc'] / d['count'], 1) if d['count'] else 0,
            'total_eng': d['slc'],
        })

    # === IMAGE ORIENTATION ===
    orient = defaultdict(lambda: {'count': 0, 'slc': 0})
    orient_map = {'Horiz.': 'Horizontali', 'Vertik.': 'Vertikali', 'Kvadr.': 'Kvadrats'}
    for p in posts:
        if p['a_prop']:
            key = orient_map.get(p['a_prop'], p['a_prop'])
            orient[key]['count'] += 1
            orient[key]['slc'] += p['slc']

    D['orientation'] = []
    for name in ['Vertikali', 'Horizontali', 'Kvadrats']:
        d = orient[name]
        D['orientation'].append({
            'name': name,
            'count': d['count'],
            'pct': round(d['count'] / sum(orient[k]['count'] for k in orient) * 100, 1) if orient else 0,
            'avg_eng': round(d['slc'] / d['count'], 1) if d['count'] else 0,
        })

    # === IMAGE COLORS ===
    color_names = {'#ffffff':'Balts','#0000ff':'Zils','#ffa500':'Oranzs','#000000':'Melns','#ff0000':'Sarkans'}
    color_data = defaultdict(int)
    for p in posts:
        if p['a_krasa']:
            color_data[p['a_krasa']] += 1

    D['colors'] = []
    total_colors = sum(color_data.values())
    for c, cnt in sorted(color_data.items(), key=lambda x: -x[1])[:20]:
        D['colors'].append({
            'hex': c,
            'name': color_names.get(c, c),
            'count': cnt,
            'pct': round(cnt / total_colors * 100, 1) if total_colors else 0,
        })

    # === TEXT ON IMAGE ===
    text_img = {'Nav teksta': {'count': 0, 'slc': 0}, '1-80': {'count': 0, 'slc': 0}, '81+': {'count': 0, 'slc': 0}}
    for p in posts:
        az = p['a_zimes']
        if isinstance(az, (int, float)):
            if az == 0:
                text_img['Nav teksta']['count'] += 1
                text_img['Nav teksta']['slc'] += p['slc']
            elif az <= 80:
                text_img['1-80']['count'] += 1
                text_img['1-80']['slc'] += p['slc']
            else:
                text_img['81+']['count'] += 1
                text_img['81+']['slc'] += p['slc']

    D['text_on_image'] = []
    for name in ['Nav teksta', '1-80', '81+']:
        d = text_img[name]
        D['text_on_image'].append({
            'name': name,
            'count': d['count'],
            'avg_eng': round(d['slc'] / d['count'], 1) if d['count'] else 0,
        })

    # === CAPTION LENGTH ===
    cap_buckets = {'Nav teksta': {'count': 0, 'slc': 0}, '1-120': {'count': 0, 'slc': 0}, '121-240': {'count': 0, 'slc': 0}, '241+': {'count': 0, 'slc': 0}}
    for p in posts:
        tz = p['t_zimes']
        if isinstance(tz, (int, float)):
            if tz == 0:
                cap_buckets['Nav teksta']['count'] += 1
                cap_buckets['Nav teksta']['slc'] += p['slc']
            elif tz <= 120:
                cap_buckets['1-120']['count'] += 1
                cap_buckets['1-120']['slc'] += p['slc']
            elif tz <= 240:
                cap_buckets['121-240']['count'] += 1
                cap_buckets['121-240']['slc'] += p['slc']
            else:
                cap_buckets['241+']['count'] += 1
                cap_buckets['241+']['slc'] += p['slc']

    D['caption_length'] = []
    for name in ['Nav teksta', '1-120', '121-240', '241+']:
        d = cap_buckets[name]
        D['caption_length'].append({
            'name': name,
            'count': d['count'],
            'pct': round(d['count'] / total_posts * 100, 1) if total_posts else 0,
            'avg_eng': round(d['slc'] / d['count'], 1) if d['count'] else 0,
        })

    # === TOP PAGES ===
    page_data = defaultdict(lambda: {'posts': 0, 'likes': 0, 'shares': 0, 'comments': 0, 'slc': 0, 'followers': 0})
    for p in posts:
        page_data[p['lapa']]['posts'] += 1
        page_data[p['lapa']]['likes'] += p['likes']
        page_data[p['lapa']]['shares'] += p['shares']
        page_data[p['lapa']]['comments'] += p['comments']
        page_data[p['lapa']]['slc'] += p['slc']

    # Load followers from Komunikacija CSV
    try:
        rows = read_csv('Komunikācija - Visas.csv')
        headers = rows[0]
        followers_row = rows[1]  # Sekotaju skaits
        for i, h in enumerate(headers):
            if h and h != '* Visas *' and i > 0:
                val = followers_row[i] if i < len(followers_row) else ''
                if val and val.strip():
                    try:
                        page_data[h]['followers'] = int(val.replace(',', ''))
                    except:
                        pass
    except:
        pass

    D['top_pages_eng'] = []
    for name, d in sorted(page_data.items(), key=lambda x: -x[1]['slc'])[:15]:
        D['top_pages_eng'].append({
            'name': name,
            'posts': d['posts'],
            'engagement': d['slc'],
            'avg_eng': round(d['slc'] / d['posts'], 1) if d['posts'] else 0,
            'likes': d['likes'],
            'shares': d['shares'],
            'comments': d['comments'],
            'followers': d['followers'],
        })

    D['top_pages_avg'] = []
    for name, d in sorted(page_data.items(), key=lambda x: -x[1]['slc']/max(x[1]['posts'],1))[:15]:
        D['top_pages_avg'].append({
            'name': name,
            'posts': d['posts'],
            'engagement': d['slc'],
            'avg_eng': round(d['slc'] / d['posts'], 1) if d['posts'] else 0,
            'followers': d['followers'],
        })

    D['top_pages_posts'] = []
    for name, d in sorted(page_data.items(), key=lambda x: -x[1]['posts'])[:15]:
        D['top_pages_posts'].append({
            'name': name,
            'posts': d['posts'],
            'avg_eng': round(d['slc'] / d['posts'], 1) if d['posts'] else 0,
        })

    # === ALL PAGES for table ===
    D['all_pages'] = []
    for name, d in sorted(page_data.items(), key=lambda x: -x[1]['slc']):
        D['all_pages'].append({
            'name': name,
            'posts': d['posts'],
            'engagement': d['slc'],
            'avg_eng': round(d['slc'] / d['posts'], 1) if d['posts'] else 0,
            'likes': d['likes'],
            'shares': d['shares'],
            'comments': d['comments'],
            'followers': d['followers'],
        })

    # === TOP POSTS ===
    sorted_posts = sorted(posts, key=lambda x: -x['slc'])

    D['top_posts'] = []
    for p in sorted_posts[:10]:
        D['top_posts'].append({
            'lapa': p['lapa'],
            'type': p['type'],
            'likes': p['likes'],
            'shares': p['shares'],
            'comments': p['comments'],
            'engagement': p['slc'],
            'teksts': p['teksts'][:120],
            'date': p['date'],
            'id': p['id'],
        })

    # === WORST POSTS (with at least some followers) ===
    active_posts = [p for p in posts if p['lapa'] in [n for n, d in page_data.items() if d['followers'] > 500]]
    D['worst_posts'] = []
    for p in sorted(active_posts, key=lambda x: x['slc'])[:10]:
        D['worst_posts'].append({
            'lapa': p['lapa'],
            'type': p['type'],
            'likes': p['likes'],
            'shares': p['shares'],
            'comments': p['comments'],
            'engagement': p['slc'],
            'teksts': p['teksts'][:120],
            'date': p['date'],
        })

    # === CONTEST ANALYSIS ===
    contest = [p for p in posts if p['is_contest']]
    non_contest = [p for p in posts if not p['is_contest']]
    contest_slc = sum(p['slc'] for p in contest)
    non_contest_slc = sum(p['slc'] for p in non_contest)

    D['contest'] = {
        'contest_posts': len(contest),
        'contest_pct': round(len(contest) / total_posts * 100, 1),
        'contest_eng': contest_slc,
        'contest_avg': round(contest_slc / len(contest), 1) if contest else 0,
        'non_contest_posts': len(non_contest),
        'non_contest_eng': non_contest_slc,
        'non_contest_avg': round(non_contest_slc / len(non_contest), 1) if non_contest else 0,
        'contest_eng_pct': round(contest_slc / total_slc * 100, 1) if total_slc else 0,
    }

    # === ENGAGEMENT CONCENTRATION ===
    sorted_by_eng = sorted(posts, key=lambda x: -x['slc'])
    top1pct_n = max(1, int(total_posts * 0.01))
    top10pct_n = max(1, int(total_posts * 0.1))
    top1_eng = sum(p['slc'] for p in sorted_by_eng[:top1pct_n])
    top10_eng = sum(p['slc'] for p in sorted_by_eng[:top10pct_n])

    D['concentration'] = {
        'top1_pct_posts': top1pct_n,
        'top1_pct_eng': top1_eng,
        'top1_pct_share': round(top1_eng / total_slc * 100, 1),
        'top10_pct_posts': top10pct_n,
        'top10_pct_eng': top10_eng,
        'top10_pct_share': round(top10_eng / total_slc * 100, 1),
        'rest_eng': total_slc - top10_eng,
        'rest_share': round((total_slc - top10_eng) / total_slc * 100, 1),
    }

    # === WORK vs WEEKEND ===
    work_posts = [p for p in posts if p['day'] in [1,2,3,4,5]]
    weekend_posts = [p for p in posts if p['day'] in [6,7]]
    work_slc = sum(p['slc'] for p in work_posts)
    weekend_slc = sum(p['slc'] for p in weekend_posts)

    D['work_weekend'] = {
        'work_posts': len(work_posts),
        'work_pct': round(len(work_posts) / total_posts * 100, 1),
        'work_avg': round(work_slc / len(work_posts), 1) if work_posts else 0,
        'weekend_posts': len(weekend_posts),
        'weekend_pct': round(len(weekend_posts) / total_posts * 100, 1),
        'weekend_avg': round(weekend_slc / len(weekend_posts), 1) if weekend_posts else 0,
    }

    # === TIME SLOTS ===
    slots = {'09-19': {'posts':0,'slc':0}, '19-01': {'posts':0,'slc':0}, '01-09': {'posts':0,'slc':0}}
    for p in posts:
        h = p['hour']
        if h is None: continue
        if 9 <= h < 19:
            slots['09-19']['posts'] += 1
            slots['09-19']['slc'] += p['slc']
        elif h >= 19 or h < 1:
            slots['19-01']['posts'] += 1
            slots['19-01']['slc'] += p['slc']
        else:
            slots['01-09']['posts'] += 1
            slots['01-09']['slc'] += p['slc']

    D['time_slots'] = []
    for name in ['09-19', '19-01', '01-09']:
        d = slots[name]
        D['time_slots'].append({
            'name': name,
            'posts': d['posts'],
            'avg_eng': round(d['slc'] / d['posts'], 1) if d['posts'] else 0,
            'pct': round(d['posts'] / total_posts * 100, 1),
        })

    # === FORMAT + ORIENTATION CROSS ===
    format_orient = defaultdict(lambda: {'count': 0, 'slc': 0})
    for p in posts:
        if p['a_prop'] and p['type']:
            key = f"{p['type']}_{p['a_prop']}"
            format_orient[key]['count'] += 1
            format_orient[key]['slc'] += p['slc']

    # === POPULAR LINKS ===
    try:
        rows = read_csv('Populārākās saites - Visas.csv')
        D['popular_links'] = []
        for r in rows[1:11]:
            D['popular_links'].append({'domain': r[0], 'count': int(r[1]), 'pct': r[2]})
    except:
        D['popular_links'] = []

    # === ENGAGEMENT DISTRIBUTION ===
    eng_buckets = {'0': 0, '1-20': 0, '21-50': 0, '51-100': 0, '101-200': 0, '201-500': 0, '500+': 0}
    for p in posts:
        e = p['slc']
        if e == 0: eng_buckets['0'] += 1
        elif e <= 20: eng_buckets['1-20'] += 1
        elif e <= 50: eng_buckets['21-50'] += 1
        elif e <= 100: eng_buckets['51-100'] += 1
        elif e <= 200: eng_buckets['101-200'] += 1
        elif e <= 500: eng_buckets['201-500'] += 1
        else: eng_buckets['500+'] += 1

    D['eng_dist'] = [{'bucket': k, 'count': v} for k, v in eng_buckets.items()]

    # === LIKES vs SHARES vs COMMENTS ratio ===
    D['engagement_breakdown'] = {
        'likes_pct': round(total_likes / total_slc * 100, 1),
        'shares_pct': round(total_shares / total_slc * 100, 1),
        'comments_pct': round(total_comments / total_slc * 100, 1),
    }

    # === WITHOUT TOP 3 PAGES ===
    top3_pages = [d['name'] for d in D['top_pages_eng'][:3]]
    without_top3 = [p for p in posts if p['lapa'] not in top3_pages]
    wt3_slc = sum(p['slc'] for p in without_top3)
    D['without_top3'] = {
        'pages': top3_pages,
        'posts': len(without_top3),
        'engagement': wt3_slc,
        'avg_eng': round(wt3_slc / len(without_top3), 1) if without_top3 else 0,
        'original_avg': D['kpi']['avg_eng_per_post'],
    }

    # === H1 vs H2 ===
    h1 = [p for p in posts if p['date'] and '-' in p['date'] and int(p['date'].split('-')[1]) <= 6]
    h2 = [p for p in posts if p['date'] and '-' in p['date'] and int(p['date'].split('-')[1]) > 6]
    h1_slc = sum(p['slc'] for p in h1)
    h2_slc = sum(p['slc'] for p in h2)
    D['half_year'] = [
        {'name': 'H1 (Jan-Jun)', 'posts': len(h1), 'engagement': h1_slc, 'avg_eng': round(h1_slc/len(h1),1) if h1 else 0},
        {'name': 'H2 (Jul-Dec)', 'posts': len(h2), 'engagement': h2_slc, 'avg_eng': round(h2_slc/len(h2),1) if h2 else 0},
    ]
    if h1 and h2:
        D['half_year_growth'] = round((h2_slc/len(h2) - h1_slc/len(h1)) / (h1_slc/len(h1)) * 100, 1)
    else:
        D['half_year_growth'] = 0

    return D


def generate_html(D):
    """Generate the full HTML report."""

    data_json = json.dumps(D, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="lv"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ventspils Facebook 2025 — Kopejais Parskats</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root {{
  --bg: #060911;
  --surface-1: #131820;
  --surface-2: #1A2030;
  --surface-3: #232B3B;
  --border: rgba(255,255,255,0.05);
  --border-hover: rgba(255,255,255,0.12);
  --text-1: #F0F2F5;
  --text-2: #8B95A5;
  --text-2b: #A8B2C1;
  --text-3: #5A6577;
  --accent: #1877F2;
  --accent-hover: #4293F5;
  --accent-dim: rgba(24,119,242,0.12);
  --green: #34D399;
  --green-dim: rgba(52,211,153,0.12);
  --red: #F87171;
  --red-dim: rgba(248,113,113,0.12);
  --orange: #FBBF24;
  --orange-dim: rgba(251,191,36,0.12);
  --purple: #A78BFA;
  --purple-dim: rgba(167,139,250,0.12);
  --chart-grid: rgba(255,255,255,0.04);
  --shadow-1: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
  --shadow-2: 0 4px 16px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3);
  --radius-card: 20px;
  --radius-btn: 12px;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{
  font-family:'Inter',system-ui,sans-serif;
  background:var(--bg);
  background-image:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(24,119,242,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(167,139,250,0.05) 0%, transparent 60%);
  background-attachment:fixed;
  color:var(--text-1);line-height:1.6;-webkit-font-smoothing:antialiased;
}}
body::after{{
  content:'';position:fixed;top:0;left:0;width:100%;height:100%;
  opacity:0.015;pointer-events:none;z-index:9999;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}}
.container{{max-width:1280px;margin:0 auto;padding:0 48px 120px}}
.hero{{padding:100px 48px 80px;text-align:center;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:900px;height:600px;background:radial-gradient(ellipse,rgba(24,119,242,0.12) 0%,rgba(167,139,250,0.06) 40%,transparent 70%);animation:heroGlow 8s ease-in-out infinite alternate;pointer-events:none}}
@keyframes heroGlow{{0%{{opacity:0.8;transform:translateX(-50%) scale(1)}}100%{{opacity:1;transform:translateX(-50%) scale(1.15)}}}}
.hero h1{{font-family:'Space Grotesk',sans-serif;font-size:3.4em;font-weight:700;letter-spacing:-0.05em;line-height:1.1;margin-bottom:16px}}
.hero h1 span{{background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.subtitle{{color:var(--text-2b);font-size:1.15em;letter-spacing:0.02em;opacity:0.7}}

/* KPI */
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:80px}}
.kpi{{background:rgba(19,24,32,0.6);backdrop-filter:blur(16px);border-radius:20px;padding:28px 24px;border:1px solid rgba(255,255,255,0.05);box-shadow:0 4px 24px rgba(0,0,0,0.2),inset 0 1px 0 rgba(255,255,255,0.03);position:relative;overflow:hidden;text-align:center;transition:all .3s ease}}
.kpi::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(24,119,242,0.2),transparent)}}
.kpi:hover{{border-color:rgba(24,119,242,0.15);box-shadow:0 8px 32px rgba(0,0,0,0.3),0 0 0 1px rgba(24,119,242,0.08);transform:translateY(-4px)}}
.kpi .label{{font-size:0.72em;letter-spacing:2px;color:var(--text-3);text-transform:uppercase;font-weight:600}}
.kpi .value{{font-size:2.2em;font-weight:800;margin:10px 0;background:linear-gradient(135deg,var(--text-1),var(--text-2b));-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-variant-numeric:tabular-nums}}
.kpi .sub{{font-size:0.78em;color:var(--text-2)}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
.kpi{{animation:fadeInUp 0.6s ease-out both}}
.kpi:nth-child(1){{animation-delay:0.05s}}.kpi:nth-child(2){{animation-delay:0.1s}}.kpi:nth-child(3){{animation-delay:0.15s}}.kpi:nth-child(4){{animation-delay:0.2s}}.kpi:nth-child(5){{animation-delay:0.25s}}.kpi:nth-child(6){{animation-delay:0.3s}}.kpi:nth-child(7){{animation-delay:0.35s}}.kpi:nth-child(8){{animation-delay:0.4s}}

/* Section */
.stitle{{font-family:'Space Grotesk',sans-serif;font-size:1.8em;font-weight:700;color:var(--text-1);letter-spacing:-0.02em;margin-bottom:20px;padding-left:4px}}
.stitle .num{{font-size:0.6em;color:rgba(24,119,242,0.4);margin-right:10px;font-weight:700}}
.sdesc{{color:var(--text-2b);font-size:0.92em;line-height:1.65;max-width:600px;margin-bottom:20px;padding-left:4px}}
.section{{opacity:0;transform:translateY(40px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1);margin-bottom:100px}}
.section.visible{{opacity:1;transform:translateY(0)}}
.cs{{background:rgba(19,24,32,0.5);backdrop-filter:blur(12px);border-radius:20px;padding:32px;border:1px solid rgba(255,255,255,0.04);box-shadow:0 2px 16px rgba(0,0,0,0.15),inset 0 1px 0 rgba(255,255,255,0.02);transition:all .3s ease}}
.cs:hover{{border-color:rgba(255,255,255,0.08);box-shadow:0 8px 32px rgba(0,0,0,0.25)}}
.ch{{display:flex;justify-content:flex-end;align-items:center;gap:8px;margin-bottom:16px}}
.cc button{{padding:6px 16px;border-radius:12px;cursor:pointer;font-size:0.76em;font-weight:500;font-family:'Inter',sans-serif;transition:all .2s;border:1px solid var(--border);background:var(--surface-2);color:var(--text-2)}}
.cc button.active{{background:var(--accent);color:#fff;border-color:var(--accent);box-shadow:0 0 20px rgba(24,119,242,0.25)}}
.cc button:hover:not(.active){{border-color:var(--border-hover);color:var(--text-1)}}
.cw{{position:relative;height:420px}}.cw.tall{{height:580px}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:32px}}

/* Tables */
table{{width:100%;border-collapse:collapse;font-size:0.85em;margin-top:8px}}
th,td{{padding:14px 16px;text-align:left;border-bottom:1px solid var(--border)}}
th{{color:var(--text-3);font-weight:600;font-size:0.72em;text-transform:uppercase;letter-spacing:1px;border-bottom:2px solid rgba(24,119,242,0.1)}}
td{{font-variant-numeric:tabular-nums;color:var(--text-2b)}}
tr:hover td{{background:rgba(24,119,242,0.03)}}
a{{color:var(--accent);text-decoration:none;transition:color .2s}}a:hover{{color:var(--accent-hover)}}

/* Badges */
.b{{display:inline-block;padding:4px 14px;border-radius:14px;font-size:0.76em;font-weight:600}}
.bg{{background:var(--green-dim);color:var(--green)}}
.br{{background:var(--red-dim);color:var(--red)}}
.bb{{background:var(--accent-dim);color:var(--accent)}}
.bo{{background:var(--orange-dim);color:var(--orange)}}

/* Section divider */
.sd2{{font-family:'Space Grotesk',sans-serif;text-align:center;font-size:1.5em;font-weight:700;color:var(--text-2);letter-spacing:-0.01em;margin:100px 0 60px;padding:24px 0;position:relative}}
.sd2::after{{content:'';position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:80px;height:3px;border-radius:2px;background:linear-gradient(90deg,var(--accent),var(--purple))}}

/* Conclusions */
.con-grid{{display:grid;grid-template-columns:1fr 1fr;gap:28px;max-width:1400px;margin:0 auto}}
.con{{background:rgba(19,24,32,0.5);backdrop-filter:blur(12px);border-radius:20px;padding:32px;border:1px solid rgba(255,255,255,0.04);border-left:4px solid var(--accent);box-shadow:0 2px 16px rgba(0,0,0,0.15);transition:all .5s cubic-bezier(.16,1,.3,1);opacity:0;transform:translateY(30px)}}
.con.visible{{opacity:1;transform:translateY(0)}}
.con:hover{{border-color:rgba(255,255,255,0.06);box-shadow:0 8px 32px rgba(0,0,0,0.25);transform:translateY(-3px)}}
.con h3{{margin-bottom:14px;color:var(--accent);font-size:1.15em;font-weight:700}}
.con p{{color:var(--text-2b);font-size:0.92em;margin-bottom:10px;line-height:1.7}}
.hl{{color:var(--text-1);font-weight:600}}.st{{color:var(--orange);font-weight:700}}
.good{{border-left-color:var(--green)}}.good h3{{color:var(--green)}}
.bad{{border-left-color:var(--red)}}.bad h3{{color:var(--red)}}
.tip{{border-left-color:var(--orange)}}.tip h3{{color:var(--orange)}}

/* Footer */
.footer{{text-align:center;padding:64px 0 40px;color:var(--text-3);font-size:0.8em}}

/* Scrollbar */
::-webkit-scrollbar{{width:8px}}::-webkit-scrollbar-thumb{{background:rgba(24,119,242,0.15);border-radius:4px}}::-webkit-scrollbar-thumb:hover{{background:rgba(24,119,242,0.3)}}
::selection{{background:rgba(24,119,242,0.25);color:var(--text-1)}}
</style>
</head><body>

<div class="hero">
<h1>Ventspils <span>Facebook</span> 2025</h1>
<p class="subtitle">50 lapu · Janvaris — Decembris 2025 · 12 213 publikacijas · Kopejais parskats</p>
</div>

<div class="container">
<div class="kpi-grid" id="kpiG"></div>

<div class="section"><h2 class="stitle"><span class="num">01</span>Iesaiste pa menesiem</h2>
<p class="sdesc">Kopeja iesaiste (likes + shares + comments) katru menesi. Vasara un novembri iesaiste ir augstaka.</p>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sw('mEng','bar',this)">Bar</button><button onclick="sw('mEng','line',this)">Line</button></div></div><div class="cw"><canvas id="mEngC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">02</span>Publikaciju skaits pa menesiem</h2>
<p class="sdesc">Cik publikacijas katra menesi. Oktobri/Novembri visvairak, vasara vismazak.</p>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sw('mPosts','bar',this)">Bar</button><button onclick="sw('mPosts','line',this)">Line</button></div></div><div class="cw"><canvas id="mPostsC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">03</span>Videja iesaiste pa menesiem</h2>
<p class="sdesc">Videja iesaiste uz vienu publikaciju katru menesi. Augstak — janvari, julija, junija.</p>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sw('mAvg','bar',this)">Bar</button><button onclick="sw('mAvg','line',this)">Line</button></div></div><div class="cw"><canvas id="mAvgC"></canvas></div></div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">04</span>Satura formats</h2>
<p class="sdesc">Photo dominee ar 65%, Reel 15%, Video 11%, Link 9%.</p>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sw('fmtC','doughnut',this)">Doughnut</button><button onclick="sw('fmtC','bar',this)">Bar</button></div></div><div class="cw"><canvas id="fmtCC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">05</span>Formata efektivitate</h2>
<p class="sdesc">Videja iesaiste pec formata — kurs formats darbojas vislabak?</p>
<div class="cs"><div class="cw"><canvas id="fmtAvgC"></canvas></div></div></div>
</div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">06</span>Bilzu orientacija</h2>
<p class="sdesc">Vertikali 46% ir popularakais. Horizontali 33%, Kvadrats 21%.</p>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sw('oriC','doughnut',this)">Doughnut</button><button onclick="sw('oriC','bar',this)">Bar</button></div></div><div class="cw"><canvas id="oriCC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">07</span>Orientacijas efektivitate</h2>
<p class="sdesc">Videja iesaiste pec bildes orientacijas.</p>
<div class="cs"><div class="cw"><canvas id="oriAvgC"></canvas></div></div></div>
</div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">08</span>Teksts uz bildes</h2>
<p class="sdesc">Cik teksta ir uz vizualajiem materialiem. Labakais: 1-80 zimes.</p>
<div class="cs"><div class="cw"><canvas id="txtImgC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">09</span>Pavadosa teksta garums</h2>
<p class="sdesc">Isaks teksts (1-120) ir visefektivakais. Gari teksti (241+) — zemaka iesaiste.</p>
<div class="cs"><div class="cw"><canvas id="capLenC"></canvas></div></div></div>
</div></div>

<div class="section"><h2 class="stitle"><span class="num">10</span>Publiceshanas dienas</h2>
<p class="sdesc">Sestdienas uzrada 2x augstaku iesaisti neka darba dienas! Briivdienas ir nenovertetas.</p>
<div class="cs"><div class="cw"><canvas id="wdayC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">11</span>Publiceshanas laiks (stundas)</h2>
<p class="sdesc">Vakara stundas (17:00, 22:00-23:00) uzrada augstaku iesaisti. Visvairak publice 17:00.</p>
<div class="cs"><div class="cw tall"><canvas id="hourC"></canvas></div></div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">12</span>Darba dienas vs Briivdienas</h2>
<p class="sdesc">83% publikaciju darba dienas, tikai 17% briivdienas.</p>
<div class="cs"><div class="cw"><canvas id="wwC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">13</span>Laika slots</h2>
<p class="sdesc">Vakari (19-01) uzrada augstaku vid. iesaisti neka darba laiks (9-19).</p>
<div class="cs"><div class="cw"><canvas id="slotC"></canvas></div></div></div>
</div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">14</span>Iesaistes sadalijums</h2>
<p class="sdesc">Likes, Shares un Comments proporcija kopeja iesaiste.</p>
<div class="cs"><div class="cw"><canvas id="engBrkC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">15</span>Iesaistes koncentracija</h2>
<p class="sdesc">Top 1% postu genere {D['concentration']['top1_pct_share']}% no visas iesaistes.</p>
<div class="cs"><div class="cw"><canvas id="concC"></canvas></div></div></div>
</div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">16</span>H1 vs H2 (pusgadi)</h2>
<p class="sdesc">Pirma vs otra pusgada salidzinajums. Izaugsme: {D['half_year_growth']:+.1f}%.</p>
<div class="cs"><div class="cw"><canvas id="halfC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">17</span>Konkursi vs Parastie posti</h2>
<p class="sdesc">{D['contest']['contest_posts']} konkursu posti ({D['contest']['contest_pct']}%). Videja iesaiste: {D['contest']['contest_avg']} vs {D['contest']['non_contest_avg']}.</p>
<div class="cs"><div class="cw"><canvas id="contestC"></canvas></div></div></div>
</div></div>

<div class="section"><h2 class="stitle"><span class="num">18</span>Iesaistes sadalijums pa diapazoniem</h2>
<p class="sdesc">Cik publikacijas iekrit katra iesaistes diapazona.</p>
<div class="cs"><div class="cw"><canvas id="engDistC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">19</span>Bilzu krasas</h2>
<p class="sdesc">Dominejosas krasas vizualajos materialos.</p>
<div class="cs"><div class="cw"><canvas id="colorC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">20</span>Top 15 lapas pec kopejas iesaistes</h2>
<div class="cs"><div class="cw tall"><canvas id="topPagesC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">21</span>Top 15 lapas pec videjas iesaistes</h2>
<div class="cs"><div class="cw tall"><canvas id="topPagesAvgC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">22</span>Top 15 lapas pec publikaciju skaita</h2>
<div class="cs"><div class="cw tall"><canvas id="topPagesPostsC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">23</span>Popularakas saites</h2>
<div class="cs"><div class="cw"><canvas id="linksC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">24</span>Top 10 publikacijas</h2>
<div class="cs"><div style="overflow-x:auto"><table id="topT"></table></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">25</span>Visu lapu parskats</h2>
<div class="cs"><div style="overflow-x:auto"><table id="allPagesT"></table></div></div></div>

<div class="sd2">Secinajumi un Ieteikumi</div>
<div class="con-grid" id="conG"></div>

<div class="footer">Ventspils Facebook 2025 — 50 lapas · Kopejais parskats</div>
</div>

<script>
const D={data_json};

function nf(n){{return n.toString().replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,' ')}}

// Chart defaults
Chart.defaults.color='#8B95A5';
Chart.defaults.borderColor='rgba(255,255,255,0.04)';
Chart.defaults.font.family="'Inter',system-ui,sans-serif";
Chart.defaults.font.size=12;
Chart.defaults.plugins.legend.labels.padding=16;
Chart.defaults.plugins.legend.labels.usePointStyle=true;
Chart.defaults.plugins.legend.labels.pointStyle='circle';
Chart.defaults.plugins.tooltip.backgroundColor='#1A2030';
Chart.defaults.plugins.tooltip.borderColor='rgba(255,255,255,0.08)';
Chart.defaults.plugins.tooltip.borderWidth=1;
Chart.defaults.plugins.tooltip.cornerRadius=10;
Chart.defaults.plugins.tooltip.padding=12;
Chart.defaults.plugins.tooltip.titleFont={{weight:'600',size:13}};
Chart.defaults.elements.bar.borderRadius=8;
Chart.defaults.elements.bar.borderSkipped=false;
Chart.defaults.elements.line.borderWidth=2;
Chart.defaults.elements.point.radius=3;
Chart.defaults.elements.point.hoverRadius=6;

var CL=['#1877F2','#34D399','#FBBF24','#F87171','#A78BFA','#06b6d4','#ec4899','#f97316','#84cc16','#6366f1','#0ea5e9','#e11d48','#10b981','#7c3aed','#2563eb'];
var CH={{}};var CT={{}};
function sw(id,tp,btn){{CT[id]=tp;btn.parentElement.querySelectorAll('button').forEach(function(b){{b.classList.remove('active')}});btn.classList.add('active');rc(id)}}
function rc(id){{if(CH[id])CH[id].destroy();var c=CFG[id](CT[id]||'bar');CH[id]=new Chart(document.getElementById(c.cid),c.cfg)}}
function scOpts(){{return{{grid:{{color:'rgba(255,255,255,0.04)'}},ticks:{{color:'#8B95A5',font:{{size:11}}}}}}}}

var CFG={{}};

// 01: Monthly Engagement
CFG.mEng=function(t){{var m=D.monthly;return{{cid:'mEngC',cfg:{{type:t,data:{{labels:m.map(function(x){{return x.name}}),datasets:[{{label:'Iesaiste',data:m.map(function(x){{return x.engagement}}),backgroundColor:'rgba(24,119,242,0.5)',borderColor:'#1877F2',borderWidth:2,tension:.4}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};CT.mEng='bar';

// 02: Monthly Posts
CFG.mPosts=function(t){{var m=D.monthly;return{{cid:'mPostsC',cfg:{{type:t,data:{{labels:m.map(function(x){{return x.name}}),datasets:[{{label:'Publikacijas',data:m.map(function(x){{return x.posts}}),backgroundColor:'rgba(167,139,250,0.5)',borderColor:'#A78BFA',borderWidth:2,tension:.4}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};CT.mPosts='bar';

// 03: Monthly Avg
CFG.mAvg=function(t){{var m=D.monthly;return{{cid:'mAvgC',cfg:{{type:t,data:{{labels:m.map(function(x){{return x.name}}),datasets:[{{label:'Vid. iesaiste',data:m.map(function(x){{return x.avg_eng}}),backgroundColor:'rgba(52,211,153,0.5)',borderColor:'#34D399',borderWidth:2,tension:.4}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};CT.mAvg='bar';

// 04: Format distribution
CFG.fmtC=function(t){{var f=D.formats;return{{cid:'fmtCC',cfg:{{type:t,data:{{labels:f.map(function(x){{return x.type+' ('+x.pct+'%)'}}),datasets:[{{data:f.map(function(x){{return x.count}}),backgroundColor:CL.slice(0,4),borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:t==='doughnut'?{{}}:{{x:scOpts(),y:scOpts()}}}}}}}}}};CT.fmtC='doughnut';

// 05: Format effectiveness
CFG.fmtAvgC=function(){{var f=D.formats;return{{cid:'fmtAvgC',cfg:{{type:'bar',data:{{labels:f.map(function(x){{return x.type}}),datasets:[{{label:'Vid. iesaiste',data:f.map(function(x){{return x.avg_eng}}),backgroundColor:CL.slice(0,4)}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// 06: Orientation
CFG.oriC=function(t){{var o=D.orientation;return{{cid:'oriCC',cfg:{{type:t,data:{{labels:o.map(function(x){{return x.name+' ('+x.pct+'%)'}}),datasets:[{{data:o.map(function(x){{return x.count}}),backgroundColor:['#34D399','#F87171','#FBBF24'],borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:t==='doughnut'?{{}}:{{x:scOpts(),y:scOpts()}}}}}}}}}};CT.oriC='doughnut';

// 07: Orientation effectiveness
CFG.oriAvgC=function(){{var o=D.orientation;return{{cid:'oriAvgC',cfg:{{type:'bar',data:{{labels:o.map(function(x){{return x.name}}),datasets:[{{label:'Vid. iesaiste',data:o.map(function(x){{return x.avg_eng}}),backgroundColor:['#34D399','#F87171','#FBBF24']}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// 08: Text on image
CFG.txtImgC=function(){{var t=D.text_on_image;return{{cid:'txtImgC',cfg:{{type:'bar',data:{{labels:t.map(function(x){{return x.name}}),datasets:[{{label:'Skaits',data:t.map(function(x){{return x.count}}),backgroundColor:'rgba(24,119,242,0.4)',yAxisID:'y'}},{{label:'Vid. iesaiste',data:t.map(function(x){{return x.avg_eng}}),backgroundColor:'rgba(251,191,36,0.6)',yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:Object.assign({{}},scOpts(),{{position:'left',title:{{display:true,text:'Skaits',color:'#8B95A5'}}}}),y1:Object.assign({{}},scOpts(),{{position:'right',grid:{{drawOnChartArea:false}},title:{{display:true,text:'Vid. iesaiste',color:'#8B95A5'}}}})}}}}}}}}}};

// 09: Caption length
CFG.capLenC=function(){{var c=D.caption_length;return{{cid:'capLenC',cfg:{{type:'bar',data:{{labels:c.map(function(x){{return x.name}}),datasets:[{{label:'Skaits',data:c.map(function(x){{return x.count}}),backgroundColor:'rgba(167,139,250,0.4)',yAxisID:'y'}},{{label:'Vid. iesaiste',data:c.map(function(x){{return x.avg_eng}}),backgroundColor:'rgba(52,211,153,0.6)',yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:Object.assign({{}},scOpts(),{{position:'left',title:{{display:true,text:'Skaits',color:'#8B95A5'}}}}),y1:Object.assign({{}},scOpts(),{{position:'right',grid:{{drawOnChartArea:false}},title:{{display:true,text:'Vid. iesaiste',color:'#8B95A5'}}}})}}}}}}}}}};

// 10: Weekday
CFG.wdayC=function(){{var w=D.weekday;return{{cid:'wdayC',cfg:{{type:'bar',data:{{labels:w.map(function(x){{return x.name}}),datasets:[{{label:'Publikacijas',data:w.map(function(x){{return x.posts}}),backgroundColor:'rgba(24,119,242,0.3)',yAxisID:'y'}},{{label:'Vid. iesaiste',data:w.map(function(x){{return x.avg_eng}}),backgroundColor:w.map(function(x){{return x.day>=6?'rgba(52,211,153,0.7)':'rgba(251,191,36,0.5)'}}),yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:Object.assign({{}},scOpts(),{{position:'left',title:{{display:true,text:'Publikacijas',color:'#8B95A5'}}}}),y1:Object.assign({{}},scOpts(),{{position:'right',grid:{{drawOnChartArea:false}},title:{{display:true,text:'Vid. iesaiste',color:'#8B95A5'}}}})}}}}}}}}}};

// 11: Hourly
CFG.hourC=function(){{var h=D.hourly;return{{cid:'hourC',cfg:{{type:'bar',data:{{labels:h.map(function(x){{return x.hour}}),datasets:[{{label:'Publikacijas',data:h.map(function(x){{return x.posts}}),backgroundColor:'rgba(24,119,242,0.25)',yAxisID:'y'}},{{label:'Vid. iesaiste',data:h.map(function(x){{return x.avg_eng}}),type:'line',borderColor:'#FBBF24',backgroundColor:'rgba(251,191,36,0.1)',tension:.4,fill:true,yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:Object.assign({{}},scOpts(),{{position:'left',title:{{display:true,text:'Publikacijas',color:'#8B95A5'}}}}),y1:Object.assign({{}},scOpts(),{{position:'right',grid:{{drawOnChartArea:false}},title:{{display:true,text:'Vid. iesaiste',color:'#8B95A5'}}}})}}}}}}}}}};

// 12: Work vs Weekend
CFG.wwC=function(){{var w=D.work_weekend;return{{cid:'wwC',cfg:{{type:'doughnut',data:{{labels:['Darba dienas ('+w.work_pct+'%)','Briivdienas ('+w.weekend_pct+'%)'],datasets:[{{data:[w.work_posts,w.weekend_posts],backgroundColor:['rgba(24,119,242,0.5)','rgba(52,211,153,0.5)'],borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false}}}}}}}};

// 13: Time slots
CFG.slotC=function(){{var s=D.time_slots;return{{cid:'slotC',cfg:{{type:'bar',data:{{labels:s.map(function(x){{return x.name}}),datasets:[{{label:'Publikacijas',data:s.map(function(x){{return x.posts}}),backgroundColor:'rgba(24,119,242,0.3)',yAxisID:'y'}},{{label:'Vid. iesaiste',data:s.map(function(x){{return x.avg_eng}}),backgroundColor:'rgba(251,191,36,0.6)',yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:Object.assign({{}},scOpts(),{{position:'left'}}),y1:Object.assign({{}},scOpts(),{{position:'right',grid:{{drawOnChartArea:false}}}})}}}}}}}}}};

// 14: Engagement breakdown
CFG.engBrkC=function(){{var e=D.engagement_breakdown;return{{cid:'engBrkC',cfg:{{type:'doughnut',data:{{labels:['Likes ('+e.likes_pct+'%)','Shares ('+e.shares_pct+'%)','Comments ('+e.comments_pct+'%)'],datasets:[{{data:[D.kpi.total_likes,D.kpi.total_shares,D.kpi.total_comments],backgroundColor:['#1877F2','#34D399','#FBBF24'],borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false}}}}}}}};

// 15: Concentration
CFG.concC=function(){{var c=D.concentration;return{{cid:'concC',cfg:{{type:'doughnut',data:{{labels:['Top 1% ('+c.top1_pct_share+'%)','Top 2-10% ('+(c.top10_pct_share-c.top1_pct_share).toFixed(1)+'%)','Parējie ('+c.rest_share+'%)'],datasets:[{{data:[c.top1_pct_eng,c.top10_pct_eng-c.top1_pct_eng,c.rest_eng],backgroundColor:['#F87171','#FBBF24','#1877F2'],borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false}}}}}}}};

// 16: Half year
CFG.halfC=function(){{var h=D.half_year;return{{cid:'halfC',cfg:{{type:'bar',data:{{labels:h.map(function(x){{return x.name}}),datasets:[{{label:'Publikacijas',data:h.map(function(x){{return x.posts}}),backgroundColor:'rgba(24,119,242,0.3)',yAxisID:'y'}},{{label:'Vid. iesaiste',data:h.map(function(x){{return x.avg_eng}}),backgroundColor:'rgba(52,211,153,0.6)',yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:Object.assign({{}},scOpts(),{{position:'left'}}),y1:Object.assign({{}},scOpts(),{{position:'right',grid:{{drawOnChartArea:false}}}})}}}}}}}}}};

// 17: Contest
CFG.contestC=function(){{var c=D.contest;return{{cid:'contestC',cfg:{{type:'bar',data:{{labels:['Konkursu posti','Parastie posti'],datasets:[{{label:'Skaits',data:[c.contest_posts,c.non_contest_posts],backgroundColor:['rgba(248,113,113,0.4)','rgba(24,119,242,0.4)'],yAxisID:'y'}},{{label:'Vid. iesaiste',data:[c.contest_avg,c.non_contest_avg],backgroundColor:['rgba(248,113,113,0.7)','rgba(24,119,242,0.7)'],yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:Object.assign({{}},scOpts(),{{position:'left',title:{{display:true,text:'Skaits',color:'#8B95A5'}}}}),y1:Object.assign({{}},scOpts(),{{position:'right',grid:{{drawOnChartArea:false}},title:{{display:true,text:'Vid. iesaiste',color:'#8B95A5'}}}})}}}}}}}}}};

// 18: Engagement distribution
CFG.engDistC=function(){{var e=D.eng_dist;return{{cid:'engDistC',cfg:{{type:'bar',data:{{labels:e.map(function(x){{return x.bucket}}),datasets:[{{label:'Publikacijas',data:e.map(function(x){{return x.count}}),backgroundColor:CL.slice(0,7)}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// 19: Colors
CFG.colorC=function(){{var c=D.colors;return{{cid:'colorC',cfg:{{type:'bar',data:{{labels:c.map(function(x){{return x.name+' ('+x.pct+'%)'}}),datasets:[{{label:'Skaits',data:c.map(function(x){{return x.count}}),backgroundColor:c.map(function(x){{return x.hex==='#ffffff'?'rgba(255,255,255,0.6)':x.hex==='#000000'?'rgba(100,100,100,0.6)':x.hex}})}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// 20: Top pages by engagement
CFG.topPagesC=function(){{var p=D.top_pages_eng;return{{cid:'topPagesC',cfg:{{type:'bar',data:{{labels:p.map(function(x){{return x.name.length>25?x.name.substring(0,25)+'...':x.name}}),datasets:[{{label:'Kopeja iesaiste',data:p.map(function(x){{return x.engagement}}),backgroundColor:CL}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// 21: Top pages by avg
CFG.topPagesAvgC=function(){{var p=D.top_pages_avg;return{{cid:'topPagesAvgC',cfg:{{type:'bar',data:{{labels:p.map(function(x){{return x.name.length>25?x.name.substring(0,25)+'...':x.name}}),datasets:[{{label:'Vid. iesaiste',data:p.map(function(x){{return x.avg_eng}}),backgroundColor:CL}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// 22: Top pages by posts
CFG.topPagesPostsC=function(){{var p=D.top_pages_posts;return{{cid:'topPagesPostsC',cfg:{{type:'bar',data:{{labels:p.map(function(x){{return x.name.length>25?x.name.substring(0,25)+'...':x.name}}),datasets:[{{label:'Publikacijas',data:p.map(function(x){{return x.posts}}),backgroundColor:CL}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// 23: Popular links
CFG.linksC=function(){{var l=D.popular_links;return{{cid:'linksC',cfg:{{type:'bar',data:{{labels:l.map(function(x){{return x.domain}}),datasets:[{{label:'Reizes',data:l.map(function(x){{return x.count}}),backgroundColor:CL}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Build KPI
function buildKPI(){{
  var k=D.kpi;
  var items=[
    ['Publikacijas',nf(k.total_posts),'50 lapas · '+k.avg_posts_per_day+' diena'],
    ['Kopeja iesaiste',nf(k.total_engagement),'Likes + Shares + Comments'],
    ['Vid. iesaiste / post',k.avg_eng_per_post,''],
    ['Likes',nf(k.total_likes),'Vid. '+k.avg_likes_per_post+' / post'],
    ['Shares',nf(k.total_shares),'Vid. '+k.avg_shares_per_post+' / post'],
    ['Komentari',nf(k.total_comments),'Vid. '+k.avg_comments_per_post+' / post'],
    ['Facebook lapas',k.unique_pages,'Ventspils pasvaldiba'],
    ['Vid. posts / diena',k.avg_posts_per_day,'Visas lapas kopa'],
  ];
  document.getElementById('kpiG').innerHTML=items.map(function(it){{
    return '<div class="kpi"><div class="label">'+it[0]+'</div><div class="value">'+it[1]+'</div><div class="sub">'+it[2]+'</div></div>';
  }}).join('');
}}

// Build top posts table
function buildTopPosts(){{
  var t=D.top_posts;
  var h='<tr><th>#</th><th>Lapa</th><th>Tips</th><th>Datums</th><th>Likes</th><th>Shares</th><th>Comm.</th><th>Kopa</th><th>Teksts</th></tr>';
  t.forEach(function(p,i){{
    var fbUrl=p.id?'https://facebook.com/'+p.id:'#';
    h+='<tr><td>'+(i+1)+'</td><td>'+p.lapa+'</td><td>'+p.type+'</td><td>'+p.date+'</td><td>'+nf(p.likes)+'</td><td>'+nf(p.shares)+'</td><td>'+nf(p.comments)+'</td><td><strong>'+nf(p.engagement)+'</strong></td><td style="max-width:250px;font-size:0.82em;color:var(--text-3)">'+p.teksts.substring(0,80)+'...</td></tr>';
  }});
  document.getElementById('topT').innerHTML=h;
}}

// Build all pages table
function buildAllPages(){{
  var p=D.all_pages;
  var h='<tr><th>#</th><th>Lapa</th><th>Sekotaji</th><th>Posti</th><th>Iesaiste</th><th>Vid.</th><th>Likes</th><th>Shares</th><th>Comm.</th></tr>';
  p.forEach(function(pg,i){{
    h+='<tr><td>'+(i+1)+'</td><td>'+pg.name+'</td><td>'+nf(pg.followers)+'</td><td>'+pg.posts+'</td><td>'+nf(pg.engagement)+'</td><td><strong>'+pg.avg_eng+'</strong></td><td>'+nf(pg.likes)+'</td><td>'+nf(pg.shares)+'</td><td>'+nf(pg.comments)+'</td></tr>';
  }});
  document.getElementById('allPagesT').innerHTML=h;
}}

// Build conclusions
function buildConclusions(){{
  var k=D.kpi;var c=D.contest;var w=D.work_weekend;var cn=D.concentration;var wt=D.without_top3;
  var items=[
    ['good','Iespaidigs kopejais apjoms','<span class="st">'+nf(k.total_posts)+'</span> publikacijas no <span class="hl">50 lapam</span> ar kopejo iesaisti <span class="st">'+nf(k.total_engagement)+'</span>. Videja iesaiste: <span class="st">'+k.avg_eng_per_post+'</span> uz postu.'],
    ['good','Briivdienas — 2x augstaka iesaiste','Sestdienas vid. iesaiste <span class="st">'+w.weekend_avg+'</span> ir <span class="st">'+Math.round(w.weekend_avg/w.work_avg*100-100)+'% augstaka</span> neka darba dienas ('+w.work_avg+'). Bet tikai <span class="st">'+w.weekend_pct+'%</span> postu ir briivdienas!'],
    ['tip','Ieteikums: vairak publiceties briivdienas','Palaidinat saturu <span class="hl">briivdienas</span> — meerkjis butu vismaz <span class="st">25-30%</span> publikaciju briivdienas (pashlaik tikai '+w.weekend_pct+'%). Sezona sesdiena ir labaka diena!'],
    ['good','Vakari uzrada augstaku iesaisti','Laika slots <span class="hl">19:00-01:00</span> uzrada augstaku vid. iesaisti. Stunda <span class="st">23:00</span> ir ar visaugstako vid. iesaisti, lai ari maz postu. <span class="hl">17:00</span> ir popularakais publiceshanas laiks.'],
    ['tip','Vertikals attels ir labakais formats','Vertikalie atteli (<span class="st">46%</span>) dominee un uzrada labu iesaisti. <span class="hl">Horizontali</span> atteli ir vismazak efektivi. Ieteikums: fokuss uz vertikaliem un kvadrata formatiem.'],
    ['tip','Isaks pavadoshais teksts — efektivakais','Teksts <span class="st">1-120 zimes</span> uzrada labu iesaisti. Gari teksti (241+ zimes) — <span class="st">56%</span> no visiem postiem — ir mazak efektivi. Ieteikums: saisiniet tekstus!'],
    ['good','Photo — dominejoshais formats','<span class="st">65%</span> no visam publikacijam ir Photo formata. Reel (<span class="st">15%</span>) aug, Video (<span class="st">11%</span>) ir stabils, Link postu (<span class="st">9%</span>) ir vismazak.'],
    ['tip','Teksts uz bildes: mazak ir vairak','Labaka iesaiste ir attelos ar <span class="st">1-80 zimem</span> teksta. Atteli bez teksta vai ar parmeerigu tekstu (81+) uzrada zemaku iesaisti.'],
    ['bad','Konkursu posti nepalielina iesaisti','Pret intuiciju: konkursu postu vid. iesaiste (<span class="st">'+c.contest_avg+'</span>) ir <span class="st">zemaka</span> neka parastu postu ('+c.non_contest_avg+'). Konkursi veido tikai '+c.contest_pct+'% no postiem.'],
    ['good','Iesaistes koncentracija','Top <span class="st">1%</span> postu ('+cn.top1_pct_posts+') genere <span class="st">'+cn.top1_pct_share+'%</span> no visas iesaistes. Top 10% — <span class="st">'+cn.top10_pct_share+'%</span>. Padejie 90% — tikai '+cn.rest_share+'%.'],
    ['good','H2 uzrada augstaku vid. iesaisti','2. pusgads (Jul-Dec) uzrada vid. iesaisti <span class="st">'+D.half_year[1].avg_eng+'</span>, kas ir <span class="st">'+D.half_year_growth+'%</span> salidzinajuma ar H1 ('+D.half_year[0].avg_eng+').'],
    ['good','Top 3 lapas dominee','<span class="hl">'+wt.pages[0]+'</span>, <span class="hl">'+wt.pages[1]+'</span> un <span class="hl">'+wt.pages[2]+'</span> kopā veido lielu dalju no kopejas iesaistes. Bez vinjam vid. iesaiste ir <span class="st">'+wt.avg_eng+'</span> (vs '+wt.original_avg+' ar visam).'],
    ['tip','Publiceshanas konsekvence pa menesiem','Oktobri/Novembri visvairak postu (~1236), bet vasara mazak (~860). Ieteikums: palidzinat konsekvenci, jo vasara iesaiste ir augstaka bet postu mazak.'],
    ['good','Likes dominee iesaisti','Likes veido <span class="st">'+D.engagement_breakdown.likes_pct+'%</span>, Shares <span class="st">'+D.engagement_breakdown.shares_pct+'%</span>, Comments tikai <span class="st">'+D.engagement_breakdown.comments_pct+'%</span>. Shares ir lielaka vertiba — tie izplata saturu talak.'],
    ['tip','Ieteikums: stimuleet vairak Shares','Shares ir <span class="st">'+D.engagement_breakdown.shares_pct+'%</span> — tas ir organiska izplatiba. Veidojiet saturu, ko cilveeki velas dalities — <span class="hl">emocionalus stastus, vizualus foto, lokalo lepnumu</span>.'],
    ['tip','Vairak Reel formata','Reel ir tikai <span class="st">15%</span> no visa satura, bet platformas algoritms to prioritize. Ieteikums: paliddzinat Reel dalju lidz <span class="st">25-30%</span> 2026. gada.'],
    ['good','Ventspils lapa — Nr.1 pec iesaistes','<span class="hl">Ventspils</span> lapa ar 1 072 postiem un 164 454 kopeju iesaisti ir absoluutais liideris. Vid. iesaiste: <span class="st">153.4</span>.'],
    ['good','Ziemelkurzemes slimniica — augstaka vid. iesaiste','Ar vid. <span class="st">187.6</span> uz postu, slimniica uzrada visaugstako efektivitaati no visam 50 lapam.'],
    ['tip','Mazas lapas — nepietiekams saturs','9 lapas publicee mazak par <span class="st">50 postiem gada</span> (mazak par 1x nedela). Taam japalielina regularitaate.'],
    ['tip','Ricibas plans 2026','<p>1. Palielinat briivdienu saturu lidz 25%+</p><p>2. Fokuss uz vakara publiceshanu (17-22)</p><p>3. Vertikali + isaks teksts = labakais formuls</p><p>4. Reel dalju palielinat lidz 25-30%</p><p>5. Stimuleet Shares ar emocionaliem stastiem</p>'],
  ];
  var g=document.getElementById('conG');
  g.innerHTML=items.map(function(it){{
    return '<div class="con '+it[0]+'"><h3>'+it[1]+'</h3><p>'+it[2]+'</p></div>';
  }}).join('');
}}

// Scroll animations
function initScroll(){{
  var obs=new IntersectionObserver(function(e){{e.forEach(function(en){{if(en.isIntersecting)en.target.classList.add('visible')}});}},{{threshold:0.08,rootMargin:'0px 0px -40px 0px'}});
  document.querySelectorAll('.section,.con').forEach(function(el){{obs.observe(el)}});
}}

document.addEventListener('DOMContentLoaded',function(){{
  buildKPI();
  Object.keys(CFG).forEach(function(id){{rc(id)}});
  buildTopPosts();
  buildAllPages();
  buildConclusions();
  document.querySelectorAll('.con').forEach(function(el,i){{el.style.transitionDelay=(i*0.06)+'s'}});
  initScroll();
}});
</script>
</body></html>'''

    return html


def main():
    posts = load_all_data()
    D = compute_data(posts)
    html = generate_html(D)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nGenerated: {OUTPUT}")
    print(f"File size: {os.path.getsize(OUTPUT) / 1024:.0f} KB")


if __name__ == '__main__':
    main()
