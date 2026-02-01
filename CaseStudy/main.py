import streamlit as st
from datetime import date, datetime
import re
import requests

from storage import load_data, save_data, now_ts


# =========================
# LOAD JSON DATA ON STARTUP
# =========================
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
goals = data["goals"]            # list[dict] {name,status}
updates = data["updates"]        # list[dict] {goal,date,text,created_at}
ai_events = data["ai_events"]    # list[dict] {event_type,goal,user_text,prompt,answer,context,created_at}


# =========================
# OLLAMA
# =========================
OLLAMA_MODEL = "llama3.1"
OLLAMA_URL = "http://localhost:11434/api/generate"


def ollama_generate(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.6, "num_predict": 220},
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        r.raise_for_status()
        return (r.json().get("response") or "").strip()
    except Exception as e:
        return f"⚠️ Ollama error: {e}"


def choose_context(all_updates, goal: str, question: str, n: int = 6):
    items = [u for u in all_updates if u["goal"] == goal]
    items.sort(key=lambda x: (x.get("date", ""), x.get("created_at", "")), reverse=True)
    return items[:n]


def build_prompt(goal: str, question: str, context_updates):
    context_text = "\n".join([f"- {u['date']}: {u['text']}" for u in context_updates])
    return f"""
You are Goalbot, a private, empathetic journaling companion.
You help the user reflect without judgment and suggest small actionable steps.
Do NOT provide medical advice. If the user mentions self-harm, encourage them to seek immediate professional help.

GOAL:
{goal}

RECENT JOURNAL UPDATES:
{context_text}

USER QUESTION:
{question}

Respond with:
1) A warm reflection (2-4 sentences)
2) 2 reflection questions (bulleted)
3) 1 small next step for tomorrow (specific and low effort)
""".strip()


# =========================
# UI
# =========================
st.set_page_config(page_title="Goalbot", page_icon="🎯", layout="wide")

