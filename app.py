import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config("Personal Study Assistant", layout="wide")

# =====================================================
# USER LOGIN
# =====================================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None

st.sidebar.title("👤 Login")

if st.session_state.user_id is None:
    uid = st.sidebar.text_input("Enter User ID")
    if st.sidebar.button("Login"):
        if uid.strip():
            st.session_state.user_id = uid.strip()
            st.rerun()
else:
    st.sidebar.success(f"Logged in as {st.session_state.user_id}")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

if st.session_state.user_id is None:
    st.stop()

user_id = st.session_state.user_id

# =====================================================
# FILE HELPERS
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

TASK_FILE = "tasks_data.json"
tasks_db = load_json(TASK_FILE, {})

def get_tasks(uid):
    return tasks_db.get(uid, [])

def save_tasks(uid, tasks):
    tasks_db[uid] = tasks
    save_json(TASK_FILE, tasks_db)

# =====================================================
# MENU
# =====================================================
section = st.sidebar.radio(
    "Sections",
    [
        "➕ Add Task",
        "⏳ Pending Tasks",
        "⭐ Priority Tasks",
        "📚 QB"
    ]
)

# =====================================================
# ADD TASK
# =====================================================
if section == "➕ Add Task":
    st.header("➕ Add Task")
    title = st.text_input("Task Name")
    subject = st.text_input("Subject")
    deadline = st.date_input("Deadline")
    difficulty = st.slider("Difficulty", 1, 5, 3)
    importance = st.slider("Importance", 1, 5, 3)

    if st.button("Add Task") and title.strip():
        tasks = get_tasks(user_id)
        tasks.append({
            "title": title,
            "subject": subject,
            "deadline": str(deadline),
            "difficulty": difficulty,
            "importance": importance,
            "done": False
        })
        save_tasks(user_id, tasks)
        st.success("Task added")
        st.rerun()

# =====================================================
# PENDING TASKS
# =====================================================
elif section == "⏳ Pending Tasks":
    st.header("⏳ Pending Tasks")
    for i, t in enumerate(get_tasks(user_id)):
        if not t["done"]:
            c1, c2 = st.columns([4,1])
            c1.write(f"**{t['title']}** ({t['subject']})")
            if c2.checkbox("Done", key=i):
                t["done"] = True
                save_tasks(user_id, get_tasks(user_id))
                st.rerun()

# =====================================================
# PRIORITY TASKS
# =====================================================
elif section == "⭐ Priority Tasks":
    st.header("⭐ Priority Tasks")
    tasks = sorted(
        get_tasks(user_id),
        key=lambda x: x["importance"] + x["difficulty"],
        reverse=True
    )
    for t in tasks:
        if not t["done"]:
            st.info(f"{t['title']} → {t['subject']}")

