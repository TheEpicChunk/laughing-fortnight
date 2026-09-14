import streamlit as st
import streamlit.components.v1 as components
import re
import json
import time
from datetime import datetime

st.set_page_config(page_title="Student Toolkit", page_icon="🎓", layout="wide")

# ==========================================
# AUDIO RESOURCES
# ==========================================
SFX_POP = "https://raw.githubusercontent.com/TheEpicChunk/laughing-fortnight/main/sounds/dragon-studio-pop-402322.mp3"
SFX_FANFARE = "https://raw.githubusercontent.com/TheEpicChunk/laughing-fortnight/main/sounds/freesound_community-fanfare-46385.mp3"
SFX_WARNING = "https://raw.githubusercontent.com/TheEpicChunk/laughing-fortnight/main/sounds/freesound_community-warning-sound-6686.mp3"
SFX_CONFIRM = "https://raw.githubusercontent.com/TheEpicChunk/laughing-fortnight/main/sounds/soundshelfstudio-ui-chime-confirm-567486.mp3"
SFX_TRASH = "https://raw.githubusercontent.com/TheEpicChunk/laughing-fortnight/main/sounds/soundshelfstudio-ui-soft-glass-ping-526562.mp3"

# ==========================================
# DEFAULT DATA DEFS
# ==========================================
DEFAULT_GPA_SCALE = [
    {"Grade": "A+", "Standard": 4.5, "Honors": 5.0, "AP/IB/DE": 5.5},
    {"Grade": "A",  "Standard": 4.0, "Honors": 4.5, "AP/IB/DE": 5.0},
    {"Grade": "B+", "Standard": 3.5, "Honors": 4.0, "AP/IB/DE": 4.5},
    {"Grade": "B",  "Standard": 3.0, "Honors": 3.5, "AP/IB/DE": 4.0},
    {"Grade": "C+", "Standard": 2.5, "Honors": 3.0, "AP/IB/DE": 3.5},
    {"Grade": "C",  "Standard": 2.0, "Honors": 2.5, "AP/IB/DE": 3.0},
    {"Grade": "D+", "Standard": 1.5, "Honors": 2.0, "AP/IB/DE": 2.5},
    {"Grade": "D",  "Standard": 1.0, "Honors": 1.5, "AP/IB/DE": 2.0},
    {"Grade": "F",  "Standard": 0.0, "Honors": 0.0, "AP/IB/DE": 0.0}
]

def get_default_classes():
    return {"Select 'Manage Active Class' to rename me!": {"paste": "", "s_weight": 70, "f_weight": 30, "upcoming": []}}

def get_default_settings():
    return {
        "animations": True,
        "celebrations": True,
        "sfx_enabled": True,
        "text_outline": True,
        "accent_color": "#FF4B4B",
        "bg_color": "#0E1117", 
        "default_target": 90.0
    }

# --- PER-USER SESSION ISOLATION ---
if 'classes' not in st.session_state:
    st.session_state.classes = get_default_classes()
if 'gpa_scale' not in st.session_state:
    st.session_state.gpa_scale = [dict(row) for row in DEFAULT_GPA_SCALE]
if 'settings' not in st.session_state:
    st.session_state.settings = get_default_settings()
if 'pending_audio' not in st.session_state:
    st.session_state.pending_audio = None

# ==========================================
# ROBUST JAVASCRIPT AUDIO ENGINE
# ==========================================
def trigger_sound(url):
    if st.session_state.settings.get("sfx_enabled", True):
        # Append timestamp to force Streamlit to re-render the HTML component 
        # so overlapping sounds play reliably without getting cached out.
        st.session_state.pending_audio = f"{url}?t={time.time()}"

