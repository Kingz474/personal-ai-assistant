import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Personal AI Assistant", layout="centered")

# ---------- MEMORY ----------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

tasks = st.session_state.tasks

# ---------- ACADEMIC SUBJECTS ----------
learning_content = {
    "Math": "Revise formulas + solve 5 problems",
    "MPR": "Practice problems + revise theory",
    "EGM": "Understand concepts + solve examples",
    "PCO": "Circuit analysis + revision",
    "Chemistry": "Revise chapters + solve problems",
    "Physics": "Understand formulas + numerical practice",
    "EDG": "Draw diagrams + read notes"
}

# ---------- FUNCTIONS ----------
def priority_score(task):
    days_left = (task["deadline"] - datetime.now().date()).days
    return (task["importance"] * 2) + task["difficulty"] - days_left

# ---------- UI ----------
st.title("🤖 Personal AI Assistant")

menu = st.sidebar.radio(
    "Menu",
    ["Add Task", "Priority Tasks", "Daily Plan", "Study Help", "Pending Tasks"]
)

# ---------- ADD TASK ----------
if menu == "Add Task":
    st.header("➕ Add New Task")

    name = st.text_input("Task Name")
    deadline = st.date_input("Deadline")
    difficulty = st.slider("Difficulty", 1, 5, 3)
    importance = st.slider("Importance", 1, 5, 3)
    subject = st.selectbox("Subject", list(learning_content.keys()))

    if st.button("Add Task"):
        if name:
            tasks.append({
                "name": name,
                "deadline": deadline,
                "difficulty": difficulty,
                "importance": importance,
                "subject": subject,
                "status": "pending"
            })
            st.success("Task added successfully")
        else:
            st.error("Task name required")

# ---------- PRIORITY TASKS ----------
elif menu == "Priority Tasks":
    st.header("🔥 Priority Task List")

    if tasks:
        sorted_tasks = sorted(tasks, key=priority_score, reverse=True)
        for t in sorted_tasks:
            st.write(
                f"**{t['name']}** | Subject: {t['subject']} | Due: {t['deadline']} | Score: {priority_score(t)}"
            )
    else:
        st.info("No tasks added yet")

# ---------- DAILY PLAN ----------
elif menu == "Daily Plan":
    st.header("📅 Daily Plan")
    hours = st.number_input("Available study hours today", 1, 12, 5)

    if st.button("Generate Plan"):
        plan = []
        remaining = hours

        for task in sorted(tasks, key=priority_score, reverse=True):
            if task["status"] == "pending" and remaining > 0:
                plan.append(task["name"])
                remaining -= task["difficulty"]

        if plan:
            st.success("Today's Plan:")
            for p in plan:
                st.write("•", p)
        else:
            st.info("No pending tasks")

# ---------- STUDY HELP ----------
elif menu == "Study Help":
    st.header("📘 Study Help")
    subject = st.selectbox("Choose Subject", list(learning_content.keys()))
    st.write(learning_content[subject])

# ---------- PENDING TASKS ----------
elif menu == "Pending Tasks":
    st.header("⏰ Pending Tasks")

    pending = [t for t in tasks if t["status"] == "pending"]
    if pending:
        for t in pending:
            st.write(f"• {t['name']} | Subject: {t['subject']} | Due: {t['deadline']}")
    else:
        st.success("All tasks completed 🎉")
