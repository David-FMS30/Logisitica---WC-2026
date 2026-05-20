"""
Copa do Mundo 2026 — Análise de Desgaste Logístico
Streamlit app completo:
  • Visão Geral (KPIs + ranking)
  • Mapa de Rotas (Folium interativo)
  • Milhas Voadas (gráfico de barras comparativo)
  • Heatmap de Fadiga (Seaborn)
  • Detalhes por Seleção (deep-dive)
  • Exportar dados (CSV)
"""

from __future__ import annotations

import base64
import io
import math
from pathlib import Path

import folium
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from geopy.distance import geodesic
from matplotlib.colors import LinearSegmentedColormap
from streamlit_folium import st_folium

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Copa 2026 · Fadiga Logística",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Override Streamlit base */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 16.5px !important;
}
.main { background: #080c14; }
section[data-testid="stSidebar"] {
    background: #0b1120 !important;
    border-right: 1px solid #1e2d47 !important;
}
.stMarkdown, .stCaption, p, label, div[data-testid="stText"] {
    font-size: 1rem !important;
}

.sidebar-logo {
    width: 112px;
    max-width: 72%;
    display: block;
    margin: 4px 0 14px;
    border-radius: 8px;
    border: 1px solid #1e3a5f;
    background: #000;
}

.hero-card {
    display: flex;
    align-items: center;
    gap: 22px;
    background: linear-gradient(135deg,#080c14 0%,#0b1628 60%,#060d1e 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 22px;
}

.hero-logo {
    width: 92px;
    height: 92px;
    object-fit: cover;
    border-radius: 10px;
    border: 1px solid #1e3a5f;
    background: #000;
    flex: 0 0 auto;
}

.hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: #e8f4fd;
    line-height: 1.15;
}

.hero-sub {
    font-size: 0.96rem;
    color: #5d8ab5;
    margin-top: 7px;
    line-height: 1.45;
}

@media (max-width: 760px) {
    .hero-card { align-items: flex-start; gap: 14px; padding: 16px; }
    .hero-logo { width: 70px; height: 70px; }
    .hero-title { font-size: 1.45rem; }
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0e1a2e 0%, #0b1628 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 18px 20px;
    transition: border-color .25s, transform .2s;
}
div[data-testid="metric-container"]:hover {
    border-color: #2e6faf;
    transform: translateY(-2px);
}
div[data-testid="metric-container"] label {
    color: #5d8ab5 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: .08em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8f4fd !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: #48bb78 !important;
    font-size: 0.86rem !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.96rem !important;
    letter-spacing: .02em;
    color: #5d8ab5 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #60a5fa !important;
    border-bottom: 2px solid #60a5fa !important;
}

/* Section headers */
.sec-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 12px;
    margin-bottom: 6px;
    border-bottom: 1px solid #1e2d47;
}
.sec-header .icon { font-size: 1.3rem; }
.sec-header .label {
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #5d8ab5;
}