if st.session_state.settings.get("sfx_enabled", True):
    # 1. Frontend Listener: Attach POP sound to Tab switches instantly via JS
    components.html(
        f"""
        <script>
            const sfxPop = new Audio("{SFX_POP}");
            function attachTabListeners() {{
                const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
                tabs.forEach(tab => {{
                    if (!tab.dataset.hasSoundListener) {{
                        tab.addEventListener('click', () => {{
                            sfxPop.cloneNode().play().catch(e => console.log(e));
                        }});
                        tab.dataset.hasSoundListener = 'true';
                    }}
                }});
            }}
            attachTabListeners();
            setInterval(attachTabListeners, 1000); // Re-attach if Streamlit redraws UI
        </script>
        """,
        height=0
    )

    # 2. Backend Player: Play triggered specific sounds (bypasses HTML audio tag limits)
    if st.session_state.pending_audio:
        base_url = st.session_state.pending_audio.split('?')[0]
        ts = st.session_state.pending_audio.split('?t=')[1]
        components.html(
            f"""
            <script>
                // Execution ID: {ts}
                var audio = new Audio("{base_url}");
                audio.play().catch(e => console.log("Audio play failed:", e));
            </script>
            """,
            height=0
        )
        st.session_state.pending_audio = None

# ==========================================
# DYNAMIC CSS INJECTION
# ==========================================
custom_css = ""
if st.session_state.settings.get("animations", True):
    custom_css += """
    .stButton>button { transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important; border-radius: 8px !important; }
    .stButton>button:hover { transform: scale(1.03) translateY(-2px) !important; box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important; }
    .stButton>button:active { transform: scale(0.95) !important; }
    [data-testid="stMetric"] { transition: transform 0.2s ease, box-shadow 0.2s ease !important; padding: 10px !important; border-radius: 10px !important; }
    [data-testid="stMetric"]:hover { transform: translateY(-3px) !important; background-color: rgba(150, 150, 150, 0.05) !important; }
    """
if st.session_state.settings.get("text_outline", True):
    custom_css += """
    h1, h2, h3, h4, h5, h6, p, span, label, li, .stMarkdown, .stText {
        text-shadow: 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000 !important;
    }
    """
accent = st.session_state.settings.get("accent_color", "#FF4B4B")
bg_color = st.session_state.settings.get("bg_color", "#0E1117")
custom_css += f"""
.stApp {{ background-color: {bg_color} !important; }}
.stButton>button:hover {{ border-color: {accent} !important; color: {accent} !important; }}
[data-testid="stMetricValue"] {{ color: {accent} !important; }}
"""
if custom_css:
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("📚 Class Manager")

with st.sidebar.form("add_class_form", clear_on_submit=True):
    new_class_name = st.text_input("Create New Class")
    if st.form_submit_button("➕ Add Class") and new_class_name:
        if new_class_name not in st.session_state.classes:
            st.session_state.classes[new_class_name] = {"paste": "", "s_weight": 80, "f_weight": 20, "upcoming": []}
            if st.session_state.settings.get("celebrations", True): st.toast(f'Added {new_class_name}!', icon='📚')
            trigger_sound(SFX_CONFIRM)
            st.rerun()
        else:
            trigger_sound(SFX_POP)

class_list = list(st.session_state.classes.keys())
if class_list:
    active_class = st.sidebar.selectbox("Select Active Class:", class_list)
    c_data = st.session_state.classes[active_class]

    with st.sidebar.expander("⚙️ Manage Active Class"):
        rename_val = st.text_input("Rename Class:", value=active_class, key=f"rename_{active_class}")
        if st.button("Save New Name"):
            if rename_val and rename_val != active_class:
                if rename_val not in st.session_state.classes:
                    st.session_state.classes[rename_val] = st.session_state.classes.pop(active_class)
                    trigger_sound(SFX_CONFIRM)
                    st.rerun()
                else:
                    st.sidebar.error("Class name already exists.")
                    trigger_sound(SFX_POP)

        st.write("---")
        if st.button("🗑️ Delete Class", type="secondary"):
            if len(st.session_state.classes) > 1:
                del st.session_state.classes[active_class]
                trigger_sound(SFX_TRASH)
                st.rerun()
            else:
                st.sidebar.error("You must have at least one class.")
                trigger_sound(SFX_POP)
else:
    st.session_state.classes = get_default_classes()
    st.rerun()

st.sidebar.write("---")
st.sidebar.markdown("### 💾 Personal Data Backup")

export_data = json.dumps({"classes": st.session_state.classes, "gpa_scale": st.session_state.gpa_scale, "settings": st.session_state.settings}, indent=2)
st.sidebar.download_button(label="📥 Download Data Backup (.json)", data=export_data, file_name="my_student_toolkit_data.json", mime="application/json", use_container_width=True)

