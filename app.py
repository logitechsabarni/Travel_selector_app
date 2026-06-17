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
        "local_foods": [],
        "hidden_gems": [],
        "local_experiences": [],
        "travel_tips": [],
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


# ─── MASTER AI INTELLIGENCE ENGINE ────────────────────────────────────────────
# Single comprehensive Gemini call for all destination-specific data.
# Replaces scattered mock functions with one accurate, verified AI response.

MASTER_SYSTEM_PROMPT = """You are TravelGPT Elite operating as VoyageAI — an advanced AI travel planner, local destination expert, weather-aware travel advisor, itinerary designer, food guide, and budget consultant for Indian travel.

━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Every response must be generated dynamically.
2. NEVER use generic placeholder attractions. NEVER use:
   - "Old City Heritage Walk", "Sunset Beach Point", "Local Food Street"
   - "Spice Plantation Tour", "Night Bazaar Market", "Generic Heritage Tour"
   - "Generic Beach Spot"
   unless they are ACTUAL named locations in the destination.
3. Attractions, food, weather advice, experiences, budget estimates, and itinerary MUST change when destination changes.
4. Use authentic local knowledge. Prefer real landmarks, local cuisine, and culturally relevant activities.
5. Do NOT invent famous attractions. Every place must physically exist.
6. For Indian cities use correct local knowledge:
   - Chennai → Marina Beach, Kapaleeshwarar Temple, Mylapore, Fort St. George, San Thome Basilica, Besant Nagar
   - Goa → Calangute, Anjuna, Baga, Basilica of Bom Jesus, Panjim, Fontainhas, Dudhsagar Falls
   - Jaipur → Hawa Mahal, Amber Fort, City Palace, Jantar Mantar, Johri Bazaar, Nahargarh Fort
   - Mumbai → Gateway of India, Marine Drive, Elephanta Caves, Dharavi, Colaba Causeway, Bandra
   - Delhi → Red Fort, Qutub Minar, Humayun's Tomb, Chandni Chowk, Lotus Temple, India Gate
   - Kolkata → Victoria Memorial, Howrah Bridge, Dakshineswar, Park Street, College Street
   - Varanasi → Dashashwamedh Ghat, Kashi Vishwanath, Sarnath, Assi Ghat, Manikarnika Ghat
   - Agra → Taj Mahal, Agra Fort, Fatehpur Sikri, Mehtab Bagh, Itimad-ud-Daulah
   - Manali → Rohtang Pass, Solang Valley, Hadimba Temple, Old Manali, Beas River

━━━━━━━━━━━━━━━━━━━━━━━━━━
WEATHER RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━

- Generate estimated weather based on destination, travel month, and season.
- Weather must vary per destination — coastal cities differ from hill stations differ from desert cities.
- Include: temperature range, humidity, condition, rain probability, UV level, clothing advice.
- Generate a 5-day forecast.

━━━━━━━━━━━━━━━━━━━━━━━━━━
FOOD RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommend 4-5 authentic local dishes with:
- name, description, why it is famous, where to try it (a real restaurant or area name)

━━━━━━━━━━━━━━━━━━━━━━━━━━
LOCAL EXPERIENCES
━━━━━━━━━━━━━━━━━━━━━━━━━━

Suggest 4-5 destination-specific experiences based on trip type:
- cultural events, local markets, festivals, workshops, adventure activities, romantic activities

━━━━━━━━━━━━━━━━━━━━━━━━━━
HIDDEN GEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━

Suggest 3-4 lesser-known but real places locals love that tourists typically miss.

━━━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━

Before responding verify:
✓ Attractions belong to the destination.
✓ Food recommendations belong to the destination.
✓ Weather matches destination and season.
✓ Itinerary is realistic with practical timing and travel flow.
✓ Budget estimates are reasonable for destination and duration.
✓ No placeholder attractions exist.
✓ Recommendations match interests and trip type.
✓ Output differs for different destinations.
✓ Hidden gems are real lesser-known spots, not famous tourist traps.

━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON. No markdown. No explanations. No code blocks."""


def build_master_prompt(description: str) -> str:
    """Build the master user prompt injecting trip description into TravelGPT Elite schema."""
    return f"""Analyze this Indian travel plan and generate a complete, accurate, destination-specific travel package.

User Input: "{description}"

━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT: Parse the user input to extract:
- source_city, destination_city, departure_date, duration_days, travelers, budget, trip_type, season, interests
Then use those values to fill every section below with REAL, DESTINATION-SPECIFIC content.
━━━━━━━━━━━━━━━━━━━━━━━━━━

Return this EXACT JSON structure (all fields required):
{{
  "trip_summary": {{
    "origin": "city name",
    "destination": "city name",
    "travel_date": "YYYY-MM-DD",
    "return_date": "YYYY-MM-DD or null",
    "duration_days": 5,
    "travelers": 2,
    "budget": "low/medium/high",
    "interests": ["interest1", "interest2"],
    "season": "summer/monsoon/winter/spring",
    "trip_type": "leisure/adventure/cultural/family/solo/romantic",
    "description": "2-3 sentence engaging trip summary mentioning the destination and highlights",
    "trip_highlight": "One compelling sentence about the best thing about this destination right now",
    "travel_advice": ["Practical tip 1 specific to destination", "Practical tip 2", "Practical tip 3"]
  }},

  "weather": {{
    "emoji": "☀️",
    "temp_high": 32,
    "temp_low": 24,
    "condition": "Destination and season specific condition",
    "humidity": 65,
    "rain_chance": 10,
    "uv_index": 7,
    "advice": "Clothing and precaution advice specific to this destination and season",
    "forecast": [
      {{"day": "Mon", "emoji": "☀️", "high": 32, "low": 24}},
      {{"day": "Tue", "emoji": "⛅", "high": 30, "low": 23}},
      {{"day": "Wed", "emoji": "🌧️", "high": 27, "low": 22}},
      {{"day": "Thu", "emoji": "☀️", "high": 33, "low": 25}},
      {{"day": "Fri", "emoji": "⛅", "high": 31, "low": 24}}
    ]
  }},

  "travel_tips": [
    "Transportation tip specific to destination",
    "Local customs or etiquette tip",
    "Budgeting tip for this destination",
    "Safety tip relevant to this destination",
    "Weather or season-specific precaution",
    "Local etiquette tip",
    "Scam or tourist trap to avoid in this city"
  ],

  "attractions": [
    {{
      "name": "REAL place name that actually exists in destination city",
      "emoji": "🏛️",
      "type": "Heritage/Nature/Food/Adventure/Shopping/Beach/Temple/Museum",
      "distance_km": 2.5,
      "rating": 4.6,
      "entry_fee": "Free or ₹200",
      "timing": "6 AM–8 PM",
      "description": "2-sentence description of why this place is worth visiting",
      "tip": "Insider tip only a local would give"
    }}
  ],

  "local_foods": [
    {{
      "name": "Real dish name from destination",
      "emoji": "🍛",
      "description": "What the dish is and how it tastes",
      "why_famous": "Why this dish is iconic to the destination",
      "where_to_try": "Name of a real restaurant, street, or area in the destination"
    }}
  ],

  "hidden_gems": [
    {{
      "name": "Real lesser-known place in destination",
      "emoji": "💎",
      "type": "Cafe/Viewpoint/Market/Temple/Beach/Garden/etc",
      "why_special": "Why locals love it and tourists usually miss it",
      "tip": "How to get there or best time to visit"
    }}
  ],

  "local_experiences": [
    {{
      "experience": "Name of the experience",
      "emoji": "🎭",
      "description": "What you do and why it's special to this destination",
      "best_for": "solo/couple/family/group"
    }}
  ],

  "transport_options": [
    {{
      "id": "t1",
      "type": "train/bus/flight",
      "name": "Real or realistic service name for this route",
      "number": "Train or flight number",
      "departure": "HH:MM",
      "arrival": "HH:MM",
      "duration": "Xh Ym",
      "price_per_person": 1500,
      "class": "3A AC / Sleeper / Economy",
      "seats_available": 20,
      "amenities": ["amenity1", "amenity2"],
      "operator": "Indian Railways / IndiGo / VRL etc.",
      "rating": 4.2
    }}
  ],

  "hotels": [
    {{
      "id": "h1",
      "name": "Real hotel name or realistic name for a real locality in destination",
      "stars": 4,
      "price_per_night": 3500,
      "locality": "Real neighbourhood in destination city",
      "rating": 4.3,
      "review_count": 1240,
      "amenities": ["WiFi", "Pool", "AC"],
      "type": "budget/mid-range/luxury",
      "highlights": "What makes this property special"
    }}
  ],

  "itinerary": [
    {{
      "day": 1,
      "title": "Meaningful day theme",
      "activities": [
        {{"time": "09:00", "activity": "Visit specific real place with brief description", "emoji": "🏛️"}}
      ]
    }}
  ],

  "budget_breakdown": {{
    "Transport": 3000,
    "Accommodation": 8000,
    "Food & Dining": 4000,
    "Sightseeing": 2500,
    "Shopping": 2000,
    "Miscellaneous": 1500
  }},

  "packing_list": {{
    "Essentials": ["Valid ID / Aadhaar Card", "Travel tickets & bookings", "Cash & UPI-linked card"],
    "Clothing": ["Season and destination appropriate items"],
    "Toiletries": ["Sunscreen SPF 50+", "Items relevant to destination weather"],
    "Electronics": ["Phone + charger", "Power bank"],
    "Documents": ["E-tickets downloaded offline", "Hotel bookings printout"],
    "Destination-Specific": ["Items specific to this destination and trip type"]
  }},

  "savings_tips": [
    "Specific money-saving tip for this destination",
    "Transport booking tip",
    "Food saving tip",
    "Accommodation tip"
  ]
}}

QUANTITY REQUIREMENTS:
- top_attractions: 6-8 real places in destination city
- local_foods: 4-5 authentic local dishes
- hidden_gems: 3-4 real lesser-known spots
- local_experiences: 4-5 destination-specific activities
- transport_options: 5-6 options (mix of train, bus, flight)
- hotels: 4 options (one luxury, two mid-range, one budget)
- itinerary: one entry per day for the full trip duration
- travel_tips: 6-7 practical tips
- Each itinerary day must have Morning/Afternoon/Evening activities

VALIDATION: Before returning, verify every attraction and food recommendation belongs to the destination city."""


