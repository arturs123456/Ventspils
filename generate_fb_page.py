#!/usr/bin/env python3
"""Generate individual Facebook page report – one-pager with premium design."""
import openpyxl
import json
import os
import re
import math
from datetime import datetime
from collections import defaultdict, Counter

DIR = os.path.dirname(os.path.abspath(__file__))
XLSX = '/Users/arturs25/Downloads/facebook_posts-2026-02-24.xlsx'

# ── which page to generate (can override via argv) ──
import sys
PAGE_NAME = sys.argv[1] if len(sys.argv) > 1 else 'Ventspils'

MONTH_NAMES = ['Jan','Feb','Mar','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dec']
DAY_NAMES = ['Pirmdiena','Otrdiena','Trešdiena','Ceturtdiena','Piektdiena','Sestdiena','Svētdiena']

def safe_int(v):
    if v is None: return 0
    try: return int(v)
    except: return 0

def safe_float(v):
    if v is None: return 0.0
    try: return float(v)
    except: return 0.0

def load_page_data():
    print(f"Loading data for: {PAGE_NAME}")
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb['Worksheet']

    posts = []
    all_pages_names = set()

    for row in ws.iter_rows(min_row=2, values_only=True):
        all_pages_names.add(row[1])
        if row[1] != PAGE_NAME:
            continue

        ts = row[12]
        hour = None
        if ts and isinstance(ts, (int, float)):
            try:
                hour = datetime.fromtimestamp(ts).hour
            except:
                pass

        teksts = str(row[3]) if row[3] else ''
        t_lower = teksts.lower()
        is_contest = any(k in t_lower for k in ['konkurs','laimē','izlozē','loterij','izloze','laimēt','piedalies un laimē','piedalies'])

        posts.append({
            'id': row[0],
            'type': row[2] or 'Other',
            'teksts': teksts,
            't_zimes': safe_int(row[4]),
            'picture': str(row[5]) if row[5] else '',
            'gif': str(row[6]).upper() == 'Y' if row[6] else False,
            'a_zimes': safe_int(row[7]),
            'a_prop': str(row[8]) if row[8] else '',
            'a_krasa': str(row[9]) if row[9] else '',
            'date': str(row[11]) if row[11] else '',
            'hour': hour,
            'day': safe_int(row[13]),
            'shares': safe_int(row[14]),
            'likes': safe_int(row[15]),
            'comments': safe_int(row[16]),
            'slc': safe_int(row[17]),
            'video_len': safe_float(row[18]),
            'views': safe_int(row[19]),
            'is_contest': is_contest,
            'fb_url': str(row[27]) if row[27] else '',
            'top1s': str(row[21]) == 'Y',
            'top1l': str(row[22]) == 'Y',
            'top1c': str(row[23]) == 'Y',
            'top10s': str(row[24]) == 'Y',
            'top10l': str(row[25]) == 'Y',
            'top10c': str(row[26]) == 'Y',
        })

    wb.close()
    print(f"  Loaded {len(posts)} posts")
    return posts, sorted(all_pages_names)