uploaded_backup = st.sidebar.file_uploader("📤 Restore Data Backup", type=["json"])
if uploaded_backup is not None:
    if st.sidebar.button("⚠️ Confirm Restore File"):
        try:
            loaded = json.load(uploaded_backup)
            if "classes" in loaded:
                st.session_state.classes = loaded["classes"]
                st.session_state.gpa_scale = loaded.get("gpa_scale", [dict(row) for row in DEFAULT_GPA_SCALE])
                st.session_state.settings = loaded.get("settings", get_default_settings())
                if st.session_state.settings.get("celebrations", True): st.toast('Data restored successfully!', icon='💾')
                trigger_sound(SFX_CONFIRM)
                st.rerun()
        except Exception:
            st.sidebar.error("Invalid backup file format.")
            trigger_sound(SFX_POP)

if st.sidebar.button("🔄 Reset Entire App to Default"):
    st.session_state.classes = get_default_classes()
    st.session_state.gpa_scale = [dict(row) for row in DEFAULT_GPA_SCALE]
    st.session_state.settings = get_default_settings()
    trigger_sound(SFX_TRASH)
    st.rerun()

# ==========================================
# PARSER HELPER
# ==========================================
def calculate_grade(paste_data, s_w, f_w, drop_lowest=False):
    s_earned, s_pos, f_earned, f_pos = 0.0, 0.0, 0.0, 0.0
    assignments = []

    if paste_data:
        pattern = r'(?:([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})\s*\n\s*)?([^\n]+)\s*\n\s*(Summative|Formative)(?:(?!(?:Summative|Formative)).)*?Raw Score\s*([\d\.]+)\s*/\s*([\d\.]+)'
        matches = re.findall(pattern, paste_data, flags=re.IGNORECASE | re.DOTALL)

        for date_str, name, cat, earned, possible in matches:
            name, cat = name.strip(), cat.lower()
            earned, possible = float(earned), float(possible)
            if possible > 0:
                assignments.append({"date": date_str.strip() if date_str else "N/A", "name": name, "cat": cat, "earned": earned, "possible": possible, "pct": earned / possible})

        if drop_lowest and assignments:
            assignments.sort(key=lambda x: x["pct"])
            assignments.pop(0)

        for ast in assignments:
            if ast["cat"] == 'summative': s_earned += ast["earned"]; s_pos += ast["possible"]
            else: f_earned += ast["earned"]; f_pos += ast["possible"]

    s_pct = (s_earned / s_pos) if s_pos > 0 else 0.0
    f_pct = (f_earned / f_pos) if f_pos > 0 else 0.0

    overall = 0.0
    if s_pos > 0 and f_pos > 0: overall = ((s_pct * (s_w / 100)) + (f_pct * (f_w / 100))) * 100
    elif s_pos > 0: overall = s_pct * 100
    elif f_pos > 0: overall = f_pct * 100

    return overall, s_earned, s_pos, f_earned, f_pos, s_pct, f_pct, assignments

# ==========================================
# MAIN APP HEADER & TABS
# ==========================================
st.title("🎓 Student Toolkit")
tab_dash, tab_grade, tab_panic, tab_cal, tab_gpa, tab_settings = st.tabs([
    "📊 Dashboard", "📝 Class Calculator", "🚨 Exam Panic Calc", "📅 Due Dates", "🎯 GPA Planner", "⚙️ Settings"
])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dash:
    st.markdown("### 📈 Overall Academic Overview")
    cols = st.columns(3)
    class_stats = []

    for idx, (c_name, data) in enumerate(st.session_state.classes.items()):
        overall, s_earned, s_pos, f_earned, f_pos, s_pct, f_pct, _ = calculate_grade(data["paste"], data["s_weight"], data["f_weight"])
        status_color = "🟢" if overall >= 90 else "🟡" if overall >= 80 else "🔴" if overall > 0 else "⚪"
        col = cols[idx % 3]
        col.info(f"### {status_color} {c_name}\n**{round(overall, 2)}%**" if overall > 0 else f"### {status_color} {c_name}\n**No Data**")

        priority_score = 0
        reasons = []
        if overall > 0:
            mod = overall % 10
            if 8.5 <= mod <= 9.9 or 78.5 <= overall <= 79.9:
                priority_score += 40
                reasons.append("🎯 **Grade Edge Alert**: Very close to crossing a letter grade boundary!")
            if overall < 80:
                priority_score += 30
                reasons.append("⚠️ **Grade Below 80%**: Needs attention to raise standing.")
            upcoming_count = len(data.get("upcoming", []))
            if upcoming_count > 0:
                priority_score += upcoming_count * 15
                reasons.append(f"📌 **Upcoming Assignments**: {upcoming_count} pending.")

        class_stats.append({"name": c_name, "overall": overall, "priority": priority_score, "reasons": reasons})

    st.write("---")
    st.markdown("### 🎯 Smart Study Priority Matrix")
    class_stats.sort(key=lambda x: x["priority"], reverse=True)

    for item in class_stats:
        p_score = item["priority"]
        badge = "🔴 HIGH PRIORITY" if p_score >= 40 else "🟡 MEDIUM PRIORITY" if p_score >= 15 else "🟢 LOW PRIORITY"
        with st.expander(f"{badge} — **{item['name']}** ({round(item['overall'], 2)}%)"):
            if item["reasons"]:
                for r in item["reasons"]: st.markdown(f"- {r}")
            else:
                st.write("✨ Class grade is stable with no immediate high-stakes deadlines detected.")

