import streamlit as st
import json, os
from datetime import datetime, time, timedelta

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Personal AI Study Assistant",
    page_icon="📚",
    layout="centered"
)

# ================= FILES =================
TASK_FILE = "tasks.json"
REC_FILE = "recommendations.json"

# ================= FAST LOAD (CACHE) =================
@st.cache_data
def load(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

tasks = load(TASK_FILE)
recs = load(REC_FILE)

# ================= TITLE =================
st.title("📚 Personal AI Study Assistant")
st.caption("Plan smarter • Study better • Stay consistent")

# ===== VERSION TAG =====
st.markdown(
    """
    <div style="
        position: fixed;
        top: 15px;
        right: 25px;
        font-size: 13px;
        color: gray;
        opacity: 0.75;
        z-index: 9999;
    ">
        v1.3 <b>beta</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ================= USER =================
user = st.text_input("👤 Enter your User ID", placeholder="e.g. kingz01")
if not user:
    st.info("Enter a User ID to continue")
    st.stop()

tasks.setdefault(user, [])
save(TASK_FILE, tasks)

# ================= SIDEBAR =================
section = st.sidebar.radio(
    "📌 Navigation",
    [
        "➕ Add Task",
        "⏳ Pending Tasks",
        "⭐ Priority Tasks",
        "🧠 Daily Study Plan",
        "📩 Recommendations"
    ]
)

# =====================================================
# ➕ ADD TASK
# =====================================================
if section == "➕ Add Task":
    st.header("➕ Add Task")

    with st.form("add_task"):
        title = st.text_input("Task Name")
        subject = st.text_input("Subject")
        deadline = st.date_input("Deadline")

        c1, c2, c3 = st.columns(3)
        difficulty = c1.slider("Difficulty", 1, 5)
        importance = c2.slider("Importance", 1, 5)
        workload = c3.slider("Workload", 1, 5)

        submitted = st.form_submit_button("Add Task")

    if submitted:
        tasks[user].append({
            "title": title,
            "subject": subject,
            "deadline": str(deadline),
            "difficulty": difficulty,
            "importance": importance,
            "workload": workload,
            "done": False,
            "done_time": None
        })
        save(TASK_FILE, tasks)
        st.success("✅ Task added")

# =====================================================
# ⏳ PENDING TASKS
# =====================================================
elif section == "⏳ Pending Tasks":
    st.header("⏳ Pending Tasks")
    now = datetime.now()

    if not tasks[user]:
        st.info("No tasks yet")
    else:
        for i, t in enumerate(tasks[user]):
            deadline = datetime.fromisoformat(t["deadline"]).date()
            expired = now.date() > deadline

            col1, col2 = st.columns([6,1])
            with col1:
                if t["done"]:
                    st.markdown(
                        f"<div style='opacity:0.4'>✔ {t['title']} ({t['subject']})</div>",
                        unsafe_allow_html=True
                    )
                elif expired:
                    st.error(f"❌ {t['title']} ({t['subject']}) — Missed")
                else:
                    st.info(f"{t['title']} ({t['subject']})")

            with col2:
                if st.checkbox("✔", key=f"pend{i}", value=t["done"]):
                    t["done"] = True
                    t["done_time"] = datetime.now().isoformat()

    save(TASK_FILE, tasks)

# =====================================================
# ⭐ PRIORITY TASKS
# =====================================================
elif section == "⭐ Priority Tasks":
    st.header("⭐ Priority Tasks")

    for i, t in enumerate(tasks[user]):
        score = t["difficulty"] + t["importance"] + t["workload"]
        expired = datetime.now().date() > datetime.fromisoformat(t["deadline"]).date()

        col1, col2 = st.columns([5,1])
        with col1:
            if expired and not t["done"]:
                st.error(f"{t['title']} ({t['subject']})")
            elif t["done"]:
                st.markdown(
                    f"<div style='opacity:0.4'>✔ {t['title']}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.info(f"{t['title']} | Priority: {score}")

        with col2:
            if st.checkbox("✔", key=f"prio{i}", value=t["done"]):
                t["done"] = True
                t["done_time"] = datetime.now().isoformat()

    save(TASK_FILE, tasks)

# =====================================================
# 🧠 DAILY STUDY PLAN
# =====================================================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Weekly Obstacle Timetable")

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    TIME_SLOTS = [f"{h:02d}:00-{h+1:02d}:00" for h in range(24)]

    if "table" not in st.session_state:
        st.session_state.table = {
            slot: {day: "" for day in DAYS}
            for slot in TIME_SLOTS
        }

    with st.expander("➕ Add Obstacle"):
        obs_name = st.text_input("Obstacle Name")
        obs_day = st.selectbox("Day", DAYS)
        c1, c2 = st.columns(2)
        start = c1.time_input("Start Time", time(9,0))
        end = c2.time_input("End Time", time(10,0))

        if st.button("Add Obstacle"):
            if start >= end:
                st.error("End time must be after start time")
            else:
                for slot in TIME_SLOTS:
                    s, e = slot.split("-")
                    if time.fromisoformat(s) >= start and time.fromisoformat(e) <= end:
                        st.session_state.table[slot][obs_day] = obs_name
                st.success("Obstacle added")

    for slot in TIME_SLOTS:
        cols = st.columns(len(DAYS) + 1)
        cols[0].markdown(f"**{slot}**")
        for i, day in enumerate(DAYS):
            val = st.session_state.table[slot][day]
            cols[i+1].success("FREE" if not val else val)

# =====================================================
# 📩 RECOMMENDATIONS
# =====================================================
elif section == "📩 Recommendations":
    st.header("📩 Recommendations")

    if user == "proto":
        pwd = st.text_input("Owner Password", type="password")
        if pwd == "1357924680proto":
            for r in recs.get("proto", []):
                st.info(f"From: {r['from']}\n\n{r['msg']}")
        else:
            st.error("Wrong password")
    else:
        msg = st.text_area("Send recommendation to owner (proto)")
        if st.button("Send"):
            recs.setdefault("proto", []).append({
                "from": user,
                "msg": msg,
                "time": datetime.now().isoformat()
            })
            save(REC_FILE, recs)
            st.success("Sent")


