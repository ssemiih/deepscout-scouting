"""
DeepScout — Leaderboard Demo
streamlit run app.py
"""
import math, os, base64
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DeepScout", page_icon="⚡", layout="wide",
                   initial_sidebar_state="expanded")

# ── 🌟 ADVANCED SPORTS ANALYTICS PALETTE (STROKE EFFECTS & RADAR MAX) 🌟 ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;800&family=JetBrains+Mono:wght@700;800&display=swap');

*, html, body { box-sizing: border-box; }
html, body, [class*="css"], .main, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 30%, #090F1C 0%, #04050A 100%) !important;
    color: #E2E8F0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
[data-testid="stSidebar"] { background: #020306 !important; border-right: 1px solid #1E293B !important; }
[data-testid="stSidebar"] * { color: #94A3B8 !important; font-family: 'Space Grotesk', sans-serif !important; }

/* 🕹️ STROKE EFFECT FOR NATIVE BUTTONS (CATEGORIES) */
button[data-testid="baseButton-secondary"] {
    background: linear-gradient(135deg, #0F172A, #0B1120) !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-weight: 1000 !important;
    font-size: 20px !important;
    padding: 8px 12px !important;
    -webkit-text-stroke: 0.4px #1E293B;
    transition: all 0.2s ease !important;
}
button[data-testid="baseButton-secondary"]:hover {
    border-color: #00F2FE !important;
    color: #00F2FE !important;
    -webkit-text-stroke: 0.5px #05070F;
}
button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.15), rgba(59, 130, 246, 0.15)) !important;
    border: 1px solid #00F2FE !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 20px !important;
    padding: 8px 12px !important;
    -webkit-text-stroke: 0.5px #05070F;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.1) !important;
}