# ==========================================
# TAB 2: CLASS CALCULATOR
# ==========================================
with tab_grade:
    st.header(f"Editing: {active_class}")

    with st.expander("📋 1. Paste StudentVUE Data & Set Weights", expanded=not bool(c_data["paste"])):
        col_s, col_f = st.columns(2)
        with col_s: c_data["s_weight"] = st.number_input("Summative Weight (%)", value=c_data["s_weight"], max_value=100, step=5)
        with col_f: c_data["f_weight"] = st.number_input("Formative Weight (%)", value=c_data["f_weight"], max_value=100, step=5)
        c_data["paste"] = st.text_area("Paste assignments from StudentVUE here:", value=c_data["paste"], height=150)
        
        if st.button("🗑️ Clear Pasted Data for This Class"):
            c_data["paste"] = ""
            trigger_sound(SFX_TRASH)
            st.rerun()

    drop_lowest = st.toggle("Drop Lowest Assignment Score")
    overall, s_earned, s_pos, f_earned, f_pos, s_pct, f_pct, parsed_assignments = calculate_grade(c_data["paste"], c_data["s_weight"], c_data["f_weight"], drop_lowest)

    st.write("---")
    st.markdown("### 📊 2. Current Stats")
    m1, m2, m3 = st.columns(3)
    m1.metric("Summative Total", f"{s_earned}/{s_pos}", f"{round(s_pct*100, 2)}%" if s_pos > 0 else "N/A")
    m2.metric("Formative Total", f"{f_earned}/{f_pos}", f"{round(f_pct*100, 2)}%" if f_pos > 0 else "N/A")
    m3.metric("Overall Grade", f"{round(overall, 2)}%")

    with st.expander("🔍 View Detected Graded Assignments"):
        if parsed_assignments:
            display_list = [{"Date": a["date"], "Name": a["name"], "Category": a["cat"].capitalize(), "Score": f"{a['earned']} / {a['possible']}", "Percent": f"{a['pct']*100:.1f}%"} for a in parsed_assignments]
            st.dataframe(display_list, use_container_width=True)
        else:
            st.info("No graded assignments found in the pasted text yet.")

    st.write("---")
    st.markdown("### 🔮 3. Future Grade Planner & Scenario Sliders")

    col_auto, col_clear = st.columns([2, 1])
    with col_auto:
        if st.button("🔍 Auto-Detect Upcoming Assignments"):
            pattern_upcoming = r'(?:([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})\s*\n\s*)?([^\n]+)\s*\n\s*(Summative|Formative)(?:(?!(?:Summative|Formative)).)*?Not Due(?:(?!(?:Summative|Formative)).)*?([\d\.]+)\s*Points'
            matches = re.findall(pattern_upcoming, c_data["paste"], flags=re.IGNORECASE | re.DOTALL)
            if matches:
                count = 0
                for date_str, name, cat, pts in matches:
                    if not any(a["Name"] == name.strip() for a in c_data["upcoming"]):
                        c_data["upcoming"].append({"Date": date_str.strip() if date_str else "N/A", "Name": name.strip(), "Category": cat.capitalize(), "Points": float(pts)})
                        count += 1
                if count > 0:
                    if st.session_state.settings.get("celebrations", True): st.toast(f'Added {count} upcoming assignments!', icon='📌')
                    trigger_sound(SFX_POP)
                else:
                    st.info("No new upcoming assignments found.")
                    trigger_sound(SFX_POP)
                st.rerun()
            else:
                st.warning("No upcoming assignments found with 'Not Due' and 'Points Possible'.")
                trigger_sound(SFX_POP)

    with col_clear:
        if st.button("🗑️ Clear Upcoming List"):
            c_data["upcoming"] = []
            trigger_sound(SFX_TRASH)
            st.rerun()

    with st.expander("➕ Manually Add an Upcoming Assignment"):
        c_cat, c_name, c_pts, c_btn = st.columns([1.5, 2, 1, 1])
        with c_cat: m_cat = st.selectbox("Category", ["Summative", "Formative"], key=f"m_cat_{active_class}")
        with c_name: m_name = st.text_input("Name", value="New Assignment", key=f"m_name_{active_class}")
        with c_pts: m_pts = st.number_input("Points", min_value=1.0, value=100.0, step=1.0, key=f"m_pts_{active_class}")
        with c_btn:
            st.write("")
            st.write("")
            if st.button("Add", key=f"m_btn_{active_class}", use_container_width=True):
                c_data["upcoming"].append({"Date": "N/A", "Name": m_name, "Category": m_cat, "Points": m_pts})
                trigger_sound(SFX_POP)
                st.rerun()

    edited_upcoming = st.data_editor(
        c_data["upcoming"], num_rows="dynamic",
        column_config={
            "Date": st.column_config.TextColumn("Due Date"),
            "Name": st.column_config.TextColumn("Assignment Name", required=True),
            "Category": st.column_config.SelectboxColumn("Category", options=["Summative", "Formative"], required=True),
            "Points": st.column_config.NumberColumn("Points Possible", min_value=0.1, required=True)
        },
        use_container_width=True, key=f"editor_{active_class}"
    )

    if edited_upcoming != c_data["upcoming"]: c_data["upcoming"] = edited_upcoming

    if len(edited_upcoming) > 0:
        st.write("---")
        st.markdown("#### 🎯 Min-Max Target Calculator")
        target_grade = st.number_input("What is your Target Overall Grade? (%)", min_value=0.0, max_value=150.0, value=st.session_state.settings.get("default_target", 90.0), step=1.0)

        assumed_scores = []
        if len(edited_upcoming) > 1:
            st.info("💡 Adjust the sliders to see how your estimated score on earlier assignments alters what you need on the final assignment.")
            for i in range(len(edited_upcoming) - 1):
                item = edited_upcoming[i]
                cat, pts, name = item.get("Category"), float(item.get("Points", 1.0)), item.get("Name", "Assignment")
                pct = st.slider(f"Expected Score for: {name} ({pts} pts)", 0.0, 100.0, 90.0, step=1.0, key=f"sl_{active_class}_{i}")
                assumed_scores.append(pct / 100.0 * pts)

        last_ast = edited_upcoming[-1]
        last_cat, last_pts, last_name = last_ast.get("Category", "Summative"), float(last_ast.get("Points", 1.0)), last_ast.get("Name", "Final Assignment")

        s_earned_new, s_pos_new, f_earned_new, f_pos_new = s_earned, s_pos, f_earned, f_pos

        for i in range(len(edited_upcoming) - 1):
            cat, pts, e = edited_upcoming[i].get("Category"), float(edited_upcoming[i].get("Points", 1.0)), assumed_scores[i]
            if cat == "Summative": s_earned_new += e; s_pos_new += pts
            else: f_earned_new += e; f_pos_new += pts

        if last_cat == "Summative": s_pos_new += last_pts
        else: f_pos_new += last_pts

        target_dec, w_s, w_f = target_grade / 100.0, c_data["s_weight"] / 100.0, c_data["f_weight"] / 100.0
        active_w_s = w_s if (f_pos_new > 0) else 1.0
        active_w_f = w_f if (s_pos_new > 0) else 1.0

        needed_points = 0.0
        if last_cat == "Summative":
            f_pct_new = (f_earned_new / f_pos_new) if f_pos_new > 0 else 0.0
            f_contribution = f_pct_new * active_w_f if f_pos_new > 0 else 0.0
            if active_w_s > 0: needed_points = ((target_dec - f_contribution) / active_w_s) * s_pos_new - s_earned_new
        else:
            s_pct_new = (s_earned_new / s_pos_new) if s_pos_new > 0 else 0.0
            s_contribution = s_pct_new * active_w_s if s_pos_new > 0 else 0.0
            if active_w_f > 0: needed_points = ((target_dec - s_contribution) / active_w_f) * f_pos_new - f_earned_new

        st.markdown(f"#### Score needed on: **{last_name}** ({last_pts} pts)")
        if needed_points > last_pts: st.error(f"You need **{needed_points:.1f} / {last_pts}** (**{needed_points/last_pts*100:.1f}%**) — Requires Extra Credit!")
        elif needed_points <= 0: st.success(f"You need **{needed_points:.1f} / {last_pts}** — Safe even with a 0!")
        else: st.success(f"You need **{needed_points:.1f} / {last_pts}** (**{needed_points/last_pts*100:.1f}%**)")

