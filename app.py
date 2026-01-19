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
    subject = st.text_input("Subject (type your own)")
    deadline = st.date_input("Deadline")

    difficulty = st.slider("Difficulty", 1, 10, 5)
    importance = st.slider("Importance", 1, 10, 5)
    workload = st.slider("Workload", 1, 10, 5)

    if st.button("Add Task"):
        if name.strip() == "":
            st.error("Task name required")
        else:
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
            st.success("✅ Task added")

# ====================================================
# 📋 PENDING TASKS
# ====================================================
elif section == "📋 Pending Tasks":
    st.header("📋 Pending Tasks")

    for t in tasks[user_id][:]:
        deadline_dt = datetime.fromisoformat(t["deadline"])
        overdue = now > deadline_dt and not t["done"]

        style = ""
        if overdue:
            style = "color:red;"
        if t["done"]:
            style = "opacity:0.4;"

        st.markdown(
            f"<div style='{style}'>"
            f"📌 <b>{t['name']}</b> | {t['subject']}<br>"
            f"🎯 Importance: {t['importance']} | "
            f"🧠 Difficulty: {t['difficulty']} | "
            f"📦 Workload: {t['workload']}<br>"
            f"⏰ Deadline: {t['deadline']}"
            f"</div>",
            unsafe_allow_html=True
        )

        if st.checkbox("Completed", value=t["done"], key=t["name"]):
            if not t["done"]:
                t["done"] = True
                t["done_time"] = now.isoformat()
                save(TASK_FILE, tasks)

        # auto delete after 1 day
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
        return (
            t["importance"] * 2 +
            t["difficulty"] +
            t["workload"] +
            urgency
        )

    priority = sorted(
        tasks[user_id],
        key=lambda x: (x["done"], -priority_score(x))
    )

    for t in priority:
        style = "opacity:0.4;" if t["done"] else ""
        st.markdown(
            f"<div style='{style}'>"
            f"🔥 <b>{t['name']}</b> | {t['subject']}<br>"
            f"Score: {priority_score(t)} | "
            f"🎯 {t['importance']} | "
            f"🧠 {t['difficulty']} | "
            f"📦 {t['workload']} | "
            f"⏰ {t['deadline']}"
            f"</div>",
            unsafe_allow_html=True
        )

# ====================================================
# 🧠 DAILY STUDY PLAN
# ====================================================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Daily Study Plan (Hours & Minutes)")

    day_start = st.time_input("Day starts at", time(6, 0))
    day_end = st.time_input("Day ends at", time(22, 0))

    if "study_blocks" not in st.session_state:
        st.session_state.study_blocks = []

    task = st.text_input("Activity / Subject")

    col1, col2 = st.columns(2)
    with col1:
        hrs = st.number_input("Hours", 0, 12, 1)
    with col2:
        mins = st.number_input("Minutes", 0, 59, 0)

    if st.button("➕ Add Block"):
        st.session_state.study_blocks.append({
            "task": task,
            "minutes": hrs * 60 + mins
        })

    total = 0
    for b in st.session_state.study_blocks:
        total += b["minutes"]
        st.write(f"• {b['task']} — {b['minutes']} minutes")

    available = (
        datetime.combine(datetime.today(), day_end)
        - datetime.combine(datetime.today(), day_start)
    ).seconds // 60

    st.divider()
    if total > available:
        st.error("❌ Plan exceeds available time")
    else:
        st.success("✅ Plan fits the day")

    st.info("🧠 Do high priority & difficult tasks early")

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
        st.success("📨 Sent")

    if user_id == "proto":
        pwd = st.text_input("Owner Password", type="password")
        if pwd == "1357924680proto":
            for r in recs.get("proto", []):
                st.info(f"From: {r['from']}\n\n{r['msg']}")

