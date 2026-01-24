import streamlit as st
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Personal Study Assistant", layout="wide")

# ===============================
# JSON HELPERS
# ===============================
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
    with open(file, "r") as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ===============================
# FILE PATHS
# ===============================
TASK_FILE = "tasks_data.json"
OBSTACLE_FILE = "obstacles.json"
REC_FILE = "recommendations.json"

tasks_db = load_json(TASK_FILE, {})
obstacles_db = load_json(OBSTACLE_FILE, {})
recs_db = load_json(REC_FILE, [])

# ===============================
# USER LOGIN (SIMPLE ID)
# ===============================
st.sidebar.title("👤 User")
user_id = st.sidebar.text_input("Enter your User ID", value="guest")

# ===============================
# SIDEBAR SECTIONS
# ===============================
section = st.sidebar.radio(
    "Sections",
    [
        "➕ Add Task",
        "⏳ Pending Tasks",
        "⭐ Priority Tasks",
        "🧠 Daily Study Plan",
        "📘 Study Help",
        "📩 Recommendations"
    ]
)

# ===============================
# TASK HELPERS
# ===============================
def get_tasks(uid):
    return tasks_db.get(uid, [])

def save_tasks(uid, tasks):
    tasks_db[uid] = tasks
    save_json(TASK_FILE, tasks_db)

# ===============================
# ➕ ADD TASK
# ===============================
if section == "➕ Add Task":
    st.header("➕ Add Task")

    title = st.text_input("Task Title")
    subject = st.text_input("Subject")
    deadline = st.date_input("Deadline")
    difficulty = st.slider("Difficulty", 1, 5, 3)
    importance = st.slider("Importance", 1, 5, 3)
    workload = st.slider("Workload", 1, 10, 5)

    if st.button("Add Task"):
        if title.strip() == "":
            st.warning("Enter task title")
        else:
            tasks = get_tasks(user_id)
            tasks.append({
                "title": title,
                "subject": subject,
                "deadline": str(deadline),
                "difficulty": difficulty,
                "importance": importance,
                "workload": workload,
                "done": False,
                "done_time": None
            })
            save_tasks(user_id, tasks)
            st.success("Task Added")
            st.rerun()

# ===============================
# ⏳ PENDING TASKS
# ===============================
elif section == "⏳ Pending Tasks":
    st.header("⏳ Pending Tasks")

    tasks = get_tasks(user_id)
    today = datetime.now().date()

    for i, t in enumerate(tasks):
        if not t["done"]:
            deadline = datetime.fromisoformat(t["deadline"]).date()
            expired = deadline < today

            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(
                    f"**{t['title']}** ({t['subject']})  \n"
                    f"Deadline: {t['deadline']}"
                )
            with cols[1]:
                if expired:
                    st.error("Late")
                else:
                    if st.checkbox("Done", key=f"done_{i}"):
                        t["done"] = True
                        t["done_time"] = datetime.now().isoformat()
                        save_tasks(user_id, tasks)
                        st.rerun()

# ===============================
# ⭐ PRIORITY TASKS
# ===============================
elif section == "⭐ Priority Tasks":
    st.header("⭐ Priority Tasks")

    tasks = get_tasks(user_id)
    tasks_sorted = sorted(
        tasks,
        key=lambda x: x["importance"] + x["difficulty"] + x["workload"],
        reverse=True
    )

    for t in tasks_sorted:
        if not t["done"]:
            st.info(
                f"{t['title']} | {t['subject']}  \n"
                f"Importance: {t['importance']} | Difficulty: {t['difficulty']} | Workload: {t['workload']}"
            )

# ===============================
# 🧠 DAILY STUDY PLAN (OBSTACLES)
# ===============================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Daily Study Plan")

    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    HOURS = [f"{h:02d}:00" for h in range(24)]

    user_obs = obstacles_db.get(user_id, {})

    st.subheader("Add Obstacle")
    day = st.selectbox("Day", DAYS)
    hour = st.selectbox("Hour", HOURS)
    label = st.text_input("Obstacle Name")

    if st.button("Add Obstacle"):
        user_obs.setdefault(day, {})[hour] = label
        obstacles_db[user_id] = user_obs
        save_json(OBSTACLE_FILE, obstacles_db)
        st.success("Obstacle added")
        st.rerun()

    st.subheader("Weekly Timeline")

    for h in HOURS:
        cols = st.columns(len(DAYS) + 1)
        cols[0].markdown(f"**{h}**")
        for i, d in enumerate(DAYS):
            val = user_obs.get(d, {}).get(h)
            with cols[i + 1]:
                if val:
                    st.warning(val)
                else:
                    st.success("FREE")

    if st.button("Reset Planner"):
        obstacles_db[user_id] = {}
        save_json(OBSTACLE_FILE, obstacles_db)
        st.rerun()

# ===============================
# 📘 STUDY HELP (FREE)
# ===============================
elif section == "📘 Study Help":
    st.header("📘 Study Help (Free)")

    subject = st.selectbox(
        "Subject",
        ["Math", "Physics", "Chemistry", "EGM", "EDG", "PCO", "MPR", "Other"]
    )
    q = st.text_area("Ask your question")

    if st.button("Get Help"):
        if subject == "Physics" and "ohm" in q.lower():
            st.success("Main Answer")
            st.write("Ohm's Law: Voltage is proportional to current.")
            st.info("Explanation")
            st.write("V = I × R")
        else:
            st.info("Study Tip")
            st.write(
                "1. Understand question\n"
                "2. Write formula\n"
                "3. Solve step-by-step\n"
                "4. Revise"
            )

# ===============================
# 📩 RECOMMENDATIONS
# ===============================
elif section == "📩 Recommendations":
    st.header("📩 Recommendations")

    msg = st.text_area("Send a recommendation")

    if st.button("Send"):
        if msg.strip():
            recs_db.append({
                "from": user_id,
                "msg": msg,
                "time": datetime.now().isoformat()
            })
            save_json(REC_FILE, recs_db)
            st.success("Sent")
            st.rerun()

    if user_id == "proto":
        st.subheader("Owner Inbox")
        password = st.text_input("Owner Password", type="password")

        if password == "1357924680proto":
            for r in recs_db[::-1]:
                st.info(f"{r['from']} → {r['msg']}")
