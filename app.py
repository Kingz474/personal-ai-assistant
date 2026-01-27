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

elif section == "📚 QB":
    import streamlit as st

    st.title("📚 Question Bank (QB)")
    st.subheader("📘 Engineering Mechanics (EGM)")
    st.markdown("Easy explanations + memory tricks for fast exam revision")

    st.markdown("""
## 🟢 1️⃣ Mechanical Advantage & Velocity Ratio

### 🔹 Mechanical Advantage (MA)
**Simple meaning:**  
Mechanical Advantage tells us how much a machine helps us.  
If a small effort lifts a heavy load, the machine is good.

**Formula:**  
MA = Load / Effort  

🧠 **Memory Trick:**  
👉 *Machine Advantage = Load ÷ Effort*

---

### 🔹 Velocity Ratio (VR)
**Simple meaning:**  
It compares the distance moved by effort to the distance moved by load.

**Formula:**  
VR = Distance moved by effort / Distance moved by load  

🧠 **Memory Trick:**  
👉 *VR = Distance ratio*

---

## 🟢 2️⃣ Moment of Force

**Meaning:**  
Moment is the turning effect of a force.

**Example:**  
Opening a door is easier when pushing far from the hinge.

**Formula:**  
Moment = Force × Distance  

**SI Unit:**  
Newton-meter (Nm)

🧠 **Memory Trick:**  
👉 *Force × Distance = Moment*

---

## 🟢 3️⃣ Varignon’s Theorem

**Easy meaning:**  
When many forces act on a body, the total turning effect equals the sum of the turning effects of each force.

🧠 **Memory Trick:**  
👉 *Total moment = sum of all moments*

---

## 🟢 4️⃣ Equilibrium of Forces

**Simple meaning:**  
When forces balance each other, the object does not move.

**Example:**  
A book lying on a table.

**Condition:**  
Resultant force = 0

🧠 **Memory Trick:**  
👉 *Balanced forces = no motion*

---

## 🟢 5️⃣ Resultant Force vs Equilibrant Force

### 🔹 Resultant Force
A single force that replaces all forces acting on a body.

### 🔹 Equilibrant Force
A force that balances the resultant.  
Same magnitude, opposite direction.

🧠 **Memory Trick:**  
👉 *Equilibrant = Resultant but opposite*

---

## 🟢 6️⃣ Lami’s Theorem

### 🔹 Used when:
• Exactly three forces  
• Forces meet at one point  
• Body is at rest  

### 🔹 Statement (easy)
Each force is proportional to the sine of the angle between the other two forces.

🧠 **Memory Trick:**  
👉 *3 forces + rest = Lami*

---

## 🟡 7️⃣ Differential Axle & Wheel (Efficiency)

### 🔹 Steps:
1. Find Velocity Ratio (VR)  
2. Find Mechanical Advantage (MA)  
3. Efficiency = (MA / VR) × 100  

🧠 **Memory Trick:**  
👉 *Efficiency = MA ÷ VR × 100*

---

## 🟡 8️⃣ Differential Pulley Block (Effort)

### 🔹 Steps:
1. Find VR using number of teeth  
2. Use efficiency formula  
3. Calculate effort  

🧠 **Memory Trick:**  
👉 *VR first → MA → Effort*

---

## 🟡 9️⃣ Force System & Classification

### 🔹 Force System:
Two or more forces acting on a body.

### 🔹 Types:
• Coplanar → Forces in one plane  
• Non-coplanar → Forces in different planes  

🧠 **Memory Trick:**  
👉 *Plane = Coplanar*

---

## 🟠 🔟 Resultant by Analytical Method

### 🔹 Steps:
1. Resolve forces into horizontal & vertical components  
2. Add components  
3. Find magnitude and direction  

🧠 **Memory Trick:**  
👉 *Resolve → Add → Resultant*

---

## 🟠 1️⃣1️⃣ Two Forces Acting at an Angle

### 🔹 Method Used:
Cosine rule is applied to find the resultant force.

🧠 **Memory Trick:**  
👉 *Angle given → Cosine rule*

---

## 🔴 1️⃣2️⃣ Hanging Body Using Lami’s Theorem

### 🔹 Situation:
A body hangs in equilibrium using strings at angles.

### 🔹 Steps:
1. Draw clear force diagram  
2. Find all angles  
3. Apply Lami’s theorem  

🧠 **Memory Trick:**  
👉 *Draw triangle → Apply Lami*

---

## 🔴 1️⃣3️⃣ Reaction by Planes

### 🔹 What happens?
When a body touches two surfaces, both surfaces apply reaction forces.

### 🔹 Steps:
1. Draw diagram  
2. Resolve forces  
3. Apply equilibrium conditions  

🧠 **Memory Trick:**  
👉 *Contact surface = reaction force*

---

## 🎯 SUPER FAST REVISION

Before exam, remember just this 👇  
**Definitions → Machines → Resultant → Lami → Planes**
""")

st.subheader("📘 Manufacturing Processes (MPR) – Question Bank")
st.markdown("Easy explanations + memory tricks for fast exam revision")

