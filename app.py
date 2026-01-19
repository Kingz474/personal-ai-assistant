import streamlit as st
import json, os
from datetime import datetime, time

# ================= FILES =================
TASK_FILE = "tasks.json"
REC_FILE = "recommendations.json"
OBS_FILE = "obstacles.json"

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
obstacles = load(OBS_FILE)

# ================= USER =================
st.title("📚 Personal AI Study Assistant")

user = st.text_input("Enter your User ID")
if not user:
    st.stop()

tasks.setdefault(user, [])
obstacles.setdefault(user, {})
save(TASK_FILE, tasks)
save(OBS_FILE, obstacles)

# ================= MENU =================
section = st.sidebar.radio(
    "Sections",
    [
        "➕ Add Task",
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

    title = st.text_input("Task Name")
    subject = st.text_input("Subject")
    deadline = st.date_input("Deadline")

    col1, col2, col3 = st.columns(3)
    difficulty = col1.slider("Difficulty", 1, 5)
    importance = col2.slider("Importance", 1, 5)
    workload = col3.slider("Workload", 1, 5)

    if st.button("Add Task"):
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
        st.success("Task added")

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
                st.markdown(f"~~{t['title']}~~")
            else:
                st.info(f"{t['title']} ({t['subject']}) | Priority: {score}")

        with col2:
            if st.checkbox("✔", key=f"done{i}", value=t["done"]):
                t["done"] = True
                t["done_time"] = datetime.now().isoformat()

    save(TASK_FILE, tasks)

# =====================================================
# 🧠 DAILY STUDY PLAN (UPDATED SECTION)
# =====================================================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Weekly Obstacle Timetable (24-Hour)")

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    TIME_SLOTS = [f"{h:02d}:00-{h+1:02d}:00" for h in range(0, 24)]

    if "table" not in st.session_state:
        st.session_state.table = {
            slot: {day: "" for day in DAYS}
            for slot in TIME_SLOTS
        }

    st.subheader("➕ Add Obstacle")
    obs_name = st.text_input("Obstacle Name (College, Lunch, Travel etc)")
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
                s_time = datetime.strptime(s, "%H:%M").time()
                e_time = datetime.strptime(e, "%H:%M").time()
                if s_time >= start and e_time <= end:
                    st.session_state.table[slot][obs_day] = obs_name
            st.success("Obstacle added")

    st.subheader("📅 Weekly Timetable")

    for slot in TIME_SLOTS:
        cols = st.columns(len(DAYS) + 1)
        cols[0].markdown(f"**{slot}**")
        for i, day in enumerate(DAYS):
            val = st.session_state.table[slot][day]
            if val:
                cols[i+1].warning(val)
            else:
                cols[i+1].success("FREE")

    if st.button("🔄 Reset Timetable"):
        for slot in st.session_state.table:
            for day in DAYS:
                st.session_state.table[slot][day] = ""
        st.success("Timetable reset")

# =====================================================
# 📩 RECOMMENDATIONS
# =====================================================
elif section == "📩 Recommendations":
    st.header("📩 Recommendations")

    if user == "proto":
        pwd = st.text_input("Owner Password", type="password")
        if pwd == "1357924680proto":
            recs.setdefault("proto", [])
            for r in recs["proto"]:
                st.info(f"From: {r['from']}\n\n{r['msg']}")
        else:
            st.error("Wrong password")
    else:
        msg = st.text_area("Send recommendation to owner (proto)")
        if st.button("Send"):
            recs.setdefault("proto", [])
            recs["proto"].append({
                "from": user,
                "msg": msg,
                "time": datetime.now().isoformat()
            })
            save(REC_FILE, recs)
            st.success("Sent")

