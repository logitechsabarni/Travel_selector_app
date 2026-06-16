import streamlit as st
import json
import re
import time
import random
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Optional AI imports — gracefully degrade if missing
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoyageAI — Smart Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500&display=swap');

:root {
  --ink: #0a0a0f;
  --surface: #111118;
  --card: #16161f;
  --border: #2a2a3a;
  --accent: #7c6bff;
  --accent2: #ff6b9d;
  --accent3: #00d4aa;
  --text: #e8e8f0;
  --muted: #7070a0;
  --train: #ffd166;
  --bus: #06d6a0;
  --flight: #118ab2;
  --gold: #f4a261;
  --warn: #ff6b35;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: var(--ink) !important; font-family: 'Inter', sans-serif; color: var(--text); }

/* ── Hero ── */
.hero { text-align: center; padding: 3.5rem 2rem 2rem; position: relative; overflow: hidden; }
.hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(124,107,255,0.18) 0%, transparent 70%); pointer-events: none; }
.hero-eyebrow { font-family: 'Space Grotesk', sans-serif; font-size: 0.75rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.9rem; animation: fadeDown 0.7s ease both; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: clamp(2.4rem, 5vw, 3.8rem); font-weight: 700; line-height: 1.1; color: var(--text); animation: fadeDown 0.8s 0.1s ease both; }
.hero-title span { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1rem; color: var(--muted); margin-top: 0.8rem; font-weight: 300; animation: fadeDown 0.9s 0.2s ease both; }

/* ── Steps bar ── */
.steps-bar { display: flex; justify-content: center; gap: 0; margin: 2rem auto 2.5rem; max-width: 640px; }
.step-item { display: flex; flex-direction: column; align-items: center; flex: 1; position: relative; }
.step-item:not(:last-child)::after { content: ''; position: absolute; top: 15px; left: 55%; right: -45%; height: 2px; background: var(--border); }
.step-item.done:not(:last-child)::after, .step-item.active:not(:last-child)::after { background: linear-gradient(90deg, var(--accent), var(--border)); }
.step-dot { width: 30px; height: 30px; border-radius: 50%; border: 2px solid var(--border); background: var(--surface); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 600; color: var(--muted); transition: all 0.4s ease; font-family: 'Space Grotesk', sans-serif; }
.step-item.done .step-dot { background: var(--accent); border-color: var(--accent); color: white; }
.step-item.active .step-dot { background: linear-gradient(135deg, var(--accent), var(--accent2)); border-color: var(--accent); color: white; box-shadow: 0 0 16px rgba(124,107,255,0.5); animation: pulse-dot 2s infinite; }
.step-label { font-size: 0.62rem; margin-top: 6px; color: var(--muted); font-family: 'Space Grotesk', sans-serif; }
.step-item.active .step-label, .step-item.done .step-label { color: var(--accent); }

/* ── Cards ── */
.glass-card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 1.8rem; margin-bottom: 1.2rem; animation: slideUp 0.5s ease both; transition: border-color 0.3s; }
.glass-card:hover { border-color: rgba(124,107,255,0.3); }
.section-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: var(--text); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }

/* ── Transport Cards ── */
.transport-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; margin-top: 1rem; }
.transport-card { background: var(--surface); border: 1.5px solid var(--border); border-radius: 14px; padding: 1.3rem; cursor: pointer; transition: all 0.3s ease; position: relative; overflow: hidden; animation: slideUp 0.5s ease both; }
.transport-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.transport-card.train::before { background: var(--train); }
.transport-card.bus::before { background: var(--bus); }
.transport-card.flight::before { background: var(--flight); }
.transport-card:hover { border-color: var(--accent); transform: translateY(-3px); box-shadow: 0 12px 32px rgba(124,107,255,0.15); }
.transport-card.selected { border-color: var(--accent); background: rgba(124,107,255,0.08); box-shadow: 0 0 0 3px rgba(124,107,255,0.2); }
.tc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.8rem; }
.tc-type { font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 600; font-family: 'Space Grotesk', sans-serif; }
.tc-type.train { color: var(--train); }
.tc-type.bus { color: var(--bus); }
.tc-type.flight { color: var(--flight); }
.tc-name { font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 600; margin-bottom: 0.4rem; }
.tc-route { font-size: 0.82rem; color: var(--muted); margin-bottom: 0.7rem; }
.tc-meta { display: flex; gap: 1rem; flex-wrap: wrap; }
.tc-meta-item { font-size: 0.78rem; color: var(--muted); }
.tc-meta-item strong { color: var(--text); font-weight: 500; }
.tc-price { font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700; color: var(--accent3); }
.tc-check { width: 22px; height: 22px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; opacity: 0; transition: opacity 0.3s; }
.transport-card.selected .tc-check { opacity: 1; }

/* ── Itinerary ── */
.day-block { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.3rem; margin-bottom: 0.9rem; animation: slideUp 0.5s ease both; }
.day-label { font-family: 'Space Grotesk', sans-serif; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem; }
.day-title { font-size: 1rem; font-weight: 600; margin-bottom: 0.8rem; }
.activity-list { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }
.activity-item { display: flex; align-items: flex-start; gap: 0.7rem; font-size: 0.85rem; color: var(--muted); padding: 0.5rem 0.7rem; border-radius: 8px; transition: background 0.2s; }
.activity-item:hover { background: rgba(124,107,255,0.06); color: var(--text); }
.activity-time { font-family: 'Space Grotesk', sans-serif; font-size: 0.7rem; font-weight: 600; color: var(--accent); min-width: 52px; }

/* ── Summary Banner ── */
.summary-banner { background: linear-gradient(135deg, rgba(124,107,255,0.12), rgba(255,107,157,0.08)); border: 1px solid rgba(124,107,255,0.3); border-radius: 16px; padding: 1.6rem; margin-bottom: 1.5rem; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem; }
.summary-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--text); }
.summary-key { font-size: 0.72rem; color: var(--muted); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── AI Bubble ── */
.ai-bubble { background: rgba(124,107,255,0.08); border: 1px solid rgba(124,107,255,0.2); border-radius: 0 14px 14px 14px; padding: 1.2rem 1.4rem; font-size: 0.88rem; line-height: 1.7; color: var(--text); position: relative; margin: 0.5rem 0 1.2rem; }
.ai-bubble::before { content: '✦ VoyageAI'; font-family: 'Space Grotesk', sans-serif; font-size: 0.68rem; letter-spacing: 0.1em; color: var(--accent); display: block; margin-bottom: 0.6rem; font-weight: 600; }

/* ── Hotel Cards ── */
.hotel-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; margin-top: 1rem; }
.hotel-card { background: var(--surface); border: 1.5px solid var(--border); border-radius: 14px; padding: 1.2rem; transition: all 0.3s; animation: slideUp 0.5s ease both; }
.hotel-card:hover { border-color: var(--gold); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(244,162,97,0.12); }
.hotel-stars { color: var(--gold); font-size: 0.85rem; margin-bottom: 0.3rem; }
.hotel-name { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.3rem; }
.hotel-price { font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--accent3); }
.hotel-tag { display: inline-block; background: rgba(244,162,97,0.1); border: 1px solid rgba(244,162,97,0.25); border-radius: 20px; padding: 0.15rem 0.6rem; font-size: 0.68rem; color: var(--gold); margin: 0.15rem; font-family: 'Space Grotesk'; }