def analyze_trip_master(description: str):
    """
    Single master AI call that returns all trip data at once.
    Falls back gracefully to mock data if no API key or call fails.
    """
    llm = get_llm()
    if not llm:
        return None  # Will trigger mock fallback

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=MASTER_SYSTEM_PROMPT),
        HumanMessage(content=build_master_prompt(description))
    ])
    try:
        result = (prompt | llm).invoke({})
        text = re.sub(r"```json|```", "", result.content.strip()).strip()
        data = json.loads(text)
        return data
    except Exception as e:
        st.warning(f"AI call failed, using demo data. Error: {str(e)[:80]}")
        return None


def extract_analysis(master_data: dict) -> dict:
    """Extract the trip_summary portion as the 'analysis' object used throughout."""
    if not master_data:
        return {}
    s = master_data.get("trip_summary", {})
    return {
        "origin": s.get("origin", ""),
        "destination": s.get("destination", ""),
        "travel_date": s.get("travel_date", ""),
        "return_date": s.get("return_date", None),
        "duration_days": s.get("duration_days", 5),
        "travelers": s.get("travelers", 2),
        "budget": s.get("budget", "medium"),
        "interests": s.get("interests", []),
        "season": s.get("season", "winter"),
        "trip_type": s.get("trip_type", "leisure"),
        "summary": s.get("description", ""),
        "trip_highlight": s.get("trip_highlight", ""),
        "tips": s.get("travel_advice", []),
    }


# ─── MOCK DATA (fallback when no API key) ─────────────────────────────────────
def _mock_analysis(desc):
    words = desc.lower()
    cities = ["Mumbai", "Delhi", "Kolkata", "Bengaluru", "Chennai", "Hyderabad", "Jaipur", "Goa", "Kerala", "Manali", "Shimla", "Varanasi", "Agra", "Pune"]
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


