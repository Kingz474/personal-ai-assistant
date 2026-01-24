import streamlit as st
import json
import os
from datetime import datetime
from PyPDF2 import PdfReader

# ==========================
# OPTIONAL OCR (SAFE)
# ==========================
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

st.set_page_config("Personal Study Assistant", layout="wide")

# =====================================================
# SESSION LOGIN (FIXED USER ID)
# =====================================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None

st.sidebar.title("👤 Login")

if st.session_state.user_id is None:
    temp_id = st.sidebar.text_input("Enter User ID")
    if st.sidebar.button("Login"):
        if temp_id.strip():
            st.session_state.user_id = temp_id.strip()
            st.rerun()
else:
    st.sidebar.success(f"Logged in as: {st.session_state.user_id}")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

if st.session_state.user_id is None:
    st.stop()

user_id = st.session_state.user_id

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
# SIDEBAR SECTIONS
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
# TASK HELPERS
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

    if st.button("Add Task") and title.strip():
        tasks = get_tasks(user_id)
        tasks.append({
            "title": title,
            "subject": subject,
            "deadline": str(deadline),
            "difficulty": difficulty,
            "importance": importance,
            "workload": workload,
            "done": False
        })
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
# 🧠 DAILY STUDY PLAN
# =====================================================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Daily Study Planner (24-Hour)")

    DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    HOURS = list(range(24))
    user_obs = obstacles_db.get(user_id, [])

    st.subheader("Add Obstacle")
    day = st.selectbox("Day", DAYS)
    start = st.number_input("Start Hour (0–23)", 0, 23)
    end = st.number_input("End Hour (1–24)", 1, 24)
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

# =====================================================
# 📘 STUDY HELP (PDF + IMAGE + TEXT)
# =====================================================
elif section == "📘 Study Help":
    st.header("📘 Study Help (Upload Once, Use Forever)")

    topic = st.text_input("Topic / Chapter Name")

    tabs = st.tabs(["📄 PDF", "🖼 Image", "✍ Text"])
    extracted_text = ""

    with tabs[0]:
        pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if pdf:
            reader = PdfReader(pdf)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""

    with tabs[1]:
        img = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])
        if img:
            if OCR_AVAILABLE:
                image = Image.open(img)
                st.image(image, caption="Uploaded Image")
                extracted_text += pytesseract.image_to_string(image)
            else:
                st.warning("Image OCR not available. Use PDF or Text.")

    with tabs[2]:
        extracted_text += st.text_area("Paste notes manually")

    if st.button("Save Notes"):
        if topic.strip() and extracted_text.strip():
            kb_db[topic.lower()] = extracted_text
            save_json(KB_FILE, kb_db)
            st.success("Saved for all users")

    st.divider()

    query = st.text_input("Search Topic")
    if query.lower() in kb_db:
        st.success("Main Content")
        st.write(kb_db[query.lower()])
        st.info("Explanation")
        st.write(
            "• Read carefully\n"
            "• Understand concepts\n"
            "• Apply formulas\n"
            "• Practice examples"
        )

# =====================================================
# 📩 RECOMMENDATIONS
# =====================================================
elif section == "📩 Recommendations":
    st.header("📩 Recommendations")

    msg = st.text_area("Send recommendation to owner")

    if st.button("Send") and msg.strip():
        recs_db.append({
            "from": user_id,
            "msg": msg,
            "time": datetime.now().isoformat()
        })
        save_json(REC_FILE, recs_db)
        st.success("Sent")

    if user_id == "proto":
        pwd = st.text_input("Owner Password", type="password")
        if pwd == "1357924680proto":
            for r in recs_db[::-1]:
                st.info(f"{r['from']} → {r['msg']}")
