import streamlit as st
import json, os
from datetime import datetime, timedelta

# ---------------- FILES ----------------
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

# ---------------- LOGIN ----------------
st.title("📚 Personal AI Study Assistant")

user_id = st.text_input("Enter your User ID")

if not user_id:
    st.stop()

if user_id not in tasks:
    tasks[user_id] = []
    save(TASK_FILE, tasks)

# ---------------- SECTION SELECTOR ----------------
section = st.sidebar.radio(
    "Choose Section",
    [
        "➕ Add Task",
        "📋 Pending Tasks",
        "🔥 Priority Tasks",
        "🧠 Study Plan",
        "💡 Recommendations"
    ]
)

now = datetime.now()

# =================================================
# ➕ ADD TASK
# =================================================
if section == "➕ Add Task":
    st.header("➕ Add New Task")

    name = st.text_input("Task name")
    subject = st.text_input("Subject (type your own)")
    deadline = st.date_input("Deadline")
    workload = st.slider("Workload (how heavy?)", 1, 10, 5)

    if st.button("Add Task"):
        tasks[user_id].append({
            "name": name,
            "subject": subject,
            "deadline": deadline.isoformat(),
            "workload": workload,
            "done": False,
            "done_time": None
        })
        save(TASK_FILE, tasks)
        st.success("Task added successfully!")

# =================================================
# 📋 PENDING TASKS
# =================================================
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
            f"📌 {t['name']} | {t['subject']} | "
            f"Workload: {t['workload']} | "
            f"Deadline: {t['deadline']}"
            f"</div>",
            unsafe_allow_html=True
        )

        if st.checkbox("Completed", value=t["done"], key=t["name"]):
            if not t["done"]:
                t["done"] = True
                t["done_time"] = now.isoformat()
                save(TASK_FILE, tasks)

        # remove after 1 day
        if t["done"] and t["done_time"]:
            if now > datetime.fromisoformat(t["done_time"]) + timedelta(days=1):
                tasks[user_id].remove(t)
                save(TASK_FILE, tasks)

# =================================================
# 🔥 PRIORITY TASKS
# =================================================
elif section == "🔥 Priority Tasks":
    st.header("🔥 Priority Tasks")

    priority = sorted(
        tasks[user_id],
        key=lambda x: (
            x["done"],
            datetime.fromisoformat(x["deadline"]),
            -x["workload"]
        )
    )

    for t in priority:
        style = "opacity:0.4;" if t["done"] else ""
        st.markdown(
            f"<div style='{style}'>"
            f"🔥 {t['name']} | {t['subject']} | "
            f"Workload: {t['workload']} | "
            f"Deadline: {t['deadline']}"
            f"</div>",
            unsafe_allow_html=True
        )

# =================================================
# 🧠 STUDY PLAN
# =================================================
elif section == "🧠 Study Plan":
    st.header("🧠 Daily Study Plan")

    schedule = st.text_area(
        "Enter your full-day schedule",
        placeholder="6–7 Wake up\n7–9 College\n9–11 Study Math\n..."
    )

    if st.button("Get Suggestions"):
        st.success("AI Suggestions")
        st.write("""
        • Do highest workload tasks first  
        • Study difficult subjects in the morning  
        • Use 50 min study + 10 min break  
        • Revise completed tasks lightly at night  
        """)

# =================================================
# 💡 RECOMMENDATIONS
# =================================================
elif section == "💡 Recommendations":
    st.header("💡 Recommendations")

    msg = st.text_area("Write your recommendation")

    if st.button("Send to Owner"):
        recs.setdefault("proto", []).append({
            "from": user_id,
            "msg": msg,
            "time": now.isoformat()
        })
        save(REC_FILE, recs)
        st.success("Sent to owner!")

    # OWNER VIEW
    if user_id == "proto":
        st.subheader("🔐 Owner Inbox")
        pwd = st.text_input("Owner password", type="password")

        if pwd == "1357924680proto":
            for r in recs.get("proto", []):
                st.info(f"From: {r['from']}\n\n{r['msg']}")
        elif pwd:
            st.error("Wrong password")