/* ── Packing List ── */
.pack-section { margin-bottom: 1rem; }
.pack-title { font-family: 'Space Grotesk', sans-serif; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent2); margin-bottom: 0.5rem; }
.pack-item { display: flex; align-items: center; gap: 0.6rem; font-size: 0.84rem; color: var(--muted); padding: 0.35rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.pack-item:hover { color: var(--text); }

/* ── Budget ── */
.budget-stat { text-align: center; padding: 1rem; background: var(--surface); border-radius: 12px; border: 1px solid var(--border); }
.budget-val { font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700; }
.budget-lbl { font-size: 0.7rem; color: var(--muted); margin-top: 3px; text-transform: uppercase; letter-spacing: 0.07em; }

/* ── Weather ── */
.weather-card { background: linear-gradient(135deg, rgba(0,212,170,0.08), rgba(124,107,255,0.08)); border: 1px solid rgba(0,212,170,0.2); border-radius: 14px; padding: 1.2rem; display: flex; align-items: center; gap: 1.2rem; margin-bottom: 1rem; }
.weather-icon { font-size: 2.5rem; }
.weather-temp { font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; }
.weather-desc { font-size: 0.82rem; color: var(--muted); margin-top: 2px; }
.weather-meta { display: flex; gap: 0.8rem; margin-top: 0.4rem; flex-wrap: wrap; }
.weather-meta-item { font-size: 0.75rem; color: var(--muted); background: rgba(255,255,255,0.05); padding: 0.2rem 0.5rem; border-radius: 6px; }

/* ── Savings Tip ── */
.savings-pill { background: linear-gradient(135deg, rgba(0,212,170,0.1), rgba(0,212,170,0.05)); border: 1px solid rgba(0,212,170,0.25); border-radius: 10px; padding: 0.6rem 1rem; margin-bottom: 0.5rem; font-size: 0.82rem; color: var(--accent3); display: flex; gap: 0.5rem; align-items: flex-start; }

/* ── Booking Confirm ── */
.booking-confirm { background: linear-gradient(135deg, rgba(0,212,170,0.1), rgba(0,212,170,0.05)); border: 1px solid rgba(0,212,170,0.3); border-radius: 16px; padding: 2rem; text-align: center; animation: popIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both; }
.confirm-icon { font-size: 3rem; margin-bottom: 0.8rem; }
.confirm-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700; color: var(--accent3); margin-bottom: 0.4rem; }
.pnr-badge { display: inline-block; background: rgba(0,212,170,0.15); border: 1px solid rgba(0,212,170,0.3); border-radius: 8px; padding: 0.4rem 1rem; font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--accent3); letter-spacing: 0.12em; margin-top: 0.6rem; }

/* ── Attractions ── */
.attract-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.9rem; margin-top: 1rem; }
.attract-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; transition: all 0.3s; animation: slideUp 0.5s ease both; }
.attract-card:hover { border-color: rgba(124,107,255,0.4); transform: translateY(-2px); }
.attract-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
.attract-name { font-family: 'Space Grotesk', sans-serif; font-size: 0.88rem; font-weight: 600; margin-bottom: 0.3rem; }
.attract-dist { font-size: 0.72rem; color: var(--muted); }
.attract-rating { font-size: 0.72rem; color: var(--gold); }

/* ── Divider ── */
.fancy-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 1.5rem 0; }

/* ── Streamlit overrides ── */
.stTextArea textarea { background: var(--surface) !important; border: 1.5px solid var(--border) !important; border-radius: 12px !important; color: var(--text) !important; font-family: 'Inter', sans-serif !important; font-size: 0.92rem !important; padding: 1rem !important; resize: vertical !important; transition: border-color 0.3s !important; }
.stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(124,107,255,0.15) !important; }
.stTextInput input { background: var(--surface) !important; border: 1.5px solid var(--border) !important; border-radius: 10px !important; color: var(--text) !important; font-family: 'Inter', sans-serif !important; }
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(124,107,255,0.15) !important; }
label[data-testid="stWidgetLabel"] p { color: var(--muted) !important; font-size: 0.82rem !important; letter-spacing: 0.04em; }
.stButton button { background: linear-gradient(135deg, var(--accent), #9b6bff) !important; color: white !important; border: none !important; border-radius: 10px !important; font-family: 'Space Grotesk', sans-serif !important; font-weight: 600 !important; font-size: 0.9rem !important; padding: 0.65rem 1.6rem !important; transition: all 0.3s ease !important; letter-spacing: 0.03em !important; }
.stButton button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(124,107,255,0.35) !important; }
div[data-baseweb="select"] > div { background: var(--surface) !important; border-color: var(--border) !important; }
.stSlider [data-testid="stSlider"] { color: var(--accent) !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 10px; gap: 0; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; font-family: 'Space Grotesk', sans-serif !important; font-size: 0.82rem !important; }
.stTabs [aria-selected="true"] { background: rgba(124,107,255,0.15) !important; color: var(--accent) !important; border-radius: 8px; }

/* ── Loading ── */
.loading-ring { display: inline-block; width: 40px; height: 40px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.9s linear infinite; }
.loading-text { font-family: 'Space Grotesk', sans-serif; font-size: 0.85rem; color: var(--muted); margin-top: 0.8rem; }

/* ── Tag chips ── */
.tag { display: inline-block; background: rgba(124,107,255,0.12); border: 1px solid rgba(124,107,255,0.25); border-radius: 20px; padding: 0.2rem 0.7rem; font-size: 0.72rem; color: var(--accent); font-family: 'Space Grotesk', sans-serif; font-weight: 500; margin: 0.2rem; }

/* ── orbs ── */
.orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.07; animation: float 8s ease-in-out infinite; }
.orb1 { width: 500px; height: 500px; background: var(--accent); top: -200px; left: -100px; animation-delay: 0s; }
.orb2 { width: 400px; height: 400px; background: var(--accent2); bottom: -100px; right: -80px; animation-delay: 3s; }
.orb3 { width: 300px; height: 300px; background: var(--accent3); top: 50%; left: 50%; transform: translate(-50%,-50%); animation-delay: 6s; }