CITY_MOCK_DATA = {
    "Goa": {
        "attractions": [
            {"name": "Baga Beach", "emoji": "🏖️", "type": "Beach", "distance_km": 15.0, "rating": 4.5, "entry_fee": "Free", "timing": "24 hours", "tip": "Visit early morning for a peaceful walk before the crowds arrive"},
            {"name": "Basilica of Bom Jesus", "emoji": "⛪", "type": "Heritage", "distance_km": 9.0, "rating": 4.7, "entry_fee": "Free", "timing": "9 AM–6:30 PM", "tip": "UNESCO World Heritage Site — visit on weekday mornings to avoid tour groups"},
            {"name": "Anjuna Flea Market", "emoji": "🛍️", "type": "Shopping", "distance_km": 18.0, "rating": 4.2, "entry_fee": "Free", "timing": "Wed 8 AM–6 PM", "tip": "Wednesday only — bargain hard, first price is always inflated 2x"},
            {"name": "Dudhsagar Falls", "emoji": "💦", "type": "Nature", "distance_km": 60.0, "rating": 4.6, "entry_fee": "₹400 (Jeep)", "timing": "Oct–May, 7 AM–6 PM", "tip": "Book a jeep safari from Mollem — accessible only by 4WD after the trek point"},
            {"name": "Panjim Latin Quarter (Fontainhas)", "emoji": "🏘️", "type": "Heritage", "distance_km": 1.0, "rating": 4.4, "entry_fee": "Free", "timing": "All day", "tip": "Walk the narrow lanes at dusk — the colonial architecture glows beautifully"},
            {"name": "Calangute Beach", "emoji": "🌊", "type": "Beach", "distance_km": 16.0, "rating": 4.3, "entry_fee": "Free", "timing": "24 hours", "tip": "Water sports hub — parasailing + banana boat combo available at fixed government rates"},
            {"name": "Spice Plantation (Tropical Spice Farm)", "emoji": "🌿", "type": "Nature", "distance_km": 20.0, "rating": 4.3, "entry_fee": "₹400", "timing": "9 AM–4 PM", "tip": "Includes a traditional Goan lunch — book morning slot for guided spice walk"},
            {"name": "Old Goa Churches Complex", "emoji": "🕌", "type": "Heritage", "distance_km": 9.5, "rating": 4.6, "entry_fee": "Free", "timing": "8 AM–6 PM", "tip": "Visit Se Cathedral and Bom Jesus together — they're just 5 min apart on foot"},
        ],
        "hotels": [
            {"id":"h1","name":"Taj Holiday Village Resort","stars":5,"price_per_night":15000,"locality":"Candolim","rating":4.8,"review_count":3200,"amenities":["Pool","Spa","Beach Access","Restaurant","WiFi"],"type":"luxury","highlights":"Private beach access with Goan heritage cottages"},
            {"id":"h2","name":"Casa de Goa Boutique Resort","stars":4,"price_per_night":5500,"locality":"Calangute","rating":4.4,"review_count":1820,"amenities":["Pool","WiFi","Breakfast Included","AC","Restaurant"],"type":"mid-range","highlights":"Portuguese colonial architecture, 5 min walk to beach"},
            {"id":"h3","name":"Hotel Mandovi","stars":3,"price_per_night":2800,"locality":"Panjim City Centre","rating":4.1,"review_count":987,"amenities":["WiFi","AC","Hot Water","TV","Restaurant"],"type":"mid-range","highlights":"Historic Panjim landmark, walking distance to Fontainhas"},
            {"id":"h4","name":"Zostel Goa","stars":2,"price_per_night":700,"locality":"Anjuna","rating":4.3,"review_count":2100,"amenities":["Free WiFi","Common Kitchen","Pool","Lockers","Social Events"],"type":"budget","highlights":"Best backpacker hostel in Goa — vibrant social scene near Anjuna"},
        ]
    },
    "Chennai": {
        "attractions": [
            {"name": "Marina Beach", "emoji": "🏖️", "type": "Beach", "distance_km": 3.0, "rating": 4.5, "entry_fee": "Free", "timing": "24 hours", "tip": "World's second longest urban beach — visit at sunrise for stunning light and fewer crowds"},
            {"name": "Kapaleeshwarar Temple", "emoji": "🛕", "type": "Temple", "distance_km": 5.0, "rating": 4.7, "entry_fee": "Free", "timing": "5 AM–12 PM, 4–10 PM", "tip": "Remove footwear at the entrance and dress conservatively — the gopuram is best photographed in morning light"},
            {"name": "Mylapore Heritage Walk", "emoji": "🏛️", "type": "Heritage", "distance_km": 4.5, "rating": 4.4, "entry_fee": "Free", "timing": "All day", "tip": "Explore the narrow streets around the temple tank — the oldest urban neighbourhood in Chennai"},
            {"name": "Fort St. George", "emoji": "🏰", "type": "Heritage", "distance_km": 2.0, "rating": 4.3, "entry_fee": "₹25", "timing": "9 AM–5 PM (closed Sun)", "tip": "Home to the oldest English church in India — the museum inside is free and underrated"},
            {"name": "Government Museum Chennai", "emoji": "🏛️", "type": "Museum", "distance_km": 6.0, "rating": 4.2, "entry_fee": "₹15", "timing": "9:30 AM–5 PM (closed Wed)", "tip": "Second oldest museum in India — the bronze gallery with Chola sculptures is unmissable"},
            {"name": "San Thome Basilica", "emoji": "⛪", "type": "Heritage", "distance_km": 4.0, "rating": 4.6, "entry_fee": "Free", "timing": "6 AM–8 PM", "tip": "Built over the tomb of St. Thomas the Apostle — peaceful inside even during peak hours"},
            {"name": "Bessant Nagar (Elliot's Beach)", "emoji": "🌅", "type": "Beach", "distance_km": 7.0, "rating": 4.4, "entry_fee": "Free", "timing": "24 hours", "tip": "Far quieter than Marina — locals call it Bessy Beach; great for evening walks and bhajji stalls"},
            {"name": "Mahabalipuram (day trip)", "emoji": "🗿", "type": "Heritage", "distance_km": 58.0, "rating": 4.8, "entry_fee": "₹40", "timing": "6 AM–6 PM", "tip": "1 hour south of Chennai — the Shore Temple at sunrise is one of India's most beautiful sights"},
        ],
        "hotels": [
            {"id":"h1","name":"ITC Grand Chola","stars":5,"price_per_night":18000,"locality":"Guindy","rating":4.9,"review_count":4100,"amenities":["Pool","Spa","Multiple Restaurants","WiFi","Gym"],"type":"luxury","highlights":"South India's grandest hotel — Chola empire architecture with modern luxury"},
            {"id":"h2","name":"Radha Regent","stars":4,"price_per_night":5000,"locality":"Arumbakkam","rating":4.3,"review_count":1560,"amenities":["Pool","WiFi","Restaurant","AC","Gym"],"type":"mid-range","highlights":"Great value 4-star with rooftop pool, near Metro access"},
            {"id":"h3","name":"Hanu Reddy Residences","stars":3,"price_per_night":2500,"locality":"Mylapore","rating":4.2,"review_count":820,"amenities":["WiFi","AC","Hot Water","Kitchenette"],"type":"mid-range","highlights":"Charming heritage stay in the heart of old Chennai, near Kapaleeshwarar"},
            {"id":"h4","name":"Zostel Chennai","stars":2,"price_per_night":600,"locality":"Egmore","rating":4.1,"review_count":940,"amenities":["Free WiFi","Common Kitchen","Lockers","AC Dorms"],"type":"budget","highlights":"Sociable hostel near Chennai Central railway station"},
        ]
    },
    "Jaipur": {
        "attractions": [
            {"name": "Amber Fort (Amer Fort)", "emoji": "🏰", "type": "Heritage", "distance_km": 11.0, "rating": 4.7, "entry_fee": "₹200 (Indian)", "timing": "8 AM–5:30 PM", "tip": "Take the elephant ride at 8 AM or walk up Suraj Pol — buy combo ticket with Jaigarh Fort"},
            {"name": "Hawa Mahal", "emoji": "🏯", "type": "Heritage", "distance_km": 2.0, "rating": 4.5, "entry_fee": "₹50 (Indian)", "timing": "9 AM–4:30 PM", "tip": "Best photographed from the tea shop across the street — go at 9 AM for soft morning light"},
            {"name": "City Palace", "emoji": "👑", "type": "Heritage", "distance_km": 1.5, "rating": 4.6, "entry_fee": "₹200", "timing": "9:30 AM–5 PM", "tip": "Still home to the royal family — book the museum + Mubarak Mahal combo ticket"},
            {"name": "Johri Bazaar", "emoji": "💎", "type": "Shopping", "distance_km": 2.5, "rating": 4.4, "entry_fee": "Free", "timing": "10 AM–9 PM (closed Tue)", "tip": "Jaipur is India's gem capital — best for precious stones, silver jewellery, and blue pottery"},
            {"name": "Jantar Mantar", "emoji": "🔭", "type": "Heritage", "distance_km": 1.8, "rating": 4.5, "entry_fee": "₹50 (Indian)", "timing": "9 AM–4:30 PM", "tip": "UNESCO World Heritage site — the Samrat Yantra sundial is accurate to within 2 seconds"},
            {"name": "Nahargarh Fort", "emoji": "🌄", "type": "Heritage", "distance_km": 15.0, "rating": 4.4, "entry_fee": "₹50", "timing": "10 AM–5:30 PM", "tip": "Best sunset viewpoint over the Pink City — the rooftop café serves amazing thalis"},
            {"name": "Albert Hall Museum", "emoji": "🏛️", "type": "Museum", "distance_km": 3.0, "rating": 4.3, "entry_fee": "₹40 (Indian)", "timing": "9 AM–5 PM, 7–10 PM", "tip": "Ram Niwas Garden surrounds it — visit in the evening when it's beautifully lit up"},
            {"name": "Chokhi Dhani Village", "emoji": "🎭", "type": "Culture", "distance_km": 22.0, "rating": 4.5, "entry_fee": "₹900 (incl. dinner)", "timing": "5–11 PM", "tip": "Authentic Rajasthani village experience with folk dances, camel rides, and traditional thali dinner"},
        ],
        "hotels": [
            {"id":"h1","name":"Rambagh Palace","stars":5,"price_per_night":25000,"locality":"Bhawani Singh Road","rating":4.9,"review_count":3800,"amenities":["Pool","Spa","Polo Ground","Multiple Restaurants","WiFi"],"type":"luxury","highlights":"Former royal residence of the Maharaja — the most iconic palace hotel in Rajasthan"},
            {"id":"h2","name":"Samode Haveli","stars":4,"price_per_night":7000,"locality":"Old City","rating":4.6,"review_count":1240,"amenities":["Courtyard Pool","Heritage Decor","WiFi","Restaurant","AC"],"type":"mid-range","highlights":"Authentic 475-year-old haveli in the walled city — stunning Rajput architecture"},
            {"id":"h3","name":"Hotel Pearl Palace","stars":3,"price_per_night":1800,"locality":"Hathroi Fort Area","rating":4.5,"review_count":3200,"amenities":["Rooftop Restaurant","WiFi","AC","Travel Desk"],"type":"mid-range","highlights":"Legendary budget-mid hotel — family-run, famous rooftop restaurant with city views"},
            {"id":"h4","name":"Zostel Jaipur","stars":2,"price_per_night":500,"locality":"Moti Dungri","rating":4.2,"review_count":1800,"amenities":["Free WiFi","Common Kitchen","Bike Rentals","Events"],"type":"budget","highlights":"Best located hostel in Jaipur — within walking distance of Hawa Mahal"},
        ]
    },
}

