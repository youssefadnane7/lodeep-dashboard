"""
Lodeep - Tableau de bord Performance Commerciale
Lancer :  streamlit run app.py
"""
import base64
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Lodeep - Performance Commerciale", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

ASSETS = Path(__file__).parent / "assets"
NAVY, BLUE, ORANGE, INK = "#1B2A9B", "#1E90FF", "#E8743B", "#1a1f3c"
TYPE_COLORS = {"GMS": BLUE, "Distributeur": NAVY, "Grands Comptes": ORANGE}
DEFAULT_SHEETS = ["GMS", "Distributeur", "Grands Comptes"]
PERIODS = ["Cette semaine", "Semaine dernière", "Mois complet"]
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"


def b64(name: str) -> str:
    p = ASSETS / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


LOGO, SIDE = b64("logo.png"), b64("sidebar.png")

# ----------------------------------------------------------------------------
# Style (CSS)
# ----------------------------------------------------------------------------
st.markdown(
    f"""
<style>
  #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ visibility:visible; height:0; }}
  header[data-testid="stHeader"] {{ background:transparent; }}
  .stApp {{ background:#E9ECF6; }}
  .block-container {{ padding:.9rem 1.6rem .6rem 1.6rem; max-width:100%; }}
  [data-testid="stMainBlockContainer"] > div > [data-testid="stVerticalBlock"] {{ gap:.6rem; }}

  /* ---------- Sidebar ---------- */
  section[data-testid="stSidebar"] {{
      background:#06204d url("data:image/png;base64,{SIDE}") no-repeat center / 100% 100%;
      min-width:250px !important; max-width:250px !important; border-right:none;
  }}
  section[data-testid="stSidebar"] > div {{ background:transparent; }}
  section[data-testid="stSidebar"] label p {{ color:#fff !important; font-weight:600; font-size:.85rem; }}
  section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
      background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.55); border-radius:6px; }}
  section[data-testid="stSidebar"] [data-baseweb="select"] * {{ color:#fff !important; }}
  section[data-testid="stSidebar"] [data-baseweb="tag"] {{ background:{BLUE} !important; }}
  section[data-testid="stSidebar"] svg {{ fill:#fff; }}
  section[data-testid="stSidebar"] .stButton button {{
      background:rgba(255,255,255,.10); color:#fff; border:1px solid rgba(255,255,255,.7);
      border-radius:8px; font-weight:600; padding:.55rem 0; }}
  section[data-testid="stSidebar"] .stButton button:hover {{ background:rgba(255,255,255,.22); border-color:#fff; }}
  .side-logo {{ text-align:center; margin:.2rem 0 2.5rem 0; }}
  .side-logo img {{ width:170px; }}

  /* ---------- Titres ---------- */
  h1.title {{ margin:0; padding:0; font-size:1.7rem; font-weight:800; color:{INK}; letter-spacing:.2px; line-height:1.1; }}
  h1.title span {{ color:{NAVY}; }}
  p.sub {{ color:{NAVY}; font-size:.95rem; margin:.15rem 0 0 0; letter-spacing:.5px; }}

  /* ---------- Cartes (visuels) : hauteur basée sur l'écran ---------- */
  div[data-testid="stVerticalBlockBorderWrapper"] {{
      background:#fff; border:1px solid #dde2f0 !important; border-radius:12px;
      box-shadow:0 2px 8px rgba(27,42,155,.07); }}
  [class*="st-key-r1"] {{ height:max(215px, calc((100vh - 190px) * .42)) !important; flex:0 0 auto !important; }}
  [class*="st-key-r2"] {{ height:max(250px, calc((100vh - 190px) * .58)) !important; flex:0 0 auto !important; }}
  [class*="st-key-r1"], [class*="st-key-r2"] {{ overflow:hidden; gap:.15rem !important; }}
  [class*="st-key-r1"] .stElementContainer:has(.stPlotlyChart),
  [class*="st-key-r2"] .stElementContainer:has(.stPlotlyChart),
  [class*="st-key-r2"] .stElementContainer:has(iframe) {{ flex:1 1 0; min-height:0; height:auto !important; }}
  [class*="st-key-r1"] .stElementContainer:has(.stPlotlyChart) *:not(.modebar):not(.modebar *):not(svg *),
  [class*="st-key-r2"] .stElementContainer:has(.stPlotlyChart) *:not(.modebar):not(.modebar *):not(svg *) {{ max-height:100%; }}
  [class*="st-key-r1"] .stPlotlyChart, [class*="st-key-r2"] .stPlotlyChart,
  [class*="st-key-r1"] .stPlotlyChart > div, [class*="st-key-r2"] .stPlotlyChart > div {{ height:100% !important; }}
  [class*="st-key-r2"] iframe {{ height:100% !important; }}
  [class*="st-key-r1"] > .stElementContainer:has(.vt), [class*="st-key-r2"] > .stElementContainer:has(.vt) {{ flex:0 0 auto !important; height:auto !important; min-height:24px; }}
  section[data-testid="stSidebar"] [data-testid="stExpander"] {{ border:1px solid rgba(255,255,255,.35); border-radius:8px; background:rgba(255,255,255,.06); }}
  section[data-testid="stSidebar"] [data-testid="stExpander"] summary, section[data-testid="stSidebar"] [data-testid="stExpander"] summary * {{ color:#fff !important; }}
  section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{ background:rgba(255,255,255,.12); border:1px dashed rgba(255,255,255,.55); }}
  section[data-testid="stSidebar"] [data-testid="stFileUploader"] section * {{ color:#fff !important; }}
  section[data-testid="stSidebar"] [data-testid="stFileChip"] > div:nth-child(2), section[data-testid="stSidebar"] [data-testid="stFileChip"] > div:nth-child(2) *,
  section[data-testid="stSidebar"] [data-testid="stFileChipDeleteBtn"], section[data-testid="stSidebar"] [data-testid="stFileChipDeleteBtn"] * {{ color:{INK} !important; }}
  section[data-testid="stSidebar"] [data-testid="stFileUploader"] section button {{ background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.6); }}
  .vt {{ font-weight:700; font-size:.95rem; color:{INK}; margin:0; line-height:1.2; }}
  .vt small {{ font-weight:400; color:#7a819c; font-size:.75rem; margin-left:6px; }}

  /* ---------- KPI ---------- */
  .kpi {{ position:relative; background:#fff; border:1px solid #dde2f0; border-radius:12px;
          box-shadow:0 2px 8px rgba(27,42,155,.07); padding:9px 8px 8px; text-align:center; overflow:hidden; }}
  .kpi::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:5px;
          background:linear-gradient(180deg,{BLUE},{NAVY}); }}
  .kpi::after {{ content:""; position:absolute; right:-14px; top:-14px; width:42px; height:42px; border-radius:50%;
          background:linear-gradient(135deg,{BLUE},{NAVY}); opacity:.16; }}
  .kpi .l {{ font-size:.85rem; color:#4a5070; font-weight:600; }}
  .kpi .v {{ font-size:1.55rem; font-weight:800; color:{INK}; line-height:1.2; }}

  /* ---------- Période ---------- */
  .per-label {{ font-size:.75rem; color:#4a5070; font-weight:600; margin-bottom:0; }}
  [data-testid="stButtonGroup"] button {{ border-radius:6px !important; font-weight:600; background:#fff; color:{INK};
          border:1px solid #d3d8e8; min-height:2rem; }}
  [data-testid="stButtonGroup"] button[kind="segmented_controlActive"],
  [data-testid="stButtonGroup"] button[aria-checked="true"] {{ background:{NAVY} !important; color:#fff !important; border-color:{NAVY}; }}
  [data-testid="stButtonGroup"] button[kind="segmented_controlActive"] p {{ color:#fff !important; }}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Préparation des données
# ----------------------------------------------------------------------------
def list_sheets(file_bytes: bytes):
    return pd.ExcelFile(io.BytesIO(file_bytes), engine="openpyxl").sheet_names


@st.cache_data(show_spinner="Lecture du fichier…")
def prepare_data(file_bytes: bytes, sheets: tuple) -> pd.DataFrame:
    """Pour chaque feuille : supprime les 4 premières lignes, garde les 5 premières
    colonnes, ajoute la colonne 'Type' (= nom de la feuille), puis empile le tout."""
    frames = []
    for sheet in sheets:
        df = pd.read_excel(
            io.BytesIO(file_bytes), sheet_name=sheet, header=None,
            skiprows=4,            # 1) on supprime les 4 premières lignes
            usecols=range(5),      # 2) on garde seulement les 5 premières colonnes
            engine="openpyxl",
        )
        df = df.iloc[1:].copy()    # la ligne 5 du fichier = en-têtes -> on la retire
        df.columns = ["Date", "Enseigne", "Famille", "Désignation", "Réalisation"]
        df["Type"] = sheet         # 3) colonne Type
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)
    data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
    data["Réalisation"] = pd.to_numeric(data["Réalisation"], errors="coerce")
    data = data.dropna(subset=["Date", "Réalisation"])
    for c in ["Enseigne", "Famille", "Désignation"]:
        data[c] = data[c].astype(str).str.strip()      # "EAU GAZEUSE " -> "EAU GAZEUSE"
    return data


def fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", " ")


def kpi(col, label, value):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div></div>',
                 unsafe_allow_html=True)


def card_title(text, sub=""):
    s = f"<small>{sub}</small>" if sub else ""
    st.markdown(f'<div class="vt">{text}{s}</div>', unsafe_allow_html=True)


def style(fig, height=300, legend=True, r=4, t=6, b=None):
    fig.update_layout(
        height=height, margin=dict(l=4, r=r, t=(30 if legend else t), b=(4 if b is None else b)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=INK),
        legend_title_text="", showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0) if legend else None,
    )
    return fig


# ----------------------------------------------------------------------------
# Matrice (Enseigne > Famille > Désignation) : HTML + JS dans une iframe
# ----------------------------------------------------------------------------
def build_matrix_html(df: pd.DataFrame, total: float) -> str:
    n = lambda v: f"{v:,.0f}"
    g_e = df.groupby("Enseigne")["Réalisation"].sum().sort_values(ascending=False)
    g_f = df.groupby(["Enseigne", "Famille"])["Réalisation"].sum()
    g_p = df.groupby(["Enseigne", "Famille", "Désignation"])["Réalisation"].sum()
    nf = df.groupby("Enseigne")["Famille"].nunique()
    np_e = df.groupby("Enseigne")["Désignation"].nunique()
    np_f = df.groupby(["Enseigne", "Famille"])["Désignation"].nunique()

    rows = []
    for i, (ens, v) in enumerate(g_e.items()):
        ke = f"e{i}"
        rows.append((0, ke, ens, v, nf[ens], np_e[ens], True))
        fams = g_f[ens].sort_values(ascending=False)
        for j, (fam, fv) in enumerate(fams.items()):
            kf = f"{ke}_f{j}"
            rows.append((1, kf, fam, fv, 1, np_f[(ens, fam)], True))
            prods = g_p[(ens, fam)].sort_values(ascending=False)
            for k, (prod, pv) in enumerate(prods.items()):
                rows.append((2, f"{kf}_p{k}", prod, pv, 1, 1, False))

    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    trs = []
    for lvl, key, name, v, a, b, has_kids in rows:
        tg = '<span class="tg"></span>' if has_kids else '<span class="tg none"></span>'
        trs.append(
            f'<tr class="l{lvl}" data-k="{key}" data-l="{lvl}" data-n="{esc(name).lower()}"'
            f'{"" if lvl == 0 else " hidden"}>'
            f'<td style="padding-left:{8 + lvl * 20}px">{tg}{esc(name)}</td>'
            f"<td>{n(v)}</td><td>{v / total * 100:.2f}%</td><td>{a}</td><td>{b}</td></tr>")

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
      html,body {{ margin:0; height:100%; font-family:{FONT}; color:{INK}; background:#fff; }}
      .wrap {{ display:flex; flex-direction:column; height:100%; }}
      .bar {{ display:flex; gap:6px; align-items:center; padding:2px 0 6px 0; }}
      .bar input {{ flex:1; max-width:260px; border:1px solid #d3d8e8; border-radius:6px; padding:5px 8px; font-size:12px; outline:none; }}
      .bar button {{ border:1px solid #d3d8e8; background:#fff; color:{INK}; border-radius:6px; padding:5px 10px; font-size:12px; font-weight:600; cursor:pointer; }}
      .bar button:hover {{ background:#eef3ff; border-color:{NAVY}; }}
      .scroll {{ flex:1; overflow:auto; border-radius:6px; }}
      table {{ width:100%; border-collapse:collapse; font-size:12.5px; table-layout:fixed; }}
      col.n {{ width:82px; }} col.p {{ width:74px; }}
      td:first-child {{ overflow:hidden; text-overflow:ellipsis; }}
      thead th {{ position:sticky; top:0; z-index:2; background:#123E7C; color:#fff; padding:7px 4px; text-align:center; font-weight:700; font-size:12px; }}
      thead th:first-child {{ text-align:left; }}
      td {{ padding:5px 4px; text-align:center; border-bottom:1px solid #eef0f7; }}
      td:first-child {{ text-align:left; white-space:nowrap; }}
      tr.l0 {{ background:#e6effb; font-weight:700; cursor:pointer; }}
      tr.l1 {{ background:#f2f6fd; font-weight:700; cursor:pointer; }}
      tr.l2 {{ background:#fff; }}
      tr.l0:hover, tr.l1:hover {{ background:#d8e6fb; }}
      tr[hidden] {{ display:none; }}
      .tg {{ display:inline-block; width:11px; height:11px; border:1px solid #6b7390; margin-right:8px; position:relative;
             vertical-align:-1px; background:#fff; box-sizing:border-box; }}
      .tg::before {{ content:""; position:absolute; left:2px; right:2px; top:4px; height:1px; background:#333; }}
      .tg::after {{ content:""; position:absolute; top:2px; bottom:2px; left:4px; width:1px; background:#333; }}
      .open > td > .tg::after {{ display:none; }}
      .tg.none {{ visibility:hidden; }}
      tfoot td {{ position:sticky; bottom:0; background:#dfe8fb; font-weight:800; border-top:2px solid #123E7C; }}
    </style></head><body><div class="wrap">
      <div class="bar"><input id="q" placeholder="🔍 Rechercher une enseigne…">
        <button onclick="setAll(true)">⊞ Tout développer</button><button onclick="setAll(false)">⊟ Tout réduire</button></div>
      <div class="scroll"><table><colgroup><col><col class='n'><col class='p'><col class='p'><col class='p'></colgroup><thead><tr><th>Enseigne</th><th>Réalisation</th><th>% CA</th><th>Familles</th><th>Produits</th></tr></thead>
      <tbody id="b">{''.join(trs)}</tbody>
      <tfoot><tr><td>Total</td><td>{n(total)}</td><td>100.00%</td><td>{df['Famille'].nunique()}</td><td>{df['Désignation'].nunique()}</td></tr></tfoot>
      </table></div></div>
    <script>
      const rows=[...document.querySelectorAll('#b tr')], open={{}};
      function refresh(){{
        const q=document.getElementById('q').value.trim().toLowerCase(); let chain=[true,false,false], match=true;
        rows.forEach(r=>{{
          const l=+r.dataset.l; if(l===0) match=!q||r.dataset.n.includes(q);
          const vis=match&&(l===0||chain[l-1]); r.hidden=!vis;
          chain[l]=vis&&!!open[r.dataset.k]; r.classList.toggle('open',!!open[r.dataset.k]);
        }});
      }}
      rows.forEach(r=>r.addEventListener('click',()=>{{ if(r.dataset.l==='2')return; open[r.dataset.k]=!open[r.dataset.k]; refresh(); }}));
      function setAll(v){{ rows.forEach(r=>{{ if(r.dataset.l!=='2') open[r.dataset.k]=v; }}); refresh(); }}
      document.getElementById('q').addEventListener('input',refresh); refresh();
    </script></body></html>"""


# ----------------------------------------------------------------------------
# En-tête
# ----------------------------------------------------------------------------


def reset():
    st.session_state.update(f_type=[], f_fam=[], f_per="Mois complet")


side_top = st.sidebar.container()
side_bottom = st.sidebar.container()

with side_top:
    if LOGO:
        st.markdown(f'<div class="side-logo"><img src="data:image/png;base64,{LOGO}"></div>',
                    unsafe_allow_html=True)

with side_bottom:
    st.markdown("<hr style='border-color:rgba(255,255,255,.25);margin:1.2rem 0 .6rem'>", unsafe_allow_html=True)
    uploaded = st.file_uploader("📁 Fichier Excel (.xlsx / .xlsm)", type=["xlsx", "xlsm"])
    chosen = DEFAULT_SHEETS
    if uploaded is not None:
        file_bytes = uploaded.getvalue()
        all_sheets = list_sheets(file_bytes)
        with st.expander("⚙️ Feuilles analysées"):
            chosen = st.multiselect("Feuilles à analyser", all_sheets, label_visibility="collapsed",
                                    default=[s for s in DEFAULT_SHEETS if s in all_sheets])

h1, h2 = st.columns([3, 1.6])
with h1:
    st.markdown('<h1 class="title">TABLEAU DE BORD — <span>PERFORMANCE COMMERCIALE</span></h1>'
                '<p class="sub">Suivi du CA • Enseignes • Familles • Produits</p>', unsafe_allow_html=True)

if uploaded is None:
    st.info("⬅️ Charge ton fichier Excel dans le menu de gauche pour afficher le tableau de bord.")
    st.stop()
if not chosen:
    st.warning("Choisis au moins une feuille.")
    st.stop()

try:
    data = prepare_data(file_bytes, tuple(chosen))
except Exception as e:
    st.error(f"Impossible de lire ces feuilles (structure attendue : 4 lignes à supprimer, "
             f"puis en-têtes + 5 colonnes). Détail : {e}")
    st.stop()

# ----------------------------------------------------------------------------
# Filtres
# ----------------------------------------------------------------------------
with side_top:
    st.multiselect("Type Client", sorted(data["Type"].unique()), key="f_type", placeholder="All")
    st.multiselect("Famille", sorted(data["Famille"].unique()), key="f_fam", placeholder="All")
    st.button("↺  Réinitialiser", on_click=reset, width="stretch")

with h2:
    st.markdown('<div class="per-label">Période :</div>', unsafe_allow_html=True)
    if "f_per" not in st.session_state:
        st.session_state["f_per"] = "Mois complet"
    st.segmented_control("Période", PERIODS, key="f_per", label_visibility="collapsed")
per = st.session_state.get("f_per") or "Mois complet"

last_day = data["Date"].max()
week_start = last_day - pd.Timedelta(days=last_day.weekday())

month_start = last_day.replace(day=1)
month_end = month_start + pd.offsets.MonthEnd(0)
if per == "Cette semaine":
    p_start, p_end = week_start, min(week_start + pd.Timedelta(days=6), month_end)
elif per == "Semaine dernière":
    p_start, p_end = week_start - pd.Timedelta(days=7), week_start - pd.Timedelta(days=1)
else:
    p_start, p_end = month_start, month_end
# jours de la période hors dimanche (même logique que la mesure Power BI)
nb_days_period = max(int((pd.date_range(p_start, p_end).dayofweek != 6).sum()), 1)

df = data.copy()
if st.session_state.get("f_type"):
    df = df[df["Type"].isin(st.session_state["f_type"])]
if st.session_state.get("f_fam"):
    df = df[df["Famille"].isin(st.session_state["f_fam"])]
if per == "Cette semaine":
    df = df[df["Date"] >= week_start]
elif per == "Semaine dernière":
    df = df[(df["Date"] >= week_start - pd.Timedelta(days=7)) & (df["Date"] < week_start)]

if df.empty:
    st.warning("Aucune donnée pour ces filtres.")
    st.stop()

# ----------------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------------
total = df["Réalisation"].sum()
k = st.columns(5)
kpi(k[0], "Réalisation", f"{fmt(total)} DH")
kpi(k[1], "Nb Enseignes", fmt(df["Enseigne"].nunique()))
kpi(k[2], "Nb Familles", fmt(df["Famille"].nunique()))
kpi(k[3], "Nb Produits", fmt(df["Désignation"].nunique()))
kpi(k[4], "CA Moyen / Jour", fmt(total / nb_days_period))

CFG = {"displayModeBar": False}

# ----------------------------------------------------------------------------
# Ligne 1 : évolution / camembert / familles
# ----------------------------------------------------------------------------
c1, c2, c3 = st.columns([1.35, 1, 1.1])

with c1.container(border=True, key="r1_evo"):
    card_title("Évolution CA Par Jour", "DH")
    daily = df.groupby("Date", as_index=False)["Réalisation"].sum()
    fig = go.Figure(go.Scatter(
        x=daily["Date"], y=daily["Réalisation"], mode="lines+markers", line=dict(color=NAVY, width=2.5, shape="spline"),
        marker=dict(size=6, color="#fff", line=dict(color=NAVY, width=2)),
        fill="tozeroy", fillcolor="rgba(27,42,155,0.10)",
        hovertemplate="%{x|%d/%m/%Y}<br><b>%{y:,.0f} DH</b><extra></extra>"))
    span = (daily["Date"].max() - daily["Date"].min()).days
    fig.update_xaxes(tickformat="%d", dtick=86400000 * (1 if span <= 12 else 3), showgrid=False, title=None)
    fig.update_yaxes(tickformat="~s", gridcolor="#eceff7", zeroline=False, title=None, rangemode="tozero")
    st.plotly_chart(style(fig, None, legend=False), height="stretch", config=CFG)

with c2.container(border=True, key="r1_pie"):
    card_title("CA par Type Client")
    by_type = df.groupby("Type", as_index=False)["Réalisation"].sum()
    fig = px.pie(by_type, names="Type", values="Réalisation", color="Type", color_discrete_map=TYPE_COLORS)
    fig.update_traces(
        textinfo="percent", textposition="inside", insidetextorientation="horizontal",
        textfont=dict(color="#fff", size=13), sort=False, direction="clockwise",
        marker=dict(line=dict(color="#fff", width=2)),
        hovertemplate="%{label}<br><b>%{value:,.0f} DH</b> (%{percent})<extra></extra>")
    style(fig, None, legend=False, t=14, b=8).update_layout(showlegend=True, margin=dict(l=4, r=4, t=14, b=8), legend=dict(orientation="v", yanchor="middle", y=0.5, x=0.98))
    st.plotly_chart(fig, height="stretch", config=CFG)

with c3.container(border=True, key="r1_fam"):
    card_title("CA par Famille", "DH")
    by_fam = df.groupby("Famille", as_index=False)["Réalisation"].sum().sort_values("Réalisation")
    fig = go.Figure(go.Bar(
        x=by_fam["Réalisation"], y=by_fam["Famille"], orientation="h", marker_color=BLUE,
        text=by_fam["Réalisation"].map(fmt), textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br><b>%{x:,.0f} DH</b><extra></extra>"))
    fig.update_xaxes(tickformat="~s", gridcolor="#eceff7", title=None, range=[0, by_fam["Réalisation"].max() * 1.3])
    fig.update_yaxes(title=None)
    st.plotly_chart(style(fig, None, legend=False, r=70), height="stretch", config=CFG)

# ----------------------------------------------------------------------------
# Ligne 2 : famille x type / matrice enseignes
# ----------------------------------------------------------------------------
d1, d2 = st.columns([1, 1.45])

with d1.container(border=True, key="r2_ft"):
    card_title("CA par Famille et Type de Client", "DH")
    ft = df.groupby(["Famille", "Type"], as_index=False)["Réalisation"].sum()
    fig = px.bar(ft, x="Famille", y="Réalisation", color="Type", barmode="group", color_discrete_map=TYPE_COLORS)
    fig.update_xaxes(title=None)
    fig.update_yaxes(tickformat="~s", gridcolor="#eceff7", title=None)
    fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: <b>%{y:,.0f} DH</b><extra></extra>")
    st.plotly_chart(style(fig, None), height="stretch", config=CFG)

with d2.container(border=True, key="r2_mat"):
    card_title("PERFORMANCE DES ENSEIGNES — CA, FAMILLES & PRODUITS", "clique sur ⊞ pour détailler")
    st.iframe(build_matrix_html(df, total), height=300)

# ----------------------------------------------------------------------------
# Données nettoyées
# ----------------------------------------------------------------------------
with st.expander("📄 Voir / télécharger les données nettoyées"):
    st.dataframe(data, width="stretch", hide_index=True)
    st.download_button("Télécharger en CSV", data.to_csv(index=False).encode("utf-8-sig"),
                       "donnees_nettoyees.csv", "text/csv")
