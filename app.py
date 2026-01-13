import streamlit as st
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="Personal AI Assistant", layout="centered")

# ---------- STORAGE ----------
DATA_FILE = "tasks_data.json"

# Load JSON
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

with open(DATA_FILE, "r") as f:
    all_users_tasks = json.load(f)

# ---------- USER LOGIN ----------
st.sidebar.title("User Login")
user_id = st.sidebar.text_input("Enter your user ID or name")

if not user_id:
    st.warning("Please enter your user ID to continue")
    st.stop()

# Ensure user has a list in JSON
if user_id not in all_users_tasks:
    all_users_tasks[user_id] = []

tasks = all_users_tasks[user_id]

# ---------- DEFAULT STUDY HELP ----------
default_subjects = {
    "Math": "Revise formulas + solve 5 problems",
    "MPR": "Practice problems + revise theory",
    "EGM": "Understand concepts + solve examples",
    "PCO": "Circuit analysis + revision",
    "Chemistry": "Revise chapters + solve problems",
    "Physics": "Understand formulas + numerical practice",
    "EDG": "Draw diagrams + read notes"
}

# ---------- FUNCTIONS ----------
def save_tasks():
    all_users_tasks[user_id] = tasks
    with open(DATA_FILE, "w") as f:
        json.dump(all_users_tasks, f, default=str)

def priority_score(task):
    days_left = (datetime.strptime(task["deadline"], "%Y-%m-%d").date() - datetime.now().date()).days
    return (task["importance"] * 2) + task["difficulty"] - days_left

def remove_old_completed():
    today = datetime.now().date()
    global tasks
    tasks[:] = [t for t in tasks if not (t["status"]=="done" and t.get("completed_date") and (today - datetime.strptime(t["completed_date"], "%Y-%m-%d").date()).days >= 1)]
    save_tasks()

def get_task_style(task):
    if task["status"] == "done":
        return "color: grey; opacity:0.5;"  # faded
    elif datetime.strptime(task["deadline"], "%Y-%m-%d").date() < datetime.now().date() and task["status"] != "done":
        return "color: red; font-weight: bold;"  # overdue
    else:
        return ""

# ---------- UI ----------
st.title(f"🤖 Personal AI Assistant - {user_id}")

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
    subject = st.text_input("Subject (type your own or use default)")

    if st.button("Add Task"):
        if name and subject:
            tasks.append({
                "name": name,
                "deadline": str(deadline),
                "difficulty": difficulty,
                "importance": importance,
                "subject": subject,
                "status": "pending",
                "completed_date": None
            })
            save_tasks()
            st.success("Task added successfully")
        else:
            st.error("Task name and subject required")

# ---------- PRIORITY TASKS ----------
elif menu == "Priority Tasks":
    st.header("🔥 Priority Task List")
    remove_old_completed()

    if tasks:
        sorted_tasks = sorted(tasks, key=priority_score, reverse=True)
        for idx, t in enumerate(sorted_tasks):
            checked = t["status"] == "done"
            new_checked = st.checkbox(
                f"{t['name']} | {t['subject']} | Due: {t['deadline']} | Score: {priority_score(t)}",
                value=checked, key=f"priority_{idx}"
            )
            if new_checked and not checked:
                t["status"] = "done"
                t["completed_date"] = str(datetime.now().date())
                save_tasks()
            elif not new_checked and checked:
                t["status"] = "pending"
                t["completed_date"] = None
                save_tasks()
            style = get_task_style(t)
            st.markdown(f"<span style='{style}'></span>", unsafe_allow_html=True)
    else:
        st.info("No tasks added yet")

# ---------- DAILY PLAN ----------
elif menu == "Daily Plan":
    st.header("📅 Daily Plan")
    remove_old_completed()
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
    subject = st.text_input("Choose Subject (or type your own)")
    if subject:
        info = default_subjects.get(subject, f"Study plan for {subject}: Create your own notes, exercises, and revision.")
        st.write(info)

# ---------- PENDING TASKS ----------
elif menu == "Pending Tasks":
    st.header("⏰ Pending Tasks")
    remove_old_completed()

    if tasks:
        for idx, t in enumerate(tasks):
            checked = t["status"] == "done"
            new_checked = st.checkbox(
                f"{t['name']} | {t['subject']} | Due: {t['deadline']}",
                value=checked, key=f"pending_{idx}"
            )
            if new_checked and not checked:
                t["status"] = "done"
                t["completed_date"] = str(datetime.now().date())
                save_tasks()
            elif not new_checked and checked:
                t["status"] = "pending"
                t["completed_date"] = None
                save_tasks()
            style = get_task_style(t)
            st.markdown(f"<span style='{style}'></span>", unsafe_allow_html=True)
    else:
        st.success("All tasks completed 🎉")
