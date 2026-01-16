import streamlit as st
import json
import os
from datetime import datetime, timedelta

# ------------------ FILES ------------------
TASK_FILE = "tasks.json"
REC_FILE = "recommendations.json"

# ------------------ HELPERS ------------------
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

tasks_data = load_json(TASK_FILE, {})
rec_data = load_json(REC_FILE, {})

# ------------------ LOGIN ------------------
st.title("📚 Personal AI Study Assistant")

user_id = st.text_input("Enter your User ID")

if not user_id:
    st.stop()

if user_id not in tasks_data:
    tasks_data[user_id] = []
    save_json(TASK_FILE, tasks_data)

# ------------------ ADD TASK ------------------
st.header("➕ Add Task")

task_name = st.text_input("Task Name")
subject = st.text_input("Subject (type your own)")
deadline = st.date_input("Deadline")
workload = st.slider("How heavy is the work?", 1, 10, 5)

if st.button("Add Task"):
    tasks_data[user_id].append({
        "task": task_name,
        "subject": subject,
        "deadline": deadline.isoformat(),
        "workload": workload,
        "completed": False,
        "completed_time": None
    })
    save_json(TASK_FILE, tasks_data)
    st.success("Task added!")

# ------------------ TASK VIEW ------------------
st.header("📋 Your Tasks")

now = datetime.now()

for t in tasks_data[user_id][:]:
    deadline_dt = datetime.fromisoformat(t["deadline"])
    overdue = now > deadline_dt and not t["completed"]

    style = ""
    if overdue:
        style = "color:red;"
    if t["completed"]:
        style = "opacity:0.4;"

    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(
            f"<div style='{style}'>"
            f"📌 {t['task']} | {t['subject']} | "
            f"Workload: {t['workload']} | "
            f"Deadline: {t['deadline']}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col2:
        if st.checkbox("Done", value=t["completed"], key=t["task"]):
            if not t["completed"]:
                t["completed"] = True
                t["completed_time"] = datetime.now().isoformat()
                save_json(TASK_FILE, tasks_data)

    # auto delete after 1 day
    if t["completed"] and t["completed_time"]:
        if datetime.now() > datetime.fromisoformat(t["completed_time"]) + timedelta(days=1):
            tasks_data[user_id].remove(t)
            save_json(TASK_FILE, tasks_data)

# ------------------ STUDY PLAN ------------------
st.header("🧠 Study Plan")

schedule = st.text_area(
    "Enter your full day schedule",
    placeholder="Example:\n6-7 Wake up\n7-9 College\n9-11 Study Math..."
)

if st.button("Get Study Suggestions"):
    st.success("📌 AI Suggestions:")
    st.write("""
    • Study high workload tasks first  
    • Use 50 min study + 10 min break  
    • Keep hardest subject in morning  
    • Revise completed tasks briefly at night  
    """)

# ------------------ RECOMMENDATIONS ------------------
st.header("💡 Send Recommendation")

rec_msg = st.text_area("Your recommendation")

if st.button("Send to Owner"):
    rec_data.setdefault("proto", []).append({
        "from": user_id,
        "message": rec_msg,
        "time": datetime.now().isoformat()
    })
    save_json(REC_FILE, rec_data)
    st.success("Recommendation sent!")

# ------------------ OWNER INBOX ------------------
if user_id == "proto":
    st.header("🔐 Owner Recommendation Inbox")
    pwd = st.text_input("Enter Owner Password", type="password")

    if pwd == "1357924680proto":
        for r in rec_data.get("proto", []):
            st.info(f"From: {r['from']}\n\n{r['message']}")
    else:
        st.warning("Wrong password")