/* ── Animations ── */
@keyframes fadeDown { from { opacity: 0; transform: translateY(-16px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse-dot { 0%, 100% { box-shadow: 0 0 16px rgba(124,107,255,0.5); } 50% { box-shadow: 0 0 28px rgba(124,107,255,0.8); } }
@keyframes popIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
</style>

<div class="orbs">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>
</div>
""", unsafe_allow_html=True)


# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk, Inter, sans-serif", color="#e8e8f0", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    showlegend=True,
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)


# ─── STATE ────────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "step": 1,
        "tour_desc": "",
        "ai_analysis": None,
        "transport_options": [],
        "selected_transport": None,
        "itinerary": None,
        "hotels": [],
        "packing_list": {},
        "budget_breakdown": {},
        "attractions": [],
        "weather": {},
        "booked": False,
        "pnr": None,
        "gemini_key": "",
        "extra_budget": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── LLM HELPERS ─────────────────────────────────────────────────────────────
def get_llm():
    if not LANGCHAIN_AVAILABLE:
        return None
    key = st.session_state.get("gemini_key", "").strip()
    if not key:
        return None
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=key, temperature=0.7)


def _llm_json(system_msg, user_content):
    """Generic LLM call that returns parsed JSON or None."""
    llm = get_llm()
    if not llm:
        return None
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_msg),
        HumanMessage(content=user_content if isinstance(user_content, str) else json.dumps(user_content))
    ])
    try:
        result = (prompt | llm).invoke({})
        text = re.sub(r"```json|```", "", result.content.strip()).strip()
        return json.loads(text)
    except Exception:
        return None


def analyze_tour_with_ai(description: str):
    result = _llm_json(
        """You are VoyageAI, an expert Indian travel planner. Analyze the user's travel plan and return ONLY valid JSON:
{
  "origin": "city", "destination": "city",
  "travel_date": "YYYY-MM-DD", "return_date": "YYYY-MM-DD or null",
  "duration_days": number, "travelers": number,
  "budget": "low/medium/high",
  "interests": ["list"],
  "summary": "2-3 sentence friendly summary",
  "tips": ["tip1","tip2","tip3"],
  "season": "summer/monsoon/winter/spring",
  "trip_type": "leisure/adventure/cultural/family/solo/romantic"
}
Return ONLY the JSON.""",
        description
    )
    return result or _mock_analysis(description)


def fetch_transport_with_ai(analysis: dict):
    result = _llm_json(
        """You are a transport booking AI for Indian travel. Generate realistic transport options as a JSON array (4-6 items):
[{
  "id":"unique_id","type":"train/bus/flight","name":"service name","number":"number",
  "departure":"HH:MM","arrival":"HH:MM","duration":"Xh Ym","price_per_person":number,
  "class":"class name","seats_available":number,"amenities":["list"],"operator":"name","rating":4.1
}]
Return ONLY valid JSON array.""",
        analysis
    )
    return result or _mock_transport(analysis)


def generate_itinerary_with_ai(analysis: dict, transport: dict):
    result = _llm_json(
        """You are an expert Indian travel itinerary planner. Create a day-by-day itinerary as a JSON array:
[{"day":1,"title":"Day theme","activities":[{"time":"HH:MM","activity":"description","emoji":"emoji"}]}]
Keep activities realistic and location-specific. Return ONLY valid JSON array.""",
        {"trip": analysis, "transport": transport}
    )
    return result or _mock_itinerary(analysis)


def generate_hotels_with_ai(analysis: dict):
    result = _llm_json(
        """You are a hotel recommendation AI for Indian travel. Generate 4-6 hotel options as a JSON array:
[{
  "id":"h1","name":"Hotel Name","stars":4,"price_per_night":2500,
  "locality":"area name","rating":4.2,"review_count":1240,
  "amenities":["WiFi","Pool","AC"],"type":"budget/mid-range/luxury",
  "highlights":"one line selling point"
}]
Return ONLY valid JSON array.""",
        analysis
    )
    return result or _mock_hotels(analysis)


def generate_packing_list_with_ai(analysis: dict):
    result = _llm_json(
        """You are a travel packing expert. Generate a context-aware packing list as JSON:
{
  "Essentials": ["item1","item2"],
  "Clothing": ["item1","item2"],
  "Toiletries": ["item1","item2"],
  "Electronics": ["item1","item2"],
  "Documents": ["item1","item2"],
  "Destination-Specific": ["item1","item2"]
}
Return ONLY valid JSON.""",
        analysis
    )
    return result or _mock_packing(analysis)


def generate_budget_breakdown_with_ai(analysis: dict, transport: dict):
    pax = analysis.get("travelers", 1)
    days = analysis.get("duration_days", 5)
    transport_cost = transport.get("price_per_person", 0) * pax
    result = _llm_json(
        f"""You are a travel budget estimator. Given a trip, estimate the total budget breakdown in INR as JSON:
{{
  "Transport": {transport_cost},
  "Accommodation": number,
  "Food & Dining": number,
  "Sightseeing": number,
  "Shopping": number,
  "Miscellaneous": number
}}
Base it on {pax} traveler(s), {days} days, {analysis.get("budget","medium")} budget level.
Transport is already set to {transport_cost}. Return ONLY valid JSON.""",
        analysis
    )
    return result or _mock_budget(analysis, transport_cost)


def generate_attractions_with_ai(analysis: dict):
    result = _llm_json(
        """Generate 6-8 must-visit attractions for the destination as a JSON array:
[{
  "name":"Attraction Name","emoji":"🏛️","type":"Heritage/Nature/Food/Adventure/Shopping/Beach",
  "distance_km":5.2,"rating":4.5,"entry_fee":"Free/₹200","timing":"9 AM–5 PM",
  "tip":"insider tip in one sentence"
}]
Return ONLY valid JSON array.""",
        analysis
    )
    return result or _mock_attractions(analysis)


def generate_weather_with_ai(analysis: dict):
    result = _llm_json(
        """Generate mock realistic weather data for the destination and travel season as JSON:
{
  "emoji":"☀️","temp_high":32,"temp_low":24,"condition":"Sunny with light breeze",
  "humidity":65,"rain_chance":10,"uv_index":7,
  "advice":"What to wear/carry","forecast":[
    {"day":"Mon","emoji":"☀️","high":32,"low":24},
    {"day":"Tue","emoji":"⛅","high":30,"low":23},
    {"day":"Wed","emoji":"🌧️","high":27,"low":22},
    {"day":"Thu","emoji":"☀️","high":33,"low":25},
    {"day":"Fri","emoji":"⛅","high":31,"low":24}
  ]
}
Return ONLY valid JSON.""",
        analysis
    )
    return result or _mock_weather(analysis)


# ─── MOCK DATA ────────────────────────────────────────────────────────────────
def _mock_analysis(desc):
    words = desc.lower()
    cities = ["Mumbai", "Delhi", "Kolkata", "Bengaluru", "Chennai", "Hyderabad", "Jaipur", "Goa", "Kerala"]
    dest = next((c for c in cities if c.lower() in words), "Goa")
    return {
        "origin": "Kolkata", "destination": dest,
        "travel_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "return_date": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
        "duration_days": 5, "travelers": 2, "budget": "medium",
        "interests": ["sightseeing", "food", "culture", "beaches"],
        "summary": f"An exciting 5-day trip from Kolkata to {dest} for 2 travelers, blending culture, cuisine, and memorable experiences.",
        "tips": ["Book tickets in advance during peak season", "Carry local currency for small vendors", "Try authentic local street food"],
        "season": "winter", "trip_type": "romantic"
    }


def _mock_transport(analysis):
    return [
        {"id":"t1","type":"train","name":"Gitanjali Express","number":"12859","departure":"14:05","arrival":"08:35+1","duration":"18h 30m","price_per_person":1450,"class":"3A AC","seats_available":12,"amenities":["Pantry Car","Bedding","Charging Points"],"operator":"Indian Railways","rating":4.2},
        {"id":"t2","type":"train","name":"Howrah Goa Express","number":"22887","departure":"22:00","arrival":"16:30+1","duration":"18h 30m","price_per_person":890,"class":"Sleeper","seats_available":28,"amenities":["Pantry Car","Charging Points"],"operator":"Indian Railways","rating":3.8},
        {"id":"f1","type":"flight","name":"IndiGo","number":"6E-401","departure":"06:30","arrival":"09:00","duration":"2h 30m","price_per_person":6200,"class":"Economy","seats_available":45,"amenities":["Cabin Baggage 7kg","Meal on purchase"],"operator":"IndiGo Airlines","rating":4.1},
        {"id":"f2","type":"flight","name":"Air India","number":"AI-665","departure":"10:15","arrival":"12:45","duration":"2h 30m","price_per_person":7800,"class":"Economy Flex","seats_available":18,"amenities":["Free Meal","Cabin Baggage 7kg","Check-in 15kg"],"operator":"Air India","rating":4.4},
        {"id":"b1","type":"bus","name":"VRL Travels AC Sleeper","number":"VRL-902","departure":"19:00","arrival":"13:00+1","duration":"18h 00m","price_per_person":1100,"class":"AC Sleeper","seats_available":6,"amenities":["WiFi","Charging","Blanket","Water Bottle"],"operator":"VRL Travels","rating":4.0},
        {"id":"b2","type":"bus","name":"Paulo Travels Deluxe","number":"PT-210","departure":"20:30","arrival":"14:30+1","duration":"18h 00m","price_per_person":850,"class":"Semi-Sleeper AC","seats_available":15,"amenities":["Charging","Water Bottle"],"operator":"Paulo Travels","rating":3.7},
    ]


def _mock_itinerary(analysis):
    days = analysis.get("duration_days", 5)
    plans = [
        ("Arrival & Settle In", [("14:00","Check in to hotel","🏨"),("16:00","Freshen up & local walk","🚶"),("19:00","Sunset at the beach","🌅"),("21:00","Welcome dinner at local restaurant","🍽️")]),
        ("Explore the City", [("08:00","Morning breakfast","☕"),("09:30","Visit famous monuments","🏛️"),("12:30","Lunch at local dhaba","🍛"),("14:30","Shopping at local market","🛍️"),("17:00","Cultural show","🎭"),("20:00","Rooftop dinner","🌃")]),
        ("Day Trips & Adventures", [("07:00","Early morning excursion","🌄"),("09:00","Scenic viewpoint","📷"),("12:00","Picnic lunch","🧺"),("15:00","Water sports","🏄"),("18:30","Return to hotel","🏨"),("20:30","BBQ dinner","🔥")]),
        ("Leisure & Local Culture", [("09:00","Breakfast & relaxation","☕"),("11:00","Local cooking class","👨‍🍳"),("13:30","Lunch","🍽️"),("15:00","Spa session","💆"),("17:30","Evening beach walk","🏖️"),("20:00","Night market","🌙")]),
        ("Departure Day", [("08:00","Final breakfast","☕"),("09:30","Last-minute sightseeing","📸"),("11:30","Souvenir shopping","🎁"),("13:00","Check out from hotel","🏨"),("15:00","Head to station/airport","🚉"),("17:00","Depart with memories","✈️")]),
    ]
    return [{"day": i+1, "title": t, "activities": [{"time": tm, "activity": a, "emoji": e} for tm, a, e in acts]}
            for i, (t, acts) in enumerate(plans[:days])]


def _mock_hotels(analysis):
    dest = analysis.get("destination", "Goa")
    return [
        {"id":"h1","name":f"Grand Radiance {dest}","stars":5,"price_per_night":8500,"locality":"City Centre","rating":4.7,"review_count":2341,"amenities":["Pool","Spa","Gym","Free WiFi","Restaurant"],"type":"luxury","highlights":"Panoramic city views & rooftop bar"},
        {"id":"h2","name":"The Heritage Palace","stars":4,"price_per_night":4200,"locality":"Old Quarter","rating":4.4,"review_count":1820,"amenities":["Pool","Free WiFi","Breakfast Included","AC"],"type":"mid-range","highlights":"Heritage property with colonial charm"},
        {"id":"h3","name":"Comfort Suites Express","stars":3,"price_per_night":2100,"locality":"Station Area","rating":4.1,"review_count":987,"amenities":["Free WiFi","AC","Hot Water","TV"],"type":"mid-range","highlights":"Great value, 5 min from station"},
        {"id":"h4","name":"Backpacker's Haven","stars":2,"price_per_night":800,"locality":"Backpacker Lane","rating":4.0,"review_count":654,"amenities":["Free WiFi","Common Kitchen","Lockers"],"type":"budget","highlights":"Social atmosphere, meet fellow travellers"},
    ]


def _mock_packing(analysis):
    dest = analysis.get("destination", "Goa")
    season = analysis.get("season", "winter")
    return {
        "Essentials": ["Valid ID / Aadhaar Card", "Travel tickets & bookings", "Cash & cards", "Travel insurance", "Phone + charger"],
        "Clothing": ["Light cotton shirts (3-4)", "Comfortable trousers/shorts", "Swimwear", "Light jacket/shawl for evenings", "Comfortable walking shoes", "Flip flops / sandals"],
        "Toiletries": ["Sunscreen SPF 50+", "Insect repellent", "Moisturiser", "Travel-size shampoo & soap", "Hand sanitiser"],
        "Electronics": ["Camera & memory cards", "Power bank (10000mAh+)", "Universal travel adapter", "Earphones / AirPods"],
        "Documents": ["E-tickets (downloaded offline)", "Hotel bookings", "Emergency contacts list", "Travel itinerary copy"],
        "Destination-Specific": [f"Beach bag for {dest} beaches", "Waterproof bag for valuables", "Reusable water bottle", "Snorkel gear (or rent locally)"]
    }


def _mock_budget(analysis, transport_cost):
    days = analysis.get("duration_days", 5)
    pax = analysis.get("travelers", 1)
    b = analysis.get("budget", "medium")
    mult = {"low": 0.6, "medium": 1.0, "high": 1.8}.get(b, 1.0)
    return {
        "Transport": int(transport_cost),
        "Accommodation": int(2500 * days * pax * mult),
        "Food & Dining": int(800 * days * pax * mult),
        "Sightseeing": int(500 * days * pax * mult),
        "Shopping": int(600 * days * pax * 0.5 * mult),
        "Miscellaneous": int(300 * days * pax * mult)
    }


def _mock_attractions(analysis):
    dest = analysis.get("destination", "Goa")
    return [
        {"name": "Old City Heritage Walk", "emoji": "🏛️", "type": "Heritage", "distance_km": 2.1, "rating": 4.6, "entry_fee": "Free", "timing": "All day", "tip": "Best explored in early morning to avoid crowds"},
        {"name": "Spice Plantation Tour", "emoji": "🌿", "type": "Nature", "distance_km": 18.5, "rating": 4.4, "entry_fee": "₹400", "timing": "9 AM–5 PM", "tip": "Includes lunch with authentic local cuisine"},
        {"name": "Local Food Street", "emoji": "🍛", "type": "Food", "distance_km": 0.8, "rating": 4.8, "entry_fee": "Free", "timing": "Evening 5–11 PM", "tip": "Must-try: local seafood & coconut sweets"},
        {"name": "Sunset Beach Point", "emoji": "🌅", "type": "Nature", "distance_km": 5.5, "rating": 4.9, "entry_fee": "Free", "timing": "Sunrise / Sunset", "tip": "Arrive 20 min early for the best spot"},
        {"name": "Water Sports Hub", "emoji": "🏄", "type": "Adventure", "distance_km": 7.2, "rating": 4.3, "entry_fee": "₹1500–3000", "timing": "8 AM–6 PM", "tip": "Book parasailing + jet ski combo for discount"},
        {"name": "Night Bazaar Market", "emoji": "🛍️", "type": "Shopping", "distance_km": 1.5, "rating": 4.2, "entry_fee": "Free", "timing": "Sat 6 PM–12 AM", "tip": "Bargain for handicrafts — first quote is always 2x"},
    ]


def _mock_weather(analysis):
    return {
        "emoji": "⛅", "temp_high": 30, "temp_low": 22, "condition": "Partly cloudy, pleasant breeze",
        "humidity": 72, "rain_chance": 20, "uv_index": 6,
        "advice": "Light cotton clothes recommended. Carry a small umbrella just in case.",
        "forecast": [
            {"day": "Mon", "emoji": "☀️", "high": 30, "low": 22},
            {"day": "Tue", "emoji": "⛅", "high": 29, "low": 21},
            {"day": "Wed", "emoji": "🌧️", "high": 26, "low": 20},
            {"day": "Thu", "emoji": "☀️", "high": 31, "low": 23},
            {"day": "Fri", "emoji": "⛅", "high": 30, "low": 22},
        ]
    }


def generate_pnr():
    return "VYG" + "".join([str(random.randint(0, 9)) for _ in range(8)])


# ─── CHART HELPERS ────────────────────────────────────────────────────────────
def budget_pie_chart(breakdown: dict):
    labels = list(breakdown.keys())
    values = list(breakdown.values())
    colors = ["#7c6bff", "#ff6b9d", "#00d4aa", "#ffd166", "#118ab2", "#06d6a0"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.52,
        marker=dict(colors=colors, line=dict(color="#0a0a0f", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="#e8e8f0"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
        annotations=[dict(text=f"₹{sum(values):,.0f}<br><span style='font-size:10px'>Total</span>",
                          showarrow=False, font=dict(size=14, color="#e8e8f0"), x=0.5, y=0.5)])
    return fig


def transport_comparison_chart(options: list, pax: int):
    names = [f"{o.get('name','')} ({o.get('type','').upper()[0]})" for o in options]
    prices = [o.get("price_per_person", 0) * pax for o in options]
    ratings = [o.get("rating", 0) for o in options]
    colors_map = {"train": "#ffd166", "bus": "#06d6a0", "flight": "#118ab2"}
    bar_colors = [colors_map.get(o.get("type", "train"), "#7c6bff") for o in options]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names, y=prices, name="Total Cost (₹)",
        marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0.2)", width=1)),
        hovertemplate="<b>%{x}</b><br>₹%{y:,}<extra></extra>",
        yaxis="y"
    ))
    fig.add_trace(go.Scatter(
        x=names, y=ratings, name="Rating",
        mode="lines+markers",
        line=dict(color="#ff6b9d", width=2),
        marker=dict(size=8, color="#ff6b9d"),
        hovertemplate="Rating: %{y}<extra></extra>",
        yaxis="y2"
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
        yaxis=dict(title="Total Cost (₹)", titlefont=dict(color="#7070a0"), tickfont=dict(color="#7070a0"), gridcolor="#2a2a3a"),
        yaxis2=dict(title="Rating", titlefont=dict(color="#ff6b9d"), tickfont=dict(color="#ff6b9d"), overlaying="y", side="right", range=[0, 5]),
        barmode="group", legend=dict(orientation="h", y=-0.2),
    )
    return fig


def weather_forecast_chart(forecast):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=forecast["date"],
            y=forecast["temp_max"],
            mode="lines+markers",
            name="Max Temp"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["date"],
            y=forecast["temp_min"],
            mode="lines+markers",
            name="Min Temp"
        )
    )

    # Apply base layout first
    fig.update_layout(**PLOTLY_LAYOUT)

    # Update axes separately
    fig.update_yaxes(
        gridcolor="#2a2a3a",
        ticksuffix="°C"
    )

    fig.update_xaxes(
        gridcolor="#1e1e2e"
    )

    # Final layout settings
    fig.update_layout(
        height=200,
        legend=dict(
            orientation="h",
            y=-0.3
        )
    )

    return fig
def rating_radar_chart(options: list):
    if not options:
        return None
    cats = ["Price Value", "Comfort", "Speed", "Availability", "Rating"]
    fig = go.Figure()
    colors = ["#7c6bff", "#00d4aa", "#ff6b9d", "#ffd166", "#118ab2", "#06d6a0"]
    for i, opt in enumerate(options[:4]):
        price_score = max(1, 5 - options.index(opt))
        vals = [
            price_score,
            {"flight": 4.5, "train": 3.5, "bus": 2.5}.get(opt.get("type",""), 3),
            {"flight": 5, "train": 3, "bus": 2}.get(opt.get("type",""), 3),
            min(5, opt.get("seats_available", 10) / 10),
            opt.get("rating", 3)
        ]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself", name=opt.get("name",""),
            line=dict(color=colors[i % len(colors)]),
            fillcolor=colors[i % len(colors)].replace("#", "rgba(") + ",0.1)" if "#" in colors[i] else colors[i],
            opacity=0.8,
        ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#2a2a3a", tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="#2a2a3a"),
        ),
    )
    return fig


# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">✦ AI-Powered Travel Intelligence</div>
  <div class="hero-title">Plan Smarter with <span>VoyageAI</span></div>
  <div class="hero-sub">Describe your dream trip — we'll handle tickets, routes, hotels, packing & your perfect itinerary.</div>
</div>
""", unsafe_allow_html=True)


# ─── STEP BAR ─────────────────────────────────────────────────────────────────
step = st.session_state.step
steps = ["Describe", "Analysis", "Transport", "Hotels", "Itinerary", "Confirm"]
html_steps = '<div class="steps-bar">'
for i, s in enumerate(steps, 1):
    cls = "done" if i < step else ("active" if i == step else "")
    icon = "✓" if i < step else str(i)
    html_steps += f'<div class="step-item {cls}"><div class="step-dot">{icon}</div><div class="step-label">{s}</div></div>'
html_steps += "</div>"
st.markdown(html_steps, unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    key_input = st.text_input("Gemini API Key", type="password",
        value=st.session_state.gemini_key,
        help="Get free key at aistudio.google.com/app/apikey")
    if key_input:
        st.session_state.gemini_key = key_input
    if st.session_state.gemini_key:
        st.success("✓ API key set — using Gemini AI")
    else:
        st.info("No key → Demo mode with rich sample data")

    st.markdown("---")
    st.markdown("**🎯 Quick Trip Templates**")
    demos = [
        "I want to travel from Kolkata to Goa next week for 5 days with my partner. Budget is medium.",
        "Planning a solo trip from Delhi to Jaipur for 3 days to see palaces and eat street food.",
        "Family trip (4 people) from Mumbai to Kerala for 7 days in December.",
        "Adventure trip from Bangalore to Manali for 6 days with 3 friends, budget-friendly.",
    ]
    for d in demos:
        if st.button(d[:48]+"…", key="demo_" + d[:15]):
            st.session_state.tour_desc = d
            st.session_state.step = 1
            st.rerun()

    if st.session_state.step > 1:
        st.markdown("---")
        st.markdown("**📊 Trip Progress**")
        progress = (st.session_state.step - 1) / (len(steps) - 1)
        st.progress(progress)
        st.markdown(f"<div style='font-size:0.78rem;color:#7070a0;'>Step {st.session_state.step} of {len(steps)}</div>", unsafe_allow_html=True)

        if st.button("🔄 Start Over", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k != "gemini_key":
                    del st.session_state[k]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — DESCRIBE YOUR TRIP
# ═══════════════════════════════════════════════════════════════════════════════
if step == 1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗺️ Tell us about your trip</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.85rem;color:#7070a0;margin-bottom:1rem;">Describe naturally — origin, destination, dates, duration, travelers, budget & interests.</p>', unsafe_allow_html=True)

    tour_input = st.text_area("Your travel plan", value=st.session_state.tour_desc, height=160,
        placeholder="e.g. I want to travel from Kolkata to Goa next week for 5 days with my girlfriend. We love beaches, local food, and nightlife. Budget is medium.",
        label_visibility="collapsed")
    st.session_state.tour_desc = tour_input

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        analyze_btn = st.button("✦ Analyze Trip →", use_container_width=True)
    with col3:
        st.markdown('<div style="font-size:0.72rem;color:#7070a0;padding-top:0.7rem;">Powered by Gemini AI</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Feature highlights
    cols = st.columns(4)
    features = [
        ("🤖", "AI Analysis", "Smart parsing of your travel plan"),
        ("📊", "Visual Charts", "Budget breakdowns & comparisons"),
        ("🏨", "Hotel Finder", "AI-curated accommodation options"),
        ("🎒", "Packing List", "Context-aware what-to-pack guide"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
<div class="glass-card" style="text-align:center;padding:1.2rem 0.8rem;">
  <div style="font-size:1.8rem;margin-bottom:0.5rem;">{icon}</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;margin-bottom:0.3rem;">{title}</div>
  <div style="font-size:0.72rem;color:#7070a0;">{desc}</div>
</div>""", unsafe_allow_html=True)

    if analyze_btn:
        if len(tour_input.strip()) < 20:
            st.error("Please describe your trip in a bit more detail.")
        else:
            with st.spinner("VoyageAI is reading your plan…"):
                analysis = analyze_tour_with_ai(tour_input)
                weather = generate_weather_with_ai(analysis)
                st.session_state.ai_analysis = analysis
                st.session_state.weather = weather
            st.session_state.step = 2
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — AI ANALYSIS + WEATHER + ATTRACTIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    analysis = st.session_state.ai_analysis
    weather = st.session_state.weather

    # Main analysis card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✦ Trip Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-bubble">{analysis.get("summary","")}</div>', unsafe_allow_html=True)

    travelers = analysis.get("travelers", 1)
    dur = analysis.get("duration_days", 0)
    trip_type = analysis.get("trip_type", "leisure").title()
    season = analysis.get("season", "").title()

    st.markdown(f"""
<div class="summary-banner">
  <div class="summary-grid">
    <div class="summary-item"><div class="summary-value">{analysis.get("origin","—")}</div><div class="summary-key">From</div></div>
    <div class="summary-item"><div class="summary-value">{analysis.get("destination","—")}</div><div class="summary-key">To</div></div>
    <div class="summary-item"><div class="summary-value">{analysis.get("travel_date","—")}</div><div class="summary-key">Departure</div></div>
    <div class="summary-item"><div class="summary-value">{dur} Days</div><div class="summary-key">Duration</div></div>
    <div class="summary-item"><div class="summary-value">{travelers} 👤</div><div class="summary-key">Travelers</div></div>
    <div class="summary-item"><div class="summary-value">{analysis.get("budget","—").title()}</div><div class="summary-key">Budget</div></div>
    <div class="summary-item"><div class="summary-value">{trip_type}</div><div class="summary-key">Trip Type</div></div>
    <div class="summary-item"><div class="summary-value">{season}</div><div class="summary-key">Season</div></div>
  </div>
</div>""", unsafe_allow_html=True)

    interests = analysis.get("interests", [])
    if interests:
        chips = "".join([f'<span class="tag">{i}</span>' for i in interests])
        st.markdown(f"<div style='margin-bottom:1rem;'><span style='font-size:0.78rem;color:#7070a0;'>Interests: </span>{chips}</div>", unsafe_allow_html=True)

    tips = analysis.get("tips", [])
    if tips:
        for t in tips:
            st.markdown(f'<div class="savings-pill">💡 {t}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Weather card
    if weather:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🌤️ Weather at {analysis.get("destination","")}</div>', unsafe_allow_html=True)

        w_col1, w_col2 = st.columns([1, 2])
        with w_col1:
            st.markdown(f"""
<div class="weather-card">
  <div class="weather-icon">{weather.get("emoji","🌤️")}</div>
  <div>
    <div class="weather-temp">{weather.get("temp_high",28)}°C</div>
    <div class="weather-desc">{weather.get("condition","Pleasant")}</div>
    <div class="weather-meta">
      <div class="weather-meta-item">💧 {weather.get("humidity",60)}%</div>
      <div class="weather-meta-item">🌧 {weather.get("rain_chance",15)}%</div>
      <div class="weather-meta-item">☀ UV {weather.get("uv_index",5)}</div>
    </div>
  </div>
</div>
<div style="font-size:0.8rem;color:#00d4aa;padding:0.5rem 0;">👕 {weather.get("advice","Pack light cotton clothes.")}</div>
""", unsafe_allow_html=True)

        with w_col2:
            if weather.get("forecast"):
                st.plotly_chart(weather_forecast_chart(weather["forecast"]), use_container_width=True, config={"displayModeBar": False})

        st.markdown('</div>', unsafe_allow_html=True)

    # Attractions preview
    with st.spinner("Loading top attractions…"):
        if not st.session_state.attractions:
            st.session_state.attractions = generate_attractions_with_ai(analysis)

    attractions = st.session_state.attractions
    if attractions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">📍 Top Attractions in {analysis.get("destination","")}</div>', unsafe_allow_html=True)
        st.markdown('<div class="attract-grid">', unsafe_allow_html=True)
        for a in attractions:
            st.markdown(f"""
<div class="attract-card">
  <div class="attract-icon">{a.get("emoji","🏛️")}</div>
  <div class="attract-name">{a.get("name","")}</div>
  <div class="attract-rating">{"★" * int(a.get("rating",4))} {a.get("rating","4.0")}</div>
  <div class="attract-dist">📍 {a.get("distance_km",0)} km &nbsp;|&nbsp; {a.get("entry_fee","Free")}</div>
  <div style="font-size:0.72rem;color:#7070a0;margin-top:0.4rem;line-height:1.4;">{a.get("tip","")}</div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Edit Trip", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Fetch Transport Options →", use_container_width=True):
            with st.spinner("Searching best routes…"):
                options = fetch_transport_with_ai(analysis)
                st.session_state.transport_options = options
            st.session_state.step = 3
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — CHOOSE TRANSPORT (with comparison charts)
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    analysis = st.session_state.ai_analysis
    options = st.session_state.transport_options
    pax = analysis.get("travelers", 1)

    tab1, tab2 = st.tabs(["📋 Browse Options", "📊 Compare Charts"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🚉 Transport — {analysis.get("origin","")} → {analysis.get("destination","")}</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            filter_type = st.selectbox("Filter", ["All", "Train", "Bus", "Flight"], label_visibility="collapsed")
        with c2:
            sort_by = st.selectbox("Sort by", ["Price ↑", "Price ↓", "Duration", "Rating ↓"], label_visibility="collapsed")

        filtered = options if filter_type == "All" else [o for o in options if o.get("type","").lower() == filter_type.lower()]
        sort_map = {
            "Price ↑": lambda x: x.get("price_per_person", 0),
            "Price ↓": lambda x: -x.get("price_per_person", 0),
            "Duration": lambda x: x.get("duration", ""),
            "Rating ↓": lambda x: -x.get("rating", 0),
        }
        filtered = sorted(filtered, key=sort_map[sort_by])

        type_icons = {"train": "🚂", "bus": "🚌", "flight": "✈️"}

        st.markdown('<div class="transport-grid">', unsafe_allow_html=True)
        for opt in filtered:
            oid = opt["id"]
            otype = opt.get("type", "train")
            icon = type_icons.get(otype, "🚌")
            price = opt.get("price_per_person", 0)
            total = price * pax
            selected_cls = "selected" if st.session_state.selected_transport == oid else ""
            amenities = ", ".join(opt.get("amenities", [])[:3])

            st.markdown(f"""
<div class="transport-card {otype} {selected_cls}">
  <div class="tc-header">
    <div>
      <div class="tc-type {otype}">{icon} {otype.upper()}</div>
      <div class="tc-name">{opt.get("name","")} <span style="color:#7070a0;font-size:0.8rem;font-weight:400">#{opt.get("number","")}</span></div>
      <div class="tc-route">{analysis.get("origin","")} → {analysis.get("destination","")}</div>
    </div>
    <div style="text-align:right;">
      <div class="tc-price">₹{price:,}</div>
      <div style="font-size:0.7rem;color:#7070a0;">per person</div>
      <div style="font-size:0.75rem;color:#00d4aa;margin-top:4px;">Total ₹{total:,}</div>
    </div>
  </div>
  <div class="tc-meta">
    <div class="tc-meta-item">🕐 <strong>{opt.get("departure","")}</strong> → <strong>{opt.get("arrival","")}</strong></div>
    <div class="tc-meta-item">⏱ {opt.get("duration","")}</div>
    <div class="tc-meta-item">💺 {opt.get("class","")}</div>
    <div class="tc-meta-item">🪑 {opt.get("seats_available",0)} seats</div>
  </div>
  <div style="margin-top:0.7rem;font-size:0.75rem;color:#7070a0;">🛎 {amenities} &nbsp;&nbsp; ⭐ {opt.get("rating","")}</div>
  <div class="tc-check">✓</div>
</div>""", unsafe_allow_html=True)

            if st.button(f"{'✓ Selected' if st.session_state.selected_transport == oid else 'Select'}", key=f"sel_{oid}"):
                st.session_state.selected_transport = oid
                st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Transport Comparison</div>', unsafe_allow_html=True)

        st.markdown("**Price vs Rating — All Options**")
        st.plotly_chart(transport_comparison_chart(options, pax), use_container_width=True, config={"displayModeBar": False})

        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
        st.markdown("**Radar Score — Top 4 Options**")
        radar = rating_radar_chart(options)
        if radar:
            st.plotly_chart(radar, use_container_width=True, config={"displayModeBar": False})

        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Find Hotels →", use_container_width=True):
            if not st.session_state.selected_transport:
                st.error("Please select a transport option first.")
            else:
                with st.spinner("Finding best hotels…"):
                    hotels = generate_hotels_with_ai(analysis)
                    st.session_state.hotels = hotels
                st.session_state.step = 4
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — HOTELS + BUDGET BREAKDOWN
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    analysis = st.session_state.ai_analysis
    hotels = st.session_state.hotels
    options = st.session_state.transport_options
    chosen = next((o for o in options if o["id"] == st.session_state.selected_transport), options[0] if options else {})
    pax = analysis.get("travelers", 1)
    days = analysis.get("duration_days", 5)

    tab1, tab2, tab3 = st.tabs(["🏨 Hotels", "💰 Budget Planner", "🎒 Packing List"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🏨 Hotels in {analysis.get("destination","")}</div>', unsafe_allow_html=True)

        budget_filter = st.selectbox("Filter by type", ["All", "Budget", "Mid-range", "Luxury"], label_visibility="collapsed")
        filtered_hotels = hotels if budget_filter == "All" else [h for h in hotels if h.get("type","").lower() == budget_filter.lower()]

        star_map = {"luxury": "⭐⭐⭐⭐⭐", "mid-range": "⭐⭐⭐⭐", "budget": "⭐⭐⭐"}

        st.markdown('<div class="hotel-grid">', unsafe_allow_html=True)
        for h in filtered_hotels:
            amenities_html = "".join([f'<span class="hotel-tag">{a}</span>' for a in h.get("amenities", [])[:4]])
            total_hotel_cost = h.get("price_per_night", 0) * days
            st.markdown(f"""
<div class="hotel-card">
  <div class="hotel-stars">{star_map.get(h.get("type","").lower(), "⭐⭐⭐")}</div>
  <div class="hotel-name">{h.get("name","")}</div>
  <div style="font-size:0.75rem;color:#7070a0;margin-bottom:0.5rem;">📍 {h.get("locality","")} &nbsp;|&nbsp; ⭐ {h.get("rating",4.0)} ({h.get("review_count",0):,} reviews)</div>
  <div style="font-size:0.78rem;color:#a0a0c0;margin-bottom:0.6rem;font-style:italic;">{h.get("highlights","")}</div>
  <div>{amenities_html}</div>
  <div style="margin-top:0.8rem;display:flex;justify-content:space-between;align-items:flex-end;">
    <div><div class="hotel-price">₹{h.get("price_per_night",0):,}<span style="font-size:0.7rem;color:#7070a0;font-weight:400">/night</span></div>
    <div style="font-size:0.72rem;color:#00d4aa;">Total ₹{total_hotel_cost:,} for {days} nights</div></div>
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 AI Budget Estimator</div>', unsafe_allow_html=True)

        if not st.session_state.budget_breakdown:
            with st.spinner("Calculating budget…"):
                st.session_state.budget_breakdown = generate_budget_breakdown_with_ai(analysis, chosen)

        breakdown = st.session_state.budget_breakdown

        st.markdown('<div style="font-size:0.8rem;color:#7070a0;margin-bottom:0.8rem;">Adjust your spending estimates:</div>', unsafe_allow_html=True)

        adjusted = {}
        for category, base_val in breakdown.items():
            adj_val = st.slider(f"{category}", 0, int(base_val * 2.5), int(base_val), step=100, key=f"budget_{category}")
            adjusted[category] = adj_val

        total = sum(adjusted.values())
        per_person = total // pax if pax else total

        b_cols = st.columns(3)
        with b_cols[0]:
            st.markdown(f'<div class="budget-stat"><div class="budget-val" style="color:#00d4aa;">₹{total:,}</div><div class="budget-lbl">Total Budget</div></div>', unsafe_allow_html=True)
        with b_cols[1]:
            st.markdown(f'<div class="budget-stat"><div class="budget-val" style="color:#7c6bff;">₹{per_person:,}</div><div class="budget-lbl">Per Person</div></div>', unsafe_allow_html=True)
        with b_cols[2]:
            daily = total // max(days, 1)
            st.markdown(f'<div class="budget-stat"><div class="budget-val" style="color:#ff6b9d;">₹{daily:,}</div><div class="budget-lbl">Per Day</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(budget_pie_chart(adjusted), use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div style="font-size:0.8rem;font-family:Space Grotesk;color:#7070a0;text-transform:uppercase;letter-spacing:0.08em;margin:0.8rem 0 0.5rem;">💡 Smart Savings Tips</div>', unsafe_allow_html=True)
        tips_list = [
            f"Book train tickets 60-90 days in advance to save up to 20%",
            f"Opt for homestays in {analysis.get('destination','')} — often 40% cheaper than hotels",
            f"Eat at local dhabas & street stalls — authentic food at 1/3 the price",
            f"Use UPI payments everywhere — avoid forex/ATM charges",
        ]
        for tip in tips_list:
            st.markdown(f'<div class="savings-pill">💚 {tip}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🎒 AI Packing List</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.8rem;color:#7070a0;margin-bottom:1rem;">Personalised for {analysis.get("destination","")} · {analysis.get("season","").title()} · {analysis.get("trip_type","").title()} trip</div>', unsafe_allow_html=True)

        if not st.session_state.packing_list:
            with st.spinner("Generating packing list…"):
                st.session_state.packing_list = generate_packing_list_with_ai(analysis)

        packing = st.session_state.packing_list
        section_icons = {"Essentials": "📋", "Clothing": "👔", "Toiletries": "🧴", "Electronics": "🔌", "Documents": "📄", "Destination-Specific": "🌴"}

        pack_cols = st.columns(2)
        for i, (section, items) in enumerate(packing.items()):
            with pack_cols[i % 2]:
                icon = section_icons.get(section, "📦")
                st.markdown(f'<div class="pack-section"><div class="pack-title">{icon} {section}</div>', unsafe_allow_html=True)
                for item in items:
                    st.markdown(f'<div class="pack-item"><span style="color:#7c6bff;font-size:0.8rem;">☐</span> {item}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Change Transport", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Generate Itinerary →", use_container_width=True):
            with st.spinner("Building your perfect itinerary…"):
                itinerary = generate_itinerary_with_ai(analysis, chosen)
                st.session_state.itinerary = itinerary
            st.session_state.step = 5
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — ITINERARY
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 5:
    analysis = st.session_state.ai_analysis
    itinerary = st.session_state.itinerary
    options = st.session_state.transport_options
    chosen = next((o for o in options if o["id"] == st.session_state.selected_transport), options[0] if options else {})
    pax = analysis.get("travelers", 1)
    days = analysis.get("duration_days", 5)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">📋 Your {days}-Day Itinerary — {analysis.get("destination","")}</div>', unsafe_allow_html=True)

    if chosen:
        icon = {"train": "🚂", "bus": "🚌", "flight": "✈️"}.get(chosen.get("type", ""), "🚀")
        st.markdown(f"""
<div style="background:rgba(124,107,255,0.07);border:1px solid rgba(124,107,255,0.2);border-radius:12px;padding:1rem 1.3rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
  <span style="font-size:1.6rem;">{icon}</span>
  <div>
    <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.95rem;">{chosen.get("name","")} #{chosen.get("number","")}</div>
    <div style="font-size:0.8rem;color:#7070a0;">{analysis.get("origin","")} → {analysis.get("destination","")} &nbsp;|&nbsp; {chosen.get("departure","")}–{chosen.get("arrival","")} ({chosen.get("duration","")}) &nbsp;|&nbsp; {chosen.get("class","")}</div>
  </div>
  <div style="margin-left:auto;text-align:right;">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;color:#00d4aa;">₹{chosen.get("price_per_person",0)*pax:,}</div>
    <div style="font-size:0.7rem;color:#7070a0;">Transport for {pax} traveler(s)</div>
  </div>
</div>""", unsafe_allow_html=True)

    for day in itinerary:
        st.markdown(f"""
<div class="day-block">
  <div class="day-label">Day {day["day"]}</div>
  <div class="day-title">{day["title"]}</div>
  <ul class="activity-list">""", unsafe_allow_html=True)
        for act in day.get("activities", []):
            st.markdown(f"""
    <li class="activity-item">
      <span class="activity-time">{act.get("time","")}</span>
      <span>{act.get("emoji","•")}</span>
      <span>{act.get("activity","")}</span>
    </li>""", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.budget_breakdown:
        total_budget = sum(st.session_state.budget_breakdown.values())
        st.markdown(f"""
<div style="background:rgba(0,212,170,0.06);border:1px solid rgba(0,212,170,0.2);border-radius:12px;padding:1rem 1.4rem;margin-bottom:1.2rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
  <div style="font-family:'Space Grotesk';font-weight:600;">💰 Estimated Total Trip Cost</div>
  <div style="font-family:'Space Grotesk';font-size:1.4rem;font-weight:700;color:#00d4aa;">₹{total_budget:,}</div>
  <div style="font-size:0.78rem;color:#7070a0;">{days} days · {pax} traveler(s) · {analysis.get("budget","medium")} budget</div>
</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Change Hotels", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("✓ Confirm & Book →", use_container_width=True):
            st.session_state.pnr = generate_pnr()
            st.session_state.booked = True
            st.session_state.step = 6
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6 — BOOKING CONFIRMED
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 6:
    analysis = st.session_state.ai_analysis
    options = st.session_state.transport_options
    chosen = next((o for o in options if o["id"] == st.session_state.selected_transport), options[0] if options else {})
    pax = analysis.get("travelers", 1)
    breakdown = st.session_state.budget_breakdown

    st.markdown(f"""
<div class="booking-confirm">
  <div class="confirm-icon">🎉</div>
  <div class="confirm-title">Trip Confirmed!</div>
  <div style="color:#7070a0;font-size:0.9rem;margin-bottom:0.5rem;">Your booking reference:</div>
  <div class="pnr-badge">{st.session_state.pnr}</div>
  <div style="font-size:0.8rem;color:#7070a0;margin-top:0.8rem;">Save this PNR. Your tickets will be sent to your registered email.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    if chosen and analysis:
        with col1:
            st.markdown(f"""
<div class="glass-card" style="text-align:center;">
  <div style="font-size:2rem">🗺️</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;margin:0.4rem 0;">{analysis.get("origin","")} → {analysis.get("destination","")}</div>
  <div style="font-size:0.8rem;color:#7070a0;">{analysis.get("travel_date","")}</div>
  <div style="font-size:0.78rem;color:#7070a0;margin-top:0.3rem;">{analysis.get("duration_days",0)} days · {pax} traveler(s)</div>
</div>""", unsafe_allow_html=True)
        with col2:
            icon = {"train":"🚂","bus":"🚌","flight":"✈️"}.get(chosen.get("type",""),"🚀")
            st.markdown(f"""
<div class="glass-card" style="text-align:center;">
  <div style="font-size:2rem">{icon}</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;margin:0.4rem 0;">{chosen.get("name","")}</div>
  <div style="font-size:0.8rem;color:#7070a0;">{chosen.get("departure","")} → {chosen.get("arrival","")} · {chosen.get("class","")}</div>
</div>""", unsafe_allow_html=True)
        with col3:
            total = sum(breakdown.values()) if breakdown else chosen.get("price_per_person",0) * pax
            st.markdown(f"""
<div class="glass-card" style="text-align:center;">
  <div style="font-size:2rem">💳</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.4rem;font-weight:700;margin:0.4rem 0;color:#00d4aa;">₹{total:,}</div>
  <div style="font-size:0.8rem;color:#7070a0;">All-in estimate · {analysis.get("budget","medium")} budget</div>
</div>""", unsafe_allow_html=True)

    if breakdown:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Final Budget Breakdown</div>', unsafe_allow_html=True)
        f_col1, f_col2 = st.columns([1, 1])
        with f_col1:
            st.plotly_chart(budget_pie_chart(breakdown), use_container_width=True, config={"displayModeBar": False})
        with f_col2:
            st.markdown('<div style="padding-top:1rem;">', unsafe_allow_html=True)
            for cat, val in breakdown.items():
                pct = int(val / sum(breakdown.values()) * 100) if sum(breakdown.values()) else 0
                st.markdown(f"""
<div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid #1e1e2e;font-size:0.83rem;">
  <span style="color:#a0a0c0;">{cat}</span>
  <span style="font-family:'Space Grotesk';font-weight:600;">₹{val:,} <span style="color:#7070a0;font-weight:400;font-size:0.72rem;">({pct}%)</span></span>
</div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🌍 Plan Another Trip", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "gemini_key":
                del st.session_state[k]
        st.rerun()
