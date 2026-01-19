import streamlit as st
import json, os, hashlib
from datetime import datetime, time, timedelta

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Personal Study Assistant",
    page_icon="📚",
    layout="wide"
)

# ================= SOFT UI CSS =================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.card {
    padding: 1.2rem;
    border-radius: 12px;
    background-color: #ffffff10;
    margin-bottom: 1rem;
}
.chat-user {
    background: #1f2937;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 6px;
}
.chat-ai {
    background: #0f766e;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# ================= FILES =================
TASK_FILE = "tasks.json"
REC_FILE = "recommendations.json"
KB_FILE = "knowledge_base.json"

# ================= LOAD / SAVE =================
@st.cache_data
def load(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

tasks = load(TASK_FILE)
recs = load(REC_FILE)
knowledge_base = load(KB_FILE)

# ================= HEADER =================
st.markdown("## 📚 Personal Study Assistant")
st.caption("Plan • Organize • Learn smarter")

st.markdown("""
<div style="position:fixed;top:18px;right:30px;
font-size:12px;color:#9ca3af;">
v1.3
</div>
""", unsafe_allow_html=True)

st.divider()

# ================= USER =================
user = st.text_input("User ID", placeholder="Enter your name or ID")
if not user:
    st.stop()

tasks.setdefault(user, [])
save(TASK_FILE, tasks)

# ================= SIDEBAR =================
st.sidebar.markdown("### 📌 Menu")
section = st.sidebar.radio(
    "",
    [
        "➕ Add Task",
        "⏳ Pending Tasks",
        "⭐ Priority Tasks",
        "🧠 Daily Study Plan",
        "📚 Study Help",
        "📩 Recommendations"
    ]
)

# =====================================================
# ➕ ADD TASK
# =====================================================
if section == "➕ Add Task":
    st.markdown("### ➕ Add New Task")

    with st.form("task_form", clear_on_submit=True):
        title = st.text_input("Task Name")
        subject = st.text_input("Subject")
        deadline = st.date_input("Deadline")

        c1, c2, c3 = st.columns(3)
        difficulty = c1.slider("Difficulty", 1, 5)
        importance = c2.slider("Importance", 1, 5)
        workload = c3.slider("Workload", 1, 5)

        submit = st.form_submit_button("Add Task")

    if submit and title.strip():
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
        st.success("Task added successfully")

# =====================================================
# ⏳ PENDING TASKS
# =====================================================
elif section == "⏳ Pending Tasks":
    st.markdown("### ⏳ Pending Tasks")

    now = datetime.now()
    for i, t in enumerate(tasks[user]):
        deadline = datetime.fromisoformat(t["deadline"]).date()
        expired = now.date() > deadline

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if t["done"]:
            st.markdown(f"✔ **{t['title']}** *(completed)*")
        elif expired:
            st.error(f"{t['title']} — Deadline missed")
        else:
            st.info(f"{t['title']} ({t['subject']})")

        if st.checkbox("Mark as done", key=f"p{i}", value=t["done"]):
            t["done"] = True
            t["done_time"] = datetime.now().isoformat()

        st.markdown("</div>", unsafe_allow_html=True)

    save(TASK_FILE, tasks)

# =====================================================
# ⭐ PRIORITY TASKS
# =====================================================
elif section == "⭐ Priority Tasks":
    st.markdown("### ⭐ Priority Overview")

    for i, t in enumerate(tasks[user]):
        score = t["difficulty"] + t["importance"] + t["workload"]

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"**{t['title']}** — Priority: `{score}`")

        if st.checkbox("Completed", key=f"s{i}", value=t["done"]):
            t["done"] = True
            t["done_time"] = datetime.now().isoformat()

        st.markdown("</div>", unsafe_allow_html=True)

    save(TASK_FILE, tasks)

# =====================================================
# 🧠 DAILY STUDY PLAN
# =====================================================
elif section == "🧠 Daily Study Plan":
    st.markdown("### 🧠 Weekly Study Planner")

    DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    TIME_SLOTS = [f"{h:02d}:00-{h+1:02d}:00" for h in range(24)]

    if "table" not in st.session_state:
        st.session_state.table = {
            slot: {day: "" for day in DAYS} for slot in TIME_SLOTS
        }

    with st.expander("➕ Add Obstacle"):
        obs = st.text_input("Obstacle name")
        day = st.selectbox("Day", DAYS)
        c1, c2 = st.columns(2)
        start = c1.time_input("Start", time(9,0))
        end = c2.time_input("End", time(10,0))

        if st.button("Add"):
            for slot in TIME_SLOTS:
                s, e = slot.split("-")
                if time.fromisoformat(s) >= start and time.fromisoformat(e) <= end:
                    st.session_state.table[slot][day] = obs
            st.success("Obstacle added")

    for slot in TIME_SLOTS:
        cols = st.columns(len(DAYS)+1)
        cols[0].markdown(f"**{slot}**")
        for i, d in enumerate(DAYS):
            cols[i+1].markdown(
                "🟢 FREE" if not st.session_state.table[slot][d]
                else f"🔴 {st.session_state.table[slot][d]}"
            )

# =====================================================
# 📚 STUDY HELP
# =====================================================
elif section == "📚 Study Help":
    st.markdown("### 📚 Study Help")
    st.caption("Shared knowledge — upload once, reuse forever")

    uploaded = st.file_uploader(
        "Upload document",
        type=["txt","pdf","docx","pptx"]
    )

    if uploaded:
        data = uploaded.read()
        h = hashlib.md5(data).hexdigest()

        if h not in knowledge_base:
            knowledge_base[h] = {
                "filename": uploaded.name,
                "text": data.decode("utf-8", errors="ignore")
            }
            save(KB_FILE, knowledge_base)
            st.success("Document stored")

    st.divider()

    q = st.text_input("Ask a question")
    if q:
        st.markdown("<div class='chat-user'>You: " + q + "</div>", unsafe_allow_html=True)

        answers = []
        for doc in knowledge_base.values():
            for line in doc["text"].splitlines():
                if q.lower() in line.lower():
                    answers.append(line.strip())
                    if len(answers) >= 4:
                        break

        if answers:
            for a in answers:
                st.markdown("<div class='chat-ai'>" + a + "</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='chat-ai'>No matching info found.</div>", unsafe_allow_html=True)

# =====================================================
# 📩 RECOMMENDATIONS
# =====================================================
elif section == "📩 Recommendations":
    st.markdown("### 📩 Recommendations")

    if user == "proto":
        pwd = st.text_input("Password", type="password")
        if pwd == "1357924680proto":
            for r in recs.get("proto", []):
                st.info(f"From {r['from']}:\n\n{r['msg']}")
    else:
        msg = st.text_area("Send feedback")
        if st.button("Send"):
            recs.setdefault("proto", []).append({
                "from": user,
                "msg": msg,
                "time": datetime.now().isoformat()
            })
            save(REC_FILE, recs)
            st.success("Sent")


