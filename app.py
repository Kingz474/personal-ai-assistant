import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config("Personal Study Assistant", layout="wide")

# =========================
# Optional Imports
# =========================
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

# =========================
# User session
# =========================
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

# =========================
# JSON helpers
# =========================
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

# =========================
# Files
# =========================
TASK_FILE = "tasks_data.json"
OBSTACLE_FILE = "obstacles.json"
REC_FILE = "recommendations.json"
KB_FILE = "knowledge_base.json"

tasks_db = load_json(TASK_FILE, {})
obstacles_db = load_json(OBSTACLE_FILE, {})
recs_db = load_json(REC_FILE, [])
kb_db = load_json(KB_FILE, {})

# =========================
# Sections
# =========================
section = st.sidebar.radio(
    "Sections",
    [
        "➕ Add Task",
        "⏳ Pending Tasks",
        "⭐ Priority Tasks",
        "🧠 Daily Study Plan",
        "📘 Study Help",
        "📚 QB",
        "📩 Recommendations"
    ]
)

# =========================
# Task helpers
# =========================
def get_tasks(uid):
    return tasks_db.get(uid, [])

def save_tasks(uid, tasks):
    tasks_db[uid] = tasks
    save_json(TASK_FILE, tasks_db)

# =========================
# Add Task
# =========================
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

# =========================
# Pending Tasks
# =========================
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

# =========================
# Priority Tasks
# =========================
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

# =========================
# Daily Study Plan
# =========================
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
        user_obs.append({"day": day,"start": start,"end": end,"label": label})
        obstacles_db[user_id] = user_obs
        save_json(OBSTACLE_FILE, obstacles_db)
        st.success("Obstacle added")
        st.rerun()

    st.subheader("Weekly Planner")
    for h in HOURS:
        cols = st.columns(len(DAYS)+1)
        cols[0].markdown(f"**{h:02d}:00**")
        for i,d in enumerate(DAYS):
            block = None
            for o in user_obs:
                if o["day"] == d and o["start"] <= h < o["end"]:
                    block = o["label"]
            with cols[i+1]:
                st.warning(block) if block else st.success("FREE")

# =========================
# Study Help
# =========================
elif section == "📖 Study Help":
    import streamlit as st
    import json

    st.title("📖 Study Help")
    st.markdown("Ask questions from notes and get explained answers")

    KB_FILE = "knowledge_base.json"

    # ---------- LOAD DATABASE ----------
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
    except:
        knowledge_base = []

    # ---------- PDF UPLOADER (ONLY ONE) ----------
    st.subheader("📄 Upload Study Notes (PDF)")
st.subheader("Upload Study Material (PDF)")

pdf_file = st.file_uploader(
    "Upload a text-based PDF (simple English PDFs work best)",
    type=["pdf"],
    key="study_pdf"
)

if pdf_file is None:
    st.info("📄 Please upload a PDF file to continue.")
else:
    st.success(f"✅ File uploaded: {pdf_file.name}")

    # reset pointer (IMPORTANT for Streamlit Cloud)
    pdf_file.seek(0)

    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(pdf_file)
        extracted_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        if extracted_text.strip() == "":
            st.error("❌ PDF uploaded but no readable text found.")
            st.warning("⚠️ Try a text-based PDF (not scanned images).")
        else:
            st.subheader("Extracted Content Preview")
            st.text_area(
                "PDF Text",
                extracted_text[:3000],
                height=250
            )

    except Exception as e:
        st.error("❌ Error while reading PDF.")
        st.write(str(e))

    # ---------- QUESTION INPUT ----------
    st.subheader("🔍 Ask a Question")

    user_question = st.text_input(
        "Ask about any topic from your notes",
        placeholder="Example: What is Mechanical Advantage?"
    )

    if user_question:
        found = False

        for note in knowledge_base:
            if user_question.lower() in note.lower():
                found = True
                st.markdown("### ✅ Answer from your notes")
                st.write(note[:1500])  # limit output
                break

        if not found:
            st.warning("No exact match found. Try different keywords.")


elif section == "💡 Recommendation":
    import streamlit as st
    import json
    from datetime import datetime

    st.title("💡 Recommendations")

    REC_FILE = "recommendations.json"
    OWNER_ID = "proto"
    OWNER_PASS = "1357924680proto"

    # ---------- LOAD DATA ----------
    try:
        with open(REC_FILE, "r", encoding="utf-8") as f:
            recommendations = json.load(f)
    except:
        recommendations = []

    # ---------- USER SENDS RECOMMENDATION ----------
    st.subheader("✍️ Send a Recommendation")

    user_name = st.text_input("Your User ID", placeholder="Enter your ID")
    rec_text = st.text_area(
        "Your Recommendation",
        placeholder="Write your suggestion here..."
    )

    if st.button("Send Recommendation"):
        if user_name.strip() and rec_text.strip():
            recommendations.append({
                "from": user_name,
                "text": rec_text,
                "time": datetime.now().strftime("%d-%m-%Y %H:%M")
            })

            with open(REC_FILE, "w", encoding="utf-8") as f:
                json.dump(recommendations, f, indent=2)

            st.success("Recommendation sent successfully ✅")
        else:
            st.warning("Please enter User ID and recommendation.")

    st.divider()

    # ---------- OWNER LOGIN ----------
    st.subheader("🔐 Owner Login")

    owner_id = st.text_input("Owner ID")
    owner_pass = st.text_input("Password", type="password")

    if st.button("Login as Owner"):
        if owner_id == OWNER_ID and owner_pass == OWNER_PASS:
            st.success("Welcome proto 👑")

            st.subheader("📥 All Recommendations")

            if recommendations:
                for i, rec in enumerate(reversed(recommendations), start=1):
                    st.markdown(f"""
**#{i}**  
👤 From: `{rec['from']}`  
🕒 {rec['time']}  
💬 {rec['text']}
---
""")
            else:
                st.info("No recommendations yet.")
        else:
            st.error("Invalid owner credentials ❌")