st.markdown("""
## 🔹 Q2 (a) Thread Cutting Operation on Lathe Machine

### 🔧 What is Thread Cutting?
Thread cutting is the process of producing threads (screw shape) on a rotating workpiece using a **single-point cutting tool** on a lathe machine.

### 🧠 Working (Easy Steps)
1. Workpiece is fixed in the chuck and rotates  
2. Thread cutting tool is fixed on tool post  
3. Tool moves slowly parallel to the axis  
4. Threads are formed on the workpiece  
5. Tailstock supports long workpieces  

🧠 **Memory Trick:**  
👉 *Rotate → Tool cuts → Threads form*

✍️ **Exam Writing Tip (4–6 Marks):**
- Draw neat labelled sketch  
- Write points:
  - Chuck holds workpiece  
  - Tool fixed in tool post  
  - Tool cuts during rotation  
  - Tailstock supports job  

---

## 🔹 Q2 (b) Gang Milling

### 🔧 What is Gang Milling?
Gang milling is a milling operation in which **two or more cutters** are mounted on the **same arbor** to machine many surfaces at the same time.

### 🧠 Easy Explanation
- Multiple cutters rotate together  
- All cutters cut simultaneously  
- Used for **high production**  
- Cutters may be same or different sizes  

🧠 **Memory Trick:**  
👉 *Many cutters → One job → Fast work*

✍️ **Exam Tip:**
- Multiple cutters mounted  
- Cut simultaneously  
- High production rate  
- Used in mass production  

---

## 🔹 Q2 (c) Column and Knee Type Milling Machine

### 🔧 What is it?
A milling machine where:
- Column supports spindle  
- Knee moves up and down to adjust height  

### 🔹 Functions of Main Parts (VERY EASY)

**1️⃣ Base**  
- Supports whole machine  
- Collects coolant  
🧠 *Base = Support*

**2️⃣ Column**  
- Vertical structure  
- Supports spindle & drive  
🧠 *Column = Backbone*

**3️⃣ Knee**  
- Moves up and down  
- Provides vertical movement  
🧠 *Knee = Up & Down*

**4️⃣ Table**  
- Holds workpiece  
- Moves job during machining  
🧠 *Table = Holds job*

✍️ **Exam Tip:**
- Draw big neat sketch  
- Label at least 6 parts  
- Write one function each  

---

## 🔹 Q2 (d) Types of Chip Formation

### 🔧 Chip Formation
Chip formation is the way material is removed during machining.

### 🔹 Types of Chips

**1️⃣ Continuous Chip**
- Long continuous chip  
- Formed in soft materials (mild steel)  
🧠 *Soft metal → Continuous chip*

**2️⃣ Discontinuous Chip**
- Chip breaks into small pieces  
- Formed in cast iron, bronze  
🧠 *Hard & brittle → Broken chip*

**3️⃣ Continuous Chip with Built-Up Edge (BUE)**
- Material sticks to tool edge  
🧠 *Sticky metal → BUE*

✍️ **Exam Tip:**
- Name all 3 types  
- Explain any one with sketch  

---

## 🔹 Q2 (e) Pattern Colour Coding

### 🔧 Why Colour Coding?
To identify machined and unmachined surfaces in patterns.

### 🎨 Colour Meanings

- **Black** → Not machined  
- **Red** → To be machined  
- **Yellow** → Core print  
- **No colour** → Parting surface  
- **Red strips on yellow** → Base plate  
- **Black strips on yellow** → Support  

🧠 **Memory Trick:**  
👉 *Red = Cut, Black = No cut*

---

## 🔹 Q2 (f) Machining Time (Drilling)

### 🔧 What is Machining Time?
Time required to complete drilling operation.

### 🧮 Formula (IMPORTANT)
T = L ÷ (N × f)

Where:  
- L = Length of hole (mm)  
- N = Speed (rpm)  
- f = Feed (mm/rev)  

### 🧠 Steps
1. Find spindle speed (N)  
2. Substitute values  
3. Answer in minutes  

🧠 **Memory Trick:**  
👉 *Speed → Feed → Time*

---

## 🔹 Q2 (g) Radial Drilling Machine

### 🔧 What is Radial Drilling Machine?
A drilling machine where the drill head moves radially, suitable for **large and heavy workpieces**.

### 🔹 Main Parts & Functions

**1️⃣ Base** – Supports machine and job  
**2️⃣ Column** – Supports radial arm  
**3️⃣ Radial Arm** – Moves drill head left/right  
**4️⃣ Drill Head** – Holds motor & spindle  
**5️⃣ Spindle** – Rotates drill  

🧠 **Memory Trick:**  
👉 *Big job → Radial drill*

---

## 🎯 FINAL SUPER-FAST REVISION (1 Minute)

Lathe → Thread cutting  
Many cutters → Gang milling  
Knee → Vertical movement  
Broken chip → Cast iron  
Red → Machining  
Time = L ÷ (N × f)  
Big job → Radial drilling
""")



