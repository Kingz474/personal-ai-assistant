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
elif section == "📘 Study Help":
    st.header("📘 Study Help (PDF/Image/Text)")

    topic = st.text_input("Topic / Chapter Name")
    tabs = st.tabs(["📄 PDF","🖼 Image","✍ Text"])
    extracted_text = ""

    with tabs[0]:
        pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if pdf:
            if PDF_AVAILABLE:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
            else:
                st.warning("PDF support not available. Please install PyPDF2.")

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
        st.write("• Read carefully\n• Understand concepts\n• Apply formulas\n• Practice examples")

# =========================
# Recommendations
# =========================
elif section == "📩 Recommendations":
    st.header("📩 Recommendations")
    msg = st.text_area("Send recommendation to owner")
    if st.button("Send") and msg.strip():
        recs_db.append({"from": user_id,"msg": msg,"time": datetime.now().isoformat()})
        save_json(REC_FILE, recs_db)
        st.success("Sent")

    if user_id == "proto":
        pwd = st.text_input("Owner Password", type="password")
        if pwd == "1357924680proto":
            for r in recs_db[::-1]:
                st.info(f"{r['from']} → {r['msg']}")

# =====================================================
# 📚 QB – QUESTION BANK (FULL NOTES)
# =====================================================
elif section == "📚 QB":
    st.header("📚 Question Bank – Explained for Learning")
    st.caption("Use sliders to revise topics quickly with full explanations")

    # =================================================
    # EGM SECTION
    # =================================================
    st.subheader("⚙️ EGM – Engineering Mechanics")

    egm = st.slider("EGM Topics", 1, 13, 1)

    if egm >= 1:
        st.markdown("""
### 🟢 1️⃣ Mechanical Advantage & Velocity Ratio

🔹 **Mechanical Advantage (MA)**  
Mechanical Advantage tells us how much a machine helps us.  
If a small effort is used to lift a heavy load, then the machine has a good mechanical advantage.

**Formula:**  
MA = Load ÷ Effort  

🧠 **Memory Trick:**  
👉 *Machine Advantage = Load ÷ Effort*

🔹 **Velocity Ratio (VR)**  
Velocity Ratio compares the distance moved by the effort to the distance moved by the load.

**Formula:**  
VR = Distance moved by effort ÷ Distance moved by load  

🧠 **Memory Trick:**  
👉 *VR = Distance ratio*
""")

    if egm >= 2:
        st.markdown("""
### 🟢 2️⃣ Moment of Force

Moment of force is the turning effect of a force about a point or axis.

**Example:**  
When you open a door, you apply force away from the hinge, so the door opens easily.

**Formula:**  
Moment = Force × Distance  

**SI Unit:** Newton-meter (Nm)

🧠 **Memory Trick:**  
👉 *Force × Distance = Moment*
""")

    if egm >= 3:
        st.markdown("""
### 🟢 3️⃣ Varignon’s Theorem

Varignon’s theorem states that if multiple forces act on a body, then the total turning effect is equal to the sum of turning effects of individual forces.

🧠 **Memory Trick:**  
👉 *Total moment = Sum of all moments*
""")

    if egm >= 4:
        st.markdown("""
### 🟢 4️⃣ Equilibrium of Forces

A body is said to be in equilibrium when all the forces acting on it balance each other.

**Condition:**  
Resultant force = 0  

**Example:**  
A book resting on a table.

🧠 **Memory Trick:**  
👉 *Balanced forces = No motion*
""")

    if egm >= 5:
        st.markdown("""
### 🟢 5️⃣ Resultant Force and Equilibrant Force

🔹 **Resultant Force:**  
A single force that has the same effect as all forces acting together.

🔹 **Equilibrant Force:**  
A force that balances the resultant force.  
It is equal in magnitude but opposite in direction.

🧠 **Memory Trick:**  
👉 *Equilibrant = Resultant but opposite*
""")

    if egm >= 6:
        st.markdown("""
### 🟢 6️⃣ Lami’s Theorem

Lami’s theorem is used when:
- Exactly three forces act on a body
- Forces meet at one point
- Body is in equilibrium

🧠 **Memory Trick:**  
👉 *3 forces + rest = Lami*
""")

    if egm >= 7:
        st.markdown("""
### 🟡 7️⃣ Differential Axle & Wheel (Efficiency)

Steps to find efficiency:
1. Calculate Velocity Ratio (VR)
2. Calculate Mechanical Advantage (MA)
3. Apply efficiency formula

**Formula:**  
Efficiency = (MA ÷ VR) × 100  

🧠 **Memory Trick:**  
👉 *Efficiency = MA ÷ VR*
""")

    if egm >= 8:
        st.markdown("""
### 🟡 8️⃣ Differential Pulley Block (Effort)

Steps:
1. Find VR using number of teeth
2. Find MA using efficiency
3. Calculate effort required

🧠 **Memory Trick:**  
👉 *VR first → MA → Effort*
""")

    if egm >= 9:
        st.markdown("""
### 🟡 9️⃣ Force System & Classification

A force system exists when two or more forces act on a body.

Types:
- Coplanar forces → Forces in same plane
- Non-coplanar forces → Forces in different planes

🧠 **Memory Trick:**  
👉 *Plane = Coplanar*
""")

    if egm >= 10:
        st.markdown("""
### 🟠 🔟 Resultant by Analytical Method

Steps:
1. Resolve forces into horizontal and vertical components
2. Add components
3. Find resultant magnitude and direction

🧠 **Memory Trick:**  
👉 *Resolve → Add → Resultant*
""")

    if egm >= 11:
        st.markdown("""
### 🟠 1️⃣1️⃣ Two Forces at an Angle

When two forces act at an angle, the resultant is found using the cosine rule.

🧠 **Memory Trick:**  
👉 *Angle given → Cosine rule*
""")

    if egm >= 12:
        st.markdown("""
### 🔴 1️⃣2️⃣ Hanging Body using Lami’s Theorem

Steps:
1. Draw clear force diagram
2. Find all angles
3. Apply Lami’s theorem

🧠 **Memory Trick:**  
👉 *Draw triangle → Apply Lami*
""")

    if egm >= 13:
        st.markdown("""
### 🔴 1️⃣3️⃣ Reaction by Planes

When a body touches a surface, the surface applies a reaction force on the body.

🧠 **Memory Trick:**  
👉 *Contact surface = Reaction force*
""")

    # =================================================
    # MPR SECTION
    # =================================================
    st.divider()
    st.subheader("🛠️ MPR – Manufacturing Processes")

    mpr = st.slider("MPR Topics", 1, 7, 1)

    if mpr >= 1:
        st.markdown("""
### 🔹 Thread Cutting Operation on Lathe Machine

Thread cutting is the process of producing screw threads on a rotating workpiece using a single-point cutting tool.

**Working:**
- Workpiece rotates in chuck
- Tool moves parallel to axis
- Threads are formed
- Tailstock supports long workpiece

🧠 **Memory Trick:**  
👉 *Rotate → Tool cuts → Threads form*
""")

    if mpr >= 2:
        st.markdown("""
### 🔹 Gang Milling

Gang milling is a milling operation in which more than one cutter is mounted on the same arbor to machine several surfaces at a time.

Used for mass production.

🧠 **Memory Trick:**  
👉 *Many cutters → One job → Fast*
""")

    if mpr >= 3:
        st.markdown("""
### 🔹 Column and Knee Type Milling Machine

Parts and functions:
- Base → Supports whole machine
- Column → Backbone, supports spindle
- Knee → Moves up and down
- Table → Holds workpiece

🧠 **Memory Trick:**  
👉 *Base – Column – Knee*
""")

    if mpr >= 4:
        st.markdown("""
### 🔹 Types of Chip Formation

1. Continuous chip – soft metals
2. Discontinuous chip – cast iron
3. Built-up edge – sticky materials

🧠 **Memory Trick:**  
👉 *Soft metal → Continuous chip*
""")

    if mpr >= 5:
        st.markdown("""
### 🔹 Pattern Colour Coding

Purpose: To indicate machined and unmachined surfaces.

- Red → To be machined
- Black → Not machined

🧠 **Memory Trick:**  
👉 *Red = Cut*
""")

    if mpr >= 6:
        st.markdown("""
### 🔹 Machining Time (Drilling)

Machining time is the time required to complete drilling operation.

**Formula:**  
T = L ÷ (N × f)

🧠 **Memory Trick:**  
👉 *Speed → Feed → Time*
""")

    if mpr >= 7:
        st.markdown("""
### 🔹 Radial Drilling Machine

Radial drilling machine is used for large and heavy workpieces where the drill head moves radially.

🧠 **Memory Trick:**  
👉 *Big job → Radial drill*
""")

    st.success("🎯 Use QB for fast revision before exams")

