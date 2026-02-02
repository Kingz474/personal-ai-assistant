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

# ===================== LOGIN / REGISTER =====================
st.title("🤖 Personal AI Assistant")

if "user" not in st.session_state:
    st.markdown("## 🔐 Login or Register")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])

        # -------- LOGIN --------
        with tab_login:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login"):
                if username in users and users[username]["password"] == password:
                    st.session_state.user = username
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        # -------- REGISTER --------
        with tab_register:
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass")

            if st.button("Register"):
                if new_user == "" or new_pass == "":
                    st.warning("Please fill all fields")
                elif new_user in users:
                    st.error("Username already exists")
                else:
                    users[new_user] = {
                        "password": new_pass,
                        "tasks_completed": 0,
                        "points": 0
                    }
                    save_users(users)
                    st.success("Account created! Please login.")

    # ⛔ STOP EVERYTHING UNTIL LOGIN
    st.stop()

# ===================== AFTER LOGIN =====================
st.success(f"👋 Welcome, {st.session_state.user}")



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

    if not tasks[user]:
        st.info("No pending tasks")
    else:
        for i, t in enumerate(tasks[user]):
            checked = st.checkbox(
                t["task"],
                value=t.get("done", False),
                key=f"task_{user}_{i}"
            )

            if checked and not t.get("done", False):
                t["done"] = True
                ranking[user]["score"] += 10
                save(RANK, ranking)

            if t.get("done", False):
                st.markdown(
                    f"<span style='color:gray;text-decoration:line-through'>✔ {t['task']}</span>",
                    unsafe_allow_html=True
                )

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

    if not ranking:
        st.info("No ranking data yet")
    else:
        # sort users by score
        sorted_users = sorted(
            ranking.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        top3 = sorted_users[:3]

        st.markdown("### 🥇 Top Performers")

        col1, col2, col3 = st.columns([1, 1.2, 1])

        if len(top3) > 1:
            with col1:
                st.markdown(
                    f"""
                    <div style="background:#c0c0c0;padding:20px;border-radius:10px;height:160px;text-align:center">
                    <h3>🥈 2nd</h3>
                    <b>{top3[1][0]}</b><br>
                    {top3[1][1]["score"]} pts
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if len(top3) > 0:
            with col2:
                st.markdown(
                    f"""
                    <div style="background:#ffd700;padding:25px;border-radius:10px;height:220px;text-align:center">
                    <h2>🥇 1st</h2>
                    <b>{top3[0][0]}</b><br>
                    {top3[0][1]["score"]} pts
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if len(top3) > 2:
            with col3:
                st.markdown(
                    f"""
                    <div style="background:#cd7f32;padding:20px;border-radius:10px;height:160px;text-align:center">
                    <h3>🥉 3rd</h3>
                    <b>{top3[2][0]}</b><br>
                    {top3[2][1]["score"]} pts
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.markdown("### 📊 Full Ranking")

        for i, (user, data) in enumerate(sorted_users, start=1):
            st.write(f"{i}. **{user}** — {data['score']} pts | Tasks: {data.get('tasks',0)}")
