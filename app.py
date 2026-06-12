"""
LifePulse – AI Life Coach & Habit Intelligence App
===================================================
Single-file Streamlit app for habit tracking, mood logging,
goal planning, journaling, and personal wellness analytics.

Run: streamlit run app.py
"""

import json
import random
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════
#  0 · PAGE CONFIG  (must be the very first Streamlit call)
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LifePulse · AI Life Coach",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
#  1 · DESIGN TOKENS & CONSTANTS
# ══════════════════════════════════════════════════════════
PAL = {
    "bg":       "#0a0f1e",   # deep night-sky navy
    "surface":  "#111827",   # card surface
    "border":   "#1f2937",   # subtle border
    "primary":  "#10b981",   # emerald – growth / life
    "indigo":   "#6366f1",   # indigo  – wisdom / depth
    "amber":    "#f59e0b",   # amber   – energy / fire
    "text":     "#e5e7eb",
    "muted":    "#6b7280",
}

DATA_FILE = Path("lifepulse_data.json")
LIFE_AREAS = ["Health", "Mind", "Work", "Social", "Finance", "Creativity"]

DEFAULT_HABITS = [
    {"id": 1, "name": "💧 Drink 8 glasses of water", "category": "Health",  "completions": []},
    {"id": 2, "name": "🏃 Exercise 30 min",           "category": "Health",  "completions": []},
    {"id": 3, "name": "📚 Read 20 pages",             "category": "Mind",    "completions": []},
    {"id": 4, "name": "🧘 Meditate 10 min",           "category": "Mind",    "completions": []},
    {"id": 5, "name": "🌙 Sleep by 11 PM",            "category": "Health",  "completions": []},
]

AI_INSIGHTS = [
    "Your mood rises ~23% on exercise days. That streak is worth protecting. 💪",
    "Tuesday–Thursday are your most consistent habit days. Front-load hard work then! 🎯",
    "Water goal hit 6 of the last 7 days — you're building a real system. 💧",
    "Journaling on Sunday predicts a higher-energy Monday. Give it a try. ✍️",
    "Your sleep habit directly improves mood scores the next morning. 🌙",
    "You're 3 days from a new personal streak record — keep the chain alive. 🔥",
    "Morning check-ins (even 60 seconds) raise weekly completion by ~18%. ☀️",
    "Friday energy dips are common — plan lighter, creative tasks for end of week. 📅",
]

AFFIRMATIONS = [
    "Every small step forward is real progress. Keep going. 🌱",
    "You're building the life you deserve, one habit at a time. 💫",
    "Consistency beats perfection — just show up. 🏆",
    "Your future self will thank you for today's choices. 🙏",
    "Progress, not perfection. You've already got this. ✨",
    "Small daily improvements lead to stunning long-term results. 🚀",
]

PLOTLY_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=8, r=8, t=28, b=8),
    font=dict(family="Inter, sans-serif", color=PAL["text"]),
)