# ==========================================
# TAB 3 & 4: PANIC CALC & CALENDAR
# ==========================================
with tab_panic:
    st.markdown("### 🚨 Final Exam Panic Calculator")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        selected_panic_class = st.selectbox("Import grade from class:", ["Manual Entry"] + list(st.session_state.classes.keys()))
        if selected_panic_class != "Manual Entry":
            curr_g, _, _, _, _, _, _, _ = calculate_grade(st.session_state.classes[selected_panic_class]["paste"], st.session_state.classes[selected_panic_class]["s_weight"], st.session_state.classes[selected_panic_class]["f_weight"])
            current_class_grade = st.number_input("Current Grade (%)", min_value=0.0, value=float(round(curr_g, 2)))
        else:
            current_class_grade = st.number_input("Current Grade (%)", min_value=0.0, value=88.0)
        exam_weight = st.number_input("Final Exam Weight (%)", min_value=1.0, value=20.0)
        target_final_grade = st.number_input("Target Course Grade (%)", min_value=0.0, value=st.session_state.settings.get("default_target", 90.0))

    with col_p2:
        if exam_weight > 0:
            w_dec = exam_weight / 100.0
            req_exam_score = (target_final_grade - (current_class_grade * (1.0 - w_dec))) / w_dec
            st.markdown("#### Calculation Result")
            if req_exam_score > 100: st.error(f"You need **{req_exam_score:.1f}%**. (Requires extra credit!)")
            elif req_exam_score <= 0: st.success(f"You need **{req_exam_score:.1f}%** — You've secured your target grade!")
            else: st.info(f"You need **{req_exam_score:.1f}%** to reach a **{target_final_grade:.0f}%**.")