def _get_city_attractions(dest):
    """Get city-specific attractions or generate generic ones."""
    city_data = CITY_MOCK_DATA.get(dest, {})
    if city_data:
        return city_data.get("attractions", [])
    # Generic but clearly labeled as placeholder
    return [
        {"name": f"{dest} Main Temple", "emoji": "🛕", "type": "Temple", "distance_km": 2.0, "rating": 4.5, "entry_fee": "Free", "timing": "6 AM–8 PM", "tip": f"Most visited temple in {dest} — check festival calendar before visiting"},
        {"name": f"{dest} Heritage Museum", "emoji": "🏛️", "type": "Museum", "distance_km": 3.5, "rating": 4.2, "entry_fee": "₹50", "timing": "9 AM–5 PM", "tip": "Rich collection of local history and art"},
        {"name": f"{dest} Central Market", "emoji": "🛍️", "type": "Shopping", "distance_km": 1.0, "rating": 4.3, "entry_fee": "Free", "timing": "10 AM–9 PM", "tip": "Best place for local handicrafts and street food"},
        {"name": f"{dest} Lake/Waterfront", "emoji": "🌊", "type": "Nature", "distance_km": 5.0, "rating": 4.4, "entry_fee": "Free", "timing": "Sunrise–Sunset", "tip": "Beautiful at golden hour — rent a boat for ₹100"},
        {"name": f"{dest} Old Quarter", "emoji": "🏘️", "type": "Heritage", "distance_km": 2.5, "rating": 4.1, "entry_fee": "Free", "timing": "All day", "tip": "Explore the historic lanes for authentic local life"},
        {"name": f"{dest} Food Street", "emoji": "🍛", "type": "Food", "distance_km": 0.8, "rating": 4.6, "entry_fee": "Free", "timing": "Evening 5–11 PM", "tip": "Best local street food — try the regional specialties"},
    ]

def _get_city_hotels(dest, days):
    """Get city-specific hotels."""
    city_data = CITY_MOCK_DATA.get(dest, {})
    if city_data:
        return city_data.get("hotels", [])
    return [
        {"id":"h1","name":f"Grand {dest} Palace","stars":5,"price_per_night":9000,"locality":"City Centre","rating":4.7,"review_count":2341,"amenities":["Pool","Spa","Gym","Free WiFi","Restaurant"],"type":"luxury","highlights":"Premier luxury hotel with panoramic city views"},
        {"id":"h2","name":f"{dest} Heritage Inn","stars":4,"price_per_night":4500,"locality":"Old Quarter","rating":4.4,"review_count":1820,"amenities":["Pool","Free WiFi","Breakfast Included","AC"],"type":"mid-range","highlights":"Boutique property with local heritage character"},
        {"id":"h3","name":f"Comfort Suites {dest}","stars":3,"price_per_night":2200,"locality":"Station Area","rating":4.1,"review_count":987,"amenities":["Free WiFi","AC","Hot Water","TV"],"type":"mid-range","highlights":"Great value — 5 min from railway station"},
        {"id":"h4","name":f"Backpackers Hub {dest}","stars":2,"price_per_night":750,"locality":"Backpacker Lane","rating":4.0,"review_count":654,"amenities":["Free WiFi","Common Kitchen","Lockers"],"type":"budget","highlights":"Social hostel atmosphere for budget travelers"},
    ]

def _mock_transport(analysis):
    origin = analysis.get("origin", "Kolkata")
    dest = analysis.get("destination", "Goa")
    return [
        {"id":"t1","type":"train","name":"Gitanjali Express","number":"12859","departure":"14:05","arrival":"08:35+1","duration":"18h 30m","price_per_person":1450,"class":"3A AC","seats_available":12,"amenities":["Pantry Car","Bedding","Charging Points"],"operator":"Indian Railways","rating":4.2},
        {"id":"t2","type":"train","name":f"{origin} Mail","number":"12302","departure":"22:00","arrival":"16:30+1","duration":"18h 30m","price_per_person":890,"class":"Sleeper","seats_available":28,"amenities":["Pantry Car","Charging Points"],"operator":"Indian Railways","rating":3.8},
        {"id":"f1","type":"flight","name":"IndiGo","number":"6E-401","departure":"06:30","arrival":"09:00","duration":"2h 30m","price_per_person":6200,"class":"Economy","seats_available":45,"amenities":["Cabin Baggage 7kg","Meal on purchase"],"operator":"IndiGo Airlines","rating":4.1},
        {"id":"f2","type":"flight","name":"Air India","number":"AI-665","departure":"10:15","arrival":"12:45","duration":"2h 30m","price_per_person":7800,"class":"Economy Flex","seats_available":18,"amenities":["Free Meal","Cabin Baggage 7kg","Check-in 15kg"],"operator":"Air India","rating":4.4},
        {"id":"b1","type":"bus","name":"VRL Travels AC Sleeper","number":"VRL-902","departure":"19:00","arrival":"13:00+1","duration":"18h 00m","price_per_person":1100,"class":"AC Sleeper","seats_available":6,"amenities":["WiFi","Charging","Blanket","Water Bottle"],"operator":"VRL Travels","rating":4.0},
        {"id":"b2","type":"bus","name":"Paulo Travels Deluxe","number":"PT-210","departure":"20:30","arrival":"14:30+1","duration":"18h 00m","price_per_person":850,"class":"Semi-Sleeper AC","seats_available":15,"amenities":["Charging","Water Bottle"],"operator":"Paulo Travels","rating":3.7},
    ]