.stSelectbox > div > div { background: #0F172A !important; border-color: #1E293B !important; color: #E2E8F0 !important; border-radius: 6px !important;}
hr { border-color: #1E293B !important; }

/* STROKE-READY CLASSES */
.stroke-player {
    font-weight: 900 !important;
    color: #F8FAFC !important;
    -webkit-text-stroke: 0.5px #7AACAC;
}
.stroke-rank {
    font-weight: 800 !important;
    -webkit-text-stroke: 0.1px #F8F8FF;
}
.stroke-score {
    font-weight: 800 !important;
    -webkit-text-stroke: 0.8px #F8F8FF;
}
</style>
""", unsafe_allow_html=True)

# ── LOGO ENGINE ───────────────────────────────────────────────
def get_logo_html(image_path="logo.png", max_height="38px"):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded_str = base64.b64encode(img_file.read()).decode()
        return f'<img src="data:image/png;base64,{encoded_str}" style="max-height: {max_height}; max-width: 100%; width: auto; object-fit: contain; display: block; margin: 0 auto;">'
    return f'<span style="font-size: 18px; font-weight: 700; color: #00F2FE; letter-spacing: -0.5px; white-space: nowrap; display: block; text-align: center; width: 100%;">DEEPSCOUT</span>'

# ── AVATAR ENGINE ──────────────────────────────────────────────
def photo_url(name: str) -> str:
    encoded = name.replace(' ', '+')
    return f"https://ui-avatars.com/api/?name={encoded}&background=0F172A&color=00F2FE&size=128&bold=true&rounded=true&font-size=0.38"

# ── DATA LOAD ──────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("deepscout_kalecisiz.csv")
    df = df[df['Playing Time_MP'] >= 10].copy()
    df['Nation'] = df['Nation'].str.split().str[-1]
    return df

df_raw = load()

LK = {'Premier League':1.00,'La Liga':0.94,'Bundesliga':0.96,'Serie A':0.93,
      'Ligue 1':0.95,'Primeira Liga':0.86,'Süper Lig':0.85,'Eredivisie':0.83,'Pro League':0.81}

GECIS_POS   = ['FW','FW,MF','MF,FW','MF']
YARATICI_POS = ['MF','MF,FW','FW,MF','FW','MF,DF']
BITIRICI_POS = ['FW','FW,MF','MF,FW']

def norm(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn + 1e-9)

def to_score(h):
    mn, mx = h.min(), h.max()
    return ((h - mn) / (mx - mn + 1e-9) ** 0.75) * 100

def compute(df, kat):
    df = df.copy()
    df['lk'] = df['League'].map(LK).fillna(.80)

    if kat == "Fiziksel":
        d = df.copy()
        d['ham'] = (norm(d['İkili Müc. Kazanma %'])*.60 + norm(d['Aldığı Faul'])*.30 + norm(d['Faul'])*.10) * d['lk']
        d['ra'] = norm(d['İkili Müc. Kazanma %']) * 100
        d['rb'] = norm(d['Aldığı Faul']) * 100
        d['rc'] = norm(d['Faul']) * 100
        d['rd'] = norm(d['Müdahale/Maç']) * 100
        d['re'] = norm(d['Top Kapma/Maç']) * 100
        d['rl'] = [('İkili','Faul Aldı','Faul','Müdahale','Top Kapma')] * len(d)
        d['m1l'], d['m2l'] = 'İkili Müc. %', 'Aldığı Faul'
        d['m1v'] = d['İkili Müc. Kazanma %'].round(1)
        d['m2v'] = d['Aldığı Faul'].round(1)

    elif kat == "Geçiş":
        d = df[df['Pos'].isin(GECIS_POS)].copy()
        d['drib_r'] = d['B.Dribbling/Maç'] / (d['Dribbling/Maç'] + 1e-9)
        d['ham'] = (norm(d['B.Dribbling/Maç'])*.33 + norm(d['Hızlı Hücum Golü'])*.30 + norm(d['drib_r'])*.12 + norm(d['Hızlı Hücum'])*.25) * d['lk']
        d['ra'] = norm(d['B.Dribbling/Maç']) * 100
        d['rb'] = norm(d['drib_r']) * 100
        d['rc'] = norm(d['Hızlı Hücum Golü']) * 100
        d['rd'] = norm(d['Hızlı Hücum']) * 100
        d['re'] = norm(d['Şut/Maç']) * 100
        d['rl'] = [('B.Drib','Drib%','HH Gol','Hızlı Hücum','Şut')] * len(d)
        d['m1l'], d['m2l'] = 'B.Dribbling/Maç', 'HH Golü'
        d['m1v'] = d['B.Dribbling/Maç'].round(2)
        d['m2v'] = d['Hızlı Hücum Golü'].round(2)

    elif kat == "Yaratıcı":
        d = df[df['Pos'].isin(YARATICI_POS)].copy()
        d['orta_r'] = d['B.Orta/Maç'] / (d['Orta/Maç'] + 1e-9)
        d['ham'] = (norm(d['Yaratılan B.Şans'])*.28 + norm(d['Kilit Pas/Maç'])*.28 + norm(d['Asist'])*.22 + norm(d['B.Pas/Maç'])*.12 + norm(d['orta_r'])*.10) * d['lk']
        d['ra'] = norm(d['Yaratılan B.Şans']) * 100
        d['rb'] = norm(d['Kilit Pas/Maç']) * 100
        d['rc'] = norm(d['Asist']) * 100
        d['rd'] = norm(d['B.Pas/Maç']) * 100
        d['re'] = norm(d['orta_r']) * 100
        d['rl'] = [('Yar.Şans','Kilit Pas','Asist','B.Pas','Orta%')] * len(d)
        d['m1l'], d['m2l'] = 'Kilit Pas/Maç', 'Asist'
        d['m1v'] = d['Kilit Pas/Maç'].round(2)
        d['m2v'] = d['Asist'].round(1)

    elif kat == "Bitirici":
        d = df[df['Pos'].isin(BITIRICI_POS) & (df['xG'] >= 2.5)].copy()
        d['g_xg']   = d['Gol'] - d['xG']
        d['isabet'] = d['İsabetli Şut/Maç'] / (d['Şut/Maç'] + 1e-9)
        d['ham'] = (norm(d['g_xg'])*.40 + norm(d['isabet'])*.25 + norm(d['Gol'])*.15 + norm(-d['Kaçırılan B.Şans'])*.20) * d['lk']
        d['ra'] = norm(d['g_xg']) * 100
        d['rb'] = norm(d['isabet']) * 100
        d['rc'] = norm(d['Gol']) * 100
        d['rd'] = (1 - norm(d['Kaçırılan B.Şans'])) * 100
        d['re'] = norm(d['xG']) * 100
        d['rl'] = [('G-xG','İsabet','Gol','B.Şans','xG')] * len(d)
        d['m1l'], d['m2l'] = 'Gol', 'G-xG'
        d['m1v'] = d['Gol'].round(1)
        d['m2v'] = d['g_xg'].round(2)
    else:
        return pd.DataFrame()

    d['skor'] = to_score(d['ham'])
    return d

# ── 🧬 MAX RESOLUTION DNA HARİTASI (SIZE BUMPED TO 115) ────────
def radar_svg(vals, labels, color, size=115):
    n = len(vals)
    cx, cy = size/2, size/2
    r = size/2 - 16
    angles = [math.pi/2 + 2*math.pi*i/n for i in range(n)]
    hex_c = color.lstrip('#')
    ri, gi, bi = int(hex_c[0:2],16), int(hex_c[2:4],16), int(hex_c[4:6],16)
    svg = f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">'
    for pct in [0.33, 0.66, 1.0]:
        pts = " ".join(f"{cx+r*pct*math.cos(a):.1f},{cy-r*pct*math.sin(a):.1f}" for a in angles)
        svg += f'<polygon points="{pts}" fill="none" stroke="#2D3748" stroke-width="0.8"/>'
    for a in angles:
        svg += f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx+r*math.cos(a):.1f}" y2="{cy-r*math.sin(a):.1f}" stroke="#2D3748" stroke-width="0.8"/>'
    norm_v = [max(0, min(1, v/100)) for v in vals]
    pts = " ".join(f"{cx+r*nv*math.cos(a):.1f},{cy-r*nv*math.sin(a):.1f}" for nv, a in zip(norm_v, angles))
    svg += f'<polygon points="{pts}" fill="rgba({ri},{gi},{bi},0.15)" stroke="{color}" stroke-width="1.8"/>'
    for nv, a in zip(norm_v, angles):
        x, y = cx+r*nv*math.cos(a), cy-r*nv*math.sin(a)
        svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{color}"/>'
    for lbl, a in zip(labels, angles):
        lx = cx+(r+10)*math.cos(a); ly = cy-(r+10)*math.sin(a)
        anc = "middle" if abs(math.cos(a))<0.3 else ("start" if math.cos(a)>0 else "end")
        svg += f'<text x="{lx:.1f}" y="{ly+3:.1f}" text-anchor="{anc}" font-size="7.5" fill="#718096" font-family="sans-serif" font-weight="700">{lbl}</text>'
    return svg + '</svg>'

def get_rank_color(index):
    colors = [
        "#FFF275", "#F4C430", "#D4C590", "#EAF2F8", "#A6B9CE",
        "#7D93A6", "#6B7280", "#947D60", "#CD7F32", "#5C3A21"
    ]
    return colors[min(index, len(colors)-1)]

# ── SIDEBAR PANEL ─────────────────────────────────────────────
with st.sidebar:
    sidebar_logo = get_logo_html("logo.png", max_height="28px")
    st.markdown(f'<div style="width:100%; text-align:center; padding:5px 0; overflow:hidden;">{sidebar_logo}</div>', unsafe_allow_html=True)
    st.divider()
    sel_lig  = st.selectbox("LİG",  ["Tümü"] + sorted(df_raw['League'].dropna().unique().tolist()))
    yas_r    = st.slider("YAŞ", int(df_raw['Age'].min()), int(df_raw['Age'].max()), (17,42))
    sel_ulke = st.selectbox("ÜLKE", ["Tümü"] + sorted(df_raw['Nation'].dropna().unique().tolist()))
    st.divider()
    u23 = st.toggle("Sadece U23", value=False)

# ── FİLTRE MOTORU ─────────────────────────────────────────────
dff = df_raw.copy()
if sel_lig  != "Tümü": dff = dff[dff['League'] == sel_lig]
if sel_ulke != "Tümü": dff = dff[dff['Nation'] == sel_ulke]
dff = dff[(dff['Age'] >= yas_r[0]) & (dff['Age'] <= yas_r[1])]
if u23: dff = dff[dff['Age'] < 23]

# ── 💎 ANA BANNER ─────────────────────────────────────────────
logo_html = get_logo_html("logo.png", max_height="38px")
st.markdown(f"""
<div style="background: linear-gradient(135deg, #111827, #0F172A); border: 1px solid #1E293B; border-radius: 10px; padding: 16px 20px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
<div style="display:flex; align-items:center;">{logo_html}</div>
<div style="text-align: right;">
<div style="font-size:12px; color:#64748B; font-weight:600; letter-spacing:0.05em;">INTELLIGENCE RECRUITMENT SYSTEM</div>
<div style="font-size:11px; color:#334155; font-family:'JetBrains Mono',monospace;">v1.3 · MATRIX STABLE</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── 🕹️ KATEGORİ SEÇİM ALANI ────────────────────────────────────
if "kat" not in st.session_state: st.session_state.kat = "Yaratıcı"
if "mod" not in st.session_state: st.session_state.mod = "elite"

KATS = {"Fiziksel": "💪 PHYSICAL", "Geçiş": "⚡ TRANSITION", "Yaratıcı": "🧠 CREATIVE", "Bitirici": "🎯 FINISHERS"}

c1, c2, c3, c4 = st.columns(4)
for col, (k, label) in zip([c1, c2, c3, c4], KATS.items()):
    with col:
        btn_type = "primary" if st.session_state.kat == k else "secondary"
        if st.button(label, key=f"k_{k}", type=btn_type, use_container_width=True):
            st.session_state.kat = k
            st.rerun()

st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

# ── TOP 10 / FLOP 10 ──────────────────────────────────────────
c1, c2, _, inf = st.columns([1,1,4,2])
with c1:
    if st.button("🔥 ELITE 10", key="elite", type="primary" if st.session_state.mod == "elite" else "secondary", use_container_width=True): 
        st.session_state.mod = "elite"; st.rerun()
with c2:
    if st.button("💀 FLOP 10", key="flop", type="primary" if st.session_state.mod == "flop" else "secondary", use_container_width=True): 
        st.session_state.mod = "flop"; st.rerun()
with inf:
    mc = "#00F2FE" if st.session_state.mod=="elite" else "#EF4444"
    ml = "▲ HIGHEST SPECTRUM" if st.session_state.mod=="elite" else "▼ LOWEST SPECTRUM"
    st.markdown(f'<p style="font-size:12px; color:{mc}; font-family:\'JetBrains Mono\',monospace; font-weight:600; margin-top:10px; text-align:right;">{ml} · {len(dff)} PLAYERS</p>', unsafe_allow_html=True)

kat = st.session_state.kat
mod = st.session_state.mod

# ── DATA PROCESS ──────────────────────────────────────────────
if dff.empty: st.warning("Filtre sonucu oyuncu bulunamadı."); st.stop()
scored = compute(dff, kat)
if scored.empty: st.warning("Bu kategori için kriterlere uyan oyuncu yok."); st.stop()

liste = (scored.nlargest(10,'skor') if mod=="elite" else scored.nsmallest(10,'skor'))
liste  = liste.reset_index(drop=True)
max_s  = scored['skor'].max()

# ── 🌟 LEADERBOARD DÖNGÜSÜ (NO INDENT FLUSH LEFT - STROKE REVOLUTION) ──
for i, row in liste.iterrows():
    rank = i + 1
    skor = row['skor']
    
    c_color = get_rank_color(i) if mod == "elite" else "#EF4444"
    bar_gradient = "linear-gradient(90deg, #00F2FE 0%, #1E40AF 100%)" if mod == "elite" else "linear-gradient(90deg, #FCA5A5 0%, #7F1D1D 100%)"
    
    purl = photo_url(row['Player'])
    avatar = f'<img src="{purl}" style="width:48px; height:48px; border-radius:50%; object-fit:cover; border:1.5px solid {c_color};">'
    u23_tag = ('<span style="background: rgba(0, 242, 254, 0.05); border: 1px solid rgba(0, 242, 254, 0.2); border-radius:4px; padding:1px 6px; font-size:10px; color:#00F2FE; margin-left:8px; font-weight:600;">U23</span>' if row['Age'] < 23 else "")
    
    # DNA Haritası Büyük Boyut
    radar = radar_svg([row['ra'],row['rb'],row['rc'],row['rd'],row['re']], row['rl'], c_color, size=105)

    metrics = (
        f'<span style="font-size:12px; color:#64748B; margin-right:14px;">'
        f'{row["m1l"]}: <span style="color:#F1F5F9; font-weight:600; font-family:\'JetBrains Mono\';">{row["m1v"]}</span></span>'
        f'<span style="font-size:12px; color:#64748B;">'
        f'{row["m2l"]}: <span style="color:#F1F5F9; font-weight:600; font-family:\'JetBrains Mono\';">{row["m2v"]}</span></span>'
    )

    bar_w = int((skor/max_s)*100)

    # 📌 REZALET VE KAYMA RİSKİ OLMAYAN SIFIR GAP HTML BLOKU
    card_html = f"""<div style="background: linear-gradient(135deg, #111827, #0B132B); border: 1px solid #1E293B; border-left: 6px solid {c_color}; border-radius: 8px; padding: 7px 10px; margin-bottom: 5px; display: flex; align-items: center; gap: 18px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
<div class="stroke-rank" style="min-width:30px; text-align:center; font-size:16px; color:{c_color}; font-family:'JetBrains Mono',monospace;">{rank}.</div>
<div style="flex-shrink:0; display:flex;">{avatar}</div>
<div style="flex:1; min-width:0;">
<div class="stroke-player" style="font-size:20px;">{row['Player']}{u23_tag}</div>
<div style="margin-top:2px; display:flex; align-items:center; gap:6px;">
<span style="color:#64748B; font-size:12px;">{row['League']}</span>
<span style="color:#334155; font-size:12px;">•</span>
<span style="color:#64748B; font-size:12px;">{int(row['Age'])} yrs</span>
<span style="color:#334155; font-size:12px;">•</span>
<span style="color:#94A3B8; font-size:11px; font-weight:600; background:#1E293B; padding:1px 5px; border-radius:3px;">{row['Pos']}</span>
</div>
<div style="margin-top:6px;">{metrics}</div>
<div style="margin-top:8px; height:5px; background:#05070F; border-radius:2px; max-width:250px;">
<div style="height:4px; width:{bar_w}%; background: {bar_gradient}; border-radius:2px;"></div>
</div>
</div>
<div style="flex-shrink:0; background:rgba(15,23,42,0.4); border-radius:8px; padding:6px; display:flex; align-items:center; justify-content:center; min-width:125px; min-height:125px;">{radar}</div>
<div style="flex-shrink:0; text-align:right; min-width:65px;">
<div class="stroke-score" style="font-size:24px; color:{c_color}; font-family:'JetBrains Mono',monospace; letter-spacing:-0.5px;">{skor:.1f}</div>
<div style="font-size:9px; color:#475569; font-family:monospace; font-weight:700; letter-spacing:0.05em;">SCORE</div>
</div>
</div>"""

    st.markdown(card_html, unsafe_allow_html=True)