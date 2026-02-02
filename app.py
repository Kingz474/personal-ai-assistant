import streamlit as st
import json, os
from datetime import datetime
from PyPDF2 import PdfReader

st.set_page_config(page_title="Personal AI Assistant", layout="wide")

# ---------- FILES ----------
USERS = "users.json"
TASKS = "tasks_data.json"
KB = "knowledge_base.json"
OBST = "obstacles.json"
RANK = "ranking.json"

def load(f, d):
    if os.path.exists(f):
        with open(f) as file:
            return json.load(file)
    return d

def save(f, d):
    with open(f, "w") as file:
        json.dump(d, file, indent=4)

users = load(USERS, {})
tasks = load(TASKS, {})
kb = load(KB, {})
obstacles = load(OBST, {})
ranking = load(RANK, {})

# ---------- LOGIN ----------
st.sidebar.title("🔐 Login")

if "user" not in st.session_state:
    uid = st.sidebar.text_input("User ID")
    pwd = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login / Register"):
        if uid not in users:
            users[uid] = pwd
            tasks[uid] = []
            obstacles[uid] = []
            ranking[uid] = {"score": 0}
            save(USERS, users)
            save(TASKS, tasks)
            save(OBST, obstacles)
            save(RANK, ranking)
        if users.get(uid) == pwd:
            st.session_state.user = uid
            st.rerun()
        else:
            st.sidebar.error("Wrong password")

    st.stop()

user = st.session_state.user

# ---------- MENU ----------
section = st.sidebar.radio(
    "📌 Menu",
    [
        "➕ Add Task",
        "⏳ Pending Tasks",
        "⭐ Priority Tasks",
        "🧠 Daily Study Plan",
        "📘 Study Help",
        "🏆 Ranking"
    ]
)

# ---------- ADD TASK ----------
if section == "➕ Add Task":
    st.header("➕ Add Task")
    t = st.text_input("Task")
    subj = st.text_input("Subject")
    diff = st.slider("Difficulty", 1, 5, 3)
    imp = st.slider("Importance", 1, 5, 3)

    if st.button("Add"):
        tasks[user].append({
            "task": t,
            "subject": subj,
            "difficulty": diff,
            "importance": imp,
            "done": False
        })
        save(TASKS, tasks)
        st.success("Task added")

# ---------- PENDING ----------
elif section == "⏳ Pending Tasks":
    st.header("⏳ Pending Tasks")
    for i, t in enumerate(tasks[user]):
        chk = st.checkbox(t["task"], key=i)
        if chk:
            t["done"] = True
            ranking[user]["score"] += 10
            save(RANK, ranking)
    save(TASKS, tasks)

# ---------- PRIORITY ----------
elif section == "⭐ Priority Tasks":
    st.header("⭐ Priority Tasks")
    sorted_tasks = sorted(
        tasks[user],
        key=lambda x: x["difficulty"] + x["importance"],
        reverse=True
    )
    for t in sorted_tasks:
        st.write("⭐", t["task"])

# ---------- STUDY PLAN ----------
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Weekly Study Plan (24-Hour Timetable)")

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Load user obstacles
    user_obstacles = obstacles.get(user, [])

    st.subheader("➕ Add Obstacle")
    day = st.selectbox("Day", DAYS)
    obs_name = st.text_input("Obstacle name (college, sleep, food)")
    start_hour = st.number_input("Start hour (0–23)", 0, 23, 9)
    end_hour = st.number_input("End hour (0–23)", 0, 23, 17)

    if st.button("Add Obstacle"):
        user_obstacles.append({
            "day": day,
            "name": obs_name,
            "start": start_hour,
            "end": end_hour
        })
        obstacles[user] = user_obstacles
        save(OBST, obstacles)
        st.success("Obstacle added")

    st.divider()
    st.subheader("📅 Weekly Timetable")

    for d in DAYS:
        st.markdown(f"### 📆 {d}")
        day_obs = [o for o in user_obstacles if o["day"] == d]

        table_data = []
        for hr in range(24):
            label = "FREE"
            for o in day_obs:
                if o["start"] <= hr < o["end"]:
                    label = f"⛔ {o['name']}"
                    break
            table_data.append({"Hour": f"{hr}:00 – {hr+1}:00", "Status": label})

        st.table(table_data)

# ---------- STUDY HELP ----------
elif section == "📘 Study Help":
    st.header("📘 Study Help (Shared)")

    pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf:
        reader = PdfReader(pdf)
        text = ""
        for p in reader.pages:
            if p.extract_text():
                text += p.extract_text()
        kb[pdf.name] = text
        save(KB, kb)
        st.success("Saved for all users")

    q = st.text_input("Ask a topic")
    for k in kb:
        if q.lower() in k.lower():
            st.write(kb[k][:2000])

# ---------- RANKING ----------
elif section == "🏆 Ranking":
    st.header("🏆 Leaderboard")

    leaderboard = []

    for u, r in ranking.items():
        completed = 0
        if u in tasks:
            completed = sum(1 for t in tasks[u] if t.get("done"))

        leaderboard.append({
            "Name": u,
            "Tasks Completed": completed,
            "Points": r.get("score", 0)
        })

    leaderboard = sorted(leaderboard, key=lambda x: x["Points"], reverse=True)

    if leaderboard:
        st.table(leaderboard)
    else:
        st.info("No ranking data yet")