def _mock_itinerary(analysis):
    days = analysis.get("duration_days", 5)
    dest = analysis.get("destination", "Goa")
    city_attractions = _get_city_attractions(dest)
    attraction_names = [a["name"] for a in city_attractions[:6]]
    
    plans = []
    for i in range(days):
        if i == 0:
            plans.append(("Arrival & First Impressions", [
                ("14:00", "Check in to hotel and freshen up", "🏨"),
                ("16:00", f"First walk around {dest} city centre", "🚶"),
                ("18:30", f"Sunset at {attraction_names[0] if attraction_names else 'the waterfront'}", "🌅"),
                ("20:30", "Welcome dinner at a local restaurant", "🍽️"),
            ]))
        elif i == days - 1:
            plans.append(("Farewell & Departure", [
                ("08:00", "Final breakfast and packing", "☕"),
                ("09:30", f"Quick visit to {attraction_names[min(i, len(attraction_names)-1)] if attraction_names else 'local market'}", "📸"),
                ("11:30", "Last-minute souvenir shopping", "🎁"),
                ("13:00", "Hotel check-out", "🏨"),
                ("15:00", "Head to station/airport", "🚉"),
            ]))
        else:
            morning_spot = attraction_names[min(i, len(attraction_names)-1)] if attraction_names else f"Day {i+1} Exploration"
            plans.append((f"Exploring {dest} — Day {i+1}", [
                ("08:30", "Breakfast at a local café", "☕"),
                ("09:30", f"Visit {morning_spot}", "🏛️"),
                ("12:30", "Lunch at a recommended local restaurant", "🍛"),
                ("14:30", "Afternoon sightseeing", "🗺️"),
                ("17:00", "Leisure time / shopping", "🛍️"),
                ("20:00", "Dinner and evening out", "🌙"),
            ]))
    
    return [{"day": i+1, "title": t, "activities": [{"time": tm, "activity": a, "emoji": e} for tm, a, e in acts]}
            for i, (t, acts) in enumerate(plans)]


