# 🌍 VoyageAI — Smart Travel Planner

An AI-powered Streamlit travel planning app. Describe your trip in plain English, and VoyageAI:
- **Analyzes** your plan using Gemini AI via LangChain
- **Fetches** realistic train/bus/flight options
- **Builds** a day-by-day itinerary
- **Confirms** your booking with a PNR

---

## 🚀 Quick Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Get a Gemini API Key (Free)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API key"  
3. Paste it in the sidebar → instant AI power!

> Without a key, the app runs in demo mode with realistic sample data.

---

## Tech Stack
- **Streamlit** — UI framework
- **LangChain** — AI orchestration layer  
- **Gemini 1.5 Flash** — Language model (via langchain-google-genai)
- **Custom CSS** — Dark animated UI with Space Grotesk typography

## Example Prompts

- "I want to travel from Kolkata to Goa next week for 5 days with my girlfriend. We love beaches and seafood. Budget is medium."
- "Solo trip from Delhi to Jaipur for 3 days to explore forts and eat street food. Low budget."
- "Family trip (4 people) from Mumbai to Kerala for 7 days in December."

- https://travelselectorapp-jceugubclkbalfty8mknbj.streamlit.app/