with tab_cal:
    st.markdown("### 📅 Due Date Visualizer")
    all_upcoming = [{"Class": c_name, "Due Date": item.get("Date", "N/A"), "Assignment Name": item.get("Name", "Assignment"), "Category": item.get("Category", "Formative"), "Points": item.get("Points", 0)} for c_name, data in st.session_state.classes.items() for item in data.get("upcoming", [])]
    if all_upcoming:
        def parse_date(x):
            try: return datetime.strptime(x["Due Date"], "%m/%d/%y")
            except:
                try: return datetime.strptime(x["Due Date"], "%m/%d/%Y")
                except: return datetime.max
        all_upcoming.sort(key=parse_date)
        st.dataframe(all_upcoming, use_container_width=True)
    else:
        st.info("No upcoming assignments logged yet.")

# ==========================================
# TAB 5: GPA PLANNER
# ==========================================
with tab_gpa:
    st.markdown("### 🎯 GPA Planner")
    with st.expander("⚙️ Customize Your GPA Scale"):
        if st.button("🔄 Reset GPA Scale to Default"):
            st.session_state.gpa_scale = [dict(row) for row in DEFAULT_GPA_SCALE]
            trigger_sound(SFX_TRASH)
            st.rerun()
        edited_scale = st.data_editor(st.session_state.gpa_scale, num_rows="dynamic", use_container_width=True)
        try:
            gpa_dict = {str(row["Grade"]): {"Standard": float(row["Standard"]), "Honors": float(row["Honors"]), "AP/IB/DE": float(row["AP/IB/DE"])} for row in edited_scale if row.get("Grade")}
            st.session_state.gpa_scale = edited_scale
        except ValueError:
            st.error("Invalid scale values."); gpa_dict = {}

    c1, c2 = st.columns(2)
    with c1: num_classes = st.number_input("Number of courses:", min_value=1, value=6, step=1)
    with c2: gpa_mode = st.radio("Mode", ["Weighted", "Unweighted"])

    total_gpa_points, total_credits = 0.0, 0.0
    if gpa_dict:
        letter_options = list(gpa_dict.keys())
        for i in range(num_classes):
            c_name, c_grade, c_lvl, c_cred = st.columns([2, 1, 1, 1])
            with c_name: st.text_input(f"Course {i+1}", key=f"n_{i}")
            with c_grade: grade = st.selectbox("Grade", letter_options, key=f"g_{i}", index=1 if len(letter_options) > 1 else 0)
            with c_lvl: level = st.selectbox("Level", ["Standard", "Honors", "AP/IB/DE"], key=f"l_{i}")
            with c_cred: credits = st.number_input("Credits", min_value=0.0, value=1.0, step=0.5, key=f"c_{i}")
            total_gpa_points += (gpa_dict[grade]["Standard" if gpa_mode == "Unweighted" else level] * credits)
            total_credits += credits

        current_gpa = (total_gpa_points / total_credits) if total_credits > 0 else 0.0
        st.write("---"); st.metric(f"Your Current {gpa_mode} GPA", f"{current_gpa:.3f}")

        st.write("---"); st.markdown("#### 🚀 Target GPA Calculator")
        target_gpa = st.number_input("Target GPA", min_value=0.0, max_value=6.0, value=round(current_gpa + 0.1, 2), step=0.05)

        if st.button("Calculate Upgrades Needed", type="primary"):
            points_deficit = (target_gpa * total_credits) - total_gpa_points
            if points_deficit <= 0:
                st.success("🎉 You are already at or above your Target GPA!")
                if st.session_state.settings.get("celebrations", True): st.balloons()
                trigger_sound(SFX_FANFARE)
            else:
                st.error(f"You are short by **{points_deficit:.2f} total GPA points** across your schedule.")
                trigger_sound(SFX_WARNING)