def compute(posts):
    D = {}
    n = len(posts)
    if n == 0:
        return D

    total_likes = sum(p['likes'] for p in posts)
    total_shares = sum(p['shares'] for p in posts)
    total_comments = sum(p['comments'] for p in posts)
    total_eng = total_likes + total_shares + total_comments
    avg_eng = round(total_eng / n, 1) if n else 0

    # Median engagement
    sorted_eng = sorted(p['slc'] for p in posts)
    median_eng = sorted_eng[n // 2] if n else 0

    # ── KPI ──
    D['kpi'] = {
        'total_posts': n,
        'total_likes': total_likes,
        'total_shares': total_shares,
        'total_comments': total_comments,
        'total_engagement': total_eng,
        'avg_eng': avg_eng,
        'median_eng': median_eng,
        'likes_ratio': round(total_likes / total_eng * 100, 1) if total_eng else 0,
        'shares_ratio': round(total_shares / total_eng * 100, 1) if total_eng else 0,
        'comments_ratio': round(total_comments / total_eng * 100, 1) if total_eng else 0,
        'cl_ratio': round(total_comments / total_likes * 100, 2) if total_likes else 0,
    }

    # Viral posts (eng > avg*3)
    viral_threshold = avg_eng * 3
    viral = [p for p in posts if p['slc'] >= viral_threshold]
    D['kpi']['viral_count'] = len(viral)
    D['kpi']['viral_pct'] = round(len(viral) / n * 100, 1)

    # ── MONTHLY ──
    monthly = defaultdict(lambda: {'posts': 0, 'likes': 0, 'shares': 0, 'comments': 0, 'eng': 0})
    for p in posts:
        d = p['date']
        if d and len(d) >= 7:
            try:
                m = int(d[5:7])
                monthly[m]['posts'] += 1
                monthly[m]['likes'] += p['likes']
                monthly[m]['shares'] += p['shares']
                monthly[m]['comments'] += p['comments']
                monthly[m]['eng'] += p['slc']
            except:
                pass

    D['monthly'] = []
    for m in range(1, 13):
        md = monthly[m]
        D['monthly'].append({
            'month': m,
            'name': MONTH_NAMES[m - 1],
            'posts': md['posts'],
            'engagement': md['eng'],
            'avg_eng': round(md['eng'] / md['posts'], 1) if md['posts'] else 0,
            'likes': md['likes'],
            'shares': md['shares'],
            'comments': md['comments'],
        })

    # H1 vs H2
    h1 = [m for m in D['monthly'] if m['month'] <= 6]
    h2 = [m for m in D['monthly'] if m['month'] > 6]
    h1_posts = sum(m['posts'] for m in h1)
    h2_posts = sum(m['posts'] for m in h2)
    h1_eng = sum(m['engagement'] for m in h1)
    h2_eng = sum(m['engagement'] for m in h2)
    h1_avg = round(h1_eng / h1_posts, 1) if h1_posts else 0
    h2_avg = round(h2_eng / h2_posts, 1) if h2_posts else 0
    D['half_year'] = [
        {'name': 'H1 (Jan-Jun)', 'posts': h1_posts, 'engagement': h1_eng, 'avg_eng': h1_avg},
        {'name': 'H2 (Jul-Dec)', 'posts': h2_posts, 'engagement': h2_eng, 'avg_eng': h2_avg},
    ]
    D['half_year_growth'] = round((h2_avg - h1_avg) / h1_avg * 100, 1) if h1_avg else 0

    # Monthly CV (consistency)
    monthly_avgs = [m['avg_eng'] for m in D['monthly'] if m['posts'] > 0]
    if len(monthly_avgs) > 1:
        mu = sum(monthly_avgs) / len(monthly_avgs)
        std = (sum((x - mu) ** 2 for x in monthly_avgs) / len(monthly_avgs)) ** 0.5
        D['kpi']['cv'] = round(std / mu, 2) if mu else 0
    else:
        D['kpi']['cv'] = 0

    # Best/worst month
    active_months = [m for m in D['monthly'] if m['posts'] > 0]
    if active_months:
        best_m = max(active_months, key=lambda x: x['avg_eng'])
        worst_m = min(active_months, key=lambda x: x['avg_eng'])
        D['kpi']['best_month'] = f"{best_m['name']} ({best_m['avg_eng']})"
        D['kpi']['worst_month'] = f"{worst_m['name']} ({worst_m['avg_eng']})"
    else:
        D['kpi']['best_month'] = '-'
        D['kpi']['worst_month'] = '-'

    # ── WEEKDAY ──
    weekday_data = defaultdict(lambda: {'posts': 0, 'eng': 0})
    for p in posts:
        d = p['day']
        if 1 <= d <= 7:
            weekday_data[d]['posts'] += 1
            weekday_data[d]['eng'] += p['slc']

    D['weekday'] = []
    for d in range(1, 8):
        wd = weekday_data[d]
        D['weekday'].append({
            'day': d,
            'name': DAY_NAMES[d - 1],
            'posts': wd['posts'],
            'engagement': wd['eng'],
            'avg_eng': round(wd['eng'] / wd['posts'], 1) if wd['posts'] else 0,
        })

    # Work vs Weekend
    work = [p for p in posts if 1 <= p['day'] <= 5]
    weekend = [p for p in posts if p['day'] in (6, 7)]
    work_eng = sum(p['slc'] for p in work)
    wknd_eng = sum(p['slc'] for p in weekend)
    D['work_weekend'] = {
        'work_posts': len(work), 'work_pct': round(len(work) / n * 100, 1),
        'work_avg': round(work_eng / len(work), 1) if work else 0,
        'weekend_posts': len(weekend), 'weekend_pct': round(len(weekend) / n * 100, 1),
        'weekend_avg': round(wknd_eng / len(weekend), 1) if weekend else 0,
    }

    # ── HOURLY ──
    hourly = defaultdict(lambda: {'posts': 0, 'eng': 0})
    for p in posts:
        if p['hour'] is not None:
            hourly[p['hour']]['posts'] += 1
            hourly[p['hour']]['eng'] += p['slc']

    D['hourly'] = []
    for h in range(24):
        hd = hourly[h]
        D['hourly'].append({
            'hour': f"{h:02d}:00",
            'posts': hd['posts'],
            'avg_eng': round(hd['eng'] / hd['posts'], 1) if hd['posts'] else 0,
        })

    # ── HEATMAP (day x hour) ──
    heatmap = {}
    for p in posts:
        if p['hour'] is not None and 1 <= p['day'] <= 7:
            key = f"{p['day']}_{p['hour']}"
            if key not in heatmap:
                heatmap[key] = {'posts': 0, 'eng': 0}
            heatmap[key]['posts'] += 1
            heatmap[key]['eng'] += p['slc']

    D['heatmap'] = []
    for day in range(1, 8):
        for hour in range(24):
            k = f"{day}_{hour}"
            hd = heatmap.get(k, {'posts': 0, 'eng': 0})
            D['heatmap'].append({
                'day': day,
                'hour': hour,
                'posts': hd['posts'],
                'avg_eng': round(hd['eng'] / hd['posts'], 1) if hd['posts'] else 0,
            })

    # ── FORMATS ──
    fmt_data = defaultdict(lambda: {'count': 0, 'eng': 0})
    for p in posts:
        fmt_data[p['type']]['count'] += 1
        fmt_data[p['type']]['eng'] += p['slc']

    D['formats'] = []
    for t in sorted(fmt_data, key=lambda x: -fmt_data[x]['count']):
        fd = fmt_data[t]
        D['formats'].append({
            'type': t,
            'count': fd['count'],
            'pct': round(fd['count'] / n * 100, 1),
            'avg_eng': round(fd['eng'] / fd['count'], 1) if fd['count'] else 0,
            'total_eng': fd['eng'],
        })

    # ── ORIENTATION ──
    ori_map = {'Vertik.': 'Vertikāli', 'Horiz.': 'Horizontāli', 'Kvadrāts': 'Kvadrāts'}
    ori_data = defaultdict(lambda: {'count': 0, 'eng': 0})
    for p in posts:
        if p['a_prop']:
            ori_name = ori_map.get(p['a_prop'], p['a_prop'])
            ori_data[ori_name]['count'] += 1
            ori_data[ori_name]['eng'] += p['slc']

    ori_total = sum(v['count'] for v in ori_data.values())
    D['orientation'] = []
    for name in sorted(ori_data, key=lambda x: -ori_data[x]['count']):
        od = ori_data[name]
        D['orientation'].append({
            'name': name,
            'count': od['count'],
            'pct': round(od['count'] / ori_total * 100, 1) if ori_total else 0,
            'avg_eng': round(od['eng'] / od['count'], 1) if od['count'] else 0,
        })

    # ── TEXT ON IMAGE ──
    txt_img = {'Nav teksta': {'count': 0, 'eng': 0}, '1-80': {'count': 0, 'eng': 0}, '81+': {'count': 0, 'eng': 0}}
    for p in posts:
        az = p['a_zimes']
        if az == 0:
            txt_img['Nav teksta']['count'] += 1
            txt_img['Nav teksta']['eng'] += p['slc']
        elif az <= 80:
            txt_img['1-80']['count'] += 1
            txt_img['1-80']['eng'] += p['slc']
        else:
            txt_img['81+']['count'] += 1
            txt_img['81+']['eng'] += p['slc']

    D['text_on_image'] = []
    for name in ['Nav teksta', '1-80', '81+']:
        td = txt_img[name]
        D['text_on_image'].append({
            'name': name,
            'count': td['count'],
            'avg_eng': round(td['eng'] / td['count'], 1) if td['count'] else 0,
        })

    # ── CAPTION LENGTH ──
    cap_buckets = [
        ('Nav teksta', 0, 0),
        ('1-120', 1, 120),
        ('121-240', 121, 240),
        ('241-500', 241, 500),
        ('501+', 501, 99999),
    ]
    cap_data = {b[0]: {'count': 0, 'eng': 0} for b in cap_buckets}
    for p in posts:
        tz = p['t_zimes']
        for name, lo, hi in cap_buckets:
            if lo <= tz <= hi:
                cap_data[name]['count'] += 1
                cap_data[name]['eng'] += p['slc']
                break

    D['caption_length'] = []
    for name, _, _ in cap_buckets:
        cd = cap_data[name]
        D['caption_length'].append({
            'name': name,
            'count': cd['count'],
            'pct': round(cd['count'] / n * 100, 1),
            'avg_eng': round(cd['eng'] / cd['count'], 1) if cd['count'] else 0,
        })

    # ── IMAGE COLORS (top 15) ──
    color_data = defaultdict(int)
    for p in posts:
        if p['a_krasa'] and p['a_krasa'] != 'None':
            color_data[p['a_krasa']] += 1

    total_colors = sum(color_data.values())
    D['colors'] = []
    for c, cnt in sorted(color_data.items(), key=lambda x: -x[1])[:5]:
        D['colors'].append({
            'hex': c,
            'count': cnt,
            'pct': round(cnt / total_colors * 100, 1) if total_colors else 0,
        })

    # ── GIF USAGE ──
    gif_yes = [p for p in posts if p['gif']]
    gif_no = [p for p in posts if not p['gif']]
    D['gif'] = {
        'yes_count': len(gif_yes),
        'yes_avg': round(sum(p['slc'] for p in gif_yes) / len(gif_yes), 1) if gif_yes else 0,
        'no_count': len(gif_no),
        'no_avg': round(sum(p['slc'] for p in gif_no) / len(gif_no), 1) if gif_no else 0,
    }

    # ── VIDEO ANALYSIS ──
    video_posts = [p for p in posts if p['type'] in ('Video', 'Reel') and p['video_len'] > 0]
    D['video'] = {'has_data': len(video_posts) > 0}
    if video_posts:
        vid_buckets = [('0-15s', 0, 15), ('16-30s', 16, 30), ('31-60s', 31, 60), ('61-120s', 61, 120), ('120s+', 121, 99999)]
        vid_data = {b[0]: {'count': 0, 'eng': 0, 'views': 0} for b in vid_buckets}
        for p in video_posts:
            vl = p['video_len']
            for name, lo, hi in vid_buckets:
                if lo <= vl <= hi:
                    vid_data[name]['count'] += 1
                    vid_data[name]['eng'] += p['slc']
                    vid_data[name]['views'] += p['views']
                    break

        D['video']['buckets'] = []
        for name, _, _ in vid_buckets:
            vd = vid_data[name]
            D['video']['buckets'].append({
                'name': name,
                'count': vd['count'],
                'avg_eng': round(vd['eng'] / vd['count'], 1) if vd['count'] else 0,
                'avg_views': round(vd['views'] / vd['count'], 1) if vd['count'] else 0,
            })
        D['video']['total'] = len(video_posts)
        D['video']['avg_len'] = round(sum(p['video_len'] for p in video_posts) / len(video_posts), 1)
        D['video']['total_views'] = sum(p['views'] for p in video_posts)

    # ── CONTEST ANALYSIS ──
    contest = [p for p in posts if p['is_contest']]
    non_contest = [p for p in posts if not p['is_contest']]
    D['contest'] = {
        'count': len(contest),
        'pct': round(len(contest) / n * 100, 1),
        'avg_eng': round(sum(p['slc'] for p in contest) / len(contest), 1) if contest else 0,
        'non_avg': round(sum(p['slc'] for p in non_contest) / len(non_contest), 1) if non_contest else 0,
    }

    # ── CLEANED STATS (without contests and top 10 posts) ──
    sorted_by_eng = sorted(posts, key=lambda x: -x['slc'])
    top10_ids = set(p['id'] for p in sorted_by_eng[:10])
    cleaned = [p for p in posts if not p['is_contest'] and p['id'] not in top10_ids]
    if cleaned:
        cleaned_avg = round(sum(p['slc'] for p in cleaned) / len(cleaned), 1)
        cleaned_total = sum(p['slc'] for p in cleaned)
    else:
        cleaned_avg = 0
        cleaned_total = 0
    D['cleaned'] = {
        'count': len(cleaned),
        'avg_eng': cleaned_avg,
        'total_eng': cleaned_total,
        'removed_contests': len(contest),
        'removed_top10': 10,
    }

    # ── ENGAGEMENT DISTRIBUTION ──
    eng_buckets = [('0', 0, 0), ('1-50', 1, 50), ('51-100', 51, 100), ('101-200', 101, 200), ('201-500', 201, 500), ('500+', 501, 999999)]
    D['eng_dist'] = []
    for name, lo, hi in eng_buckets:
        cnt = len([p for p in posts if lo <= p['slc'] <= hi])
        pct = round(cnt / n * 100, 1)
        D['eng_dist'].append({'bucket': name, 'count': cnt, 'pct': pct})

    # ── ENGAGEMENT CONCENTRATION ──
    sorted_posts = sorted(posts, key=lambda x: -x['slc'])
    top1_n = max(1, n // 100)
    top10_n = max(1, n // 10)
    top1_eng = sum(p['slc'] for p in sorted_posts[:top1_n])
    top10_eng = sum(p['slc'] for p in sorted_posts[:top10_n])
    D['concentration'] = {
        'top1_posts': top1_n,
        'top1_share': round(top1_eng / total_eng * 100, 1) if total_eng else 0,
        'top10_posts': top10_n,
        'top10_share': round(top10_eng / total_eng * 100, 1) if total_eng else 0,
        'rest_share': round((total_eng - top10_eng) / total_eng * 100, 1) if total_eng else 0,
    }

    # ── CONTENT THEMES (topic classification with engagement) ──
    topic_defs = {
        'Sports': ['sports','futbol','hokej','volejbol','basketbol','sacensīb','čempion','turnīr','spēl','komand','uzvara','medaļ','olimp','atlēt','trenin','stadion','spēlētāj','finā','pusfin','ceturtdaļ','līga','kauss'],
        'Kultūra': ['koncert','izstād','teātr','māksla','muzej','galerij','festiv','mūzik','dziesm','dzied','dej','kor','orķestr','mākslinieks','kultūr','filmu','kino','grāmat','bibliotēk','liter'],
        'Izglītība': ['skol','student','mācīb','izglītīb','universitet','augstskol','diplom','absolvents','pedagog','skolotāj','lekcij','stipendij','studij'],
        'Pasākumi': ['pasākum','svētk','svinēš','ielūdz','aicin','pieteik','reģistrēj','biļet','ieeja','programm','noris','notik','plkst','norises','apmeklē','piedāvā'],
        'Infrastruktūra': ['celtniecīb','remonts','iela','tilts','parks','laukums','ēka','projekts','būvniecīb','atjauno','labiekārto','infrastruktūr','satiksm','autostāvviet','veloceliņ'],
        'Daba/Vide': ['dab','jūr','pludmal','mežs','ezers','ziedi','stādī','apzaļumo','laiks','saule','sniegs','rudens','pavasari','vasara','ziem','vētr','dabas'],
        'Uzņēmējdarbība': ['uzņēm','biznes','investīcij','darba','vakance','attīstīb','ekonomik','tūrist','viesnīc','restorān','kafejnīc','tirdzniecīb','veikals'],
        'Sociālais': ['brīvprātīg','labdarīb','palīdzīb','atbalst','kopiena','iedzīvotāj','ģimene','bērn','jauniet','senior','pensionār','veselīb','medicīn'],
    }
    topic_stats = {}
    for topic, keywords in topic_defs.items():
        topic_posts = []
        for p in posts:
            txt = p['teksts'].lower()
            if any(kw in txt for kw in keywords):
                topic_posts.append(p)
        if topic_posts:
            avg_e = round(sum(pp['slc'] for pp in topic_posts) / len(topic_posts), 1)
            topic_stats[topic] = {
                'name': topic,
                'count': len(topic_posts),
                'pct': round(len(topic_posts) / n * 100, 1),
                'total_eng': sum(pp['slc'] for pp in topic_posts),
                'avg_eng': avg_e,
            }

    D['themes'] = sorted(topic_stats.values(), key=lambda x: -x['count'])

    # ── TOP BIGRAMS (most common 2-word pairs) ──
    stop_words = {'un','ir','kas','ar','par','no','uz','ka','lai','bet','ja','vai','pie','pa',
                  'šo','šī','tam','to','tā','tas','ko','kā','nav','arī','jau','vēl','tikai',
                  'var','būs','bija','gan','kur','jūs','mēs','viņi','savu','sev','tur','te',
                  'pēc','līdz','bez','caur','starp','priekš','dēļ','laikā','kopš',
                  'the','and','of','in','to','for','is','on','at','by','that','this','will',
                  'aicinām','vairāk','informācija','https','www','com','facebook',
                  'ventspils','ventspilī','ventspilnieku','pagalmu','katru'}
    bigram_counter = Counter()
    for p in posts:
        words = re.findall(r'[a-zA-ZāčēģīķļņšūžĀČĒĢĪĶĻŅŠŪŽ]{3,}', p['teksts'].lower())
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        for i in range(len(filtered) - 1):
            bg = filtered[i] + ' ' + filtered[i+1]
            bigram_counter[bg] += 1

    D['bigrams'] = [{'phrase': bg, 'count': c} for bg, c in bigram_counter.most_common(10)]

    # ── TOP POSTS (top 20, sortable by eng/likes/shares/comments) ──
    sorted_top = sorted(posts, key=lambda x: -x['slc'])
    D['top_posts'] = []
    for p in sorted_top[:20]:
        D['top_posts'].append({
            'type': p['type'],
            'likes': p['likes'],
            'shares': p['shares'],
            'comments': p['comments'],
            'engagement': p['slc'],
            'teksts': p['teksts'][:120],
            'date': p['date'],
            'url': p['fb_url'],
        })

    D['worst_posts'] = []
    for p in sorted_top[-5:]:
        D['worst_posts'].append({
            'type': p['type'],
            'engagement': p['slc'],
            'teksts': p['teksts'][:80],
            'date': p['date'],
            'url': p['fb_url'],
        })

    # ── TIME SLOTS ──
    slot_data = {'Rīts (6-12)': {'posts': 0, 'eng': 0}, 'Diena (12-17)': {'posts': 0, 'eng': 0},
                 'Vakars (17-22)': {'posts': 0, 'eng': 0}, 'Nakts (22-6)': {'posts': 0, 'eng': 0}}
    for p in posts:
        h = p['hour']
        if h is None:
            continue
        if 6 <= h < 12:
            slot_data['Rīts (6-12)']['posts'] += 1; slot_data['Rīts (6-12)']['eng'] += p['slc']
        elif 12 <= h < 17:
            slot_data['Diena (12-17)']['posts'] += 1; slot_data['Diena (12-17)']['eng'] += p['slc']
        elif 17 <= h < 22:
            slot_data['Vakars (17-22)']['posts'] += 1; slot_data['Vakars (17-22)']['eng'] += p['slc']
        else:
            slot_data['Nakts (22-6)']['posts'] += 1; slot_data['Nakts (22-6)']['eng'] += p['slc']

    D['time_slots'] = []
    for name in ['Rīts (6-12)', 'Diena (12-17)', 'Vakars (17-22)', 'Nakts (22-6)']:
        sd = slot_data[name]
        D['time_slots'].append({
            'name': name,
            'posts': sd['posts'],
            'avg_eng': round(sd['eng'] / sd['posts'], 1) if sd['posts'] else 0,
            'pct': round(sd['posts'] / n * 100, 1),
        })

    # Engagement breakdown
    D['engagement_breakdown'] = {
        'likes_pct': round(total_likes / total_eng * 100, 1) if total_eng else 0,
        'shares_pct': round(total_shares / total_eng * 100, 1) if total_eng else 0,
        'comments_pct': round(total_comments / total_eng * 100, 1) if total_eng else 0,
    }

    return D


def slug(name):
    s = name.lower().replace('ā','a').replace('č','c').replace('ē','e').replace('ģ','g')
    s = s.replace('ī','i').replace('ķ','k').replace('ļ','l').replace('ņ','n')
    s = s.replace('š','s').replace('ū','u').replace('ž','z').replace('"','').replace('"','')
    s = re.sub(r'[^a-z0-9]+', '_', s).strip('_')
    return s


def generate_html(D, page_name, all_pages):
    safe_name = page_name.replace("'", "\\'").replace('"', '&quot;')
    data_json = json.dumps(D, ensure_ascii=False)

    # Build nav links for all pages
    nav_items = []
    for pg in all_pages:
        pg_slug = slug(pg)
        fn = f"Facebook_{pg_slug}_2025.html"
        is_active = pg == page_name
        nav_items.append((pg, fn, is_active))

    nav_html = ''
    for pg, fn, is_active in nav_items:
        short = pg[:18] + '…' if len(pg) > 18 else pg
        initials = ''.join(w[0].upper() for w in pg.split()[:2])
        if is_active:
            nav_html += f'<span class="uf-link active"><span class="uf-dot">{initials}</span>{short}</span>'
        else:
            nav_html += f'<a class="uf-link" href="{fn}"><span class="uf-dot">{initials}</span>{short}</a>'

    # Previous / Next navigation
    idx = [p for p, _, _ in nav_items].index(page_name) if page_name in [p for p, _, _ in nav_items] else 0
    prev_pg = nav_items[idx - 1] if idx > 0 else None
    next_pg = nav_items[idx + 1] if idx < len(nav_items) - 1 else None

    top_nav = f'<div class="nav">'
    top_nav += f'<a href="Facebook_apakšsvītra_visas_2025.html">← Kopējais</a>'
    if prev_pg:
        top_nav += f' <a href="{prev_pg[1]}">← {prev_pg[0][:20]}</a>'
    top_nav += f' <span class="cn">{safe_name}</span>'
    if next_pg:
        top_nav += f' <a href="{next_pg[1]}">{next_pg[0][:20]} →</a>'
    top_nav += '</div>'

    # Count sections and build
    section_num = [0]
    def sn():
        section_num[0] += 1
        return f'{section_num[0]:02d}'

    # ── VIDEO section HTML ──
    video_section = ''
    if D.get('video', {}).get('has_data'):
        video_section = f'''
<div class="section"><h2 class="stitle"><span class="num">{sn()}</span>Video garuma analīze</h2>
<p class="sdesc">Kā video garums ietekmē iesaisti un skatījumus. Kopā {D['video']['total']} video, vid. garums {D['video']['avg_len']}s.</p>
<div class="cs"><div class="cw"><canvas id="vidLenC"></canvas></div></div></div>'''

    # Section numbers for all sections
    s = {}
    s['monthly_combo'] = sn()
    s['format'] = sn()
    s['format_eff'] = sn()
    s['orientation'] = sn()
    s['ori_eff'] = sn()
    s['txt_img'] = sn()
    s['caption'] = sn()
    s['weekday'] = sn()
    s['hourly'] = sn()
    s['work_wknd'] = sn()
    s['time_slot'] = sn()
    s['heatmap'] = sn()
    s['eng_break'] = sn()
    s['eng_conc'] = sn()
    s['h1h2'] = sn()
    s['contest'] = sn()
    s['eng_dist'] = sn()
    s['colors'] = sn()

    # Video section number
    if D.get('video', {}).get('has_data'):
        s['video'] = sn()
        video_section = f'''
<div class="section"><h2 class="stitle"><span class="num">{s['video']}</span>Video garuma analīze</h2>
<p class="sdesc">Kā video garums ietekmē iesaisti un skatījumus. Kopā {D['video']['total']} video, vid. garums {D['video']['avg_len']}s.</p>
<div class="cs"><div class="cw"><canvas id="vidLenC"></canvas></div></div></div>'''

    s['themes'] = sn()
    s['top_posts'] = sn()
    s['worst_posts'] = sn()

    total_sections = section_num[0]

    html = f'''<!DOCTYPE html>
<html lang="lv"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_name} — Facebook 2025</title>
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
.nav{{position:sticky;top:0;z-index:100;background:rgba(6,9,17,0.85);backdrop-filter:blur(16px);padding:14px 48px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);font-size:0.82em}}
.nav a{{color:var(--accent);text-decoration:none;transition:color .2s}}.nav a:hover{{color:var(--accent-hover)}}
.nav .cn{{color:var(--text-1);font-weight:700;font-size:1.05em}}
.container{{max-width:1280px;margin:0 auto;padding:0 48px 120px}}
.hero{{padding:80px 48px 60px;text-align:center;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:900px;height:600px;background:radial-gradient(ellipse,rgba(24,119,242,0.12) 0%,rgba(167,139,250,0.06) 40%,transparent 70%);animation:heroGlow 8s ease-in-out infinite alternate;pointer-events:none}}
@keyframes heroGlow{{0%{{opacity:0.8;transform:translateX(-50%) scale(1)}}100%{{opacity:1;transform:translateX(-50%) scale(1.15)}}}}
.hero h1{{font-family:'Space Grotesk',sans-serif;font-size:2.8em;font-weight:700;letter-spacing:-0.04em;line-height:1.1;margin-bottom:12px}}
.hero h1 span{{background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.subtitle{{color:var(--text-2b);font-size:1.05em;opacity:0.7}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:18px;margin-bottom:80px}}
.kpi{{background:rgba(19,24,32,0.6);backdrop-filter:blur(16px);border-radius:20px;padding:22px 18px;border:1px solid rgba(255,255,255,0.05);box-shadow:0 4px 24px rgba(0,0,0,0.2),inset 0 1px 0 rgba(255,255,255,0.03);text-align:center;transition:all .3s ease;animation:fadeInUp 0.6s ease-out both}}
.kpi::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(24,119,242,0.2),transparent)}}
.kpi:hover{{border-color:rgba(24,119,242,0.15);transform:translateY(-4px)}}
.kpi .label{{font-size:0.72em;letter-spacing:2px;color:var(--text-3);text-transform:uppercase;font-weight:600}}
.kpi .value{{font-size:1.65em;font-weight:800;margin:8px 0;background:linear-gradient(135deg,var(--text-1),var(--text-2b));-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-variant-numeric:tabular-nums;white-space:nowrap}}
.kpi .sub{{font-size:0.7em;color:var(--text-2)}}
.badge{{display:inline-block;padding:3px 10px;border-radius:10px;font-size:0.7em;font-weight:600;margin-top:6px}}
.badge.up{{background:var(--green-dim);color:var(--green)}}.badge.down{{background:var(--red-dim);color:var(--red)}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
.kpi:nth-child(1){{animation-delay:.05s}}.kpi:nth-child(2){{animation-delay:.1s}}.kpi:nth-child(3){{animation-delay:.15s}}.kpi:nth-child(4){{animation-delay:.2s}}.kpi:nth-child(5){{animation-delay:.25s}}.kpi:nth-child(6){{animation-delay:.3s}}.kpi:nth-child(7){{animation-delay:.35s}}.kpi:nth-child(8){{animation-delay:.4s}}
.stitle{{font-family:'Space Grotesk',sans-serif;font-size:1.7em;font-weight:700;color:var(--text-1);letter-spacing:-0.02em;margin-bottom:16px;padding-left:4px}}
.stitle .num{{font-size:0.6em;color:rgba(24,119,242,0.4);margin-right:10px;font-weight:700}}
.sdesc{{color:var(--text-2b);font-size:0.9em;line-height:1.65;max-width:600px;margin-bottom:16px;padding-left:4px}}
.section{{opacity:0;transform:translateY(40px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1);margin-bottom:80px}}
.section.visible{{opacity:1;transform:translateY(0)}}
.cs{{background:rgba(19,24,32,0.5);backdrop-filter:blur(12px);border-radius:20px;padding:28px;border:1px solid rgba(255,255,255,0.04);box-shadow:0 2px 16px rgba(0,0,0,0.15),inset 0 1px 0 rgba(255,255,255,0.02);transition:all .3s ease}}
.cs:hover{{border-color:rgba(255,255,255,0.08)}}
.ch{{display:flex;justify-content:flex-end;align-items:center;gap:8px;margin-bottom:12px}}
.cc button{{padding:5px 14px;border-radius:12px;cursor:pointer;font-size:0.74em;font-weight:500;font-family:'Inter',sans-serif;transition:all .2s;border:1px solid var(--border);background:var(--surface-2);color:var(--text-2)}}
.cc button.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.cc button:hover:not(.active){{border-color:var(--border-hover);color:var(--text-1)}}
.cw{{position:relative;height:380px}}.cw.tall{{height:520px}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}
table{{width:100%;border-collapse:collapse;font-size:0.82em;margin-top:8px}}
th,td{{padding:12px 14px;text-align:left;border-bottom:1px solid var(--border)}}
th{{color:var(--text-3);font-weight:600;font-size:0.72em;text-transform:uppercase;letter-spacing:1px;border-bottom:2px solid rgba(24,119,242,0.1)}}
td{{font-variant-numeric:tabular-nums;color:var(--text-2b)}}
tr:hover td{{background:rgba(24,119,242,0.03)}}
a{{color:var(--accent);text-decoration:none}}a:hover{{color:var(--accent-hover)}}
.b{{display:inline-block;padding:3px 12px;border-radius:12px;font-size:0.74em;font-weight:600}}
.bg{{background:var(--green-dim);color:var(--green)}}.br{{background:var(--red-dim);color:var(--red)}}.bb{{background:var(--accent-dim);color:var(--accent)}}.bo{{background:var(--orange-dim);color:var(--orange)}}
.sd2{{font-family:'Space Grotesk',sans-serif;text-align:center;font-size:1.4em;font-weight:700;color:var(--text-2);letter-spacing:-0.01em;margin:80px 0 50px;padding:20px 0;position:relative}}
.sd2::after{{content:'';position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:80px;height:3px;border-radius:2px;background:linear-gradient(90deg,var(--accent),var(--purple))}}
.con-grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:1400px;margin:0 auto}}
.con{{background:rgba(19,24,32,0.5);backdrop-filter:blur(12px);border-radius:20px;padding:28px;border:1px solid rgba(255,255,255,0.04);border-left:4px solid var(--accent);box-shadow:0 2px 16px rgba(0,0,0,0.15);transition:all .5s cubic-bezier(.16,1,.3,1);opacity:0;transform:translateY(30px)}}
.con.visible{{opacity:1;transform:translateY(0)}}
.con:hover{{transform:translateY(-3px)}}
.con h3{{margin-bottom:12px;color:var(--accent);font-size:1.1em;font-weight:700}}
.con p{{color:var(--text-2b);font-size:0.88em;margin-bottom:8px;line-height:1.7}}
.hl{{color:var(--text-1);font-weight:600}}.st{{color:var(--orange);font-weight:700}}
.good{{border-left-color:var(--green)}}.good h3{{color:var(--green)}}
.bad{{border-left-color:var(--red)}}.bad h3{{color:var(--red)}}
.tip{{border-left-color:var(--orange)}}.tip h3{{color:var(--orange)}}
.hm-grid{{display:grid;grid-template-columns:40px repeat(24,1fr);gap:2px;font-size:0.65em}}
.hm-cell{{border-radius:4px;text-align:center;padding:4px 2px;font-weight:500;min-height:28px;display:flex;align-items:center;justify-content:center}}
.hm-label{{color:var(--text-3);font-weight:600;display:flex;align-items:center;justify-content:center;font-size:0.9em}}
.themes-grid{{display:flex;flex-wrap:wrap;gap:10px;padding:16px 0}}
.theme-tag{{background:var(--accent-dim);color:var(--accent);padding:6px 16px;border-radius:14px;font-size:0.82em;font-weight:600;transition:all .2s}}
.theme-tag:hover{{background:rgba(24,119,242,0.2)}}
.theme-count{{color:var(--text-3);font-size:0.8em;margin-left:4px}}

/* Unified Footer */
.unified-footer{{background:rgba(19,24,32,0.4);backdrop-filter:blur(16px);border-top:1px solid rgba(255,255,255,0.04);padding:48px 48px 32px;margin-top:80px}}
.uf-title{{font-family:'Space Grotesk',sans-serif;font-size:1.1em;font-weight:600;color:var(--text-2);text-align:center;margin-bottom:24px}}
.uf-grid{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;max-width:1200px;margin:0 auto}}
.uf-link{{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:10px;font-size:0.72em;font-weight:500;color:var(--text-2b);text-decoration:none;border:1px solid var(--border);transition:all .2s;background:rgba(255,255,255,0.02)}}
.uf-link:hover{{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}}
.uf-link.active{{background:linear-gradient(135deg,var(--accent),var(--purple));color:#fff;border-color:transparent;pointer-events:none}}
.uf-link.summary-link{{background:linear-gradient(135deg,rgba(24,119,242,0.15),rgba(167,139,250,0.15));border-color:rgba(24,119,242,0.2);color:var(--accent);font-weight:600}}
.uf-link.summary-link:hover{{background:linear-gradient(135deg,rgba(24,119,242,0.25),rgba(167,139,250,0.25))}}
.uf-dot{{width:18px;height:18px;border-radius:50%;background:rgba(24,119,242,0.15);display:flex;align-items:center;justify-content:center;font-size:0.7em;font-weight:700;color:var(--accent)}}
.uf-copy{{text-align:center;margin-top:24px;color:var(--text-3);font-size:0.7em}}
.footer{{text-align:center;padding:40px 0 30px;color:var(--text-3);font-size:0.78em}}
::-webkit-scrollbar{{width:8px}}::-webkit-scrollbar-thumb{{background:rgba(24,119,242,0.15);border-radius:4px}}
::selection{{background:rgba(24,119,242,0.25);color:var(--text-1)}}
@media(max-width:900px){{.two-col,.con-grid{{grid-template-columns:1fr}}.container{{padding:0 20px 80px}}.hero{{padding:60px 20px 40px}}.hero h1{{font-size:2em}}.nav{{padding:10px 16px;font-size:0.75em}}}}
</style>
</head><body>

{top_nav}

<div class="hero">
<h1><span>{safe_name}</span></h1>
<p class="subtitle">Facebook 2025 · {D['kpi']['total_posts']} publikācijas · Janvāris — Decembris</p>
</div>

<div class="container">
<div class="kpi-grid" id="kpiG"></div>

<div class="section"><h2 class="stitle"><span class="num">{s['monthly_combo']}</span>Mēneša pārskats</h2>
<p class="sdesc">Kopējā iesaiste, publikāciju skaits un vidējā iesaiste pa mēnešiem.</p>
<div class="cs"><div class="cw" style="height:420px"><canvas id="mComboC"></canvas></div></div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">{s['format']}</span>Satura formāts</h2>
<p class="sdesc">Publikāciju sadalījums pa formātiem.</p>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sw('fmtC','doughnut',this)">Doughnut</button><button onclick="sw('fmtC','bar',this)">Bar</button></div></div><div class="cw"><canvas id="fmtCC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">{s['format_eff']}</span>Formāta efektivitāte</h2>
<p class="sdesc">Vidējā iesaiste pēc satura formāta.</p>
<div class="cs"><div class="cw"><canvas id="fmtAvgC"></canvas></div></div></div>
</div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">{s['orientation']}</span>Bilžu orientācija</h2>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sw('oriC','doughnut',this)">Doughnut</button><button onclick="sw('oriC','bar',this)">Bar</button></div></div><div class="cw"><canvas id="oriCC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">{s['ori_eff']}</span>Orientācijas efektivitāte</h2>
<div class="cs"><div class="cw"><canvas id="oriAvgC"></canvas></div></div></div>
</div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">{s['txt_img']}</span>Teksts uz bildes</h2>
<p class="sdesc">Kā teksta daudzums uz bildes ietekmē iesaisti.</p>
<div class="cs"><div class="cw"><canvas id="txtImgC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">{s['caption']}</span>Pavadošā teksta garums</h2>
<p class="sdesc">Kā teksta garums (zīmju skaits) ietekmē iesaisti.</p>
<div class="cs"><div class="cw"><canvas id="capLenC"></canvas></div></div></div>
</div></div>

<div class="section"><h2 class="stitle"><span class="num">{s['weekday']}</span>Publicēšanas dienas</h2>
<p class="sdesc">Iesaiste pēc nedēļas dienām.</p>
<div class="cs"><div class="cw"><canvas id="wdayC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">{s['hourly']}</span>Publicēšanas laiks (stundas)</h2>
<p class="sdesc">Vidējā iesaiste un publikāciju skaits pa stundām.</p>
<div class="cs"><div class="cw tall"><canvas id="hourC"></canvas></div></div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">{s['work_wknd']}</span>Darba dienas vs Brīvdienas</h2>
<div class="cs"><div class="cw"><canvas id="wwC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">{s['time_slot']}</span>Laika sloti</h2>
<div class="cs"><div class="cw"><canvas id="slotC"></canvas></div></div></div>
</div></div>

<div class="section"><h2 class="stitle"><span class="num">{s['heatmap']}</span>Publicēšanas karstuma karte</h2>
<p class="sdesc">Diena × Stunda matrica. Tumšāks = augstāka vid. iesaiste.</p>
<div class="cs"><div class="hm-grid" id="heatmapG"></div></div></div>

<div class="sd2">Papildu Analīze</div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">{s['eng_break']}</span>Iesaistes sadalījums</h2>
<div class="cs"><div class="cw"><canvas id="engBrkC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">{s['eng_conc']}</span>Iesaistes koncentrācija</h2>
<div class="cs"><div class="cw"><canvas id="concC"></canvas></div></div></div>
</div></div>

<div class="section"><div class="two-col">
<div><h2 class="stitle"><span class="num">{s['h1h2']}</span>H1 vs H2</h2>
<p class="sdesc">Pirmā vs otrā pusgada salīdzinājums.</p>
<div class="cs"><div class="cw"><canvas id="halfC"></canvas></div></div></div>
<div><h2 class="stitle"><span class="num">{s['contest']}</span>Konkursi vs Parastie</h2>
<div class="cs"><div class="cw"><canvas id="contestC"></canvas></div></div></div>
</div></div>

<div class="section"><h2 class="stitle"><span class="num">{s['eng_dist']}</span>Cik ierakstu katrā iesaistes grupā</h2>
<p class="sdesc">Katrs stabiņš parāda, cik publikācijām iesaiste (likes+shares+comments) iekrita konkrētajā diapazonā. Piemēram, "51-100" nozīmē ierakstus ar kopējo iesaisti no 51 līdz 100. Jo vairāk ierakstu augstākos diapazenos, jo labāk konta saturs strādā.</p>
<div class="cs"><div class="cw"><canvas id="engDistC"></canvas></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">{s['colors']}</span>Bilžu krāsas</h2>
<p class="sdesc">Dominējošās krāsas vizuālajos materiālos.</p>
<div class="cs"><div class="cw"><canvas id="colorC"></canvas></div></div></div>

{video_section}

<div class="section"><h2 class="stitle"><span class="num">{s['themes']}</span>Satura tēmas un to efektivitāte</h2>
<p class="sdesc">Galvenās tēmas pēc satura analīzes — skaits un vidējā iesaiste.</p>
<div class="cs"><div class="cw" style="height:380px"><canvas id="themesC"></canvas></div></div></div>

<div class="section"><h2 class="stitle">Biežākie vārdu pāri saturā</h2>
<p class="sdesc">Top 10 biežāk kopā lietotie 2 vārdu pāri — atklāj reālās satura tēmas un kontekstu.</p>
<div class="cs"><div id="bigramsG" style="padding:16px 0"></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">{s['top_posts']}</span>Top 20 publikācijas</h2>
<div class="cs"><div class="ch"><div class="cc"><button class="active" onclick="sortTop('engagement',this)">Iesaiste</button><button onclick="sortTop('likes',this)">Likes</button><button onclick="sortTop('shares',this)">Shares</button><button onclick="sortTop('comments',this)">Comments</button></div></div><div style="overflow-x:auto"><table id="topT"></table></div></div></div>

<div class="section"><h2 class="stitle"><span class="num">{s['worst_posts']}</span>Zemākā iesaiste</h2>
<div class="cs"><div style="overflow-x:auto"><table id="worstT"></table></div></div></div>

<div class="sd2">Secinājumi un Ieteikumi</div>
<div class="con-grid" id="conG"></div>

</div>

<div class="unified-footer">
<div class="uf-title">Visu Ventspils Facebook lapu pārskati</div>
<div class="uf-grid">
<a class="uf-link summary-link" href="Facebook_apakšsvītra_visas_2025.html"><span class="uf-dot">Σ</span>Kopējais pārskats</a>
{nav_html}
</div>
<div class="uf-copy">Ventspils Facebook 2025 · Individuālais pārskats</div>
</div>

<script>
const D={data_json};

function nf(n){{return n.toString()}}

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

var CL=['#1877F2','#34D399','#FBBF24','#F87171','#A78BFA','#06b6d4','#ec4899','#f97316','#84cc16','#6366f1'];
var CH={{}};var CT={{}};
function sw(id,tp,btn){{CT[id]=tp;btn.parentElement.querySelectorAll('button').forEach(function(b){{b.classList.remove('active')}});btn.classList.add('active');rc(id)}}
function rc(id){{if(CH[id])CH[id].destroy();var c=CFG[id](CT[id]||'bar');CH[id]=new Chart(document.getElementById(c.cid),c.cfg)}}
function scOpts(){{return{{grid:{{color:'rgba(255,255,255,0.04)'}},ticks:{{color:'#8B95A5',font:{{size:11}}}}}}}}

var CFG={{}};

// Monthly combo chart (engagement bars + posts line, avg in labels)
CFG.mCombo=function(){{var m=D.monthly;return{{cid:'mComboC',cfg:{{type:'bar',data:{{labels:m.map(function(x){{return [x.name,'vid. '+x.avg_eng]}}),datasets:[{{label:'Kopējā iesaiste',data:m.map(function(x){{return x.engagement}}),backgroundColor:'rgba(24,119,242,0.4)',borderColor:'#1877F2',borderWidth:2,yAxisID:'y',order:2}},{{label:'Publikācijas',data:m.map(function(x){{return x.posts}}),type:'line',borderColor:'#A78BFA',backgroundColor:'transparent',borderWidth:3,borderDash:[6,3],pointRadius:4,pointBackgroundColor:'#A78BFA',tension:.4,yAxisID:'y1',order:1}}]}},options:{{responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},scales:{{x:scOpts(),y:Object.assign(scOpts(),{{position:'left',title:{{display:true,text:'Iesaiste',color:'#8B95A5',font:{{size:11}}}}}}),y1:{{position:'right',grid:{{display:false}},ticks:{{color:'#A78BFA',font:{{size:11}}}},title:{{display:true,text:'Publikācijas',color:'#A78BFA',font:{{size:11}}}}}}}}}}}}}}}};

// Format
CFG.fmtC=function(t){{var f=D.formats;return{{cid:'fmtCC',cfg:{{type:t,data:{{labels:f.map(function(x){{return x.type+' ('+x.pct+'%)'}}),datasets:[{{data:f.map(function(x){{return x.count}}),backgroundColor:CL.slice(0,f.length),borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:t==='doughnut'?{{}}:{{x:scOpts(),y:scOpts()}}}}}}}}}};CT.fmtC='doughnut';

CFG.fmtAvgC=function(){{var f=D.formats;return{{cid:'fmtAvgC',cfg:{{type:'bar',data:{{labels:f.map(function(x){{return x.type}}),datasets:[{{label:'Vid. iesaiste',data:f.map(function(x){{return x.avg_eng}}),backgroundColor:CL.slice(0,f.length)}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Orientation
CFG.oriC=function(t){{var o=D.orientation;return{{cid:'oriCC',cfg:{{type:t,data:{{labels:o.map(function(x){{return x.name+' ('+x.pct+'%)'}}),datasets:[{{data:o.map(function(x){{return x.count}}),backgroundColor:['#34D399','#F87171','#FBBF24'],borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:t==='doughnut'?{{}}:{{x:scOpts(),y:scOpts()}}}}}}}}}};CT.oriC='doughnut';

CFG.oriAvgC=function(){{var o=D.orientation;return{{cid:'oriAvgC',cfg:{{type:'bar',data:{{labels:o.map(function(x){{return x.name}}),datasets:[{{label:'Vid. iesaiste',data:o.map(function(x){{return x.avg_eng}}),backgroundColor:['#34D399','#F87171','#FBBF24']}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Text on image
CFG.txtImgC=function(){{var t=D.text_on_image;return{{cid:'txtImgC',cfg:{{type:'bar',data:{{labels:t.map(function(x){{return x.name+' ('+x.count+')'}}),datasets:[{{label:'Vid. iesaiste',data:t.map(function(x){{return x.avg_eng}}),backgroundColor:CL.slice(0,3)}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Caption length
CFG.capLenC=function(){{var c=D.caption_length;return{{cid:'capLenC',cfg:{{type:'bar',data:{{labels:c.map(function(x){{return x.name+' ('+x.pct+'%)'}}),datasets:[{{label:'Vid. iesaiste',data:c.map(function(x){{return x.avg_eng}}),backgroundColor:CL.slice(0,c.length),yAxisID:'y'}},{{label:'Skaits',data:c.map(function(x){{return x.count}}),type:'line',borderColor:'#A78BFA',backgroundColor:'transparent',tension:.4,yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts(),y1:{{position:'right',grid:{{display:false}},ticks:{{color:'#A78BFA',font:{{size:11}}}}}}}}}}}}}}}};

// Weekday
CFG.wdayC=function(){{var w=D.weekday;return{{cid:'wdayC',cfg:{{type:'line',data:{{labels:w.map(function(x){{return x.name}}),datasets:[{{label:'Vid. iesaiste',data:w.map(function(x){{return x.avg_eng}}),borderColor:'#1877F2',backgroundColor:'rgba(24,119,242,0.1)',fill:true,borderWidth:3,pointRadius:6,pointBackgroundColor:w.map(function(x){{return x.day>=6?'#34D399':'#1877F2'}}),pointBorderColor:w.map(function(x){{return x.day>=6?'#34D399':'#1877F2'}}),pointBorderWidth:2,tension:.4,yAxisID:'y'}},{{label:'Posti',data:w.map(function(x){{return x.posts}}),borderColor:'#A78BFA',backgroundColor:'transparent',borderWidth:2,borderDash:[6,3],pointRadius:4,pointBackgroundColor:'#A78BFA',tension:.4,yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},scales:{{x:scOpts(),y:scOpts(),y1:{{position:'right',grid:{{display:false}},ticks:{{color:'#A78BFA',font:{{size:11}}}}}}}}}}}}}}}};

// Hourly
CFG.hourC=function(){{var h=D.hourly;return{{cid:'hourC',cfg:{{type:'line',data:{{labels:h.map(function(x){{return x.hour+'h'}}),datasets:[{{label:'Vid. iesaiste',data:h.map(function(x){{return x.avg_eng}}),borderColor:'#1877F2',backgroundColor:'rgba(24,119,242,0.08)',fill:true,borderWidth:3,pointRadius:4,pointBackgroundColor:'#1877F2',tension:.4,yAxisID:'y'}},{{label:'Posti',data:h.map(function(x){{return x.posts}}),borderColor:'#FBBF24',backgroundColor:'transparent',borderWidth:2,borderDash:[6,3],pointRadius:3,pointBackgroundColor:'#FBBF24',tension:.4,yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},scales:{{x:scOpts(),y:scOpts(),y1:{{position:'right',grid:{{display:false}},ticks:{{color:'#FBBF24',font:{{size:11}}}}}}}}}}}}}}}};

// Work vs Weekend
CFG.wwC=function(){{var w=D.work_weekend;return{{cid:'wwC',cfg:{{type:'bar',data:{{labels:['Darba dienas ('+w.work_pct+'%)','Brīvdienas ('+w.weekend_pct+'%)'],datasets:[{{label:'Vid. iesaiste',data:[w.work_avg,w.weekend_avg],backgroundColor:['rgba(24,119,242,0.5)','rgba(52,211,153,0.5)'],borderColor:['#1877F2','#34D399'],borderWidth:2}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};


// Time slots
CFG.slotC=function(){{var s=D.time_slots;return{{cid:'slotC',cfg:{{type:'bar',data:{{labels:s.map(function(x){{return x.name}}),datasets:[{{label:'Vid. iesaiste',data:s.map(function(x){{return x.avg_eng}}),backgroundColor:CL.slice(0,4)}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Engagement breakdown
CFG.engBrkC=function(){{var e=D.engagement_breakdown;return{{cid:'engBrkC',cfg:{{type:'doughnut',data:{{labels:['Likes ('+e.likes_pct+'%)','Shares ('+e.shares_pct+'%)','Comments ('+e.comments_pct+'%)'],datasets:[{{data:[D.kpi.total_likes,D.kpi.total_shares,D.kpi.total_comments],backgroundColor:['#1877F2','#34D399','#FBBF24'],borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false}}}}}}}};

// Concentration
CFG.concC=function(){{var c=D.concentration;return{{cid:'concC',cfg:{{type:'doughnut',data:{{labels:['Top 1% ('+c.top1_share+'%)','Top 2-10% ('+(c.top10_share-c.top1_share).toFixed(1)+'%)','Pārējie ('+c.rest_share+'%)'],datasets:[{{data:[c.top1_share,c.top10_share-c.top1_share,c.rest_share],backgroundColor:['#F87171','#FBBF24','#1877F2'],borderWidth:0}}]}},options:{{responsive:true,maintainAspectRatio:false}}}}}}}};

// H1 vs H2
CFG.halfC=function(){{var h=D.half_year;return{{cid:'halfC',cfg:{{type:'bar',data:{{labels:h.map(function(x){{return x.name}}),datasets:[{{label:'Posti',data:h.map(function(x){{return x.posts}}),backgroundColor:['rgba(24,119,242,0.5)','rgba(52,211,153,0.5)']}},{{label:'Vid. iesaiste',data:h.map(function(x){{return x.avg_eng}}),type:'line',borderColor:'#FBBF24',backgroundColor:'transparent',yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts(),y1:{{position:'right',grid:{{display:false}},ticks:{{color:'#FBBF24',font:{{size:11}}}}}}}}}}}}}}}};

// Contest
CFG.contestC=function(){{var c=D.contest;return{{cid:'contestC',cfg:{{type:'bar',data:{{labels:['Konkursi ('+c.count+')','Parastie ('+(D.kpi.total_posts-c.count)+')'],datasets:[{{label:'Vid. iesaiste',data:[c.avg_eng,c.non_avg],backgroundColor:['rgba(248,113,113,0.5)','rgba(24,119,242,0.5)'],borderColor:['#F87171','#1877F2'],borderWidth:2}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Engagement distribution
CFG.engDistC=function(){{var e=D.eng_dist;return{{cid:'engDistC',cfg:{{type:'bar',data:{{labels:e.map(function(x){{return x.bucket+' ('+x.pct+'%)'}}),datasets:[{{label:'Publikācijas',data:e.map(function(x){{return x.count}}),backgroundColor:'rgba(24,119,242,0.5)',borderColor:'#1877F2',borderWidth:1}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Colors
CFG.colorC=function(){{var c=D.colors;return{{cid:'colorC',cfg:{{type:'bar',data:{{labels:c.map(function(x){{return x.hex+' ('+x.pct+'%)'}}),datasets:[{{label:'Skaits',data:c.map(function(x){{return x.count}}),backgroundColor:c.map(function(x){{var h=x.hex.toLowerCase();return h==='#ffffff'?'rgba(255,255,255,0.7)':h}}),borderColor:c.map(function(x){{var h=x.hex.toLowerCase();return h==='#ffffff'?'rgba(255,255,255,1)':h}}),borderWidth:2}}]}},options:{{responsive:true,maintainAspectRatio:false,scales:{{x:scOpts(),y:scOpts()}}}}}}}}}};

// Video length (if exists)
{'CFG.vidLenC=function(){var v=D.video.buckets;return{cid:"vidLenC",cfg:{type:"bar",data:{labels:v.map(function(x){return x.name}),datasets:[{label:"Skaits",data:v.map(function(x){return x.count}),backgroundColor:"rgba(24,119,242,0.5)",borderColor:"#1877F2",borderWidth:2,yAxisID:"y"},{label:"Vid. iesaiste",data:v.map(function(x){return x.avg_eng}),type:"line",borderColor:"#34D399",backgroundColor:"transparent",borderWidth:3,pointRadius:5,pointBackgroundColor:"#34D399",tension:.4,yAxisID:"y1"}]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:"index",intersect:false},scales:{x:scOpts(),y:Object.assign(scOpts(),{title:{display:true,text:"Skaits",color:"#8B95A5",font:{size:11}}}),y1:{position:"right",grid:{display:false},ticks:{color:"#34D399",font:{size:11}},title:{display:true,text:"Vid. iesaiste",color:"#34D399",font:{size:11}}}}}}}}};' if D.get('video', {}).get('has_data') else ''}

// Build KPI
function buildKPI(){{
  var k=D.kpi;
  var items=[
    ['Publikācijas',k.total_posts,'Janvāris — Decembris 2025'],
    ['Kopējā iesaiste',nf(k.total_engagement),'L:'+nf(k.total_likes)+' S:'+nf(k.total_shares)+' C:'+nf(k.total_comments)],
    ['Vid. iesaiste',k.avg_eng,'Mediāna: '+k.median_eng],
    ['Konsistence','CV '+k.cv,k.cv<0.5?'Ļoti stabils':k.cv<1?'Stabils':'Mainīgs'],
    ['Kom./Likes',k.cl_ratio+'%','Komentāru proporcija'],
    ['H1→H2',D.half_year[1].avg_eng,'H1: '+D.half_year[0].avg_eng+(D.half_year_growth>0?' ↑':' ↓')],
    ['Virālie posti',k.viral_count,k.viral_pct+'% no visiem'],
    ['Labākais mēn.',k.best_month,'Zemākais: '+k.worst_month],
  ];
  document.getElementById('kpiG').innerHTML=items.map(function(it){{
    return '<div class="kpi"><div class="label">'+it[0]+'</div><div class="value">'+it[1]+'</div><div class="sub">'+it[2]+'</div></div>';
  }}).join('');
}}

// Build heatmap (green=top5, red=worst5, yellow=middle)
function buildHeatmap(){{
  var hm=D.heatmap;
  var days=['','P','O','T','C','Pk','S','Sv'];
  // Collect all non-zero values and rank them
  var vals=hm.filter(function(x){{return x.avg_eng>0}}).map(function(x){{return x.avg_eng}});
  vals.sort(function(a,b){{return b-a}});
  var top5=vals.length>=5?vals[4]:vals[vals.length-1]||0;
  var bot5vals=vals.slice().sort(function(a,b){{return a-b}});
  var bot5=bot5vals.length>=5?bot5vals[4]:bot5vals[bot5vals.length-1]||0;
  var html='<div class="hm-label"></div>';
  for(var h=0;h<24;h++) html+='<div class="hm-label">'+h+'</div>';
  for(var d=1;d<=7;d++){{
    html+='<div class="hm-label">'+days[d]+'</div>';
    for(var h=0;h<24;h++){{
      var cell=hm.find(function(x){{return x.day===d&&x.hour===h}});
      var val=cell?cell.avg_eng:0;
      var bg;
      if(val<=0){{bg='rgba(255,255,255,0.02)'}}
      else if(val>=top5){{bg='rgba(52,211,153,0.75)'}}
      else if(val<=bot5){{bg='rgba(239,68,68,0.65)'}}
      else{{var mid=(val-bot5)/(top5-bot5);bg='rgba(251,191,36,'+(0.2+mid*0.5)+')'}}
      html+='<div class="hm-cell" style="background:'+bg+'" title="'+days[d]+' '+h+':00 — vid. '+val+'">'+(val>0?Math.round(val):'')+'</div>';
    }}
  }}
  document.getElementById('heatmapG').innerHTML=html;
}}

// Build bigrams
function buildBigrams(){{
  var bg=D.bigrams;
  if(!bg||!bg.length)return;
  var maxC=bg[0].count;
  var html='<table style="width:100%"><tr><th style="text-align:left">#</th><th style="text-align:left">Vārdu pāris</th><th style="text-align:right">Reizes</th><th style="width:50%"></th></tr>';
  bg.forEach(function(b,i){{
    var pct=Math.round(b.count/maxC*100);
    html+='<tr><td>'+(i+1)+'</td><td style="font-weight:600;color:var(--text-1)">'+b.phrase+'</td><td style="text-align:right;color:var(--accent)">'+b.count+'</td><td><div style="background:rgba(24,119,242,0.3);height:20px;border-radius:4px;width:'+pct+'%"></div></td></tr>';
  }});
  html+='</table>';
  document.getElementById('bigramsG').innerHTML=html;
}}

// Themes chart (CFG-based)
CFG.themesC=function(){{var t=D.themes;return{{cid:'themesC',cfg:{{type:'bar',data:{{labels:t.map(function(x){{return x.name+' ('+x.count+')'}}),datasets:[{{label:'Vid. iesaiste',data:t.map(function(x){{return x.avg_eng}}),backgroundColor:'rgba(24,119,242,0.5)',borderColor:'#1877F2',borderWidth:2,yAxisID:'y'}},{{label:'Ierakstu skaits',data:t.map(function(x){{return x.count}}),type:'line',borderColor:'#A78BFA',backgroundColor:'transparent',borderWidth:3,pointRadius:4,pointBackgroundColor:'#A78BFA',tension:.4,yAxisID:'y1'}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',interaction:{{mode:'index',intersect:false}},scales:{{x:scOpts(),y:scOpts(),y1:{{position:'top',grid:{{display:false}},ticks:{{color:'#A78BFA',font:{{size:11}}}}}}}}}}}}}};

// Build top posts table
var topSortKey='engagement';
function buildTopPosts(){{
  var t=D.top_posts.slice().sort(function(a,b){{return b[topSortKey]-a[topSortKey]}});
  var h='<tr><th>#</th><th>Datums</th><th>Tips</th><th>Likes</th><th>Shares</th><th>Comm.</th><th>Kopā</th><th>Teksts</th></tr>';
  t.forEach(function(p,i){{
    h+='<tr><td>'+(i+1)+'</td><td>'+p.date+'</td><td><span class="b bb">'+p.type+'</span></td><td>'+nf(p.likes)+'</td><td>'+nf(p.shares)+'</td><td>'+nf(p.comments)+'</td><td><strong>'+nf(p.engagement)+'</strong></td><td style="max-width:250px;font-size:0.8em;color:var(--text-3)">'+(p.url?'<a href="'+p.url+'" target="_blank">':'')+p.teksts.substring(0,80)+'…'+(p.url?'</a>':'')+'</td></tr>';
  }});
  document.getElementById('topT').innerHTML=h;
}}
function sortTop(key,btn){{topSortKey=key;btn.parentElement.querySelectorAll('button').forEach(function(b){{b.classList.remove('active')}});btn.classList.add('active');buildTopPosts()}}

function buildWorstPosts(){{
  var t=D.worst_posts;
  var h='<tr><th>#</th><th>Datums</th><th>Tips</th><th>Iesaiste</th><th>Teksts</th></tr>';
  t.forEach(function(p,i){{
    h+='<tr><td>'+(i+1)+'</td><td>'+p.date+'</td><td><span class="b br">'+p.type+'</span></td><td>'+p.engagement+'</td><td style="max-width:300px;font-size:0.8em;color:var(--text-3)">'+p.teksts.substring(0,60)+'…</td></tr>';
  }});
  document.getElementById('worstT').innerHTML=h;
}}

// Build conclusions
function buildConclusions(){{
  var k=D.kpi;var w=D.work_weekend;var c=D.contest;var cn=D.concentration;var cl=D.cleaned;
  var bestFmt=D.formats.reduce(function(a,b){{return a.avg_eng>b.avg_eng?a:b}});
  var bestDay=D.weekday.reduce(function(a,b){{return a.avg_eng>b.avg_eng?a:b}});
  var bestSlot=D.time_slots.reduce(function(a,b){{return a.avg_eng>b.avg_eng?a:b}});
  var bestCap=D.caption_length.reduce(function(a,b){{return a.avg_eng>b.avg_eng?a:b}});

  var items=[
    ['good','Kopējais apjoms','<span class="st">'+k.total_posts+'</span> publikācijas ar kopējo iesaisti <span class="st">'+nf(k.total_engagement)+'</span>. Vidējā iesaiste uz postu: <span class="st">'+k.avg_eng+'</span>. Bez konkursiem ('+cl.removed_contests+') un top 10 postiem — <span class="st">'+cl.count+'</span> ieraksti ar vid. iesaisti <span class="st">'+cl.avg_eng+'</span>.'],
    ['good','Labākā diena: '+bestDay.name,'<span class="hl">'+bestDay.name+'</span> uzrāda augstāko vid. iesaisti: <span class="st">'+bestDay.avg_eng+'</span> ('+bestDay.posts+' posti).'],
    [w.weekend_avg>w.work_avg*1.2?'good':'tip','Brīvdienas vs Darba dienas','Brīvdienu vid. iesaiste <span class="st">'+w.weekend_avg+'</span>'+(w.weekend_avg>w.work_avg?' ir augstāka':' ir zemāka')+' nekā darba dienās ('+w.work_avg+'). Brīvdienu postu īpatsvars: <span class="st">'+w.weekend_pct+'%</span>.'],
    ['good','Labākais laika slots','<span class="hl">'+bestSlot.name+'</span> ar vid. iesaisti <span class="st">'+bestSlot.avg_eng+'</span> ir visefektīvākais publicēšanas laiks.'],
    ['tip','Teksta garuma ietekme','Labākais pavadošā teksta garums: <span class="hl">'+bestCap.name+'</span> ar vid. iesaisti <span class="st">'+bestCap.avg_eng+'</span>.'],
    [D.half_year_growth>0?'good':'bad','H2 '+(D.half_year_growth>0?'izaugsme':'kritums')+': '+D.half_year_growth+'%','Otrais pusgads (Jul-Dec) vid. iesaiste <span class="st">'+D.half_year[1].avg_eng+'</span> '+(D.half_year_growth>0?'ir augstāka':'ir zemāka')+' nekā H1 ('+D.half_year[0].avg_eng+').'],
    [c.avg_eng>c.non_avg?'good':'bad','Konkursu efektivitāte','Konkursu vid. iesaiste: <span class="st">'+c.avg_eng+'</span> vs parastu postu: <span class="st">'+c.non_avg+'</span>. Konkursi veido <span class="hl">'+c.pct+'%</span> no visiem postiem.'],
    ['good','Iesaistes koncentrācija','Top <span class="st">1%</span> postu ('+cn.top1_posts+') ģenerē <span class="st">'+cn.top1_share+'%</span> no visas iesaistes. Top 10% — <span class="st">'+cn.top10_share+'%</span>.'],
    ['good','Likes dominē','Likes veido <span class="st">'+D.engagement_breakdown.likes_pct+'%</span>, Shares <span class="st">'+D.engagement_breakdown.shares_pct+'%</span>, Comments <span class="st">'+D.engagement_breakdown.comments_pct+'%</span>.'],
    ['tip','Konsistence: CV '+k.cv,k.cv<0.5?'Ļoti stabila satura veiktspēja visos mēnešos.':k.cv<1?'Samērā stabili rezultāti ar nelielu mainību.':'Liela mainība starp mēnešiem — ieteicams izlīdzināt satura kvalitāti.'],
    ['good','Virālie posti','<span class="st">'+k.viral_count+'</span> posti ('+k.viral_pct+'%) pārsniedz 3x vidējo iesaisti. Labākais mēnesis: <span class="hl">'+k.best_month+'</span>.'],
  ];

  // Add orientation insight
  if(D.orientation.length>0){{
    var bestOri=D.orientation.reduce(function(a,b){{return a.avg_eng>b.avg_eng?a:b}});
    items.push(['tip','Bilžu orientācija','<span class="hl">'+bestOri.name+'</span> attēli ('+bestOri.pct+'%) uzrāda augstāko vid. iesaisti: <span class="st">'+bestOri.avg_eng+'</span>.']);
  }}

  // Video insight
  if(D.video && D.video.has_data && D.video.buckets){{
    var bestVid=D.video.buckets.reduce(function(a,b){{return a.avg_eng>b.avg_eng?a:b}});
    items.push(['tip','Video garums','Labākais video garums: <span class="hl">'+bestVid.name+'</span> ar vid. iesaisti <span class="st">'+bestVid.avg_eng+'</span>. Kopā '+D.video.total+' video.']);
  }}

  // Theme insights — top 3 topics + best/worst by avg engagement
  if(D.themes.length>0){{
    var sortedByCount=D.themes.slice().sort(function(a,b){{return b.count-a.count}});
    var top3=sortedByCount.slice(0,3).map(function(t){{return '<span class="hl">'+t.name+'</span> ('+t.count+' ieraksti, vid. ies. '+t.avg_eng+')'}}).join(', ');
    items.push(['good','Populārākās tēmas','Biežākās satura tēmas: '+top3+'.']);
    var sortedByEng=D.themes.slice().sort(function(a,b){{return b.avg_eng-a.avg_eng}});
    var best=sortedByEng[0];
    var worst=sortedByEng[sortedByEng.length-1];
    items.push(['good','Efektīvākā tēma: '+best.name,'<span class="hl">'+best.name+'</span> uzrāda augstāko vid. iesaisti <span class="st">'+best.avg_eng+'</span> ('+best.count+' ieraksti). Zemākā: <span class="hl">'+worst.name+'</span> ar <span class="st">'+worst.avg_eng+'</span>.']);
  }}

  // Action plan
  items.push(['tip','Rīcības plāns 2026','<p>1. Publicēt vairāk <span class="hl">'+bestDay.name+'</span> un <span class="hl">'+bestSlot.name+'</span></p><p>2. Teksta garumu turēt īsāku: līdz <span class="st">120 zīmēm</span></p><p>3. Palielināt brīvdienu saturu (pašlaik <span class="st">'+w.weekend_pct+'%</span>)</p><p>4. Palielināt <span class="hl">video skaitu</span> — Reel un Video veicina augstāku sasniedzamību</p>']);

  var g=document.getElementById('conG');
  g.innerHTML=items.map(function(it){{
    return '<div class="con '+it[0]+'"><h3>'+it[1]+'</h3><p>'+it[2]+'</p></div>';
  }}).join('');
}}

function initScroll(){{
  var obs=new IntersectionObserver(function(e){{e.forEach(function(en){{if(en.isIntersecting)en.target.classList.add('visible')}});}},{{threshold:0.08,rootMargin:'0px 0px -40px 0px'}});
  document.querySelectorAll('.section,.con').forEach(function(el){{obs.observe(el)}});
}}

document.addEventListener('DOMContentLoaded',function(){{
  buildKPI();
  Object.keys(CFG).forEach(function(id){{rc(id)}});
  buildHeatmap();
  buildBigrams();
  buildTopPosts();
  buildWorstPosts();
  buildConclusions();
  document.querySelectorAll('.con').forEach(function(el,i){{el.style.transitionDelay=(i*0.06)+'s'}});
  initScroll();
}});
</script>
</body></html>'''

    return html


def main():
    posts, all_pages = load_page_data()
    if not posts:
        print(f"ERROR: No posts found for page '{PAGE_NAME}'")
        return

    D = compute(posts)
    html = generate_html(D, PAGE_NAME, all_pages)

    page_slug = slug(PAGE_NAME)
    out_path = os.path.join(DIR, f'Facebook_{page_slug}_2025.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    file_size = os.path.getsize(out_path) // 1024
    print(f"\nGenerated: {out_path}")
    print(f"File size: {file_size} KB")
    print(f"Sections: ~23+ | Charts: 20+ | Conclusions: 17+")


if __name__ == '__main__':
    main()
