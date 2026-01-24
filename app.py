import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config("Personal Study Assistant", layout="wide")

# =====================================================
# JSON HELPERS
# =====================================================
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

# =====================================================
# FILES
# =====================================================
TASK_FILE = "tasks_data.json"
OBSTACLE_FILE = "obstacles.json"
REC_FILE = "recommendations.json"
KB_FILE = "knowledge_base.json"

tasks_db = load_json(TASK_FILE, {})
obstacles_db = load_json(OBSTACLE_FILE, {})
recs_db = load_json(REC_FILE, [])
kb_db = load_json(KB_FILE, {})

# =====================================================
# USER
# =====================================================
st.sidebar.title("👤 User")
user_id = st.sidebar.text_input("User ID", value="guest")

# =====================================================
# SECTIONS
# =====================================================
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

# =====================================================
# TASK FUNCTIONS
# =====================================================
def get_tasks(uid):
    return tasks_db.get(uid, [])

def save_tasks(uid, tasks):
    tasks_db[uid] = tasks
    save_json(TASK_FILE, tasks_db)

# =====================================================
# ➕ ADD TASK
# =====================================================
if section == "➕ Add Task":
    st.header("➕ Add Task")

    title = st.text_input("Task Title")
    subject = st.text_input("Subject")
    deadline = st.date_input("Deadline")
    difficulty = st.slider("Difficulty", 1, 5, 3)
    importance = st.slider("Importance", 1, 5, 3)
    workload = st.slider("Workload", 1, 10, 5)

    if st.button("Add Task"):
        if title.strip():
            t = {
                "title": title,
                "subject": subject,
                "deadline": str(deadline),
                "difficulty": difficulty,
                "importance": importance,
                "workload": workload,
                "done": False
            }
            tasks = get_tasks(user_id)
            tasks.append(t)
            save_tasks(user_id, tasks)
            st.success("Task saved")
            st.rerun()

# =====================================================
# ⏳ PENDING TASKS
# =====================================================
elif section == "⏳ Pending Tasks":
    st.header("⏳ Pending Tasks")
    tasks = get_tasks(user_id)

    for i, t in enumerate(tasks):
        if not t["done"]:
            cols = st.columns([4,1])
            cols[0].markdown(f"**{t['title']}** ({t['subject']})")
            if cols[1].checkbox("Done", key=f"d{i}"):
                t["done"] = True
                save_tasks(user_id, tasks)
                st.rerun()

# =====================================================
# ⭐ PRIORITY TASKS
# =====================================================
elif section == "⭐ Priority Tasks":
    st.header("⭐ Priority Tasks")
    tasks = sorted(
        get_tasks(user_id),
        key=lambda x: x["importance"] + x["difficulty"] + x["workload"],
        reverse=True
    )
    for t in tasks:
        if not t["done"]:
            st.info(f"{t['title']} → {t['subject']}")

# =====================================================
# 🧠 DAILY STUDY PLAN (START–END OBSTACLES)
# =====================================================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Daily Study Planner (24-Hour)")

    DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    HOURS = list(range(24))

    user_obs = obstacles_db.get(user_id, [])

    st.subheader("Add Obstacle")
    day = st.selectbox("Day", DAYS)
    start = st.number_input("Start Hour (0-23)", 0, 23)
    end = st.number_input("End Hour (1-24)", 1, 24)
    label = st.text_input("Obstacle Name")

    if st.button("Add Obstacle"):
        user_obs.append({
            "day": day,
            "start": start,
            "end": end,
            "label": label
        })
        obstacles_db[user_id] = user_obs
        save_json(OBSTACLE_FILE, obstacles_db)
        st.success("Obstacle added")
        st.rerun()

    st.subheader("Weekly Planner")

    for h in HOURS:
        cols = st.columns(len(DAYS)+1)
        cols[0].markdown(f"**{h:02d}:00**")
        for i, d in enumerate(DAYS):
            block = None
            for o in user_obs:
                if o["day"] == d and o["start"] <= h < o["end"]:
                    block = o["label"]
            with cols[i+1]:
                if block:
                    st.warning(block)
                else:
                    st.success("FREE")

    if st.button("Reset Planner"):
        obstacles_db[user_id] = []
        save_json(OBSTACLE_FILE, obstacles_db)
        st.rerun()

# =====================================================
# 📘 STUDY HELP (SHARED KNOWLEDGE BASE)
# =====================================================
elif section == "📘 Study Help":
    st.header("📘 Study Help (Shared Knowledge)")

    topic = st.text_input("Topic")
    note = st.text_area("Paste Notes (only once)")

    if st.button("Save Notes"):
        if topic.strip() and note.strip():
            kb_db[topic.lower()] = note
            save_json(KB_FILE, kb_db)
            st.success("Saved for everyone")

    st.divider()

    q = st.text_input("Ask a Question")
    if q:
        key = q.lower()
        if key in kb_db:
            st.success("Main Answer")
            st.write(kb_db[key])
            st.info("Explanation")
            st.write(
                "• Read carefully\n"
                "• Understand concepts\n"
                "• Apply formulas\n"
                "• Revise examples"
            )
        else:
            st.warning("No notes yet. Add once to help all users.")

# =====================================================
# 📩 RECOMMENDATIONS
# =====================================================
elif section == "📩 Recommendations":
    st.header("📩 Recommendations")

    msg = st.text_area("Send recommendation")
    if st.button("Send"):
        if msg.strip():
            recs_db.append({
                "from": user_id,
                "msg": msg,
                "time": datetime.now().isoformat()
            })
            save_json(REC_FILE, recs_db)
            st.success("Sent")

    if user_id == "proto":
        st.subheader("Owner Inbox")
        pwd = st.text_input("Password", type="password")
        if pwd == "1357924680proto":
            for r in recs_db[::-1]:
                st.info(f"{r['from']} → {r['msg']}")