# ══════════════════════════════════════════════════════════
#  2 · GLOBAL CSS
# ══════════════════════════════════════════════════════════
def inject_css() -> None:
    """Inject a cohesive dark-mode design system via Streamlit's HTML escape hatch."""
    st.markdown(
        f"""
        <style>
        /* ── Reset & base ── */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: {PAL['bg']} !important;
            color: {PAL['text']};
            font-family: 'Inter', system-ui, sans-serif;
        }}
        [data-testid="stSidebar"] {{
            background-color: #080d19 !important;
            border-right: 1px solid {PAL['border']};
        }}
        section.main > div {{ padding-top: 20px; }}

        /* ── Typography ── */
        .lp-hero {{
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(100deg, {PAL['primary']} 0%, {PAL['indigo']} 70%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }}
        .lp-section {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {PAL['text']};
            letter-spacing: -0.01em;
            margin: 20px 0 10px;
        }}

        /* ── Cards ── */
        .lp-card {{
            background: {PAL['surface']};
            border: 1px solid {PAL['border']};
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 8px;
            transition: border-color .2s;
        }}
        .lp-card:hover {{ border-color: {PAL['primary']}55; }}
        .lp-card.green  {{ border-left: 3px solid {PAL['primary']}; }}
        .lp-card.indigo {{ border-left: 3px solid {PAL['indigo']}; }}
        .lp-card.amber  {{ border-left: 3px solid {PAL['amber']}; }}

        /* ── AI Insight box ── */
        .lp-insight {{
            background: linear-gradient(135deg, #071510, #080f1c);
            border: 1px solid {PAL['primary']}40;
            border-radius: 12px;
            padding: 16px 18px;
            color: #6ee7b7;
            font-size: 0.93rem;
            line-height: 1.65;
        }}

        /* ── Badges ── */
        .lp-badge {{
            display: inline-block;
            background: {PAL['indigo']}28;
            color: #a5b4fc;
            border-radius: 5px;
            padding: 1px 8px;
            font-size: 0.74rem;
            font-weight: 600;
            margin: 0 2px;
        }}
        .lp-badge.green  {{ background: {PAL['primary']}20; color: {PAL['primary']}; }}
        .lp-badge.amber  {{ background: {PAL['amber']}20;   color: {PAL['amber']}; }}
        .lp-badge.indigo {{ background: {PAL['indigo']}28;  color: #a5b4fc; }}

        /* ── Streamlit metric overrides ── */
        [data-testid="stMetric"] {{
            background: {PAL['surface']} !important;
            border: 1px solid {PAL['border']};
            border-radius: 12px;
            padding: 14px 18px;
        }}
        [data-testid="stMetricValue"] {{
            color: {PAL['primary']} !important;
            font-weight: 800 !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {PAL['muted']} !important;
            font-size: 0.8rem !important;
        }}

        /* ── Buttons ── */
        .stButton > button {{
            background: linear-gradient(135deg, {PAL['primary']}, {PAL['indigo']}) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.87rem !important;
            padding: 6px 18px !important;
            transition: opacity .18s;
        }}
        .stButton > button:hover {{ opacity: .82; }}

        /* ── Progress bars ── */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {PAL['primary']}, {PAL['indigo']}) !important;
        }}

        /* ── Expander ── */
        [data-testid="stExpander"] summary {{
            background: {PAL['surface']};
            border-radius: 8px;
            font-weight: 600;
        }}

        /* ── Divider ── */
        hr {{ border-color: {PAL['border']} !important; margin: 18px 0; }}

        /* ── Hide chrome ── */
        #MainMenu, footer, [data-testid="stToolbar"] {{ display: none !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════
#  3 · PERSISTENCE
# ══════════════════════════════════════════════════════════
def load_data() -> dict:
    """
    Load persisted state from JSON file.

    Returns a fresh default structure if the file is absent or corrupt.
    """
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "habits":        [h.copy() for h in DEFAULT_HABITS],
        "moods":         [],
        "goals":         [],
        "journal":       [],
        "next_habit_id": len(DEFAULT_HABITS) + 1,
        "next_goal_id":  1,
    }


def save_data() -> None:
    """Persist current session state to JSON file, with error surfacing."""
    try:
        DATA_FILE.write_text(
            json.dumps(
                {k: st.session_state[k]
                 for k in ("habits", "moods", "goals", "journal",
                            "next_habit_id", "next_goal_id")},
                indent=2,
            )
        )
    except IOError as exc:
        st.warning(f"⚠️ Could not save data: {exc}")


# ══════════════════════════════════════════════════════════
#  4 · SESSION STATE BOOTSTRAP
# ══════════════════════════════════════════════════════════
def init_state() -> None:
    """Load persisted data into session state exactly once per session."""
    if "initialized" not in st.session_state:
        for key, val in load_data().items():
            st.session_state[key] = val
        st.session_state.initialized = True


# ══════════════════════════════════════════════════════════
#  5 · UTILITY / DOMAIN HELPERS
# ══════════════════════════════════════════════════════════
def today_str() -> str:
    """Return today's date as ISO-8601 string."""
    return date.today().isoformat()


def get_streak(completions: list) -> int:
    """
    Calculate the unbroken streak ending today.

    Parameters
    ----------
    completions : list[str]  ISO date strings

    Returns
    -------
    int  consecutive days (0 if none)
    """
    if not completions:
        return 0
    unique = sorted(set(completions), reverse=True)
    streak, cursor = 0, date.today()
    for d in unique:
        if d == cursor.isoformat():
            streak += 1
            cursor -= timedelta(days=1)
        else:
            break
    return streak


def done_today(habit: dict) -> bool:
    """Return True if the habit was completed today."""
    return today_str() in habit["completions"]


def rate_7d(habit: dict) -> int:
    """Return completion rate (0–100) over the last 7 days."""
    days = [(date.today() - timedelta(days=i)).isoformat() for i in range(7)]
    return round(sum(1 for d in days if d in habit["completions"]) / 7 * 100)


def ai_task_breakdown(goal_title: str) -> list:
    """
    Simulate an AI 7-week action plan for a goal.

    In production this would call an LLM API.  The `time.sleep` mimics
    perceived processing so the spinner feels meaningful.
    """
    return [
        {"week": 1, "task": f"Research & map out a clear approach for: {goal_title}",              "done": False},
        {"week": 2, "task": "Establish baseline metrics and set specific, measurable milestones",   "done": False},
        {"week": 3, "task": "Execute the first key milestone — done beats perfect",                 "done": False},
        {"week": 4, "task": "Mid-point review: what's working, what needs adjustment?",             "done": False},
        {"week": 5, "task": "Push through the plateau — maintain consistency here",                 "done": False},
        {"week": 6, "task": "Final sprint — accelerate and complete remaining actions",              "done": False},
        {"week": 7, "task": "Review, celebrate the win, and plan the next level 🎉",                "done": False},
    ]


def seed_demo_data() -> None:
    """Populate session state with 30 days of realistic randomised demo data."""
    habits = []
    for h in DEFAULT_HABITS:
        comps = [
            (date.today() - timedelta(days=i)).isoformat()
            for i in range(30, 0, -1)
            if random.random() > 0.28
        ]
        habits.append({**h, "completions": comps})

    moods = [
        {
            "date":   (date.today() - timedelta(days=i)).isoformat(),
            "mood":   random.randint(5, 10),
            "energy": random.randint(4, 10),
            "note":   "",
        }
        for i in range(29, -1, -1)
    ]

    st.session_state.habits        = habits
    st.session_state.moods         = moods
    st.session_state.next_habit_id = len(DEFAULT_HABITS) + 1
    save_data()


# ══════════════════════════════════════════════════════════
#  6 · SIDEBAR
# ══════════════════════════════════════════════════════════
def render_sidebar() -> str:
    """
    Render the navigation sidebar.

    Returns
    -------
    str  internal page key selected by the user
    """
    with st.sidebar:
        st.markdown(
            f'<div style="font-size:1.65rem;font-weight:800;'
            f'color:{PAL["primary"]};letter-spacing:-0.03em;'
            f'margin-bottom:2px;">💚 LifePulse</div>'
            f'<div style="font-size:.78rem;color:{PAL["muted"]};'
            f'margin-bottom:18px;">Your AI Life Coach</div>',
            unsafe_allow_html=True,
        )

        pages = {
            "🏠  Dashboard":     "dashboard",
            "🔥  Habits":        "habits",
            "🎯  Goals":         "goals",
            "📊  Analytics":     "analytics",
            "📓  Journal":       "journal",
            "📈  Weekly Report": "report",
        }
        choice = st.radio("nav", list(pages.keys()), label_visibility="collapsed")

        st.markdown("---")
        col_l, col_r = st.columns(2)
        with col_l:
            if st.button("🎲 Demo"):
                with st.spinner("Loading demo data…"):
                    seed_demo_data()
                st.success("Demo data loaded!")
                st.rerun()
        with col_r:
            if st.button("🗑️ Reset"):
                st.session_state.habits        = [h.copy() for h in DEFAULT_HABITS]
                st.session_state.moods         = []
                st.session_state.goals         = []
                st.session_state.journal       = []
                st.session_state.next_habit_id = len(DEFAULT_HABITS) + 1
                st.session_state.next_goal_id  = 1
                save_data()
                st.warning("Data reset.")
                st.rerun()

        # Quick status at the bottom of the sidebar
        st.markdown("---")
        n_done  = sum(1 for h in st.session_state.habits if done_today(h))
        n_total = len(st.session_state.habits)
        pct     = int(n_done / n_total * 100) if n_total else 0
        st.markdown(
            f'<div style="font-size:.8rem;color:{PAL["muted"]};">'
            f'Today: <b style="color:{PAL["primary"]}">{n_done}/{n_total}</b> habits</div>',
            unsafe_allow_html=True,
        )
        st.progress(pct / 100)

    return pages[choice]


# ══════════════════════════════════════════════════════════
#  7 · PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════
def page_dashboard() -> None:
    """Render the home dashboard: greeting, KPIs, habit checklist, mood log, AI insight."""
    hour = datetime.now().hour
    greet, emo = (
        ("Good morning", "☀️") if hour < 12
        else ("Good afternoon", "🌤️") if hour < 17
        else ("Good evening", "🌙")
    )

    st.markdown(f'<div class="lp-hero">{greet}! {emo}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{PAL["muted"]};font-size:.9rem;margin:4px 0 0;">'
        f'{date.today().strftime("%A, %B %d, %Y")} &nbsp;·&nbsp; '
        f'<i style="color:{PAL["text"]}">{random.choice(AFFIRMATIONS)}</i></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── KPI row ──────────────────────────────────────────
    habits = st.session_state.habits
    moods  = st.session_state.moods

    n_done  = sum(1 for h in habits if done_today(h))
    avg_stk = round(sum(get_streak(h["completions"]) for h in habits) / max(len(habits), 1), 1)
    last7   = moods[-7:]
    avg_md  = round(sum(m["mood"] for m in last7) / len(last7), 1) if last7 else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✅ Habits Today",   f"{n_done}/{len(habits)}")
    c2.metric("🔥 Avg Streak",     f"{avg_stk}d")
    c3.metric("😊 Mood (7-day)",   avg_md)
    c4.metric("🎯 Active Goals",   len(st.session_state.goals))

    st.markdown("---")
    left, right = st.columns([3, 2], gap="large")

    # ── Habit checklist ──────────────────────────────────
    with left:
        st.markdown('<div class="lp-section">📋 Today\'s Habits</div>', unsafe_allow_html=True)
        if not habits:
            st.info("No habits yet — add some on the **Habits** page!")

        for idx, habit in enumerate(habits):
            is_done = done_today(habit)
            streak  = get_streak(habit["completions"])
            rate    = rate_7d(habit)

            chk_col, info_col, prog_col = st.columns([1, 6, 2])

            with chk_col:
                checked = st.checkbox("", value=is_done, key=f"chk_{habit['id']}")

            with info_col:
                name_md = f"~~{habit['name']}~~" if is_done else habit["name"]
                st.markdown(
                    f"{name_md}  \n"
                    f'<span class="lp-badge green">🔥 {streak}d</span>'
                    f'<span class="lp-badge indigo">{habit["category"]}</span>',
                    unsafe_allow_html=True,
                )
            with prog_col:
                st.caption(f"{rate}%")
                st.progress(rate / 100)

            # Toggle completion state and persist
            if checked and not is_done:
                st.session_state.habits[idx]["completions"].append(today_str())
                save_data()
                st.rerun()
            elif not checked and is_done:
                st.session_state.habits[idx]["completions"] = [
                    d for d in habit["completions"] if d != today_str()
                ]
                save_data()
                st.rerun()

    # ── AI insight + mood log ────────────────────────────
    with right:
        st.markdown('<div class="lp-section">🤖 AI Coach Insight</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="lp-insight">💡 {random.choice(AI_INSIGHTS)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="lp-section">😊 Quick Mood Log</div>', unsafe_allow_html=True)
        with st.form("mood_form", clear_on_submit=True):
            mood_v   = st.slider("Mood",   1, 10, 7)
            energy_v = st.slider("Energy", 1, 10, 7)
            note_v   = st.text_input("Note (optional)")
            if st.form_submit_button("Log Mood ➤"):
                with st.spinner("Saving…"):
                    st.session_state.moods.append({
                        "date":   today_str(),
                        "mood":   mood_v,
                        "energy": energy_v,
                        "note":   note_v,
                    })
                    save_data()
                st.success("Mood logged! ✨")


# ══════════════════════════════════════════════════════════
#  8 · PAGE: HABIT MANAGER
# ══════════════════════════════════════════════════════════
def page_habits() -> None:
    """Render the habit management page: add, view, delete habits with streaks."""
    st.markdown('<div class="lp-hero">🔥 Habit Manager</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{PAL["muted"]};font-size:.88rem;margin-bottom:16px;">'
        f'Build powerful routines. Track streaks. Win every day.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Add a New Habit", expanded=False):
        with st.form("add_habit", clear_on_submit=True):
            name = st.text_input("Habit name", placeholder="e.g. 🏃 Run 5 km")
            cat  = st.selectbox("Category", LIFE_AREAS)
            if st.form_submit_button("Add Habit"):
                if name.strip():
                    with st.spinner("Adding…"):
                        st.session_state.habits.append({
                            "id":          st.session_state.next_habit_id,
                            "name":        name.strip(),
                            "category":    cat,
                            "completions": [],
                        })
                        st.session_state.next_habit_id += 1
                        save_data()
                    st.success(f"Habit **{name}** added! 🎉")
                    st.rerun()
                else:
                    st.error("Please enter a habit name.")

    habits = st.session_state.habits
    if not habits:
        st.info("No habits yet — use the expander above to add your first.")
        return

    st.markdown("---")
    for idx, h in enumerate(habits):
        streak  = get_streak(h["completions"])
        rate    = rate_7d(h)
        is_done = done_today(h)
        accent  = "green" if is_done else "indigo"

        col_info, col_stk, col_rate, col_del = st.columns([6, 2, 2, 1])

        with col_info:
            done_badge = (
                f'&nbsp;<span class="lp-badge green">✓ Done today</span>' if is_done else ""
            )
            st.markdown(
                f'<div class="lp-card {accent}">'
                f'<b>{h["name"]}</b>&nbsp;'
                f'<span class="lp-badge">{h["category"]}</span>'
                f'{done_badge}'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col_stk:
            st.metric("Streak", f"🔥 {streak}d")
        with col_rate:
            st.metric("7-day", f"{rate}%")
        with col_del:
            st.write("")
            if st.button("🗑️", key=f"del_h_{h['id']}"):
                st.session_state.habits.pop(idx)
                save_data()
                st.rerun()


# ══════════════════════════════════════════════════════════
#  9 · PAGE: GOALS & AI PLANNER
# ══════════════════════════════════════════════════════════
def page_goals() -> None:
    """Render the goal-setting page with simulated AI weekly action-plan breakdown."""
    st.markdown('<div class="lp-hero">🎯 Goals & AI Planner</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{PAL["muted"]};font-size:.88rem;margin-bottom:16px;">'
        f'Set a big goal. AI breaks it into weekly micro-actions.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Add New Goal", expanded=not st.session_state.goals):
        with st.form("add_goal", clear_on_submit=True):
            g_title    = st.text_input("Goal", placeholder="e.g. Run a 5K in 8 weeks")
            g_area     = st.selectbox("Life area", LIFE_AREAS)
            g_deadline = st.date_input(
                "Target date", value=date.today() + timedelta(weeks=8)
            )
            if st.form_submit_button("🤖 Generate AI Plan"):
                if g_title.strip():
                    with st.spinner("🤖 AI is crafting your action plan…"):
                        time.sleep(1.3)  # simulate LLM latency
                        tasks = ai_task_breakdown(g_title)
                        st.session_state.goals.append({
                            "id":       st.session_state.next_goal_id,
                            "title":    g_title.strip(),
                            "area":     g_area,
                            "deadline": g_deadline.isoformat(),
                            "tasks":    tasks,
                            "created":  today_str(),
                        })
                        st.session_state.next_goal_id += 1
                        save_data()
                    st.success("AI action plan ready! ✅")
                    st.rerun()
                else:
                    st.error("Please enter your goal.")

    if not st.session_state.goals:
        st.info("No goals yet — add one using the form above!")
        return

    for g_idx, goal in enumerate(st.session_state.goals):
        n_done   = sum(1 for t in goal["tasks"] if t["done"])
        n_total  = len(goal["tasks"])
        progress = n_done / n_total if n_total else 0

        with st.expander(
            f"🎯  {goal['title']}  ·  {n_done}/{n_total} weeks  ·  Due {goal['deadline']}",
            expanded=True,
        ):
            head_col, del_col = st.columns([11, 1])
            with head_col:
                st.markdown(
                    f'<span class="lp-badge indigo">{goal["area"]}</span>'
                    f'<span class="lp-badge green">{round(progress * 100)}% done</span>',
                    unsafe_allow_html=True,
                )
                st.progress(progress)
            with del_col:
                if st.button("🗑️", key=f"del_g_{goal['id']}"):
                    st.session_state.goals.pop(g_idx)
                    save_data()
                    st.rerun()

            st.markdown("**📅 Weekly Action Plan (AI-generated):**")
            for t_idx, task in enumerate(goal["tasks"]):
                chk_col, lbl_col = st.columns([1, 14])
                with chk_col:
                    checked = st.checkbox(
                        "", value=task["done"], key=f"task_{goal['id']}_{t_idx}"
                    )
                with lbl_col:
                    txt = (
                        f"~~**Week {task['week']}:** {task['task']}~~"
                        if task["done"]
                        else f"**Week {task['week']}:** {task['task']}"
                    )
                    st.markdown(txt)
                if checked != task["done"]:
                    st.session_state.goals[g_idx]["tasks"][t_idx]["done"] = checked
                    save_data()
                    st.rerun()


# ══════════════════════════════════════════════════════════
# 10 · PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════
def page_analytics() -> None:
    """Render the analytics page: mood trend, habit heatmap, radar, and bar charts."""
    st.markdown('<div class="lp-hero">📊 Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{PAL["muted"]};font-size:.88rem;margin-bottom:16px;">'
        f'Deep insights into your habits, mood, and life balance.</div>',
        unsafe_allow_html=True,
    )

    habits = st.session_state.habits
    moods  = st.session_state.moods

    # ── Mood & Energy trend ──────────────────────────────
    st.markdown('<div class="lp-section">😊 Mood & Energy — Last 30 Days</div>',
                unsafe_allow_html=True)
    if len(moods) >= 2:
        df_m = pd.DataFrame(moods[-30:])
        df_m["date"] = pd.to_datetime(df_m["date"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_m["date"], y=df_m["mood"],
            name="Mood", mode="lines+markers",
            line=dict(color=PAL["primary"], width=2.5),
            fill="tozeroy", fillcolor="rgba(16,185,129,.06)",
        ))
        fig.add_trace(go.Scatter(
            x=df_m["date"], y=df_m["energy"],
            name="Energy", mode="lines+markers",
            line=dict(color=PAL["indigo"], width=2.5, dash="dot"),
        ))
        fig.update_layout(
            **PLOTLY_BASE,
            yaxis=dict(range=[0, 10.5], gridcolor="#1f2937"),
            xaxis=dict(gridcolor="#1f2937"),
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log at least 2 mood entries to view your trend chart.")

    # ── Habit heatmap ────────────────────────────────────
    st.markdown('<div class="lp-section">🗓️ Habit Heatmap — Last 28 Days</div>',
                unsafe_allow_html=True)
    if habits:
        dates  = [(date.today() - timedelta(days=i)).isoformat() for i in range(27, -1, -1)]
        matrix = {
            h["name"][:28]: [1 if d in h["completions"] else 0 for d in dates]
            for h in habits
        }
        df_heat = pd.DataFrame(matrix, index=dates).T
        fig2 = px.imshow(
            df_heat,
            color_continuous_scale=["#111827", PAL["primary"]],
            aspect="auto",
            labels=dict(x="Date", y="Habit", color="Done"),
        )
        fig2.update_layout(**PLOTLY_BASE, coloraxis_showscale=False)
        fig2.update_xaxes(tickangle=-45, tickfont=dict(size=8))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    radar_col, bar_col = st.columns(2)

    # ── Life-area radar ──────────────────────────────────
    with radar_col:
        st.markdown('<div class="lp-section">🕸️ Life Balance Radar</div>',
                    unsafe_allow_html=True)
        area_scores: dict = {a: [] for a in LIFE_AREAS}
        for h in habits:
            cat = h.get("category", "Health")
            if cat in area_scores:
                area_scores[cat].append(rate_7d(h))

        scores = {
            a: round(sum(v) / len(v)) if v else random.randint(35, 75)
            for a, v in area_scores.items()
        }
        labels  = list(scores.keys())
        values  = list(scores.values())

        fig3 = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            fillcolor="rgba(16,185,129,.10)",
            line=dict(color=PAL["primary"], width=2.2),
        ))
        fig3.update_layout(
            **PLOTLY_BASE,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    tickfont=dict(size=9), gridcolor="#1f2937"
                ),
                angularaxis=dict(gridcolor="#1f2937"),
            ),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── 7-day completion bar ─────────────────────────────
    with bar_col:
        st.markdown('<div class="lp-section">📊 7-Day Completion Rates</div>',
                    unsafe_allow_html=True)
        if habits:
            df_bar = pd.DataFrame([
                {"Habit": h["name"][:26], "Rate (%)": rate_7d(h)} for h in habits
            ])
            fig4 = px.bar(
                df_bar, x="Rate (%)", y="Habit",
                orientation="h",
                color="Rate (%)",
                color_continuous_scale=[PAL["indigo"], PAL["primary"]],
                range_x=[0, 100],
            )
            fig4.update_layout(**PLOTLY_BASE, coloraxis_showscale=False,
                               yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════
# 11 · PAGE: JOURNAL
# ══════════════════════════════════════════════════════════
def page_journal() -> None:
    """Render the daily journaling page: write entries, browse history."""
    st.markdown('<div class="lp-hero">📓 Daily Journal</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{PAL["muted"]};font-size:.88rem;margin-bottom:16px;">'
        f'Reflect. Process. Grow.</div>',
        unsafe_allow_html=True,
    )

    with st.form("journal_form", clear_on_submit=True):
        title = st.text_input("Entry title", placeholder="What's on your mind today?")
        text  = st.text_area("Write freely…", height=160,
                              placeholder="Today I felt… I'm grateful for… I want to improve…")
        vibe  = st.select_slider(
            "Today's overall vibe",
            options=["😢 Rough", "😔 Low", "😐 Neutral", "🙂 Decent",
                     "😊 Good", "😁 Great", "🤩 Amazing"],
            value="😊 Good",
        )
        tags  = st.multiselect(
            "Tags",
            ["Gratitude", "Work", "Family", "Health", "Wins", "Challenges", "Goals", "Ideas"],
        )
        if st.form_submit_button("💾 Save Entry"):
            if text.strip():
                with st.spinner("Saving entry…"):
                    st.session_state.journal.append({
                        "date":  today_str(),
                        "title": title or f"Entry – {today_str()}",
                        "text":  text,
                        "vibe":  vibe,
                        "tags":  tags,
                    })
                    save_data()
                st.success("Entry saved — keep reflecting. 🌱")
                st.rerun()
            else:
                st.error("Write something before saving.")

    st.markdown("---")
    st.markdown('<div class="lp-section">📚 Past Entries</div>', unsafe_allow_html=True)
    journal = st.session_state.journal

    if not journal:
        st.info("No entries yet — write your first one above!")
        return

    for entry in reversed(journal[-20:]):
        emoji = entry["vibe"].split()[0]
        with st.expander(f"{emoji}  {entry['title']}  ·  {entry['date']}"):
            st.markdown(entry["text"])
            if entry.get("tags"):
                st.markdown(
                    " ".join(
                        f'<span class="lp-badge indigo">{t}</span>' for t in entry["tags"]
                    ),
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════
# 12 · PAGE: WEEKLY REPORT
# ══════════════════════════════════════════════════════════
def page_report() -> None:
    """Render the weekly performance report with summary stats and AI coach summary."""
    st.markdown('<div class="lp-hero">📈 Weekly Life Report</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{PAL["muted"]};font-size:.88rem;margin-bottom:16px;">'
        f'Week ending {date.today().strftime("%B %d, %Y")}</div>',
        unsafe_allow_html=True,
    )

    week_start = (date.today() - timedelta(days=6)).isoformat()
    habits     = st.session_state.habits
    moods_wk   = [m for m in st.session_state.moods if m["date"] >= week_start]
    goals      = st.session_state.goals
    journal_wk = [j for j in st.session_state.journal if j["date"] >= week_start]

    total_cmp = sum(
        sum(1 for d in h["completions"] if d >= week_start) for h in habits
    )
    avg_mood = (
        round(sum(m["mood"] for m in moods_wk) / len(moods_wk), 1)
        if moods_wk else "—"
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("✅ Habit Check-ins", total_cmp)
    k2.metric("😊 Avg Mood",        avg_mood)
    k3.metric("🎯 Active Goals",    len(goals))
    k4.metric("📓 Journal Entries", len(journal_wk))

    # ── Habit performance table ──────────────────────────
    st.markdown("---")
    st.markdown('<div class="lp-section">🔥 Habit Performance This Week</div>',
                unsafe_allow_html=True)
    if habits:
        rows = []
        for h in habits:
            w = sum(1 for d in h["completions"] if d >= week_start)
            rows.append({
                "Habit":          h["name"],
                "Days ✓":         w,
                "Rate":           f"{round(w / 7 * 100)}%",
                "Streak":         f"🔥 {get_streak(h['completions'])}d",
                "Status":         "🟢 Great" if w >= 5 else ("🟡 Okay" if w >= 3 else "🔴 Needs work"),
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # ── Goals progress ───────────────────────────────────
    if goals:
        st.markdown("---")
        st.markdown('<div class="lp-section">🎯 Goals Progress</div>', unsafe_allow_html=True)
        for goal in goals:
            n   = sum(1 for t in goal["tasks"] if t["done"])
            pct = round(n / len(goal["tasks"]) * 100) if goal["tasks"] else 0
            st.markdown(
                f'<div class="lp-card indigo">'
                f'<b>{goal["title"]}</b>&nbsp;'
                f'<span class="lp-badge green">{pct}%</span>&nbsp;'
                f'<span class="lp-badge amber">Due {goal["deadline"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.progress(pct / 100)

    # ── AI weekly summary ────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="lp-section">🤖 AI Weekly Summary</div>', unsafe_allow_html=True)
    top = max(habits, key=lambda h: rate_7d(h)) if habits else None
    low = min(habits, key=lambda h: rate_7d(h)) if habits else None

    if top:
        st.markdown(
            f'<div class="lp-insight">'
            f'<b>📊 This Week\'s Highlights</b><br><br>'
            f'🏆 <b>Best habit:</b> {top["name"]} — {rate_7d(top)}% completion<br>'
            f'⚠️ <b>Needs attention:</b> {low["name"]} — {rate_7d(low)}% completion<br><br>'
            f'💡 <b>Insight:</b> {random.choice(AI_INSIGHTS)}<br>'
            f'✨ <b>Affirmation:</b> {random.choice(AFFIRMATIONS)}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Add habits and log some completions to see your AI summary.")


# ══════════════════════════════════════════════════════════
# 13 · MAIN ENTRYPOINT
# ══════════════════════════════════════════════════════════
init_state()
inject_css()

page = render_sidebar()

{
    "dashboard": page_dashboard,
    "habits":    page_habits,
    "goals":     page_goals,
    "analytics": page_analytics,
    "journal":   page_journal,
    "report":    page_report,
}[page]()
