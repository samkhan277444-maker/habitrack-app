import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date, timedelta

st.set_page_config(page_title="HABITRACK", page_icon="👣", layout="wide")
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; color: #FF4B4B; text-align: center; }
    .tagline { font-size: 1.2rem; color: #4B4B4B; text-align: center; font-style: italic; }
    .sidebar-brand { font-size: 1.8rem; font-weight: bold; color: #FF4B4B; text-align: center; }
</style>
""", unsafe_allow_html=True)

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if "user" not in st.session_state: st.session_state.user = None

TEMPLATES = {
    "🏃 Health & Fitness": ["10,000 Steps", "30 Min Jogging", "15 Min Yoga", "8 Glasses Water", "Gym 3x Week", "Sleep before 11 PM"],
    "🧠 Mental Health": ["10 Min Meditation", "Gratitude Journal", "Read 10 Pages", "No Scrolling"],
    "💼 Productivity": ["Wake at 6 AM", "Plan Top 3 Tasks", "Pomodoro 25 Min", "Deep Work 2hrs"],
    "💰 Finance": ["Track Expenses", "Save 20% Income", "No Impulse Buying"],
    "👨‍👩‍👧‍👦 Social": ["15 Min Family Talk", "Call 1 Friend", "Screen-free Dinner"],
    "🎨 Hobbies": ["15 Min Guitar", "Cook New Recipe", "Watch 1 Movie"],
    "🚀 High Performance": ["90 Min Deep Work", "Eat the Frog", "30 Min Skill", "Send Value Message", "Cold Shower"]
}

def login_screen():
    st.markdown('<div class="main-title">👣 HABITRACK</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">✨ Har roz ek naya footprint.</div>', unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login / Signup"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = res.user; st.rerun()
        except:
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                st.session_state.user = res.user; st.success("Account created! Login again."); st.rerun()
            except: st.error("Login failed.")

def dashboard():
    user_id = st.session_state.user.id
    habits = supabase.table("habits").select("*").eq("user_id", user_id).execute()
    checkins = supabase.table("check_ins").select("*").eq("user_id", user_id).execute()
    st.markdown('<div class="main-title">👣 HABITRACK</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">"Har roz ek naya footprint."</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Habits", len(habits.data))
    today = date.today().isoformat()
    done = sum(1 for c in checkins.data if c['date'] == today and c['is_completed'])
    c2.metric("Today Done", done)
    c3.metric("Streak", 5) # simplified for demo
    st.subheader("🔥 Add habits and check-in to see your heatmap!")

def add_habit():
    user_id = st.session_state.user.id
    st.markdown('<div class="main-title">➕ Add Habit</div>', unsafe_allow_html=True)
    mode = st.radio("", ["Custom", "Browse Templates"])
    if mode == "Custom":
        name = st.text_input("Name")
        if st.button("Add"):
            supabase.table("habits").insert({"user_id": user_id, "name": name, "icon": "✅"}).execute()
            st.success("Added!"); st.rerun()
    else:
        for cat, habits in TEMPLATES.items():
            with st.expander(cat):
                for h in habits:
                    if st.button(f"+ {h}", key=h):
                        supabase.table("habits").insert({"user_id": user_id, "name": h, "icon": "✅", "category": cat}).execute()
                        st.rerun()

if not st.session_state.user:
    login_screen()
else:
    st.sidebar.markdown('<div class="sidebar-brand">HABITRACK</div>', unsafe_allow_html=True)
    st.sidebar.write(f"👋 {st.session_state.user.email}")
    menu = st.sidebar.radio("", ["📊 Dashboard", "➕ Add Habit"])
    if menu == "📊 Dashboard": dashboard()
    else: add_habit()