def _mock_packing(analysis):
    dest = analysis.get("destination", "Goa")
    season = analysis.get("season", "winter")
    trip_type = analysis.get("trip_type", "leisure")
    
    season_clothing = {
        "summer": ["Light cotton shirts (3-4)", "Shorts or light trousers", "Sun hat / cap", "Sunglasses", "Comfortable sandals"],
        "monsoon": ["Rain jacket / poncho", "Quick-dry clothes", "Waterproof footwear", "Umbrella", "Extra set of clothes"],
        "winter": ["Light jacket or fleece", "Mix of t-shirts and full sleeves", "Comfortable trousers", "Walking shoes", "Scarf"],
        "spring": ["Light cotton clothes", "A light layer for evenings", "Comfortable walking shoes", "Sunglasses"],
    }
    
    return {
        "Essentials": ["Valid ID / Aadhaar Card", "Travel tickets & bookings (downloaded offline)", "Cash + UPI-linked debit card", "Travel insurance documents", "Phone + charger"],
        "Clothing": season_clothing.get(season, season_clothing["winter"]),
        "Toiletries": ["Sunscreen SPF 50+", "Insect repellent (essential in coastal/forested areas)", "Moisturiser", "Travel-size shampoo & soap", "Hand sanitiser", "Personal medications"],
        "Electronics": ["Camera & extra memory cards", "Power bank (10000mAh+)", "Universal travel adapter", "Earphones / AirPods"],
        "Documents": ["E-tickets (downloaded, not just screenshot)", "Hotel booking confirmations", "Emergency contacts list", "Trip itinerary copy"],
        "Destination-Specific": [
            f"Beach bag and towel" if dest in ["Goa", "Goa", "Chennai", "Kerala"] else f"Comfortable walking shoes for {dest} sightseeing",
            "Waterproof bag for electronics near water",
            "Reusable water bottle (stay hydrated!)",
            f"Modest clothing for temple visits" if dest in ["Jaipur", "Varanasi", "Chennai", "Madurai"] else "Casual wear for evenings",
        ]
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


def _mock_weather(analysis):
    dest = analysis.get("destination", "Goa")
    season = analysis.get("season", "winter")
    
    weather_by_season = {
        "summer": {"emoji": "☀️", "temp_high": 38, "temp_low": 28, "condition": "Hot and sunny", "humidity": 55, "rain_chance": 5, "uv_index": 10, "advice": "Stay hydrated. Light cotton clothes, sunscreen and hat essential."},
        "monsoon": {"emoji": "🌧️", "temp_high": 28, "temp_low": 22, "condition": "Heavy showers with bright spells", "humidity": 90, "rain_chance": 80, "uv_index": 3, "advice": "Pack waterproofs and quick-dry clothes. Evenings can be beautiful between showers."},
        "winter": {"emoji": "⛅", "temp_high": 30, "temp_low": 18, "condition": "Pleasantly cool and clear", "humidity": 60, "rain_chance": 5, "uv_index": 6, "advice": "Perfect travel weather. Light layers for evenings, sunscreen for daytime."},
        "spring": {"emoji": "🌤️", "temp_high": 33, "temp_low": 22, "condition": "Warm and mostly sunny", "humidity": 65, "rain_chance": 10, "uv_index": 7, "advice": "Light cotton clothes. Sunscreen and a light scarf for dusty areas."},
    }
    
    w = weather_by_season.get(season, weather_by_season["winter"])
    w["forecast"] = [
        {"day": "Mon", "emoji": "☀️", "high": w["temp_high"], "low": w["temp_low"]},
        {"day": "Tue", "emoji": "⛅", "high": w["temp_high"]-2, "low": w["temp_low"]-1},
        {"day": "Wed", "emoji": "🌧️" if season == "monsoon" else "⛅", "high": w["temp_high"]-4, "low": w["temp_low"]-2},
        {"day": "Thu", "emoji": "☀️", "high": w["temp_high"]+1, "low": w["temp_low"]+1},
        {"day": "Fri", "emoji": "⛅", "high": w["temp_high"]-1, "low": w["temp_low"]},
    ]
    return w


def _mock_savings_tips(analysis):
    dest = analysis.get("destination", "Goa")
    return [
        f"Book train/bus tickets 60-90 days in advance for the best prices — Tatkal seats are 30-40% more expensive",
        f"Eat at local restaurants and thali spots in {dest} — authentic food at one-third the tourist restaurant price",
        f"Use IRCTC app for train tickets and avoid touts — all tickets are the same price from source",
        f"Opt for homestays in {dest} via Airbnb or local listings — often 40% cheaper than equivalent hotels",
    ]


def _mock_local_foods(dest):
    city_foods = {
        "Goa": [
            {"name": "Fish Curry Rice", "emoji": "🐟", "description": "Goa's daily staple — a tangy kokum-based fish curry with steamed red rice", "why_famous": "The definitive Goan meal eaten by locals every single day", "where_to_try": "Ritz Classic Restaurant, Panaji or any local toddy shop"},
            {"name": "Prawn Balchão", "emoji": "🦐", "description": "Fiery preserved prawns cooked in a spiced vinegar masala", "why_famous": "A Portuguese-influenced Goan preserve — uniquely tart, spicy and pungent", "where_to_try": "Florentine Restaurant, Anjuna"},
            {"name": "Bebinca", "emoji": "🍮", "description": "A layered Goan dessert made from coconut milk, eggs, and ghee", "why_famous": "The queen of Goan sweets — takes hours to make but worth every bite", "where_to_try": "Confeitaria 31 de Janeiro, Panaji"},
            {"name": "Choriz Pão", "emoji": "🌭", "description": "Spicy Goan chorizo stuffed in crusty local bread (pão)", "why_famous": "A Portuguese-Goan street snack — smoky, spicy and impossible to eat just one", "where_to_try": "Margao Municipal Market or any Mapusa bakery"},
        ],
        "Chennai": [
            {"name": "Chettinad Chicken Curry", "emoji": "🍗", "description": "Deeply spiced curry from the Chettinad region with kalpasi and marathi mokku", "why_famous": "Among India's most complex curries — a symphony of 20+ spices", "where_to_try": "Anjappar Chettinad Restaurant, T. Nagar"},
            {"name": "Idli Sambar", "emoji": "🫓", "description": "Soft steamed rice cakes with lentil-based sambar and chutneys", "why_famous": "Chennai's beloved breakfast — lighter, softer and tangier than anywhere else in India", "where_to_try": "Murugan Idli Shop, T. Nagar — famous since 1946"},
            {"name": "Filter Coffee", "emoji": "☕", "description": "Strong decoction coffee mixed with frothy hot milk, served in a davara-tumbler", "why_famous": "Chennai's filter coffee ritual is a daily meditation — the frothy pour is an art form", "where_to_try": "Saravana Bhavan or any Brahmin's Coffee Bar"},
            {"name": "Kothu Parotta", "emoji": "🥘", "description": "Flaky layered flatbread shredded and stir-fried with eggs, vegetables, and curry", "why_famous": "A Chennai midnight street food classic — the rhythmic clatter of iron blades is its signature sound", "where_to_try": "Burma Bazaar area or any roadside kadai, open late"},
        ],
        "Jaipur": [
            {"name": "Dal Baati Churma", "emoji": "🫙", "description": "Baked wheat balls served with five-lentil dal and sweet crushed wheat churma", "why_famous": "Rajasthan's most iconic dish — the baati is cooked in cow dung fire traditionally", "where_to_try": "Chokhi Dhani or Handi Restaurant, C-Scheme"},
            {"name": "Laal Maas", "emoji": "🍖", "description": "Fiery mutton curry cooked with Mathania red chillies — Jaipur's most prized meat dish", "why_famous": "Historically a royal hunting camp recipe — its red colour comes from the unique Mathania chilli", "where_to_try": "Suvarna Mahal, Rambagh Palace (splurge) or Niros Restaurant, MI Road"},
            {"name": "Pyaaz Kachori", "emoji": "🥟", "description": "Deep-fried pastry filled with spiced onion and lentil mixture", "why_famous": "Jaipur's most beloved street breakfast — the filling is sweet-spicy and uniquely Rajasthani", "where_to_try": "Rawat Mishthan Bhandar, Station Road — open since 1948"},
            {"name": "Ghewar", "emoji": "🍯", "description": "A disc-shaped honeycomb sweet made from flour soaked in sugar syrup and topped with rabri", "why_famous": "Rajasthan's festival sweet — especially famous in Jaipur during Teej and Raksha Bandhan", "where_to_try": "Laxmi Misthan Bhandar (LMB), Johari Bazaar"},
        ],
    }
    default_foods = [
        {"name": f"{dest} Thali", "emoji": "🍽️", "description": "A complete regional meal with rice, dal, vegetables, and local accompaniments", "why_famous": f"The best way to taste the full spectrum of {dest}'s cuisine in one sitting", "where_to_try": f"Any traditional restaurant in {dest} city centre"},
        {"name": "Local Street Chaat", "emoji": "🥗", "description": "Tangy, spicy street snacks unique to this region", "why_famous": "Every Indian city has its own chaat style — this version reflects local spice preferences", "where_to_try": f"Evening street food market in {dest}"},
        {"name": "Regional Biryani", "emoji": "🍚", "description": "Aromatic rice dish cooked with local spices and technique", "why_famous": f"Biryani cooked in {dest}'s style uses distinct local spices and cooking method", "where_to_try": f"Old quarter of {dest}"},
    ]
    return city_foods.get(dest, default_foods)


def _mock_hidden_gems(dest):
    city_gems = {
        "Goa": [
            {"name": "Divar Island", "emoji": "🏝️", "type": "Nature/Culture", "why_special": "A sleepy island in the Mandovi river with zero tourists, colonial churches, and cycling paths through paddy fields", "tip": "Take the free government ferry from Old Goa — cycles can be rented on the island for ₹100/day"},
            {"name": "Cabo de Rama Fort", "emoji": "🏰", "type": "Heritage", "why_special": "An ancient fort on a cliff with sweeping ocean views — far less visited than Chapora or Aguada", "tip": "Go at 5 PM for stunning sunset views with almost no other tourists"},
            {"name": "Mandrem Beach", "emoji": "🏖️", "type": "Beach", "why_special": "North Goa's best-kept secret — pristine, uncrowded, with turtle nesting spots", "tip": "Walk 20 min from the village to reach the most secluded stretch"},
        ],
        "Chennai": [
            {"name": "Cholamandal Artists Village", "emoji": "🎨", "type": "Art/Culture", "why_special": "India's largest artists' commune — a working art village with galleries and studios that tourists almost never visit", "tip": "Visit on weekday mornings when artists are working — entry is free"},
            {"name": "Semmozhi Poonga Botanical Garden", "emoji": "🌿", "type": "Nature", "why_special": "A hidden urban botanical garden with 500+ plant species in the heart of the city — Chennai's green secret", "tip": "Early morning visit before 8 AM when it's quiet and perfect for photography"},
            {"name": "Parry's Corner", "emoji": "🏛️", "type": "Heritage/Commerce", "why_special": "Chennai's oldest commercial district with colonial-era architecture — a living museum of mercantile history", "tip": "Explore the narrow lanes behind NSC Bose Road — the spice traders' warehouses are 150 years old"},
        ],
        "Jaipur": [
            {"name": "Panna Meena Ka Kund", "emoji": "🔷", "type": "Heritage", "why_special": "A 16th-century stepwell with a perfect geometrical staircase — eerily empty despite being near Amer Fort", "tip": "Visit at 8 AM — you'll likely have it entirely to yourself for dramatic photos"},
            {"name": "Galta Ji (Monkey Temple)", "emoji": "🐒", "type": "Temple/Nature", "why_special": "An ancient temple complex in a mountain gorge with natural spring pools — far more atmospheric than Amer", "tip": "Go early morning, dress modestly — the views from the hilltop are better than Nahargarh"},
            {"name": "Bapu Bazaar at Night", "emoji": "🌙", "type": "Shopping/Culture", "why_special": "Jaipur's local textile market lit up at night — where Jaipuris actually shop, not tourists", "tip": "Go after 7 PM — prices are 30-40% lower than Johari Bazaar and the selection is better"},
        ],
    }
    default_gems = [
        {"name": f"{dest} Old Quarter Back Lanes", "emoji": "🏘️", "type": "Heritage", "why_special": f"The historic lanes behind {dest}'s main bazaar area where locals live and trade — rarely on tourist maps", "tip": "Hire a local guide for ₹200-300 to navigate properly"},
        {"name": f"{dest} Riverside/Lakeside at Dawn", "emoji": "🌅", "type": "Nature", "why_special": "The local waterfront at sunrise when the city's daily rituals begin — a photographer's paradise", "tip": "Arrive 30 minutes before sunrise for the best light"},
        {"name": f"Local Morning Market in {dest}", "emoji": "🛒", "type": "Culture", "why_special": "Where locals buy fresh produce, flowers, and street food at 6 AM — the real heartbeat of the city", "tip": "Best visited 6-8 AM before the heat sets in"},
    ]
    return city_gems.get(dest, default_gems)


def _mock_local_experiences(analysis):
    dest = analysis.get("destination", "Goa")
    trip_type = analysis.get("trip_type", "leisure")
    
    base = [
        {"experience": f"Sunrise Photography Walk in {dest}", "emoji": "📸", "description": f"Join local photographers for a guided sunrise walk through {dest}'s most photogenic spots — the light transforms the city", "best_for": "solo"},
        {"experience": "Local Cooking Class", "emoji": "👨‍🍳", "description": f"Learn to cook 3-4 authentic {dest} dishes in a local home — includes a market visit to source ingredients", "best_for": "couple"},
        {"experience": "Rickshaw Food Tour", "emoji": "🛺", "description": f"A 3-hour auto-rickshaw tour of {dest}'s best street food stalls — guided by a local food blogger", "best_for": "group"},
        {"experience": f"{dest} Heritage Walk", "emoji": "🚶", "description": f"A 2-hour walking tour through the historic core of {dest} with a certified local guide covering architecture, history and stories", "best_for": "family"},
        {"experience": "Village Day Trip", "emoji": "🌾", "description": f"Hire a local driver for a day to visit a nearby traditional village within 30km of {dest} — see rural life unchanged for centuries", "best_for": "family"},
    ]
    
    if trip_type == "romantic":
        base.insert(0, {"experience": "Sunset Boat Cruise", "emoji": "🚢", "description": f"A private sunset cruise along {dest}'s waterway with dinner — the most romantic experience the city offers", "best_for": "couple"})
    elif trip_type == "adventure":
        base.insert(0, {"experience": "Early Morning Trek", "emoji": "🥾", "description": f"A pre-dawn trek to the highest viewpoint near {dest} — reaching the top at sunrise is one of life's great experiences", "best_for": "group"})
    
    return base[:5]


def _mock_travel_tips(analysis):
    dest = analysis.get("destination", "Goa")
    season = analysis.get("season", "winter")
    budget = analysis.get("budget", "medium")
    
    return [
        f"Use Ola/Uber for inter-city travel in {dest} — auto-rickshaws often quote tourist prices; always ask for meter or use apps",
        f"Dress modestly when visiting temples and religious sites in {dest} — carry a scarf or dupatta to cover shoulders",
        f"Book train tickets via IRCTC app 60-90 days in advance — Tatkal quota opens 1 day before at 10 AM and sells in minutes",
        f"Carry a water bottle and stay hydrated — tap water in {dest} is not safe to drink; buy 1L bottles from general stores, not tourist shops",
        f"Learn 5-10 words of the local language — even 'dhanyavaad' (thank you) or 'kitna hua' (how much) gets a very warm response",
        f"Beware of gem stone shops and 'government-approved' stores near tourist sites — these are almost always tourist traps with 500% markups",
        f"In {dest}, pay entry fees only at official government-staffed counters — touts outside monuments often sell unofficial tickets at double the price",
    ]


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
    fig.update_layout(height=300, **{k:v for k,v in PLOTLY_LAYOUT.items() if k in ["paper_bgcolor","plot_bgcolor","font","margin"]},
        yaxis=dict(title="Total Cost (₹)", tickfont=dict(color="#7070a0"), gridcolor="#2a2a3a"),
        yaxis2=dict(title="Rating", tickfont=dict(color="#ff6b9d"), overlaying="y", side="right", range=[0, 5]),
        barmode="group", legend=dict(orientation="h", y=-0.2))
    return fig


def weather_forecast_chart(forecast):
    fig = go.Figure()

    if isinstance(forecast, list) and forecast:
        # New format: list of {day, emoji, high, low}
        if "day" in forecast[0]:
            days = [f.get("day", "") for f in forecast]
            highs = [f.get("high", 0) for f in forecast]
            lows = [f.get("low", 0) for f in forecast]
            fig.add_trace(go.Scatter(x=days, y=highs, mode="lines+markers", name="High °C",
                line=dict(color="#ff6b9d", width=2), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=days, y=lows, mode="lines+markers", name="Low °C",
                line=dict(color="#7c6bff", width=2), marker=dict(size=8)))
        else:
            dates = [item.get("date") or item.get("time") or item.get("datetime") for item in forecast]
            temps = [item.get("temperature") or item.get("temp") or item.get("temperature_2m") for item in forecast]
            fig.add_trace(go.Scatter(x=dates, y=temps, mode="lines+markers", name="Temperature"))
    elif isinstance(forecast, dict):
        dates = forecast.get("date") or forecast.get("time") or forecast.get("dates")
        temps = forecast.get("temperature") or forecast.get("temp") or forecast.get("temperature_2m")
        fig.add_trace(go.Scatter(x=dates, y=temps, mode="lines+markers", name="Temperature"))

    fig.update_layout(**PLOTLY_LAYOUT, height=200)
    fig.update_yaxes(gridcolor="#2a2a3a", ticksuffix="°C")
    fig.update_xaxes(gridcolor="#1e1e2e")
    fig.update_layout(legend=dict(orientation="h", y=-0.3))
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
            fillcolor="rgba(255,107,157,0.25)",
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
        st.success("✓ API key set — using Gemini AI for accurate, destination-specific data")
    else:
        st.info("No key → Demo mode with curated sample data (Goa, Chennai, Jaipur fully detailed)")

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
            with st.spinner("VoyageAI is reading your plan and fetching destination-specific data…"):
                # MASTER CALL: one comprehensive AI request for all trip data
                master_data = analyze_trip_master(tour_input)
                
                if master_data:
                    # AI succeeded — extract all data from master response
                    st.session_state._master_data = master_data
                    analysis = extract_analysis(master_data)
                    st.session_state.ai_analysis = analysis
                    st.session_state.weather = master_data.get("weather", {})
                    st.session_state.attractions = master_data.get("attractions", [])
                    st.session_state.transport_options = master_data.get("transport_options", [])
                    st.session_state.hotels = master_data.get("hotels", [])
                    st.session_state.itinerary = master_data.get("itinerary", [])
                    st.session_state.packing_list = master_data.get("packing_list", {})
                    st.session_state.budget_breakdown = master_data.get("budget_breakdown", {})
                    st.session_state._savings_tips = master_data.get("savings_tips", [])
                    # New TravelGPT Elite fields
                    st.session_state.local_foods = master_data.get("local_foods", [])
                    st.session_state.hidden_gems = master_data.get("hidden_gems", [])
                    st.session_state.local_experiences = master_data.get("local_experiences", [])
                    st.session_state.travel_tips = master_data.get("travel_tips", [])
                else:
                    # Fallback: mock data with city-specific content
                    analysis = _mock_analysis(tour_input)
                    st.session_state.ai_analysis = analysis
                    st.session_state.weather = _mock_weather(analysis)
                    dest = analysis.get("destination", "Goa")
                    st.session_state.attractions = _get_city_attractions(dest)
                    st.session_state.transport_options = _mock_transport(analysis)
                    st.session_state.hotels = _get_city_hotels(dest, analysis.get("duration_days", 5))
                    st.session_state.itinerary = _mock_itinerary(analysis)
                    st.session_state.packing_list = _mock_packing(analysis)
                    st.session_state._savings_tips = _mock_savings_tips(analysis)
                    st.session_state.local_foods = _mock_local_foods(dest)
                    st.session_state.hidden_gems = _mock_hidden_gems(dest)
                    st.session_state.local_experiences = _mock_local_experiences(analysis)
                    st.session_state.travel_tips = _mock_travel_tips(analysis)
                    # Budget breakdown computed after transport selection — defer
                    st.session_state.budget_breakdown = {}

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

    # Attractions — already fetched in step 1 master call
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
  <div style="font-size:0.72rem;color:#7070a0;margin-top:0.4rem;line-height:1.4;">{a.get("description") or a.get("tip","")}</div>
  <div style="font-size:0.7rem;color:#00d4aa;margin-top:0.3rem;line-height:1.3;font-style:italic;">{("💡 " + a["tip"]) if a.get("description") and a.get("tip") else ""}</div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Trip Highlight Banner ──
    highlight = analysis.get("trip_highlight", "")
    if highlight:
        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(255,107,157,0.1),rgba(124,107,255,0.1));border:1px solid rgba(255,107,157,0.25);border-radius:14px;padding:1rem 1.4rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:0.8rem;">
  <span style="font-size:1.4rem;">✨</span>
  <div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#ff6b9d;margin-bottom:0.25rem;">Trip Highlight</div>
    <div style="font-size:0.9rem;color:#e8e8f0;font-weight:500;">{highlight}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Local Foods ──
    local_foods = st.session_state.local_foods
    if local_foods:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🍛 Must-Try Food in {analysis.get("destination","")}</div>', unsafe_allow_html=True)
        food_cols = st.columns(2)
        for i, food in enumerate(local_foods):
            with food_cols[i % 2]:
                st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;margin-bottom:0.8rem;transition:all 0.3s;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
    <span style="font-size:1.5rem;">{food.get("emoji","🍛")}</span>
    <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.9rem;">{food.get("name","")}</div>
  </div>
  <div style="font-size:0.8rem;color:#a0a0c0;margin-bottom:0.4rem;line-height:1.5;">{food.get("description","")}</div>
  <div style="font-size:0.75rem;color:#ffd166;margin-bottom:0.35rem;">⭐ {food.get("why_famous","")}</div>
  <div style="font-size:0.72rem;color:#00d4aa;">📍 {food.get("where_to_try","")}</div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Hidden Gems + Local Experiences (side by side) ──
    hidden_gems = st.session_state.hidden_gems
    local_experiences = st.session_state.local_experiences
    if hidden_gems or local_experiences:
        gem_col, exp_col = st.columns(2)
        with gem_col:
            if hidden_gems:
                st.markdown('<div class="glass-card" style="height:100%">', unsafe_allow_html=True)
                st.markdown(f'<div class="section-title">💎 Hidden Gems</div>', unsafe_allow_html=True)
                for gem in hidden_gems:
                    st.markdown(f"""
<div style="background:var(--surface);border:1px solid rgba(124,107,255,0.2);border-radius:10px;padding:0.85rem;margin-bottom:0.7rem;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem;">
    <span style="font-size:1.2rem;">{gem.get("emoji","💎")}</span>
    <div>
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;">{gem.get("name","")}</div>
      <div style="font-size:0.65rem;color:#7c6bff;text-transform:uppercase;letter-spacing:0.08em;">{gem.get("type","")}</div>
    </div>
  </div>
  <div style="font-size:0.78rem;color:#a0a0c0;margin-bottom:0.35rem;line-height:1.4;">{gem.get("why_special","")}</div>
  <div style="font-size:0.72rem;color:#00d4aa;">💡 {gem.get("tip","")}</div>
</div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with exp_col:
            if local_experiences:
                st.markdown('<div class="glass-card" style="height:100%">', unsafe_allow_html=True)
                st.markdown(f'<div class="section-title">🎭 Local Experiences</div>', unsafe_allow_html=True)
                for exp in local_experiences:
                    best_for_color = {"couple": "#ff6b9d", "solo": "#7c6bff", "family": "#ffd166", "group": "#00d4aa"}.get(exp.get("best_for",""), "#7070a0")
                    st.markdown(f"""
<div style="background:var(--surface);border:1px solid rgba(255,107,157,0.15);border-radius:10px;padding:0.85rem;margin-bottom:0.7rem;">
  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem;">
    <span style="font-size:1.2rem;">{exp.get("emoji","🎭")}</span>
    <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.85rem;">{exp.get("experience","")}</div>
  </div>
  <div style="font-size:0.78rem;color:#a0a0c0;margin-bottom:0.35rem;line-height:1.4;">{exp.get("description","")}</div>
  <div style="display:inline-block;background:rgba(255,255,255,0.05);border-radius:20px;padding:0.15rem 0.6rem;font-size:0.65rem;color:{best_for_color};font-family:'Space Grotesk';">Best for {exp.get("best_for","all")}</div>
</div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Travel Tips ──
    travel_tips = st.session_state.travel_tips
    if travel_tips:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🧭 Travel Tips for {analysis.get("destination","")}</div>', unsafe_allow_html=True)
        tip_icons = ["🚗", "🙏", "💳", "🔒", "🌦️", "🤝", "⚠️"]
        for idx, tip in enumerate(travel_tips):
            icon = tip_icons[idx % len(tip_icons)]
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:0.7rem;padding:0.6rem 0.8rem;border-radius:8px;margin-bottom:0.4rem;background:rgba(124,107,255,0.04);border-left:3px solid rgba(124,107,255,0.3);">
  <span style="font-size:1rem;margin-top:0.05rem;">{icon}</span>
  <span style="font-size:0.83rem;color:#c0c0d8;line-height:1.5;">{tip}</span>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Edit Trip", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("View Transport Options →", use_container_width=True):
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
                # Compute budget breakdown now that transport is selected
                if not st.session_state.budget_breakdown:
                    chosen = next((o for o in options if o["id"] == st.session_state.selected_transport), options[0] if options else {})
                    transport_cost = chosen.get("price_per_person", 0) * analysis.get("travelers", 1)
                    st.session_state.budget_breakdown = _mock_budget(analysis, transport_cost)
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

        breakdown = st.session_state.budget_breakdown
        if not breakdown:
            transport_cost = chosen.get("price_per_person", 0) * pax
            breakdown = _mock_budget(analysis, transport_cost)
            st.session_state.budget_breakdown = breakdown

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
        savings_tips = st.session_state.get("_savings_tips", _mock_savings_tips(analysis))
        for tip in savings_tips:
            st.markdown(f'<div class="savings-pill">💚 {tip}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🎒 AI Packing List</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.8rem;color:#7070a0;margin-bottom:1rem;">Personalised for {analysis.get("destination","")} · {analysis.get("season","").title()} · {analysis.get("trip_type","").title()} trip</div>', unsafe_allow_html=True)

        packing = st.session_state.packing_list
        if not packing:
            packing = _mock_packing(analysis)
            st.session_state.packing_list = packing

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
        if st.button("View Itinerary →", use_container_width=True):
            # Itinerary already generated in step 1 master call
            if not st.session_state.itinerary:
                st.session_state.itinerary = _mock_itinerary(analysis)
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

    # ── Travel Tips recap on itinerary page ──
    travel_tips = st.session_state.travel_tips
    if travel_tips:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🧭 Before You Go — Travel Tips</div>', unsafe_allow_html=True)
        tip_icons = ["🚗", "🙏", "💳", "🔒", "🌦️", "🤝", "⚠️"]
        tip_cols = st.columns(2)
        for idx, tip in enumerate(travel_tips):
            with tip_cols[idx % 2]:
                icon = tip_icons[idx % len(tip_icons)]
                st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:0.6rem;padding:0.55rem 0.7rem;border-radius:8px;margin-bottom:0.4rem;background:rgba(124,107,255,0.04);border-left:3px solid rgba(124,107,255,0.3);">
  <span style="font-size:0.95rem;margin-top:0.05rem;">{icon}</span>
  <span style="font-size:0.8rem;color:#c0c0d8;line-height:1.5;">{tip}</span>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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