# ==========================================
# TAB 6: SETTINGS
# ==========================================
with tab_settings:
    st.markdown("### ⚙️ Application Settings")
    st.info("💡 **Tip for Native Themes:** To change between Light and Dark mode panels entirely, click the three dots (`⋮`) in the top right corner of the screen, select **Settings**, and change the **Theme**.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### Visuals & UI")
        new_anim = st.toggle("Enable Bouncy UI Animations", value=st.session_state.settings.get("animations", True))
        new_cel = st.toggle("Enable Success Celebrations (Balloons)", value=st.session_state.settings.get("celebrations", True))
        new_outline = st.toggle("Enable Text Outlines (Better Readability)", value=st.session_state.settings.get("text_outline", True))
        new_color = st.color_picker("Accent Color (Buttons & Metrics)", value=st.session_state.settings.get("accent_color", "#FF4B4B"))
        new_bg_color = st.color_picker("Background Color Override", value=st.session_state.settings.get("bg_color", "#0E1117"))

    with col_s2:
        st.markdown("#### General Defaults & Audio")
        new_sfx = st.toggle("Enable UI Sound Effects", value=st.session_state.settings.get("sfx_enabled", True))
        new_target = st.number_input("Default Target Grade (%)", min_value=0.0, max_value=150.0, value=float(st.session_state.settings.get("default_target", 90.0)), step=1.0)

    if st.button("💾 Save Settings", type="primary"):
        st.session_state.settings["animations"] = new_anim
        st.session_state.settings["celebrations"] = new_cel
        st.session_state.settings["sfx_enabled"] = new_sfx
        st.session_state.settings["text_outline"] = new_outline
        st.session_state.settings["accent_color"] = new_color
        st.session_state.settings["bg_color"] = new_bg_color
        st.session_state.settings["default_target"] = new_target
        st.toast('Settings saved successfully!', icon='✅')
        trigger_sound(SFX_CONFIRM)
        st.rerun()