# =====================================================
# 📚 QB – FULL EXPLAINED QUESTION BANK
# =====================================================
elif section == "📚 QB":
    st.header("📚 Question Bank – Explained Learning")

    # =======================
    # EGM SECTION
    # =======================
    st.subheader("⚙️ EGM – Engineering Mechanics")

    egm = st.slider("EGM Topics", 1, 13, 1)

    if egm >= 1:
        st.markdown("""
### 🟢 1️⃣ Mechanical Advantage & Velocity Ratio

**Mechanical Advantage (MA):**  
It tells us how much a machine helps us.  
If a small effort lifts a heavy load, the machine is good.

**Formula:**  
MA = Load ÷ Effort  

🧠 **Memory Trick:**  
👉 *Machine Advantage = Load ÷ Effort*

**Velocity Ratio (VR):**  
It compares how much distance the effort moves to how much the load moves.

**Formula:**  
VR = Distance moved by effort ÷ Distance moved by load  

🧠 **Memory Trick:**  
👉 *VR = Distance ratio*
""")

    if egm >= 2:
        st.markdown("""
### 🟢 2️⃣ Moment of Force

Moment is the turning effect of a force.

**Example:**  
Opening a door is easier when you push away from the hinge.

**Formula:**  
Moment = Force × Distance  

**SI Unit:** Newton-meter (Nm)

🧠 **Memory Trick:**  
👉 *Force × Distance = Moment*
""")

    if egm >= 3:
        st.markdown("""
### 🟢 3️⃣ Varignon’s Theorem

If many forces act on a body, the total turning effect is equal to the sum of turning effects of each force.

🧠 **Memory Trick:**  
👉 *Total moment = Sum of all moments*
""")

    if egm >= 4:
        st.markdown("""
### 🟢 4️⃣ Equilibrium of Forces

When forces balance each other, the body does not move.

**Condition:**  
Resultant force = 0  

🧠 **Memory Trick:**  
👉 *Balanced forces = No motion*
""")

    if egm >= 5:
        st.markdown("""
### 🟢 5️⃣ Resultant and Equilibrant

**Resultant Force:**  
Single force that replaces all forces.

**Equilibrant Force:**  
Force that balances the resultant.

👉 Same magnitude, opposite direction

🧠 **Memory Trick:**  
👉 *Equilibrant = Resultant but opposite*
""")

    if egm >= 6:
        st.markdown("""
### 🟢 6️⃣ Lami’s Theorem

Used when:
- Exactly 3 forces
- Forces meet at one point
- Body is at rest

🧠 **Memory Trick:**  
👉 *3 forces + rest = Lami*
""")

    if egm >= 7:
        st.markdown("""
### 🟡 7️⃣ Differential Axle & Wheel (Efficiency)

Steps:
1. Find Velocity Ratio
2. Find Mechanical Advantage
3. Calculate efficiency

**Formula:**  
Efficiency = (MA ÷ VR) × 100  

🧠 **Memory Trick:**  
👉 *Efficiency = MA ÷ VR*
""")

    if egm >= 8:
        st.markdown("""
### 🟡 8️⃣ Differential Pulley Block

Steps:
1. Find VR using teeth numbers
2. Use efficiency formula
3. Calculate effort

🧠 **Memory Trick:**  
👉 *VR first → MA → Effort*
""")

    if egm >= 9:
        st.markdown("""
### 🟡 9️⃣ Force System & Classification

When two or more forces act on a body.

Types:
- Coplanar → same plane
- Non-coplanar → different planes

🧠 **Memory Trick:**  
👉 *Plane = Coplanar*
""")

    if egm >= 10:
        st.markdown("""
### 🟠 🔟 Resultant by Analytical Method

Steps:
1. Resolve forces
2. Add components
3. Find magnitude & direction

🧠 **Memory Trick:**  
👉 *Resolve → Add → Resultant*
""")

    if egm >= 11:
        st.markdown("""
### 🟠 1️⃣1️⃣ Two Forces at Angle

Used when two forces act at an angle.

**Method:** Cosine Rule

🧠 **Memory Trick:**  
👉 *Angle given = Cosine rule*
""")

    if egm >= 12:
        st.markdown("""
### 🔴 1️⃣2️⃣ Hanging Body using Lami’s Theorem

Steps:
1. Draw force triangle
2. Find angles
3. Apply Lami’s theorem

🧠 **Memory Trick:**  
👉 *Draw triangle → Apply Lami*
""")

    if egm >= 13:
        st.markdown("""
### 🔴 1️⃣3️⃣ Reaction by Planes

When a body touches a surface, the surface applies a reaction force.

🧠 **Memory Trick:**  
👉 *Contact surface = Reaction*
""")

    # =======================
    # MPR SECTION
    # =======================
    st.divider()
    st.subheader("🛠️ MPR – Manufacturing Process")

    mpr = st.slider("MPR Topics", 1, 7, 1)

    if mpr >= 1:
        st.markdown("""
### 🔹 Thread Cutting on Lathe Machine

Thread cutting is the process of making threads on a rotating workpiece using a single-point cutting tool.

🧠 **Steps:**
- Workpiece rotates
- Tool cuts
- Threads form

🧠 **Memory Trick:**  
👉 *Rotate → Cut → Thread*
""")

    if mpr >= 2:
        st.markdown("""
### 🔹 Gang Milling

More than one cutter mounted on same arbor.

Used for high production.

🧠 **Memory Trick:**  
👉 *Many cutters → One job*
""")

    if mpr >= 3:
        st.markdown("""
### 🔹 Column and Knee Type Milling Machine

- Base → Supports machine
- Column → Backbone
- Knee → Moves up & down

🧠 **Memory Trick:**  
👉 *Base – Column – Knee*
""")

    if mpr >= 4:
        st.markdown("""
### 🔹 Types of Chip Formation

1. Continuous → Soft metals  
2. Discontinuous → Cast iron  
3. Built-up edge → Sticky metals

🧠 **Memory Trick:**  
👉 *Soft = Continuous*
""")

    if mpr >= 5:
        st.markdown("""
### 🔹 Pattern Colour Coding

- Red → Machined
- Black → Not machined

🧠 **Memory Trick:**  
👉 *Red = Cut*
""")

    if mpr >= 6:
        st.markdown("""
### 🔹 Machining Time (Drilling)

**Formula:**  
T = L ÷ (N × f)

🧠 **Memory Trick:**  
👉 *Speed → Feed → Time*
""")

    if mpr >= 7:
        st.markdown("""
### 🔹 Radial Drilling Machine

Used for large and heavy jobs.

🧠 **Memory Trick:**  
👉 *Big job = Radial*
""")

    st.success("🎯 Use this section for fast exam revision")
