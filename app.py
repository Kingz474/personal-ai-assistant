import streamlit as st
import json, os
from datetime import datetime, timedelta, time

# ================= FILES =================
TASK_FILE = "tasks.json"
REC_FILE = "recommendations.json"

def load(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

tasks = load(TASK_FILE, {})
recs = load(REC_FILE, {})

# ================= LOGIN =================
st.title("📚 Personal AI Study Assistant")

user_id = st.text_input("Enter your User ID")

if not user_id:
    st.stop()

if user_id not in tasks:
    tasks[user_id] = []
    save(TASK_FILE, tasks)

now = datetime.now()

# ================= SECTION SELECTOR =================
section = st.sidebar.radio(
    "Choose Section",
    [
        "➕ Add Task",
        "📋 Pending Tasks",
        "🔥 Priority Tasks",
        "🧠 Daily Study Plan",
        "💡 Recommendations"
    ]
)

# ====================================================
# ➕ ADD TASK
# ====================================================
if section == "➕ Add Task":
    st.header("➕ Add New Task")

    name = st.text_input("Task name")
    subject = st.text_input("Subject")
    deadline = st.date_input("Deadline")

    difficulty = st.slider("Difficulty", 1, 10, 5)
    importance = st.slider("Importance", 1, 10, 5)
    workload = st.slider("Workload", 1, 10, 5)

    if st.button("Add Task"):
        if name.strip():
            tasks[user_id].append({
                "name": name,
                "subject": subject,
                "deadline": deadline.isoformat(),
                "difficulty": difficulty,
                "importance": importance,
                "workload": workload,
                "done": False,
                "done_time": None
            })
            save(TASK_FILE, tasks)
            st.success("Task added")

# ====================================================
# 📋 PENDING TASKS
# ====================================================
elif section == "📋 Pending Tasks":
    st.header("📋 Pending Tasks")

    for t in tasks[user_id][:]:
        deadline_dt = datetime.fromisoformat(t["deadline"])
        overdue = now > deadline_dt and not t["done"]

        style = "color:red;" if overdue else ""
        if t["done"]:
            style = "opacity:0.4;"

        st.markdown(
            f"<div style='{style}'>"
            f"<b>{t['name']}</b> | {t['subject']}<br>"
            f"Imp: {t['importance']} | Diff: {t['difficulty']} | Load: {t['workload']}<br>"
            f"Deadline: {t['deadline']}"
            f"</div>",
            unsafe_allow_html=True
        )

        if st.checkbox("Completed", value=t["done"], key=t["name"]):
            t["done"] = True
            t["done_time"] = now.isoformat()
            save(TASK_FILE, tasks)

        if t["done"] and t["done_time"]:
            if now > datetime.fromisoformat(t["done_time"]) + timedelta(days=1):
                tasks[user_id].remove(t)
                save(TASK_FILE, tasks)

# ====================================================
# 🔥 PRIORITY TASKS
# ====================================================
elif section == "🔥 Priority Tasks":
    st.header("🔥 Priority Tasks")

    def priority_score(t):
        days_left = (datetime.fromisoformat(t["deadline"]) - now).days
        urgency = max(0, 10 - days_left)
        return t["importance"]*2 + t["difficulty"] + t["workload"] + urgency

    sorted_tasks = sorted(tasks[user_id], key=lambda x: (x["done"], -priority_score(x)))

    for t in sorted_tasks:
        style = "opacity:0.4;" if t["done"] else ""
        st.markdown(
            f"<div style='{style}'>"
            f"<b>{t['name']}</b> | Score: {priority_score(t)}"
            f"</div>",
            unsafe_allow_html=True
        )

# ====================================================
# 🧠 DAILY STUDY PLAN (OBSTACLE BASED)
# ====================================================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Daily Study Plan (Obstacle Based)")

    if "obstacles" not in st.session_state:
        st.session_state.obstacles = []

    st.subheader("➕ Add Fixed Activity / Obstacle")

    obs_name = st.text_input("Obstacle name (College, Food, Sleep, etc)")
    col1, col2 = st.columns(2)
    with col1:
        obs_start = st.time_input("Start time", time(9, 0))
    with col2:
        obs_end = st.time_input("End time", time(17, 0))

    if st.button("Add Obstacle"):
        st.session_state.obstacles.append({
            "name": obs_name,
            "start": obs_start,
            "end": obs_end
        })

    st.divider()
    st.subheader("📅 Full Day Timetable")

    if st.session_state.obstacles:
        sorted_obs = sorted(st.session_state.obstacles, key=lambda x: x["start"])

        prev_end = time(0, 0)

        for o in sorted_obs:
            if prev_end < o["start"]:
                st.success(f"🟢 Free: {prev_end} - {o['start']}")
            st.warning(f"🔒 {o['name']}: {o['start']} - {o['end']}")
            prev_end = o["end"]

        if prev_end < time(23, 59):
            st.success(f"🟢 Free: {prev_end} - 23:59")

    if st.button("🔄 Reset Timetable"):
        st.session_state.obstacles = []
        st.success("Timetable reset")

# ====================================================
# 💡 RECOMMENDATIONS
# ====================================================
elif section == "💡 Recommendations":
    st.header("💡 Recommendations")

    msg = st.text_area("Write recommendation")

    if st.button("Send to Owner"):
        recs.setdefault("proto", []).append({
            "from": user_id,
            "msg": msg,
            "time": now.isoformat()
        })
        save(REC_FILE, recs)
        st.success("Sent")

    if user_id == "proto":
        pwd = st.text_input("Owner Password", type="password")
        if pwd == "1357924680proto":
            for r in recs.get("proto", []):
                st.info(f"From: {r['from']}\n\n{r['msg']}")