st.markdown(
    """
<style>
div[data-baseweb="popover"] {
  background: #0b1220 !important;
  color: #f9fafb !important;
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  box-shadow: 0 18px 60px rgba(0,0,0,0.55) !important;
}
ul[role="listbox"], div[data-baseweb="menu"] {
  background: #0b1220 !important;
  color: #f9fafb !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 14px !important;
}
li[role="option"], div[data-baseweb="menu"] li, div[data-baseweb="menu"] div {
  background: #0b1220 !important;
  color: #f9fafb !important;
}
li[role="option"]:hover, div[data-baseweb="menu"] li:hover {
  background: rgba(255,255,255,0.08) !important;
  color: #ffffff !important;
}
li[aria-selected="true"] {
  background: rgba(255,255,255,0.12) !important;
  color: #ffffff !important;
}
div[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 14px !important;
}
div[data-baseweb="select"] span { color: #f9fafb !important; }

input, textarea {
  color: #f9fafb !important;
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 14px !important;
}
textarea::placeholder, input::placeholder { color: rgba(249,250,251,0.55) !important; }

.stButton > button {
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  padding: 0.55rem 0.95rem !important;
  background: rgba(255,255,255,0.06) !important;
  color: #f9fafb !important;
}

.goalbot-card {
  background: rgba(17, 24, 39, 0.60) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 16px !important;
  padding: 16px 18px !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35) !important;
}
.goalbot-muted { color: rgba(255, 255, 255, 0.78) !important; margin-top: 6px !important; }
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# Helpers (JSON-backed)
# =========================
def normalize_date(s: str) -> str:
    s = (s or "").strip()
    if re.match(r"^\d{4}/\d{2}/\d{2}$", s):
        s = s.replace("/", "-")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        raise ValueError("Use YYYY-MM-DD (example: 2026-01-30)")
    datetime.strptime(s, "%Y-%m-%d")
    return s


def active_goals():
    return [g["name"] for g in goals if g.get("status") == "active"]


def inactive_goals():
    return [g["name"] for g in goals if g.get("status") == "inactive"]


def add_goal(name: str) -> bool:
    name = (name or "").strip()
    if not name:
        return False
    if any(g["name"].lower() == name.lower() for g in goals):
        return False
    goals.append({"name": name, "status": "active"})
    save_data(data)
    return True


def remove_goal(name: str) -> None:
    data["goals"] = [g for g in goals if g["name"] != name]
    data["updates"] = [u for u in updates if u["goal"] != name]
    data["ai_events"] = [a for a in ai_events if a.get("goal") != name]
    save_data(data)


def set_goal_status(name: str, status: str) -> None:
    for g in goals:
        if g["name"] == name:
            g["status"] = status
            save_data(data)
            return


def save_update(goal: str, date_str: str, text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False
    updates.append({"goal": goal, "date": date_str, "text": text, "created_at": now_ts()})
    save_data(data)
    return True


def recent_for_goal(goal: str, n: int = 5):
    items = [u for u in updates if u["goal"] == goal]
    items.sort(key=lambda x: (x.get("date", ""), x.get("created_at", "")), reverse=True)
    return items[:n]


def log_ai_event(event_type: str, goal: str, user_text: str, prompt: str, answer: str, context_updates=None):
    context_updates = context_updates or []
    ai_events.append({
        "event_type": event_type,   # daily_feedback | ask_answer | progress_summary
        "goal": goal,
        "user_text": user_text,
        "prompt": prompt,
        "answer": answer,
        "context": [{"date": u.get("date"), "text": u.get("text")} for u in context_updates],
        "created_at": now_ts(),
    })
    save_data(data)


# =========================
# Sidebar navigation
# =========================
st.sidebar.title("🎯 Goalbot")
page = st.sidebar.radio("Navigate", ["Goals", "History", "Ask Goalbot"], index=0)

st.title("🎯 Goalbot")
st.caption("Log daily progress for each goal, review history, and ask Goalbot using your saved updates (JSON).")


# ============================================================
# PAGE 1: GOALS
# ============================================================
if page == "Goals":
    st.subheader("Daily Updates")

    default_date = str(date.today())
    date_str = st.text_input("Date (YYYY-MM-DD)", value=default_date, help="Example: 2026-01-30")

    try:
        entry_date = normalize_date(date_str)
        st.caption(f"Using date: {entry_date}")
    except Exception as e:
        st.error(f"Date format error: {e}")
        st.stop()

    st.write("Write a quick update under each goal. Click **Save** and Goalbot will respond.")

    # show active first then inactive
    active_list = active_goals()
    inactive_list = inactive_goals()
    goal_list = active_list + inactive_list

    if not goal_list:
        st.info("No goals yet. Add one below.")
    else:
        colA, colB = st.columns(2, gap="large")
        for idx, goal in enumerate(goal_list, start=1):
            target = colA if idx % 2 == 1 else colB

            with target:
                with st.container(border=True):
                    st.markdown(f"### {goal}")

                    # status selector + delete
                    cur_status = "active"
                    for g in goals:
                        if g["name"] == goal:
                            cur_status = g.get("status", "active")
                            break

                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        new_status = st.selectbox(
                            "Status",
                            ["active", "inactive"],
                            index=0 if cur_status == "active" else 1,
                            key=f"status_{goal}",
                            label_visibility="collapsed",
                        )
                    with c2:
                        if st.button("Update status", key=f"set_{goal}"):
                            set_goal_status(goal, new_status)
                            st.rerun()
                    with c3:
                        if st.button("🗑️", key=f"del_{goal}"):
                            remove_goal(goal)
                            st.rerun()

                    txt = st.text_area(
                        "Daily update",
                        placeholder="What did you do today? What helped or got in the way?",
                        height=120,
                        key=f"update_{goal}",
                        label_visibility="collapsed",
                    )

                    if st.button("Save", type="primary", key=f"save_{goal}"):
                        ok = save_update(goal, entry_date, txt)
                        if ok:
                            st.success("Saved ✅")

                            recent_ctx = [u for u in updates if u.get("goal") == goal]
                            recent_ctx.sort(key=lambda x: (x.get("date", ""), x.get("created_at", "")), reverse=True)
                            recent_ctx = recent_ctx[:6]  # keep last 6 max

                            recent_text = "\n".join([f"- {u.get('date')}: {u.get('text')}" for u in recent_ctx])

                            prompt = f"""
                            You are Goalbot: upbeat, supportive, and practical.

                            User goal: {goal}
                            Date: {entry_date}

                            Recent updates (most recent first):
                            {recent_text if recent_text else "- (no past updates yet)"}

                            Today’s update: {txt}

                            Write ONE short response (2–3 sentences max):
                            - 1 sentence acknowledging effort (be specific to the update)
                            - 1 sentence reflecting a helpful insight (mention a pattern if you see one from recent updates)
                            - 1 tiny next step for tomorrow (very concrete: time OR place OR first action)

                            Rules:
                            - Keep it motivational, not cheesy.
                            - No medical advice.
                            - Avoid generic phrases like "keep going" unless you attach a specific reason from the update.
                            """.strip()

                            answer = ollama_generate(prompt)

                            # save AI daily feedback + context (store the same context you gave the model)
                            log_ai_event(
                                event_type="daily_feedback",
                                goal=goal,
                                user_text=txt,
                                prompt=prompt,
                                answer=answer,
                                context_updates=recent_ctx if recent_ctx else [{"date": entry_date, "text": txt}],
                            )

                            st.markdown(
                                f"""
                            <div class="goalbot-card">
                            <h3>🤖 Goalbot Response</h3>
                            <div class="goalbot-muted">{answer}</div>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.warning("Please write an update first.")

                    recent = recent_for_goal(goal, n=2)
                    if recent:
                        st.caption("Recent:")
                        for u in recent:
                            preview = u["text"][:80] + ("..." if len(u["text"]) > 80 else "")
                            st.write(f"• {u['date']}: {preview}")

    st.divider()
    st.markdown("### Add another goal")
    with st.form("add_goal_form", clear_on_submit=True):
        c_input, c_btn = st.columns([6, 1])
        with c_input:
            bottom_goal = st.text_input(
                "New goal",
                placeholder="Type a goal name and click Add",
                label_visibility="collapsed",
            )
        with c_btn:
            submitted = st.form_submit_button("➕ Add", use_container_width=True)

        if submitted:
            if add_goal(bottom_goal):
                st.success("Goal added ✅")
                st.rerun()
            else:
                st.warning("Enter a new goal name (or it may already exist).")


# ============================================================
# PAGE 2: HISTORY
# ============================================================
elif page == "History":
    st.subheader("History")
    st.write("All saved updates + AI responses (persisted in JSON).")

    if not updates and not ai_events:
        st.info("No updates saved yet. Go to **Goals** and add one.")
    else:
        goal_names = [g["name"] for g in goals]
        goal_filter = st.selectbox("Filter by goal", ["All"] + goal_names + ["ALL_GOALS"])
        query = st.text_input("Search", placeholder="Search updates + AI responses...")

        feed = []

        for u in updates:
            feed.append({
                "type": "update",
                "goal": u.get("goal"),
                "date": u.get("date", ""),
                "text": u.get("text", ""),
                "created_at": u.get("created_at", ""),
            })

        for a in ai_events:
            feed.append({
                "type": "ai",
                "goal": a.get("goal"),
                "event_type": a.get("event_type", "ai"),
                "user_text": a.get("user_text", ""),
                "text": a.get("answer", ""),
                "context": a.get("context", []),
                "created_at": a.get("created_at", ""),
            })

        feed.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        if goal_filter != "All":
            feed = [item for item in feed if item.get("goal") == goal_filter]

        if query.strip():
            q = query.strip().lower()
            def blob(item):
                return (item.get("text","") + " " + item.get("user_text","") + " " + item.get("event_type","")).lower()
            feed = [item for item in feed if q in blob(item)]

        st.caption(f"Showing **{len(feed)}** item(s).")

        for item in feed:
            with st.container(border=True):
                if item["type"] == "update":
                    st.markdown(f"**📝 Update** — **{item['date']}** — **{item['goal']}**")
                    st.write(item["text"])
                else:
                    st.markdown(f"**🤖 AI ({item.get('event_type')}) — {item.get('goal')}**")
                    if item.get("user_text"):
                        st.markdown("**User input:**")
                        st.write(item["user_text"])
                    st.markdown("**Goalbot response:**")
                    st.write(item["text"])

                    with st.expander("Show context used"):
                        ctx = item.get("context", [])
                        if not ctx:
                            st.write("No context stored.")
                        else:
                            for c in ctx:
                                st.write(f"• {c.get('date')}: {c.get('text')}")


# ============================================================
# PAGE 3: ASK GOALBOT
# ============================================================
elif page == "Ask Goalbot":
    st.subheader("Ask Goalbot")
    st.write("Goalbot uses your saved JSON history as context to answer your question.")

    goal_options = active_goals() + inactive_goals()
    if not goal_options:
        st.info("Add a goal first on the **Goals** page.")
        st.stop()

    goal = st.selectbox("Choose a goal", goal_options)

    question = st.text_input(
        "Your question",
        placeholder="e.g., Why am I stuck? What should I do tomorrow? How can I be consistent?",
    )

    st.divider()
    st.markdown("### 📊 Progress summary (all goals)")

    make_summary = st.button("Generate progress summary", type="primary", key="progress_summary_btn")

    if make_summary:
        # newest 30 updates max
        sorted_updates = updates[:]
        sorted_updates.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        recent_all = sorted_updates[:30]

        history_text = "\n".join([f"- [{u['goal']}] {u['date']}: {u['text']}" for u in recent_all])

        prompt = f"""
You are Goalbot, a private and encouraging journaling companion.

Here are the user's recent updates across ALL goals:
{history_text}

Write a short progress report with:
1) Overall check-in (2–4 sentences)
2) Wins you notice (bulleted, max 4)
3) Patterns / blockers (bulleted, max 4)
4) One tiny next step for the next day (1 sentence)

Keep it kind, practical, and non-judgmental. No medical advice.
""".strip()

        answer = ollama_generate(prompt)

        st.markdown(
            f"""
<div class="goalbot-card">
  <h3>📊 Progress Summary</h3>
  <div class="goalbot-muted">{answer}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        log_ai_event(
            event_type="progress_summary",
            goal="ALL_GOALS",
            user_text="",
            prompt=prompt,
            answer=answer,
            context_updates=recent_all,
        )

    st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        ask = st.button("Ask", type="primary")
    with col2:
        show_context = st.checkbox("Show context used", value=True)

    if ask:
        if not question.strip():
            st.warning("Type a question first.")
        else:
            context = choose_context(updates, goal, question, n=6)
            prompt = build_prompt(goal, question, context)
            answer = ollama_generate(prompt)

            log_ai_event(
                event_type="ask_answer",
                goal=goal,
                user_text=question,
                prompt=prompt,
                answer=answer,
                context_updates=context,
            )

            st.markdown(
                f"""
<div class="goalbot-card">
  <h3>🤖 Goalbot Response</h3>
  <div class="goalbot-muted">{answer}</div>
</div>
""",
                unsafe_allow_html=True,
            )

            if show_context:
                st.divider()
                st.caption("Context used:")
                if not context:
                    st.write("No saved updates yet for this goal.")
                else:
                    for u in context:
                        st.write(f"• {u['date']}: {u['text']}")
