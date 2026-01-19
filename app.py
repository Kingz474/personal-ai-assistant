import streamlit as st
import json, os, hashlib
from datetime import datetime, time, timedelta

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Personal AI Study Assistant",
    page_icon="📚"
)

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

# ================= TITLE =================
st.title("📚 Personal AI Study Assistant")
st.caption("Plan smarter • Study better • Stay consistent")

# ===== VERSION =====
st.markdown(
    """
    <div style="position:fixed;top:15px;right:25px;
    font-size:13px;color:gray;opacity:0.75;z-index:9999;">
        v1.3 <b>beta</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ================= USER =================
user = st.text_input("👤 Enter your User ID")
if not user:
    st.stop()

tasks.setdefault(user, [])
save(TASK_FILE, tasks)

# ================= MENU =================
section = st.sidebar.radio(
    "📌 Sections",
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
    st.header("➕ Add Task")

    with st.form("add_task", clear_on_submit=True):
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
        st.success("✅ Task added")

# =====================================================
# ⏳ PENDING TASKS
# =====================================================
elif section == "⏳ Pending Tasks":
    st.header("⏳ Pending Tasks")
    now = datetime.now()

    if not tasks[user]:
        st.info("No tasks added yet")
    else:
        for i, t in enumerate(tasks[user]):
            deadline = datetime.fromisoformat(t["deadline"]).date()
            expired = now.date() > deadline

            col1, col2 = st.columns([6,1])
            with col1:
                if t["done"]:
                    st.markdown(
                        f"<div style='opacity:0.4'>✔ {t['title']}</div>",
                        unsafe_allow_html=True
                    )
                elif expired:
                    st.error(f"❌ {t['title']} — Deadline missed")
                else:
                    st.info(f"{t['title']} ({t['subject']})")

            with col2:
                if st.checkbox("✔", key=f"pend{i}", value=t["done"]):
                    t["done"] = True
                    t["done_time"] = datetime.now().isoformat()

    save(TASK_FILE, tasks)

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
                st.markdown(
                    f"<div style='opacity:0.4'>✔ {t['title']}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.info(f"{t['title']} | Priority: {score}")

        with col2:
            if st.checkbox("✔", key=f"prio{i}", value=t["done"]):
                t["done"] = True
                t["done_time"] = datetime.now().isoformat()

    save(TASK_FILE, tasks)

# =====================================================
# 🧠 DAILY STUDY PLAN
# =====================================================
elif section == "🧠 Daily Study Plan":
    st.header("🧠 Weekly Obstacle Timetable")

    DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    TIME_SLOTS = [f"{h:02d}:00-{h+1:02d}:00" for h in range(24)]

    if "table" not in st.session_state:
        st.session_state.table = {
            slot: {day: "" for day in DAYS} for slot in TIME_SLOTS
        }

    with st.expander("➕ Add Obstacle"):
        obs = st.text_input("Obstacle Name")
        day = st.selectbox("Day", DAYS)
        c1, c2 = st.columns(2)
        start = c1.time_input("Start", time(9,0))
        end = c2.time_input("End", time(10,0))

        if st.button("Add Obstacle"):
            for slot in TIME_SLOTS:
                s, e = slot.split("-")
                if time.fromisoformat(s) >= start and time.fromisoformat(e) <= end:
                    st.session_state.table[slot][day] = obs
            st.success("Obstacle added")

    for slot in TIME_SLOTS:
        cols = st.columns(len(DAYS)+1)
        cols[0].markdown(f"**{slot}**")
        for i, d in enumerate(DAYS):
            val = st.session_state.table[slot][d]
            cols[i+1].success("FREE" if not val else val)

# =====================================================
# 📚 STUDY HELP (NEW)
# =====================================================
elif section == "📚 Study Help":
    st.header("📚 Study Help (Shared Knowledge)")
    st.caption("Upload once — everyone benefits")

    uploaded = st.file_uploader(
        "Upload study material",
        type=["txt","pdf","docx","pptx"]
    )

    if uploaded:
        data = uploaded.read()
        file_hash = hashlib.md5(data).hexdigest()

        if file_hash in knowledge_base:
            st.info("📄 File already exists. Using stored copy.")
        else:
            text = data.decode("utf-8", errors="ignore")
            knowledge_base[file_hash] = {
                "filename": uploaded.name,
                "text": text,
                "uploaded_by": user,
                "time": datetime.now().isoformat()
            }
            save(KB_FILE, knowledge_base)
            st.success("✅ File stored globally")

    st.divider()

    question = st.text_input("💬 Ask a question from study material")

    if question:
        found = []
        q = question.lower()

        for doc in knowledge_base.values():
            for line in doc["text"].splitlines():
                if q in line.lower():
                    found.append(line.strip())
                    if len(found) >= 5:
                        break

        if found:
            st.success("📖 Answer from knowledge base:")
            for f in found:
                st.markdown(f"- {f}")
        else:
            st.warning("No matching information found")

# =====================================================
# 📩 RECOMMENDATIONS
# =====================================================
elif section == "📩 Recommendations":
    st.header("📩 Recommendations")

    if user == "proto":
        pwd = st.text_input("Owner Password", type="password")
        if pwd == "1357924680proto":
            for r in recs.get("proto", []):
                st.info(f"From: {r['from']}\n\n{r['msg']}")
        else:
            st.error("Wrong password")
    else:
        msg = st.text_area("Send recommendation to owner (proto)")
        if st.button("Send"):
            recs.setdefault("proto", []).append({
                "from": user,
                "msg": msg,
                "time": datetime.now().isoformat()
            })
            save(REC_FILE, recs)
            st.success("Sent")