/* Score badge */
.score-box {
    background: linear-gradient(135deg, #0e1a2e, #0a1525);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 20px 28px;
    text-align: center;
    margin-bottom: 18px;
}
.score-team { font-size: 1.05rem; font-weight: 600; color: #94b8d4; }
.score-value { font-size: 2.8rem; font-weight: 700; font-family: 'JetBrains Mono'; color: #e8f4fd; }
.score-sub { font-size: 0.78rem; color: #5d8ab5; margin-top: 4px; }

/* IFL badge */
.ifl-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    font-family: 'JetBrains Mono';
    letter-spacing: .04em;
}
.ifl-low    { background: #0a2e1a; color: #48bb78; border: 1px solid #48bb78; }
.ifl-mid    { background: #2d2007; color: #f6c90e; border: 1px solid #f6c90e; }
.ifl-high   { background: #2d1207; color: #f97316; border: 1px solid #f97316; }
.ifl-crit   { background: #2d0a0a; color: #f87171; border: 1px solid #f87171; }

/* Sidebar filter title */
.sidebar-title {
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #5d8ab5;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2d47;
    margin-bottom: 8px;
}

/* Multiselect chips */
div[data-baseweb="select"] [data-baseweb="tag"] {
    background: #102846 !important;
    border: 1px solid #2e6faf !important;
    color: #e8f4fd !important;
    border-radius: 7px !important;
}
div[data-baseweb="select"] [data-baseweb="tag"] span {
    color: #e8f4fd !important;
}
div[data-baseweb="select"] [data-baseweb="tag"] svg {
    color: #94b8d4 !important;
}

/* Download button */
.stDownloadButton > button {
    background: #0e1a2e !important;
    border: 1px solid #1e3a5f !important;
    color: #60a5fa !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: #1e3a5f !important;
    border-color: #60a5fa !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DADOS
# ─────────────────────────────────────────────────────────────────────────────

STADIUMS: dict[str, dict] = {
    "New York/NJ":   {"lat": 40.8135, "lon": -74.0744, "tz": "ET", "tz_off": -4, "country": "USA",    "stadium": "MetLife Stadium"},
    "Los Angeles":   {"lat": 34.0141, "lon": -118.2879, "tz": "PT", "tz_off": -7, "country": "USA",   "stadium": "SoFi Stadium"},
    "Dallas":        {"lat": 32.7479, "lon": -97.0929,  "tz": "CT", "tz_off": -5, "country": "USA",   "stadium": "AT&T Stadium"},
    "San Francisco": {"lat": 37.4033, "lon": -121.9694, "tz": "PT", "tz_off": -7, "country": "USA",   "stadium": "Levi's Stadium"},
    "Miami":         {"lat": 25.9580, "lon": -80.2389,  "tz": "ET", "tz_off": -4, "country": "USA",   "stadium": "Hard Rock Stadium"},
    "Atlanta":       {"lat": 33.7553, "lon": -84.4006,  "tz": "ET", "tz_off": -4, "country": "USA",   "stadium": "Mercedes-Benz Stadium"},
    "Seattle":       {"lat": 47.5952, "lon": -122.3316, "tz": "PT", "tz_off": -7, "country": "USA",   "stadium": "Lumen Field"},
    "Kansas City":   {"lat": 38.9200, "lon": -94.4878,  "tz": "CT", "tz_off": -5, "country": "USA",   "stadium": "Arrowhead Stadium"},
    "Philadelphia":  {"lat": 39.9008, "lon": -75.1675,  "tz": "ET", "tz_off": -4, "country": "USA",   "stadium": "Lincoln Financial Field"},
    "Boston":        {"lat": 42.0909, "lon": -71.2643,  "tz": "ET", "tz_off": -4, "country": "USA",   "stadium": "Gillette Stadium"},
    "Houston":       {"lat": 29.6847, "lon": -95.4107,  "tz": "CT", "tz_off": -5, "country": "USA",   "stadium": "NRG Stadium"},
    "Toronto":       {"lat": 43.6657, "lon": -79.6393,  "tz": "ET", "tz_off": -4, "country": "CAN",   "stadium": "BMO Field"},
    "Vancouver":     {"lat": 49.2769, "lon": -123.1160, "tz": "PT", "tz_off": -7, "country": "CAN",   "stadium": "BC Place"},
    "Mexico City":   {"lat": 19.3029, "lon": -99.1505,  "tz": "CT", "tz_off": -5, "country": "MEX",   "stadium": "Estadio Azteca"},
    "Guadalajara":   {"lat": 20.6430, "lon": -103.3996, "tz": "CT", "tz_off": -5, "country": "MEX",   "stadium": "Estadio Akron"},
    "Monterrey":     {"lat": 25.6693, "lon": -100.3106, "tz": "CT", "tz_off": -5, "country": "MEX",   "stadium": "Estadio BBVA"},
}

SCHEDULE: list[dict] = [
    {"team": "Brasil",     "group": "A", "match": 1, "day": 0,  "venue": "Miami"},
    {"team": "Brasil",     "group": "A", "match": 2, "day": 4,  "venue": "Los Angeles"},
    {"team": "Brasil",     "group": "A", "match": 3, "day": 8,  "venue": "Dallas"},
    {"team": "Argentina",  "group": "B", "match": 1, "day": 0,  "venue": "Mexico City"},
    {"team": "Argentina",  "group": "B", "match": 2, "day": 4,  "venue": "Dallas"},
    {"team": "Argentina",  "group": "B", "match": 3, "day": 9,  "venue": "Houston"},
    {"team": "Franca",     "group": "C", "match": 1, "day": 1,  "venue": "New York/NJ"},
    {"team": "Franca",     "group": "C", "match": 2, "day": 5,  "venue": "Philadelphia"},
    {"team": "Franca",     "group": "C", "match": 3, "day": 9,  "venue": "Boston"},
    {"team": "Alemanha",   "group": "D", "match": 1, "day": 1,  "venue": "Dallas"},
    {"team": "Alemanha",   "group": "D", "match": 2, "day": 5,  "venue": "Atlanta"},
    {"team": "Alemanha",   "group": "D", "match": 3, "day": 9,  "venue": "Miami"},
    {"team": "Espanha",    "group": "E", "match": 1, "day": 2,  "venue": "Los Angeles"},
    {"team": "Espanha",    "group": "E", "match": 2, "day": 6,  "venue": "San Francisco"},
    {"team": "Espanha",    "group": "E", "match": 3, "day": 10, "venue": "Seattle"},
    {"team": "Portugal",   "group": "F", "match": 1, "day": 2,  "venue": "Boston"},
    {"team": "Portugal",   "group": "F", "match": 2, "day": 6,  "venue": "New York/NJ"},
    {"team": "Portugal",   "group": "F", "match": 3, "day": 10, "venue": "Philadelphia"},
    {"team": "Inglaterra", "group": "G", "match": 1, "day": 2,  "venue": "Miami"},
    {"team": "Inglaterra", "group": "G", "match": 2, "day": 6,  "venue": "Atlanta"},
    {"team": "Inglaterra", "group": "G", "match": 3, "day": 10, "venue": "Houston"},
    {"team": "Mexico",     "group": "H", "match": 1, "day": 0,  "venue": "Mexico City"},
    {"team": "Mexico",     "group": "H", "match": 2, "day": 4,  "venue": "Guadalajara"},
    {"team": "Mexico",     "group": "H", "match": 3, "day": 9,  "venue": "Monterrey"},
    {"team": "EUA",        "group": "I", "match": 1, "day": 1,  "venue": "Los Angeles"},
    {"team": "EUA",        "group": "I", "match": 2, "day": 5,  "venue": "Kansas City"},
    {"team": "EUA",        "group": "I", "match": 3, "day": 9,  "venue": "Seattle"},
    {"team": "Holanda",    "group": "J", "match": 1, "day": 3,  "venue": "Toronto"},
    {"team": "Holanda",    "group": "J", "match": 2, "day": 7,  "venue": "Boston"},
    {"team": "Holanda",    "group": "J", "match": 3, "day": 11, "venue": "New York/NJ"},
    {"team": "Japao",      "group": "K", "match": 1, "day": 3,  "venue": "Los Angeles"},
    {"team": "Japao",      "group": "K", "match": 2, "day": 7,  "venue": "San Francisco"},
    {"team": "Japao",      "group": "K", "match": 3, "day": 11, "venue": "Seattle"},
    {"team": "Marrocos",   "group": "L", "match": 1, "day": 3,  "venue": "Philadelphia"},
    {"team": "Marrocos",   "group": "L", "match": 2, "day": 7,  "venue": "New York/NJ"},
    {"team": "Marrocos",   "group": "L", "match": 3, "day": 11, "venue": "Miami"},
]

TEAM_COLORS: dict[str, str] = {
    "Brasil":     "#009C3B",
    "Argentina":  "#74ACDF",
    "Franca":     "#4169E1",
    "Alemanha":   "#C0C0C0",
    "Espanha":    "#AA151B",
    "Portugal":   "#006600",
    "Inglaterra": "#CF0A2C",
    "Mexico":     "#006847",
    "EUA":        "#B31942",
    "Holanda":    "#FF6600",
    "Japao":      "#BC002D",
    "Marrocos":   "#C1272D",
}

TEAM_FLAGS: dict[str, str] = {
    "Brasil": "🇧🇷", "Argentina": "🇦🇷", "Franca": "🇫🇷",
    "Alemanha": "🇩🇪", "Espanha": "🇪🇸", "Portugal": "🇵🇹",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Mexico": "🇲🇽", "EUA": "🇺🇸",
    "Holanda": "🇳🇱", "Japao": "🇯🇵", "Marrocos": "🇲🇦",
}

TEAM_ABBREVIATIONS: dict[str, str] = {
    "Algeria": "ALG",
    "Argentina": "ARG",
    "Australia": "AUS",
    "Austria": "AUT",
    "Belgium": "BEL",
    "Bosnia and Herzegovina": "BIH",
    "Brazil": "BRA",
    "Cabo Verde": "CPV",
    "Canada": "CAN",
    "Colombia": "COL",
    "Congo DR": "COD",
    "Croatia": "CRO",
    "Curacao": "CUW",
    "Curaçao": "CUW",
    "Czechia": "CZE",
    "Ecuador": "ECU",
    "Egypt": "EGY",
    "England": "ENG",
    "Germany": "GER",
    "Ghana": "GHA",
    "Haiti": "HAI",
    "Iran": "IRN",
    "Iraq": "IRQ",
    "Japan": "JPN",
    "Jordan": "JOR",
    "Mexico": "MEX",
    "Morocco": "MAR",
    "New Zealand": "NZL",
    "Norway": "NOR",
    "Paraguay": "PAR",
    "Qatar": "QAT",
    "Saudi Arabia": "KSA",
    "Scotland": "SCO",
    "South Africa": "RSA",
    "South Korea": "KOR",
    "Spain": "ESP",
    "Switzerland": "SUI",
    "Tunisia": "TUN",
    "Türkiye": "TUR",
    "Turkiye": "TUR",
    "Uruguay": "URU",
    "USA": "USA",
    "Uzbekistan": "UZB",
}

PLOTLY_TEMPLATE = "plotly_dark"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGO_PATH = BASE_DIR / "logo wc26.jpeg"
IFL_MODEL_VERSION = "ifl-v4-marker-legend"
DATA_FILES = ("matches.csv", "teams.csv", "host_cities.csv", "tournament_stages.csv")

CITY_ALIASES = {
    "New York/New Jersey": "New York/NJ",
    "San Francisco Bay Area": "San Francisco",
}

HOST_COUNTRY_LABELS = {
    "USA": "EUA",
    "MEX": "Mexico",
    "CAN": "Canada",
}

HOST_COUNTRY_CODES = {
    "USA": "USA",
    "United States": "USA",
    "EUA": "USA",
    "Mexico": "MEX",
    "MEX": "MEX",
    "Canada": "CAN",
    "CAN": "CAN",
}

VENUE_ALTITUDE_M = {
    "Atlanta": 320,
    "Boston": 20,
    "Dallas": 170,
    "Houston": 13,
    "Kansas City": 270,
    "Los Angeles": 38,
    "Miami": 2,
    "New York/NJ": 4,
    "Philadelphia": 12,
    "San Francisco": 2,
    "Seattle": 50,
    "Toronto": 76,
    "Vancouver": 2,
    "Guadalajara": 1566,
    "Mexico City": 2240,
    "Monterrey": 540,
}

DYNAMIC_TEAM_COLORS = [
    "#60a5fa", "#f87171", "#48bb78", "#fbbf24", "#c084fc", "#2dd4bf",
    "#fb7185", "#a3e635", "#38bdf8", "#f97316", "#818cf8", "#f472b6",
]


def stadium_key(city_name: str) -> str:
    return CITY_ALIASES.get(str(city_name), str(city_name))


def host_country_code(country: str) -> str:
    return HOST_COUNTRY_CODES.get(str(country), str(country))


def host_country_label(code: str) -> str:
    return HOST_COUNTRY_LABELS.get(str(code), str(code))


def map_view_for_countries(country_codes: tuple[str, ...]) -> tuple[list[float], int]:
    codes = set(country_codes)
    if codes == {"MEX"}:
        return [23.5, -102.5], 5
    if codes == {"CAN"}:
        return [50.5, -105.0], 4
    if codes == {"USA"}:
        return [38.0, -97.0], 4
    if codes == {"USA", "MEX"}:
        return [31.5, -101.0], 4
    if codes == {"USA", "CAN"}:
        return [43.5, -101.0], 4
    return [34.0, -95.0], 4


def team_color(team: str) -> str:
    if team in TEAM_COLORS:
        return TEAM_COLORS[team]
    idx = sum((i + 1) * ord(ch) for i, ch in enumerate(str(team))) % len(DYNAMIC_TEAM_COLORS)
    return DYNAMIC_TEAM_COLORS[idx]


def team_label(team: str) -> str:
    return str(team)


def team_abbrev(team: str, code: str | None = None) -> str:
    code_text = "" if code is None else str(code).strip()
    if code_text and code_text.lower() not in {"nan", "none"}:
        return code_text.upper()[:3]
    mapped = TEAM_ABBREVIATIONS.get(str(team))
    if mapped:
        return mapped
    letters = "".join(ch for ch in str(team).upper() if ch.isalnum())
    return letters[:3] if letters else "SEL"


def readable_text_color(hex_color: str) -> str:
    color = str(hex_color).lstrip("#")
    if len(color) != 6:
        return "#ffffff"
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
    except ValueError:
        return "#ffffff"
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#08101d" if brightness > 150 else "#ffffff"


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def kickoff_label(value: str) -> str:
    try:
        return pd.to_datetime(str(value)[:19]).strftime("%d/%m %H:%M")
    except Exception:
        return str(value)[:16]


def route_ifl_color(fi: float) -> str:
    if fi < 2.5:
        return "#48bb78"
    if fi < 5.0:
        return "#f6c90e"
    if fi < 7.5:
        return "#f97316"
    return "#f87171"


def altitude_factor(venue: str) -> float:
    altitude_m = VENUE_ALTITUDE_M.get(str(venue), 0)
    return round(max(0, altitude_m - 500) / 1000 * 0.8, 3)


def minmax_0_10(values: pd.Series, reference: pd.Series | None = None) -> pd.Series:
    values = pd.to_numeric(values, errors="coerce").fillna(0.0)
    ref = values if reference is None else pd.to_numeric(reference, errors="coerce").fillna(0.0)
    min_v = float(ref.min()) if len(ref) else 0.0
    max_v = float(ref.max()) if len(ref) else 0.0
    if math.isclose(max_v, min_v):
        return pd.Series(np.zeros(len(values)), index=values.index)
    return ((values - min_v) / (max_v - min_v) * 10).clip(0, 10).round(2)


def midpoint(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def bearing_degrees(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])
    lon_delta = math.radians(b[1] - a[1])
    x = math.sin(lon_delta) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon_delta)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def marker_offset(coord: tuple[float, float], team_index: int, game_index: int) -> tuple[float, float]:
    offsets = [
        (0.0, 0.0),
        (0.028, 0.028),
        (-0.028, 0.028),
        (0.028, -0.028),
        (-0.028, -0.028),
        (0.0, 0.04),
        (0.0, -0.04),
        (0.04, 0.0),
        (-0.04, 0.0),
        (0.052, 0.026),
        (-0.052, 0.026),
        (0.052, -0.026),
        (-0.052, -0.026),
    ]
    lat_off, lon_off = offsets[(team_index + game_index) % len(offsets)]
    return coord[0] + lat_off, coord[1] + lon_off


def _fallback_schedule(source_error: str | None = None) -> pd.DataFrame:
    fallback = pd.DataFrame(SCHEDULE).copy()
    fallback["team_code"] = ""
    fallback["match_number"] = fallback["match"]
    fallback["match_label"] = "Fixture projetada"
    fallback["kickoff_at"] = ""
    fallback["city_name"] = fallback["venue"]
    fallback["venue_name"] = fallback["venue"].map(lambda v: STADIUMS[v]["stadium"])
    fallback["host_country"] = fallback["venue"].map(lambda v: STADIUMS[v]["country"])
    fallback["country_code"] = fallback["host_country"].map(host_country_code)
    fallback["data_source"] = "fallback_static"
    fallback["source_error"] = source_error or ""
    return fallback


def _read_data_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
    return pd.read_csv(path)


def data_version() -> tuple[tuple[str, int | None, int | None], ...]:
    version = []
    for filename in DATA_FILES:
        path = DATA_DIR / filename
        try:
            stat = path.stat()
            version.append((filename, stat.st_mtime_ns, stat.st_size))
        except FileNotFoundError:
            version.append((filename, None, None))
    return tuple(version)


@st.cache_data(show_spinner=False)
def _load_source_tables(
    _version: tuple[tuple[str, int | None, int | None], ...],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        _read_data_csv("matches.csv"),
        _read_data_csv("teams.csv"),
        _read_data_csv("host_cities.csv"),
        _read_data_csv("tournament_stages.csv"),
    )


def load_source_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return _load_source_tables(data_version())


@st.cache_data(show_spinner=False)
def _load_schedule_df(_version: tuple[tuple[str, int | None, int | None], ...]) -> pd.DataFrame:
    try:
        matches, teams, cities, stages = _load_source_tables(_version)

        matches = matches.copy()
        teams = teams.copy()
        cities = cities.copy()
        stages = stages.copy()

        for col in ["id", "match_number", "home_team_id", "away_team_id", "city_id", "stage_id"]:
            matches[col] = pd.to_numeric(matches[col], errors="coerce").astype("Int64")
        teams["id"] = pd.to_numeric(teams["id"], errors="coerce").astype("Int64")
        cities["id"] = pd.to_numeric(cities["id"], errors="coerce").astype("Int64")
        stages["id"] = pd.to_numeric(stages["id"], errors="coerce").astype("Int64")

        matches = matches.merge(
            stages[["id", "stage_name"]],
            left_on="stage_id",
            right_on="id",
            how="left",
            suffixes=("", "_stage"),
        ).rename(columns={"id": "match_id"})

        group_matches = matches[
            matches["stage_name"].eq("Group Stage")
            & matches["home_team_id"].notna()
            & matches["away_team_id"].notna()
        ].copy()
        if group_matches.empty:
            raise ValueError("Nenhum jogo de fase de grupos com selecoes definidas.")

        group_matches["local_date"] = pd.to_datetime(
            group_matches["kickoff_at"].astype(str).str.slice(0, 10),
            errors="coerce",
        )
        tournament_start = group_matches["local_date"].min()
        group_matches["day"] = (group_matches["local_date"] - tournament_start).dt.days.astype(int)

        base_cols = ["match_id", "match_number", "city_id", "kickoff_at", "match_label", "day"]
        home = group_matches[base_cols + ["home_team_id"]].rename(columns={"home_team_id": "team_id"})
        away = group_matches[base_cols + ["away_team_id"]].rename(columns={"away_team_id": "team_id"})
        team_games = pd.concat([home, away], ignore_index=True)

        team_games = team_games.merge(
            teams.rename(columns={"id": "team_id"}),
            on="team_id",
            how="left",
        )
        team_games = team_games.merge(
            cities.rename(columns={"id": "city_id", "country": "host_country"}),
            on="city_id",
            how="left",
        )
        team_games["country_code"] = team_games["host_country"].map(host_country_code)

        team_games["venue"] = team_games["city_name"].map(stadium_key)
        missing_venues = sorted(set(team_games["venue"].dropna()) - set(STADIUMS))
        if missing_venues:
            raise KeyError(f"Cidades sem coordenadas no app: {', '.join(missing_venues)}")

        team_games["_kickoff_utc"] = pd.to_datetime(team_games["kickoff_at"], utc=True, errors="coerce")
        team_games = team_games.sort_values(["team_id", "_kickoff_utc", "match_number"]).reset_index(drop=True)
        team_games["match"] = team_games.groupby("team_id").cumcount() + 1

        for col in ["match", "day", "match_number", "match_id"]:
            team_games[col] = team_games[col].astype(int)

        schedule = team_games.rename(
            columns={
                "team_name": "team",
                "fifa_code": "team_code",
                "group_letter": "group",
            }
        )[
            [
                "team", "team_code", "group", "match", "match_number", "match_id",
                "day", "venue", "city_name", "host_country", "venue_name",
                "kickoff_at", "match_label", "country_code",
            ]
        ].copy()
        schedule["country_code"] = schedule["host_country"].map(host_country_code)
        schedule["data_source"] = "csv_data"
        schedule["source_error"] = ""
        return schedule
    except Exception as exc:
        return _fallback_schedule(str(exc))


def load_schedule_df() -> pd.DataFrame:
    return _load_schedule_df(data_version())


@st.cache_data(show_spinner=False)
def _load_matches_catalog(_version: tuple[tuple[str, int | None, int | None], ...]) -> pd.DataFrame:
    try:
        matches, teams, cities, stages = _load_source_tables(_version)

        teams = teams[["id", "team_name", "fifa_code", "group_letter"]].copy()
        home_teams = teams.add_prefix("home_")
        away_teams = teams.add_prefix("away_")

        catalog = (
            matches
            .merge(stages[["id", "stage_name"]], left_on="stage_id", right_on="id", how="left", suffixes=("", "_stage"))
            .merge(cities.rename(columns={"id": "city_id", "country": "host_country"}), on="city_id", how="left")
            .merge(home_teams, left_on="home_team_id", right_on="home_id", how="left")
            .merge(away_teams, left_on="away_team_id", right_on="away_id", how="left")
        )
        return catalog[
            [
                "match_number", "stage_name", "match_label", "kickoff_at",
                "city_name", "host_country", "venue_name",
                "home_team_name", "home_fifa_code", "away_team_name", "away_fifa_code",
            ]
        ].sort_values("match_number").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


def load_matches_catalog() -> pd.DataFrame:
    return _load_matches_catalog(data_version())

# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULOS CORE
# ─────────────────────────────────────────────────────────────────────────────

def fatigue_index(km: float, tz_delta: int, rest_days: int, altitude: float = 0.0) -> float:
    if km == 0:
        return 0.0
    short_rest_pressure = max(0, 6 - max(rest_days, 0)) * 0.65
    raw = (km / 1000) * 1.5 + (tz_delta * 2.0) + short_rest_pressure + altitude
    return round(raw, 3)


def ifl_label(fi: float) -> str:
    if fi < 2.5:
        return "Baixo"
    if fi < 5.0:
        return "Moderado"
    if fi < 7.5:
        return "Alto"
    return "CRITICO"


def ifl_class(fi: float) -> str:
    if fi < 2.5:
        return "ifl-low"
    if fi < 5.0:
        return "ifl-mid"
    if fi < 7.5:
        return "ifl-high"
    return "ifl-crit"


@st.cache_data(show_spinner=False)
def _build_detail(
    _version: tuple[tuple[str, int | None, int | None], ...],
    _model_version: str,
) -> pd.DataFrame:
    df = _load_schedule_df(_version)
    rows = []
    for team, grp in df.groupby("team"):
        grp = grp.sort_values("match").reset_index(drop=True)
        for i, row in grp.iterrows():
            venue = row["venue"]
            stadium_info = STADIUMS[venue]
            host_country = row.get("host_country", stadium_info["country"])
            venue_name = row.get("venue_name", stadium_info["stadium"])
            if pd.isna(host_country) or host_country == "":
                host_country = stadium_info["country"]
            if pd.isna(venue_name) or venue_name == "":
                venue_name = stadium_info["stadium"]

            km = tz_d = rest = 0
            alt_factor = 0.0
            if i > 0:
                prev = grp.iloc[i - 1]
                p1 = (STADIUMS[prev["venue"]]["lat"], STADIUMS[prev["venue"]]["lon"])
                p2 = (stadium_info["lat"], stadium_info["lon"])
                km   = round(geodesic(p1, p2).km)
                tz_d = abs(stadium_info["tz_off"] - STADIUMS[prev["venue"]]["tz_off"])
                rest = int(row["day"]) - int(prev["day"])
                alt_factor = altitude_factor(venue)
            fi_raw = fatigue_index(km, tz_d, rest, alt_factor)
            rows.append({
                "team":          team,
                "team_code":     row.get("team_code", ""),
                "group":         row["group"],
                "match":         int(row["match"]),
                "match_number":  int(row.get("match_number", row["match"])),
                "match_label":   row.get("match_label", row["group"]),
                "kickoff_at":    row.get("kickoff_at", ""),
                "day":           int(row["day"]),
                "venue":         venue,
                "country":       host_country,
                "country_code":  row.get("country_code", host_country_code(host_country)),
                "stadium":       venue_name,
                "tz":            stadium_info["tz"],
                "altitude_m":    VENUE_ALTITUDE_M.get(venue, 0),
                "altitude_factor": alt_factor,
                "km_traveled":   km,
                "tz_delta":      tz_d,
                "rest_days":     rest,
                "fatigue_raw":   fi_raw,
                "data_source":   row.get("data_source", ""),
                "source_error":  row.get("source_error", ""),
            })
    detail = pd.DataFrame(rows)
    if not detail.empty:
        detail["fatigue_index"] = minmax_0_10(detail["fatigue_raw"])
        detail["ifl_label"] = detail["fatigue_index"].map(ifl_label)
    return detail


def build_detail() -> pd.DataFrame:
    return _build_detail(data_version(), IFL_MODEL_VERSION)


def route_label(values: pd.Series) -> str:
    return " -> ".join(str(value) for value in values)


@st.cache_data(show_spinner=False)
def build_summary(detail: pd.DataFrame, reference_detail: pd.DataFrame | None = None) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame(
            columns=[
                "team", "total_km", "avg_rest_days", "total_ifl",
                "peak_ifl", "route", "flag", "color", "rank",
            ]
        )
    reference_detail = detail if reference_detail is None else reference_detail

    def avg_rest(s):
        v = s[s > 0]
        return round(v.mean(), 1) if len(v) else 0.0

    df = (
        detail.groupby("team")
        .agg(
            total_km=("km_traveled", "sum"),
            avg_rest_days=("rest_days", avg_rest),
            total_ifl_raw=("fatigue_raw", "sum"),
            peak_ifl=("fatigue_index", "max"),
            route=("venue", route_label),
        )
        .reset_index()
    )

    reference_scores = (
        reference_detail.groupby("team")["fatigue_raw"]
        .sum()
        .reset_index(name="total_ifl_raw")
    )
    df["total_ifl"] = minmax_0_10(df["total_ifl_raw"], reference_scores["total_ifl_raw"])
    df = df.sort_values("total_ifl", ascending=False).reset_index(drop=True)
    df["flag"] = ""
    df["color"] = df["team"].apply(team_color)
    df["rank"] = df["total_ifl"].rank(ascending=False).astype(int)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# MAPA FOLIUM
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def build_folium(
    selected_teams: tuple[str, ...],
    detail: pd.DataFrame,
    country_codes: tuple[str, ...],
    layers_hidden: bool,
) -> folium.Map:
    center, zoom = map_view_for_countries(country_codes)
    m = folium.Map(location=center, zoom_start=zoom, tiles=None)
    folium.TileLayer(
        "CartoDB positron",
        name="Mapa claro",
        control=True,
        show=True,
    ).add_to(m)
    folium.TileLayer(
        "CartoDB dark_matter",
        name="Mapa escuro",
        control=True,
        show=False,
    ).add_to(m)
    map_css = """
    <style>
    .leaflet-container {
        font-family: 'Space Grotesk', Arial, sans-serif;
        font-size: 14px;
    }
    .leaflet-control-layers {
        background: rgba(8, 12, 20, .94) !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #e8f4fd !important;
        font-size: 13px !important;
        line-height: 1.45 !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, .28) !important;
    }
    .leaflet-control-layers label { color: #e8f4fd !important; }
    .leaflet-tooltip {
        background: rgba(8, 12, 20, .96) !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 8px !important;
        color: #e8f4fd !important;
        box-shadow: 0 8px 22px rgba(0, 0, 0, .35) !important;
    }
    </style>
    """
    m.get_root().header.add_child(folium.Element(map_css))
    country_set = set(country_codes)
    all_country_codes = set(HOST_COUNTRY_LABELS)
    limit_by_country = bool(country_set) and country_set != all_country_codes
    df_sched = load_schedule_df()
    visible_bounds: list[list[float]] = []

    # Cidades usadas pela base carregada
    active_sched = df_sched[df_sched["team"].isin(selected_teams)]
    if limit_by_country:
        active_sched = active_sched[active_sched["country_code"].isin(country_set)]
    active_venues = sorted(active_sched["venue"].dropna().unique())
    marker_occurrences: dict[str, int] = {}
    for name in active_venues:
        info = STADIUMS[name]
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=7, color="#60a5fa", fill=True,
            fill_color="#0e1a2e", fill_opacity=0.9, weight=2,
            tooltip=folium.Tooltip(
                f"<b style='color:#e8f4fd;font-size:15px'>{name}</b>"
                f"<br><span style='color:#94b8d4;font-size:13px'>{info['stadium']}</span>"
                f"<br><span style='color:#5d8ab5;font-size:12px'>Fuso: {info['tz']} (UTC{info['tz_off']:+d})</span>",
            ),
        ).add_to(m)

    for team_idx, team in enumerate(sorted(selected_teams)):
        grp = df_sched[df_sched["team"] == team].sort_values("match").reset_index(drop=True)
        if grp.empty:
            continue
        if limit_by_country and not grp["country_code"].isin(country_set).any():
            continue
        color = team_color(team)
        pin_text_color = readable_text_color(color)
        team_code = team_abbrev(team, grp.iloc[0].get("team_code", ""))
        coords = [(STADIUMS[v]["lat"], STADIUMS[v]["lon"]) for v in grp["venue"]]
        venues = list(grp["venue"])
        marker_positions: list[tuple[float, float] | None] = []
        for j, (coord, venue) in enumerate(zip(coords, venues)):
            if limit_by_country and grp.iloc[j]["country_code"] not in country_set:
                marker_positions.append(None)
                continue
            offset_index = marker_occurrences.get(venue, 0)
            marker_occurrences[venue] = offset_index + 1
            marker_positions.append(marker_offset(coord, offset_index, 0))

        fg = folium.FeatureGroup(name=team_label(team), show=not layers_hidden)

        for i in range(len(coords) - 1):
            if limit_by_country:
                origin_visible = grp.iloc[i]["country_code"] in country_set
                dest_visible = grp.iloc[i + 1]["country_code"] in country_set
                if not (origin_visible or dest_visible):
                    continue

            seg = detail[(detail["team"] == team) & (detail["match"] == i + 2)]
            km   = int(seg["km_traveled"].values[0]) if len(seg) else 0
            tz_d = int(seg["tz_delta"].values[0])    if len(seg) else 0
            fi   = float(seg["fatigue_index"].values[0]) if len(seg) else 0.0
            rest = int(seg["rest_days"].values[0])   if len(seg) else 0

            origin = grp.iloc[i]
            dest = grp.iloc[i + 1]
            fi_color = route_ifl_color(fi)
            origin_point = marker_positions[i] if marker_positions[i] is not None else coords[i]
            dest_point = marker_positions[i + 1] if marker_positions[i + 1] is not None else coords[i + 1]
            route_points = [
                [origin_point[0], origin_point[1]],
                [dest_point[0], dest_point[1]],
            ]
            visible_bounds.extend(route_points)

            route_tooltip_html = (
                f"<div style='font-family:Space Grotesk,sans-serif;min-width:260px;"
                f"background:#0e1a2e;padding:12px 14px;border-radius:8px;border:1px solid #1e3a5f'>"
                f"<b style='color:{color};font-size:15px'>{team_label(team)} ({team_code})</b>"
                f"<br><hr style='border-color:#1e3a5f;margin:7px 0'>"
                f"<span style='color:#94b8d4'>Voo:</span> "
                f"<b style='color:#e8f4fd'>{origin['venue']} -> {dest['venue']}</b>"
                f"<br><span style='color:#94b8d4'>Distancia:</span> "
                f"<b style='color:#e8f4fd'>{km:,} km</b>"
                f"<br><span style='color:#94b8d4'>Descanso:</span> "
                f"<b style='color:#e8f4fd'>{rest} dias</b>"
                f"<br><span style='color:#94b8d4'>Fuso:</span> "
                f"<b style='color:#e8f4fd'>{tz_d}h</b>"
                f"<br><span style='color:{fi_color};font-weight:700'>IFL: {fi:.2f} ({ifl_label(fi)})</span>"
                f"</div>"
            )
            folium.PolyLine(
                route_points,
                color=fi_color,
                weight=6,
                opacity=0.92,
                tooltip=folium.Tooltip(route_tooltip_html),
            ).add_to(fg)

            if origin_point != dest_point:
                arrow_point = midpoint(origin_point, dest_point)
                arrow_rotation = bearing_degrees(origin_point, dest_point) - 90
                folium.Marker(
                    location=arrow_point,
                    icon=folium.DivIcon(
                        html=(
                            f"<div style='width:0;height:0;"
                            f"border-top:7px solid transparent;"
                            f"border-bottom:7px solid transparent;"
                            f"border-left:18px solid {fi_color};"
                            f"transform:rotate({arrow_rotation:.1f}deg);"
                            f"filter:drop-shadow(0 1px 4px rgba(0,0,0,.65));'></div>"
                        ),
                        icon_size=(24, 24),
                        icon_anchor=(12, 12),
                    ),
                    tooltip=folium.Tooltip(route_tooltip_html),
                ).add_to(fg)

        for j, (coord, venue) in enumerate(zip(coords, venues)):
            if limit_by_country and grp.iloc[j]["country_code"] not in country_set:
                continue
            marker_coord = marker_positions[j] or coord
            visible_bounds.append([marker_coord[0], marker_coord[1]])
            folium.Marker(
                location=marker_coord,
                icon=folium.DivIcon(
                    html=(
                        f"<div style='width:42px;height:42px;border-radius:50%;"
                        f"background:{color};border:2px solid #e8f4fd;color:{pin_text_color};"
                        f"display:flex;flex-direction:column;align-items:center;justify-content:center;"
                        f"font-family:JetBrains Mono,monospace;font-weight:800;line-height:1;"
                        f"box-shadow:0 4px 12px rgba(0,0,0,.45)'>"
                        f"<span style='font-size:15px'>{j + 1}</span>"
                        f"<span style='font-size:8px;letter-spacing:.05em;margin-top:2px'>{team_code}</span>"
                        f"</div>"
                    ),
                    icon_size=(42, 42),
                    icon_anchor=(21, 21),
                ),
                tooltip=folium.Tooltip(
                    f"<b style='color:{color};font-size:15px'>{team_label(team)} ({team_code})</b>"
                    f"<br>Jogo {j+1}: {venue}"
                    f"<br><span style='color:#94b8d4'>{grp.iloc[j]['venue_name']}</span>"
                    f"<br><span style='color:#5d8ab5'>{kickoff_label(grp.iloc[j]['kickoff_at'])}</span>"
                ),
            ).add_to(fg)

        fg.add_to(m)

    if len(visible_bounds) >= 2:
        lats = [point[0] for point in visible_bounds]
        lons = [point[1] for point in visible_bounds]
        if math.isclose(min(lats), max(lats)) and math.isclose(min(lons), max(lons)):
            m.location = [lats[0], lons[0]]
            m.zoom_start = 7
        else:
            m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(35, 35), max_zoom=5)
    elif len(visible_bounds) == 1:
        m.location = visible_bounds[0]
        m.zoom_start = 7

    folium.LayerControl(collapsed=False).add_to(m)

    team_legend_items = []
    for team in sorted(selected_teams):
        team_rows = df_sched[df_sched["team"] == team]
        code = team_abbrev(team, team_rows.iloc[0].get("team_code", "") if len(team_rows) else "")
        color = team_color(team)
        text_color = readable_text_color(color)
        team_legend_items.append(
            f"<div class='team-legend-row'>"
            f"<span class='team-pin' style='background:{color};color:{text_color}'>{code}</span>"
            f"<span>{team_label(team)}</span>"
            f"</div>"
        )
    team_legend_html = "".join(team_legend_items)
    map_name = m.get_name()
    legend = f"""
    <style>
      #route-legend {{
        position:fixed;bottom:25px;left:25px;z-index:1000;
        border-radius:12px;padding:16px 18px;font-family:Space Grotesk,sans-serif;
        font-size:13px;min-width:300px;max-width:340px;max-height:55vh;overflow:auto;
        line-height:1.45;box-shadow:0 10px 28px rgba(0,0,0,.22);
      }}
      #route-legend.light {{
        background:rgba(248,250,252,.94);border:1px solid #cbd5e1;color:#334155;
      }}
      #route-legend.dark {{
        background:rgba(8,12,20,.95);border:1px solid #1e3a5f;color:#94b8d4;
      }}
      #route-legend .legend-title {{font-size:15px;font-weight:800;color:#0f172a}}
      #route-legend.dark .legend-title {{color:#e8f4fd}}
      #route-legend .legend-muted {{color:#475569}}
      #route-legend.dark .legend-muted {{color:#94b8d4}}
      #route-legend .legend-kicker {{
        color:#2563eb;font-size:11px;font-weight:800;letter-spacing:.08em;
      }}
      #route-legend.dark .legend-kicker {{color:#5d8ab5}}
      #route-legend hr {{border:0;border-top:1px solid rgba(100,116,139,.35);margin:8px 0}}
      #route-legend .team-legend-row {{
        display:flex;align-items:center;gap:8px;margin-top:6px;white-space:nowrap;
      }}
      #route-legend .team-pin {{
        width:30px;height:20px;border-radius:999px;display:inline-flex;align-items:center;
        justify-content:center;font-family:JetBrains Mono,monospace;font-size:10px;
        font-weight:900;border:1px solid rgba(255,255,255,.75);
        box-shadow:0 1px 5px rgba(0,0,0,.22);
      }}
      #route-legend .ifl-dot {{
        display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px;
      }}
    </style>
    <div id="route-legend" class="light">
      <div class="legend-title">Copa 2026 - Rotas de viagem</div>
      <hr>
      <span class="legend-muted">Seta na linha: sentido da viagem</span><br>
      <span class="legend-muted">Cor da linha: nivel de fadiga do trecho</span><br>
      <span class="legend-muted">Cor do pino: selecao</span>
      <hr>
      <div class="legend-kicker">PINOS POR SELECAO</div>
      {team_legend_html}
      <hr>
      <div class="legend-kicker">COR DA LINHA POR IFL</div>
      <span class="ifl-dot" style="background:#48bb78"></span>0-2.5 Baixo<br>
      <span class="ifl-dot" style="background:#f6c90e"></span>2.5-5 Moderado<br>
      <span class="ifl-dot" style="background:#f97316"></span>5-7.5 Alto<br>
      <span class="ifl-dot" style="background:#f87171"></span>Acima de 7.5 Critico
    </div>
    <script>
      setTimeout(function() {{
        var legend = document.getElementById("route-legend");
        var mapObj = {map_name};
        if (!legend || !mapObj) return;
        mapObj.on("baselayerchange", function(e) {{
          if (e.name === "Mapa escuro") {{
            legend.classList.remove("light");
            legend.classList.add("dark");
          }} else {{
            legend.classList.remove("dark");
            legend.classList.add("light");
          }}
        }});
      }}, 400);
    </script>
    """
    m.get_root().html.add_child(folium.Element(legend))
    return m


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY ROUTE MAP
# ─────────────────────────────────────────────────────────────────────────────

def build_plotly_map(selected_teams: list[str], detail: pd.DataFrame, country_codes: tuple[str, ...]) -> go.Figure:
    fig = go.Figure()
    df_s = load_schedule_df()
    country_set = set(country_codes)
    all_country_codes = set(HOST_COUNTRY_LABELS)
    limit_by_country = bool(country_set) and country_set != all_country_codes

    for team in sorted(selected_teams):
        grp = df_s[df_s["team"] == team].sort_values("match")
        if limit_by_country:
            grp = grp[grp["country_code"].isin(country_set)]
        if grp.empty:
            continue
        color = team_color(team)
        lats  = [STADIUMS[v]["lat"] for v in grp["venue"]]
        lons  = [STADIUMS[v]["lon"] for v in grp["venue"]]
        td    = detail[detail["team"] == team].sort_values("match")

        texts = []
        for i, row in grp.iterrows():
            r   = td[td["match"] == row["match"]]
            km  = int(r["km_traveled"].values[0]) if len(r) else 0
            fi  = float(r["fatigue_index"].values[0]) if len(r) else 0
            texts.append(
                f"{team_label(team)}<br>"
                f"Jogo {int(row['match'])}: {row['venue']}<br>"
                f"{row['venue_name']}<br>"
                f"{kickoff_label(row['kickoff_at'])}<br>"
                f"{km:,} km | IFL {fi:.2f}"
            )

        fig.add_trace(go.Scattergeo(
            lat=lats, lon=lons,
            mode="lines+markers",
            line=dict(width=4, color=color),
            marker=dict(size=11, color=color, line=dict(width=2, color="#0e1a2e")),
            name=team_label(team),
            text=texts, hoverinfo="text",
        ))

    active_sched = df_s[df_s["country_code"].isin(country_set)] if limit_by_country else df_s
    active_venues = sorted(active_sched["venue"].dropna().unique())
    for name in active_venues:
        info = STADIUMS[name]
        fig.add_trace(go.Scattergeo(
            lat=[info["lat"]], lon=[info["lon"]],
            mode="text", text=[name],
            textfont=dict(size=10, color="#7fb0d8"),
            showlegend=False, hoverinfo="skip",
        ))

    lat_range = [14, 55]
    lon_range = [-138, -60]
    if country_set == {"MEX"}:
        lat_range = [14, 33]
        lon_range = [-118, -86]
    elif country_set == {"CAN"}:
        lat_range = [41, 56]
        lon_range = [-130, -68]
    elif country_set == {"USA"}:
        lat_range = [24, 50]
        lon_range = [-127, -66]

    fig.update_geos(
        scope="north america",
        showland=True, landcolor="#0e1a2e",
        showocean=True, oceancolor="#080c14",
        showlakes=True, lakecolor="#080c14",
        showcountries=True, countrycolor="#1e2d47",
        showcoastlines=True, coastlinecolor="#1e3a5f",
        bgcolor="#080c14",
        lataxis_range=lat_range,
        lonaxis_range=lon_range,
    )
    fig.update_layout(
        title=dict(
            text="Rotas de Voo — Copa do Mundo 2026 · Fase de Grupos",
            font=dict(size=15, color="#e8f4fd", family="Space Grotesk"),
            x=0.5,
        ),
        paper_bgcolor="#080c14",
        legend=dict(
            bgcolor="#0e1a2e", bordercolor="#1e3a5f", borderwidth=1,
            font=dict(color="#94b8d4", size=11, family="Space Grotesk"),
            x=1.0, y=0.5,
        ),
        height=540,
        margin=dict(l=0, r=180, t=60, b=0),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO BARRAS — MILHAS VOADAS
# ─────────────────────────────────────────────────────────────────────────────

def fig_miles_bar(summary: pd.DataFrame) -> plt.Figure:
    BG = "#080c14"
    fig, ax = plt.subplots(figsize=(14, 6.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    if len(summary) <= 10:
        combo = summary.sort_values("total_km", ascending=False).reset_index(drop=True)
        colors_bar = [team_color(team) for team in combo["team"]]
        split_chart = False
    else:
        top5 = summary.head(5)
        bot5 = summary.tail(5).sort_values("total_km")
        spacer = pd.DataFrame([{"team": "__", "total_km": 0, "total_ifl": 0, "flag": ""}])
        combo = pd.concat([top5, spacer, bot5], ignore_index=True)

        palette_top = ["#f87171", "#fb923c", "#fbbf24", "#fcd34d", "#fde68a"]
        palette_bot = ["#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#1e40af"]
        colors_bar = palette_top + ["#080c14"] + palette_bot
        split_chart = True

    x = np.arange(len(combo))
    bars = ax.bar(x, combo["total_km"], color=colors_bar, width=0.68,
                  zorder=3, edgecolor="#1e2d47", linewidth=0.8)

    for bar, row in zip(bars, combo.itertuples()):
        if row.total_km == 0:
            continue
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 40,
                f"{int(row.total_km):,} km",
                ha="center", va="bottom", fontsize=9.5, fontweight="700",
                color="#e8f4fd", fontfamily="DejaVu Sans")
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                f"IFL\n{getattr(row, 'total_ifl', 0):.1f}",
                ha="center", va="center", fontsize=8.5, fontweight="700",
                color="#0e1a2e")

    if split_chart:
        ax.axvline(4.5, color="#1e3a5f", linewidth=1.5, linestyle="--", zorder=4)
        ax.text(2.2, max(combo["total_km"]) * 0.96, "MAIS DESGASTE",
                ha="center", fontsize=8, color="#f87171", fontweight="700",
                fontfamily="DejaVu Sans", style="italic")
        ax.text(6.8, max(combo["total_km"]) * 0.96, "MENOS DESGASTE",
                ha="center", fontsize=8, color="#60a5fa", fontweight="700",
                fontfamily="DejaVu Sans", style="italic")

    labels = [
        team_label(row.team) if row.team != "__" else ""
        for row in combo.itertuples()
    ]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, color="#94b8d4", fontfamily="DejaVu Sans")
    ax.set_ylabel("Distancia percorrida (km)", color="#5d8ab5", fontsize=10)
    ax.set_title(
        "Milhas Voadas na Fase de Grupos — Copa do Mundo 2026",
        color="#e8f4fd", fontsize=14, fontweight="700", pad=14,
        fontfamily="DejaVu Sans",
    )
    ax.tick_params(colors="#5d8ab5")
    ax.spines[:].set_color("#1e2d47")
    ax.yaxis.grid(True, color="#0e1a2e", linestyle="--", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.yaxis.set_tick_params(labelcolor="#5d8ab5")

    if split_chart:
        p1 = mpatches.Patch(color="#f87171", label="Top 5 - Maior desgaste")
        p2 = mpatches.Patch(color="#60a5fa", label="Top 5 - Menor desgaste")
        ax.legend(handles=[p1, p2], loc="upper right",
                  facecolor="#0e1a2e", edgecolor="#1e3a5f",
                  labelcolor="#94b8d4", fontsize=9.5)

    fig.text(0.99, 0.01,
             "Fixture FIFA 2026 | Distancias: geopy geodesic | IFL normalizado em escala 0-10",
             ha="right", fontsize=7, color="#2e4a6f", style="italic")
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# HEATMAP DE FADIGA
# ─────────────────────────────────────────────────────────────────────────────

def fig_heatmap(detail: pd.DataFrame, summary: pd.DataFrame, crit_threshold: float = 7.5) -> plt.Figure:
    BG = "#080c14"
    ordered = list(summary.sort_values("total_km", ascending=False)["team"])
    all_days = sorted(detail["day"].unique())
    pivot = (
        detail.pivot(index="team", columns="day", values="fatigue_index")
        .reindex(ordered)
        .reindex(columns=all_days, fill_value=0)
        .fillna(0)
    )
    day_labels = [f"Dia {d}" for d in all_days]

    cmap = LinearSegmentedColormap.from_list(
        "fadiga_dark",
        ["#080c14", "#0a2e1a", "#48bb78", "#f6c90e", "#f97316", "#f87171", "#7f1d1d"],
        N=256,
    )

    fig_height = max(7.5, len(ordered) * 0.32)
    fig, ax = plt.subplots(figsize=(16, fig_height))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    sns.heatmap(
        pivot, ax=ax, cmap=cmap,
        linewidths=1.0, linecolor="#0e1a2e",
        annot=True, fmt=".1f",
        annot_kws={"size": 10, "weight": "bold", "color": "#e8f4fd"},
        vmin=0, vmax=10,
        cbar_kws={"label": "Indice de Fadiga Logistica (0-10)", "shrink": 0.55},
    )

    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color("#94b8d4")
    cbar.ax.yaxis.label.set_fontsize(9.5)
    cbar.ax.tick_params(colors="#94b8d4")

    ax.set_xticklabels(day_labels, rotation=40, ha="right", color="#94b8d4", fontsize=9.5)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, color="#e8f4fd", fontsize=11, fontweight="600")
    ax.set_xlabel("Dia do Torneio (desde 11 Jun 2026)", color="#5d8ab5", fontsize=10, labelpad=8)
    ax.set_ylabel("Selecao", color="#5d8ab5", fontsize=10, labelpad=8)
    ax.set_title(
        "Heatmap de Fadiga Logistica — Copa do Mundo 2026\n"
        "Fase de Grupos  ·  Distancia x Fuso Horario x Dias de Descanso",
        color="#e8f4fd", fontsize=13, fontweight="700", pad=14,
    )
    ax.tick_params(axis="both", length=0)

    for day_idx, day in enumerate(all_days):
        for team_idx, team in enumerate(ordered):
            row = detail[(detail["team"] == team) & (detail["day"] == day)]
            if len(row) and row["fatigue_index"].values[0] >= crit_threshold:
                ax.add_patch(plt.Rectangle(
                    (day_idx, team_idx), 1, 1,
                    fill=False, edgecolor="#f87171", linewidth=2.5, zorder=5,
                ))

    fig.text(0.5, -0.02,
             "IFL = (km / 500) x (1 + delta_fuso / 3) x (1 / dias_descanso)  "
             f"  |  Borda vermelha = IFL critico (>={crit_threshold:.1f})",
             ha="center", fontsize=8.5, color="#2e4a6f", style="italic")
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────────────────────────────────────

def sec(icon: str, label: str):
    st.markdown(
        f'<div class="sec-header"><span class="label">{label}</span></div>',
        unsafe_allow_html=True,
    )


def ifl_badge(fi: float) -> str:
    return (
        f'<span class="ifl-badge {ifl_class(fi)}">'
        f'{fi:.2f} — {ifl_label(fi)}</span>'
    )


def fig_to_bytes(fig: plt.Figure) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor="#080c14")
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    logo_uri = image_data_uri(LOGO_PATH)
    detail  = build_detail()
    summary = build_summary(detail)
    source_error = ""
    if "source_error" in detail.columns and not detail.empty:
        source_values = detail["source_error"].dropna()
        source_error = str(source_values.iloc[0]) if len(source_values) else ""
    team_count = int(detail["team"].nunique())
    fixture_count = (
        int(detail["match_number"].nunique())
        if "match_number" in detail.columns
        else int(detail["match"].nunique())
    )

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        logo_html = (
            f'<img class="sidebar-logo" src="{logo_uri}" alt="FIFA World Cup 2026 logo">'
            if logo_uri else ""
        )
        st.markdown(f"""
            <div style="padding:16px 0 8px">
              {logo_html}
              <div style="font-size:1.55rem;font-weight:700;color:#e8f4fd">Copa 2026</div>
              <div style="font-size:0.72rem;color:#5d8ab5;letter-spacing:.06em;margin-top:2px">
                ANALISE DE DESGASTE LOGISTICO
              </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Grupo da Copa</div>', unsafe_allow_html=True)
        group_options = sorted(detail["group"].dropna().unique().tolist())
        selected_groups = st.multiselect(
            "",
            group_options,
            default=group_options[:1],
            format_func=lambda g: f"Grupo {g}",
            label_visibility="collapsed",
        )
        if not selected_groups:
            selected_groups = group_options[:1]

        full_summary = build_summary(detail)
        max_ifl_total = 10.0
        st.markdown('<div class="sidebar-title" style="margin-top:16px">IFL total minimo</div>',
                    unsafe_allow_html=True)
        min_total_ifl = st.slider("", 0.0, max_ifl_total, 0.0, 0.1, label_visibility="collapsed")

        group_teams = detail[detail["group"].isin(selected_groups)][["team", "group"]].drop_duplicates()
        team_filter_base = group_teams.merge(full_summary[["team", "total_ifl"]], on="team", how="left")
        team_filter_base = team_filter_base[team_filter_base["total_ifl"] >= min_total_ifl]
        available_teams = sorted(team_filter_base["team"].unique().tolist())

        st.markdown('<div class="sidebar-title" style="margin-top:16px">Selecoes no recorte</div>',
                    unsafe_allow_html=True)
        selected = st.multiselect(
            "",
            available_teams,
            default=available_teams,
            format_func=team_label,
            label_visibility="collapsed",
        )
        if selected:
            team_code_lookup = (
                detail[["team", "team_code"]]
                .drop_duplicates()
                .set_index("team")["team_code"]
                .to_dict()
                if "team_code" in detail.columns
                else {}
            )
            sidebar_team_rows = []
            for team in selected:
                color = team_color(team)
                text_color = readable_text_color(color)
                code = team_abbrev(team, team_code_lookup.get(team, ""))
                sidebar_team_rows.append(
                    f"<div style='display:flex;align-items:center;gap:8px;margin:5px 0'>"
                    f"<span style='width:34px;height:20px;border-radius:999px;background:{color};"
                    f"color:{text_color};display:inline-flex;align-items:center;justify-content:center;"
                    f"font-family:JetBrains Mono,monospace;font-size:10px;font-weight:900;"
                    f"border:1px solid rgba(255,255,255,.65)'>{code}</span>"
                    f"<span style='color:#94b8d4;font-size:.84rem'>{team_label(team)}</span>"
                    f"</div>"
                )
            st.markdown(
                "<div style='margin:8px 0 2px;padding:10px 12px;border:1px solid #1e3a5f;"
                "border-radius:8px;background:#0b1628'>"
                "<div style='font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;"
                "font-weight:800;color:#5d8ab5;margin-bottom:6px'>Cores dos pinos no mapa</div>"
                + "".join(sidebar_team_rows)
                + "</div>",
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sidebar-title" style="margin-top:16px">Pais-sede dos jogos</div>',
                    unsafe_allow_html=True)
        country_values = set(detail["country_code"].dropna().unique().tolist())
        country_options = [c for c in ("USA", "MEX", "CAN") if c in country_values]
        selected_country_codes = st.multiselect(
            "",
            country_options,
            default=country_options,
            format_func=host_country_label,
            label_visibility="collapsed",
        )
        if not selected_country_codes:
            selected_country_codes = country_options

        st.markdown('<div class="sidebar-title" style="margin-top:16px">Camadas do mapa</div>',
                    unsafe_allow_html=True)
        map_layers_hidden = st.checkbox("Iniciar selecoes ocultas no Folium", value=False)

        st.markdown('<div class="sidebar-title" style="margin-top:16px">Limiar de trecho critico</div>',
                    unsafe_allow_html=True)
        crit_threshold = st.slider("", 0.0, 10.0, 7.5, 0.1, label_visibility="collapsed")

        st.markdown("---")
        st.markdown("""
            <div style="font-size:0.7rem;color:#2e4a6f;line-height:1.6">
              <b style="color:#3d5a7a">Indice de Fadiga Logistica</b><br>
              Escala atual: 0 a 10 normalizada<br>
              Descanso so vira penalidade quando fica abaixo de 6 dias.
              <br><br>
              Fonte: CSVs locais em data/<br>
              Distancias: geopy geodesic
            </div>
        """, unsafe_allow_html=True)
        st.latex(r"IFL_{raw}=(km/1000)\times1.5+(\Delta fuso\times2)+(\max(0,6-descanso)\times0.65)+altitude")
        st.latex(r"IFL_{0-10}=10\times\frac{IFL_{raw}-IFL_{min}}{IFL_{max}-IFL_{min}}")
        if source_error:
            st.warning(f"Usando fixture interna. Erro ao carregar CSVs: {source_error}")

    # ── HEADER ───────────────────────────────────────────────────────────────
    hero_logo = (
        f'<img class="hero-logo" src="{logo_uri}" alt="FIFA World Cup 2026 logo">'
        if logo_uri else ""
    )
    st.markdown(f"""
        <div class="hero-card">
          {hero_logo}
          <div>
          <div class="hero-title">
            Copa do Mundo 2026 · Analise de Desgaste Logistico
          </div>
          <div class="hero-sub">
            EUA · Canada · Mexico &nbsp;|&nbsp;
            Mapeamento de rotas, distancias e Indice de Fadiga Logistica (IFL)
            para {team_count} selecoes em {fixture_count} jogos da fase de grupos
          </div>
          </div>
        </div>
    """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab_kpi, tab_mapa, tab_bar, tab_heat, tab_detail, tab_data, tab_about = st.tabs([
        "Visao Geral",
        "Mapa de Rotas",
        "Milhas Voadas",
        "Heatmap de Fadiga",
        "Detalhes por Selecao",
        "Exportar Dados",
        "Sobre o IFL",
    ])

    map_detail = detail[detail["team"].isin(selected)]
    filt_detail = map_detail[map_detail["country_code"].isin(selected_country_codes)]
    filt_summary = build_summary(filt_detail, detail)
    visible_teams = sorted(filt_summary["team"].unique().tolist())

    if filt_detail.empty or filt_summary.empty:
        st.warning("Nenhuma selecao ou jogo encontrado com os filtros atuais.")
        return

    # ─── TAB 1: VISAO GERAL ──────────────────────────────────────────────────
    with tab_kpi:
        sec("", "Indicadores Gerais")
        k1, k2, k3, k4, k5 = st.columns(5)

        with k1:
            st.metric("Selecoes analisadas", len(filt_summary))
        with k2:
            total_km = int(filt_summary["total_km"].sum())
            st.metric("Km totais percorridos", f"{total_km:,}".replace(",", "."))
        with k3:
            worst = filt_summary.iloc[0]
            st.metric(
                "Maior desgaste",
                f"{worst['total_ifl']:.1f}/10",
                delta=f"{team_label(worst['team'])} | {int(worst['total_km']):,} km".replace(",", "."),
            )
        with k4:
            best = filt_summary.iloc[-1]
            st.metric(
                "Menor desgaste",
                f"{best['total_ifl']:.1f}/10",
                delta=f"{team_label(best['team'])} | {int(best['total_km']):,} km".replace(",", "."),
            )
        with k5:
            crit_count = int((filt_detail["fatigue_index"] >= crit_threshold).sum())
            st.metric("Trechos criticos (IFL)", crit_count,
                      delta=f">= {crit_threshold}")

        st.markdown("<br>", unsafe_allow_html=True)
        sec("", "Ranking por Indice de Fadiga")

        cols_rank = st.columns([0.05, 0.16, 0.24, 0.13, 0.14, 0.13, 0.15])
        headers = ["#", "Selecao", "Rota", "Total (km)", "IFL Total", "IFL Pico", "Media Descanso"]
        for col, h in zip(cols_rank, headers):
            col.markdown(
                f"<div style='font-size:0.68rem;font-weight:700;letter-spacing:.1em;"
                f"text-transform:uppercase;color:#5d8ab5;padding-bottom:6px;"
                f"border-bottom:1px solid #1e2d47'>{h}</div>",
                unsafe_allow_html=True,
            )

        for _, row in filt_summary.iterrows():
            c1, c2, c_route, c3, c4, c5, c6 = st.columns([0.05, 0.16, 0.24, 0.13, 0.14, 0.13, 0.15])
            rank_color = "#f6c90e" if row["rank"] == 1 else ("#94b8d4" if row["rank"] == 2 else "#94b8d4")
            c1.markdown(f"<span style='font-family:JetBrains Mono;font-size:0.85rem;color:{rank_color}'>{row['rank']}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='font-size:1rem;font-weight:600;color:#e8f4fd'>{team_label(row['team'])}</span>", unsafe_allow_html=True)
            c_route.markdown(f"<span style='font-size:0.84rem;color:#94b8d4'>{row['route']}</span>", unsafe_allow_html=True)
            c3.markdown(f"<span style='font-family:JetBrains Mono;color:#e8f4fd'>{int(row['total_km']):,}</span>", unsafe_allow_html=True)
            c4.markdown(ifl_badge(row["total_ifl"]), unsafe_allow_html=True)
            c5.markdown(ifl_badge(row["peak_ifl"]), unsafe_allow_html=True)
            c6.markdown(f"<span style='font-family:JetBrains Mono;color:#94b8d4'>{row['avg_rest_days']:.1f} dias</span>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        sec("", "Distribuicao do IFL por selecao")
        fig_scatter = px.bar(
            filt_summary.sort_values("total_ifl", ascending=True),
            x="total_ifl", y="team",
            orientation="h",
            color="total_ifl",
            color_continuous_scale="RdYlGn_r",
            labels={"total_ifl": "IFL Total (0-10)", "team": "Selecao", "peak_ifl": "IFL Pico"},
            template=PLOTLY_TEMPLATE,
            text="total_ifl",
            hover_data={
                "peak_ifl": ":.2f",
                "total_km": ":,.0f",
                "route": True,
                "total_ifl": ":.2f",
            },
        )
        fig_scatter.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_scatter.update_layout(
            paper_bgcolor="#080c14", plot_bgcolor="#080c14",
            height=380,
            coloraxis_colorbar=dict(
    tickcolor="#94b8d4",
    tickfont=dict(color="#94b8d4"),         
    title=dict(font=dict(color="#94b8d4"))  
),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab_about:
        sec("", "O que e o Indice de Fadiga Logistica")
        st.markdown(
            """
            <div style="border:1px solid #1e3a5f;border-radius:8px;padding:18px 20px;
                        background:#0b1628;color:#c9d1d9;font-size:1rem;line-height:1.65">
              <b style="color:#e8f4fd">IFL</b> e uma nota de 0 a 10 que resume o desgaste logistico
              acumulado por cada selecao na fase de grupos. Ele combina distancia percorrida, mudanca de fuso,
              intervalo de descanso e efeito de altitude. Quanto maior a nota, maior tende a ser a pressao
              sobre recuperacao, rotina de treino, sono e preparacao para o jogo seguinte.
            </div>
            """,
            unsafe_allow_html=True,
        )

        about_worst = filt_summary.iloc[0]
        about_best = filt_summary.iloc[-1]
        avg_ifl = float(filt_summary["total_ifl"].mean())
        crit_segments_df = filt_detail[filt_detail["fatigue_index"] >= crit_threshold]
        peak_segment = filt_detail.sort_values("fatigue_index", ascending=False).iloc[0]
        peak_team = team_label(peak_segment["team"])
        previous_match = filt_detail[
            (filt_detail["team"] == peak_segment["team"])
            & (filt_detail["match"] == peak_segment["match"] - 1)
        ]
        if len(previous_match):
            peak_route = f"{previous_match.iloc[0]['venue']} -> {peak_segment['venue']}"
        else:
            peak_route = f"Jogo {int(peak_segment['match'])}: {peak_segment['venue']}"
        peak_km_label = f"{int(peak_segment['km_traveled']):,}".replace(",", ".")

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("IFL medio do recorte", f"{avg_ifl:.2f}/10")
        with m2:
            st.metric("Maior desgaste", f"{about_worst['total_ifl']:.2f}/10", delta=team_label(about_worst["team"]))
        with m3:
            st.metric("Trechos criticos", len(crit_segments_df), delta=f">= {crit_threshold:.1f}")
        with m4:
            st.metric("Trecho mais pesado", f"{peak_segment['fatigue_index']:.2f}/10", delta=peak_team)

        st.markdown("<br>", unsafe_allow_html=True)
        sec("", "Como a escala deve ser lida")
        scale_cols = st.columns(4)
        scale_items = [
            ("0 a 2.5", "Baixo", "#48bb78", "Deslocamento controlado, com baixo impacto logistico relativo."),
            ("2.5 a 5.0", "Moderado", "#f6c90e", "Viagem relevante, mas ainda administravel com boa recuperacao."),
            ("5.0 a 7.5", "Alto", "#f97316", "Pressao clara sobre descanso, adaptacao e planejamento operacional."),
            ("7.5 a 10", "Critico", "#f87171", "Trecho ou campanha que exige atencao prioritaria da comissao tecnica."),
        ]
        for col, (rng, label, color, desc) in zip(scale_cols, scale_items):
            col.markdown(
                f"""
                <div style="border:1px solid #1e3a5f;border-radius:8px;padding:14px 15px;
                            background:#0e1a2e;min-height:142px">
                  <div style="font-family:JetBrains Mono;color:{color};font-weight:700;font-size:1.1rem">{rng}</div>
                  <div style="color:#e8f4fd;font-weight:700;margin-top:6px">{label}</div>
                  <div style="color:#94b8d4;font-size:.9rem;line-height:1.45;margin-top:8px">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        sec("", "Formula aplicada")
        formula_cols = st.columns([0.56, 0.44])
        with formula_cols[0]:
            st.latex(r"IFL_{raw}=(km/1000)\times1.5+(\Delta fuso\times2)+(\max(0,6-descanso)\times0.65)+altitude")
            st.latex(r"IFL_{0-10}=10\times\frac{IFL_{raw}-IFL_{min}}{IFL_{max}-IFL_{min}}")
        with formula_cols[1]:
            st.markdown(
                """
                <div style="border-left:3px solid #60a5fa;padding-left:14px;color:#94b8d4;line-height:1.55">
                  A nota final e normalizada para comparar selecoes dentro da mesma base.
                  Distancia e fuso aumentam o desgaste. Descanso abaixo de 6 dias adiciona pressao.
                  Altitude entra como fator extra em sedes acima de 500 metros.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        sec("", "Insights que esta analise revela")
        insight_cols = st.columns(3)
        insights = [
            (
                "Risco de recuperacao",
                f"Mostra quais selecoes chegam ao proximo jogo com maior pressao fisica. No recorte atual, "
                f"{team_label(about_worst['team'])} lidera o desgaste com IFL {about_worst['total_ifl']:.2f}/10.",
            ),
            (
                "Trechos que explicam o ranking",
                f"O trecho mais pesado do recorte e {peak_route}, de {peak_team}, com "
                f"{peak_km_label} km, {int(peak_segment['tz_delta'])}h de fuso e "
                f"IFL {peak_segment['fatigue_index']:.2f}/10.",
            ),
            (
                "Vantagem logistica",
                f"Tambem identifica quem tem caminho mais leve. No recorte atual, "
                f"{team_label(about_best['team'])} aparece com IFL {about_best['total_ifl']:.2f}/10.",
            ),
            (
                "Planejamento de treino",
                "Ajuda a decidir onde reduzir carga, antecipar deslocamentos, ajustar sono e preservar atletas-chave.",
            ),
            (
                "Comparacao entre grupos",
                "Permite comparar se um grupo tem calendario mais desgastante que outro, mesmo antes de analisar desempenho tecnico.",
            ),
            (
                "Storytelling para decisao",
                "Transforma quilometros, fuso e descanso em uma leitura simples para scouts, analistas e comissao tecnica.",
            ),
        ]
        for idx, (title, text) in enumerate(insights):
            insight_cols[idx % 3].markdown(
                f"""
                <div style="border:1px solid #1e3a5f;border-radius:8px;padding:15px 16px;
                            background:#0b1628;margin-bottom:14px;min-height:138px">
                  <div style="color:#e8f4fd;font-weight:700;margin-bottom:8px">{title}</div>
                  <div style="color:#94b8d4;font-size:.94rem;line-height:1.5">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ─── TAB 2: MAPA ─────────────────────────────────────────────────────────
    with tab_mapa:
        map_type = st.radio(
            "Tipo de mapa", ["Mapa Interativo", "Mapa Estatico"],
            horizontal=True,
        )
        map_groups = ", ".join([f"Grupo {g}" for g in selected_groups])
        map_countries = ", ".join([host_country_label(c) for c in selected_country_codes])
        route_segments = max(0, int(len(map_detail) - map_detail["team"].nunique()))
        st.markdown(
            f"""
            <div style="border:1px solid #1e3a5f;border-radius:8px;padding:12px 14px;
                        background:#0b1628;color:#94b8d4;margin:8px 0 14px;font-size:1rem">
              <b style="color:#e8f4fd">Recorte do mapa</b><br>
              {map_groups} | {len(selected)} selecoes | {route_segments} deslocamentos entre jogos<br>
              Pais-sede visivel: {map_countries} | IFL minimo por selecao: {min_total_ifl:.1f}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "Folium" in map_type:
            sec("", "Mapa Interativo de Rotas - Folium")
            st.caption("As rotas mostram origem, destino, distancia, descanso, variacao de fuso e IFL do trecho.")
            m = build_folium(tuple(selected), map_detail, tuple(selected_country_codes), map_layers_hidden)
            map_key = (
                f"folium-{IFL_MODEL_VERSION}-"
                f"{'-'.join(selected)}-{'-'.join(selected_country_codes)}-{map_layers_hidden}"
            )
            st_folium(m, width=None, height=580, returned_objects=[], key=map_key)
        else:
            sec("", "Mapa de Rotas - Plotly")
            fig_pm = build_plotly_map(selected, map_detail, tuple(selected_country_codes))
            st.plotly_chart(fig_pm, use_container_width=True)

    # ─── TAB 3: BARRAS ───────────────────────────────────────────────────────
    with tab_bar:
        sec("", "Comparativo de Distancias Percorridas")
        st.caption("Comparativo das selecoes visiveis no recorte atual de grupo, pais-sede e IFL.")
        fig_b = fig_miles_bar(filt_summary)
        st.pyplot(fig_b, use_container_width=True)

        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                "Baixar grafico (PNG)",
                data=fig_to_bytes(fig_b),
                file_name="milhas_voadas_copa2026.png",
                mime="image/png",
            )
        plt.close(fig_b)

    # ─── TAB 4: HEATMAP ──────────────────────────────────────────────────────
    with tab_heat:
        sec("", "Heatmap de Fadiga Logistica")
        st.caption(
            f"Escala de cor: verde = baixo · amarelo = moderado · vermelho = alto. "
            f"**Borda vermelha** = IFL >= {crit_threshold} (limiar critico)."
        )
        fig_h = fig_heatmap(filt_detail, filt_summary, crit_threshold)
        st.pyplot(fig_h, use_container_width=True)

        col_dl2, _ = st.columns([1, 3])
        with col_dl2:
            st.download_button(
                "Baixar heatmap (PNG)",
                data=fig_to_bytes(fig_h),
                file_name="heatmap_fadiga_copa2026.png",
                mime="image/png",
            )
        plt.close(fig_h)

    # ─── TAB 5: DETALHES POR SELECAO ─────────────────────────────────────────
    with tab_detail:
        sec("", "Deep-Dive por Selecao")
        team_choice = st.selectbox(
            "Escolha uma selecao",
            visible_teams,
            format_func=team_label,
        )

        td = filt_detail[filt_detail["team"] == team_choice].sort_values("match")
        ts = filt_summary[filt_summary["team"] == team_choice].iloc[0]

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total percorrido", f"{int(ts['total_km']):,} km".replace(",", "."))
        with m2:
            st.metric("IFL total", f"{ts['total_ifl']:.2f}/10")
        with m3:
            st.metric("IFL pico", f"{ts['peak_ifl']:.2f}")
        with m4:
            st.metric("Descanso medio", f"{ts['avg_rest_days']:.1f} dias")

        st.markdown("<br>", unsafe_allow_html=True)
        sec("", "Trajeto Jogo a Jogo")

        for _, row in td.iterrows():
            prev = td[td["match"] == row["match"] - 1]
            arrow = ""
            if len(prev):
                arrow = f"&nbsp; ← &nbsp; **{prev.iloc[0]['venue']}**"
            fi = row["fatigue_index"]
            km = row["km_traveled"]
            rest = row["rest_days"]

            with st.container():
                cols = st.columns([0.08, 0.3, 0.25, 0.18, 0.19])
                cols[0].markdown(
                    f"<div style='background:#1e3a5f;border-radius:50%;width:32px;height:32px;"
                    f"display:flex;align-items:center;justify-content:center;"
                    f"font-weight:700;color:#e8f4fd;font-size:0.85rem'>"
                    f"{int(row['match'])}</div>",
                    unsafe_allow_html=True,
                )
                cols[1].markdown(
                    f"<span style='font-size:0.95rem;font-weight:600;color:#e8f4fd'>"
                    f"{row['venue']}</span><br>"
                    f"<span style='font-size:0.75rem;color:#5d8ab5'>"
                    f"{row['stadium']} · Dia {row['day']} · Fuso {row['tz']}</span>",
                    unsafe_allow_html=True,
                )
                cols[2].markdown(
                    f"<span style='font-size:0.78rem;color:#5d8ab5'>Viagem</span><br>"
                    f"<span style='font-family:JetBrains Mono;color:#94b8d4'>"
                    f"{'—' if km == 0 else f'{km:,} km'}</span>",
                    unsafe_allow_html=True,
                )
                cols[3].markdown(
                    f"<span style='font-size:0.78rem;color:#5d8ab5'>Descanso</span><br>"
                    f"<span style='font-family:JetBrains Mono;color:#94b8d4'>"
                    f"{'—' if rest == 0 else f'{rest} dias'}</span>",
                    unsafe_allow_html=True,
                )
                cols[4].markdown(ifl_badge(fi), unsafe_allow_html=True)

            if row["match"] < td["match"].max():
                st.markdown(
                    "<div style='border-left:2px dashed #1e3a5f;margin-left:16px;"
                    "height:18px'></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        sec("", "Evolucao do IFL")
        fig_line = px.line(
            td[td["match"] > 1],
            x="match", y="fatigue_index",
            markers=True,
            labels={"match": "Jogo", "fatigue_index": "IFL"},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=[team_color(team_choice)],
        )
        fig_line.update_traces(marker=dict(size=10, line=dict(width=2, color="#0e1a2e")))
        fig_line.update_layout(
            paper_bgcolor="#080c14", plot_bgcolor="#080c14", height=260,
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # ─── TAB 6: EXPORTAR ─────────────────────────────────────────────────────
    with tab_data:
        sec("", "Exportar Dados")

        st.markdown("#### Detalhes por trecho")
        cols_exp = [
            c for c in [
                "team", "team_code", "group", "match", "match_number", "match_label",
                "kickoff_at", "day", "venue", "country", "country_code", "stadium", "tz",
                "km_traveled", "tz_delta", "rest_days", "altitude_m", "altitude_factor",
                "fatigue_raw", "fatigue_index", "ifl_label",
            ]
            if c in filt_detail.columns
        ]
        st.dataframe(
            filt_detail[cols_exp].style
            .background_gradient(subset=["fatigue_index"], cmap="RdYlGn_r", vmin=0, vmax=10)
            .format({"fatigue_raw": "{:.3f}", "fatigue_index": "{:.2f}", "km_traveled": "{:,}"})
            .set_properties(**{"background-color": "#0e1a2e", "color": "#c9d1d9"}),
            use_container_width=True, hide_index=True,
        )

        st.markdown("#### Resumo por selecao")
        sum_display = filt_summary.drop(columns=["color", "total_ifl_raw"], errors="ignore")
        st.dataframe(
            sum_display.style
            .background_gradient(subset=["total_km"], cmap="Blues")
            .background_gradient(subset=["peak_ifl"], cmap="RdYlGn_r", vmin=0, vmax=10)
            .format({"total_km": "{:,.0f}", "total_ifl": "{:.3f}", "peak_ifl": "{:.3f}",
                     "avg_rest_days": "{:.1f}"}),
            use_container_width=True, hide_index=True,
        )

        catalog = load_matches_catalog()
        if not catalog.empty:
            st.markdown("#### Agenda completa da base")
            st.dataframe(catalog, use_container_width=True, hide_index=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "Baixar detalhes (CSV)",
                filt_detail[cols_exp].to_csv(index=False).encode("utf-8"),
                "copa2026_detalhe_fadiga.csv", "text/csv",
            )
        with c2:
            st.download_button(
                "Baixar resumo (CSV)",
                sum_display.to_csv(index=False).encode("utf-8"),
                "copa2026_resumo_selecoes.csv", "text/csv",
            )
        with c3:
            if not catalog.empty:
                st.download_button(
                    "Baixar agenda completa (CSV)",
                    catalog.to_csv(index=False).encode("utf-8"),
                    "copa2026_agenda_completa.csv", "text/csv",
                )


if __name__ == "__main__":
    main()
