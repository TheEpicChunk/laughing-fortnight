import streamlit as st
import re
import json
import os

st.set_page_config(page_title="Student Toolkit", page_icon="🎓", layout="wide")

DATA_FILE = "student_data.json"

# ==========================================
# HELPER: Save and Load Data
# ==========================================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "classes": st.session_state.classes,
            "gpa_scale": st.session_state.gpa_scale
        }, f)

# --- SESSION STATE (With Local Save/Load) ---
saved_data = load_data()

if 'classes' not in st.session_state:
    if saved_data and "classes" in saved_data:
        st.session_state.classes = saved_data["classes"]
        for c in st.session_state.classes.values():
            if "upcoming" not in c:
                c["upcoming"] = []
    else:
        st.session_state.classes = {"Math": {"paste": "", "s_weight": 80, "f_weight": 20, "upcoming": []}}

if 'gpa_scale' not in st.session_state:
    if saved_data and "gpa_scale" in saved_data:
        st.session_state.gpa_scale = saved_data["gpa_scale"]
    else:
        st.session_state.gpa_scale = [
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

# --- SIDEBAR ---
st.sidebar.title("📚 Your Classes")

with st.sidebar.form("add_class_form", clear_on_submit=True):
    new_class_name = st.text_input("Create New Class")
    if st.form_submit_button("Add Class") and new_class_name:
        if new_class_name not in st.session_state.classes:
            st.session_state.classes[new_class_name] = {"paste": "", "s_weight": 80, "f_weight": 20, "upcoming": []}
            save_data()
        st.rerun()

class_list = list(st.session_state.classes.keys())

if class_list:
    active_class = st.sidebar.selectbox("Select Class to Edit:", class_list)
    c_data = st.session_state.classes[active_class]

    with st.sidebar.expander("⚙️ Manage Selected Class"):
        rename_val = st.text_input("Rename Class to:", value=active_class, key=f"rename_{active_class}")
        if st.button("Save New Name"):
            if rename_val and rename_val != active_class:
                if rename_val not in st.session_state.classes:
                    st.session_state.classes[rename_val] = st.session_state.classes.pop(active_class)
                    save_data()
                    st.rerun()
                else:
                    st.sidebar.error("A class with that name already exists.")

        st.write("---")
        if st.button("🗑️ Delete Class", type="secondary"):
            if len(st.session_state.classes) > 1:
                del st.session_state.classes[active_class]
                save_data()
                st.rerun()
            else:
                st.sidebar.error("You must have at least one class.")
else:
    st.session_state.classes = {"Math": {"paste": "", "s_weight": 80, "f_weight": 20, "upcoming": []}}
    save_data()
    st.rerun()


st.title("🎓 Student Toolkit")
tab_dash, tab_grade, tab_gpa = st.tabs(["📊 Dashboard", "📝 Class Calculator", "🎯 GPA Planner"])

# ==========================================
# HELPER: Calculate Grade from Paste Data
# ==========================================
def calculate_grade(paste_data, s_w, f_w, drop_lowest=False):
    s_earned, s_pos, f_earned, f_pos = 0.0, 0.0, 0.0, 0.0
    assignments = []
    
    if paste_data:
        # NEW REGEX: Captures Name (Group 1), Category (Group 2), Earned (Group 3), Possible (Group 4)
        # Uses negative lookahead `(?:(?!(?:Summative|Formative)).)*?` to ensure it NEVER crosses into the next assignment block.
        pattern = r'([^\n]+)\s*\n\s*(Summative|Formative)(?:(?!(?:Summative|Formative)).)*?Raw Score\s*([\d\.]+)\s*/\s*([\d\.]+)'
        matches = re.findall(pattern, paste_data, flags=re.IGNORECASE | re.DOTALL)
        
        for name, cat, earned, possible in matches:
            name = name.strip()
            cat = cat.lower()
            earned = float(earned)
            possible = float(possible)
            
            if possible > 0:
                assignments.append({"name": name, "cat": cat, "earned": earned, "possible": possible, "pct": earned/possible})
        
        if drop_lowest and assignments:
            assignments.sort(key=lambda x: x["pct"])
            assignments.pop(0)

        for ast in assignments:
            if ast["cat"] == 'summative':
                s_earned += ast["earned"]
                s_pos += ast["possible"]
            else:
                f_earned += ast["earned"]
                f_pos += ast["possible"]

    s_pct = (s_earned / s_pos) if s_pos > 0 else 0.0
    f_pct = (f_earned / f_pos) if f_pos > 0 else 0.0
    
    overall = 0.0
    if s_pos > 0 and f_pos > 0:
        overall = ((s_pct * (s_w / 100)) + (f_pct * (f_w / 100))) * 100
    elif s_pos > 0:
        overall = s_pct * 100
    elif f_pos > 0:
        overall = f_pct * 100
        
    return overall, s_earned, s_pos, f_earned, f_pos, s_pct, f_pct, assignments

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dash:
    st.markdown("### 📈 Your Overall Academic Status")
    cols = st.columns(3)
    
    for idx, (c_name, data) in enumerate(st.session_state.classes.items()):
        overall, _, _, _, _, _, _, _ = calculate_grade(data["paste"], data["s_weight"], data["f_weight"])
        
        if overall >= 90:
            status_color = "🟢" 
        elif overall >= 80:
            status_color = "🟡"
        elif overall > 0:
            status_color = "🔴"
        else:
            status_color = "⚪"

        col = cols[idx % 3]
        col.info(f"### {status_color} {c_name}\n**{round(overall, 2)}%**" if overall > 0 else f"### {status_color} {c_name}\n**No Data**")

# ==========================================
# TAB 2: CLASS CALCULATOR
# ==========================================
with tab_grade:
    st.header(f"Editing: {active_class}")
    
    # 1. SETTINGS AND DATA ENTRY
    with st.expander("📋 1. Paste StudentVUE Data & Set Weights", expanded=not bool(c_data["paste"])):
        st.markdown("**Instructions:** Go to StudentVUE -> Grade Book -> Select this class. Highlight everything from the top assignment down to the bottom, copy, and paste it below.")
        col_s, col_f = st.columns(2)
        with col_s:
            c_data["s_weight"] = st.number_input("Summative Weight (%)", value=c_data["s_weight"], max_value=100, step=5)
        with col_f:
            c_data["f_weight"] = st.number_input("Formative Weight (%)", value=c_data["f_weight"], max_value=100, step=5)
        c_data["paste"] = st.text_area("Paste assignments from StudentVUE here:", value=c_data["paste"], height=150)

    # Calculate Data
    drop_lowest = st.toggle("Drop Lowest Assignment Score")
    overall, s_earned, s_pos, f_earned, f_pos, s_pct, f_pct, parsed_assignments = calculate_grade(c_data["paste"], c_data["s_weight"], c_data["f_weight"], drop_lowest)

    # 2. CURRENT STATS
    st.write("---")
    st.markdown("### 📊 2. Your Current Stats")
    m1, m2, m3 = st.columns(3)
    m1.metric("Summative Total", f"{s_earned}/{s_pos}", f"{round(s_pct*100, 2)}%" if s_pos > 0 else "N/A", delta_color="off")
    m2.metric("Formative Total", f"{f_earned}/{f_pos}", f"{round(f_pct*100, 2)}%" if f_pos > 0 else "N/A", delta_color="off")
    m3.metric("Overall Grade", f"{round(overall, 2)}%")
    
    with st.expander("🔍 View Detected Graded Assignments"):
        if parsed_assignments:
            # Format nicely for display
            display_list = [{"Assignment Name": a["name"], "Category": a["cat"].capitalize(), "Score": f"{a['earned']} / {a['possible']}", "Percent": f"{a['pct']*100:.1f}%"} for a in parsed_assignments]
            st.dataframe(display_list, use_container_width=True)
        else:
            st.info("No graded assignments found in the pasted text yet.")

    # 3. PLANNER
    st.write("---")
    st.markdown("### 🔮 3. Future Grade Planner")
    st.caption("Auto-detect upcoming assignments from your paste, or add them manually to see what you need to score on them.")
    
    col_auto, col_clear = st.columns([2, 1])
    with col_auto:
        if st.button("🔍 Auto-Detect Upcoming Assignments"):
            # NEW REGEX: Grabs Name (Group 1), Category (Group 2), and Points (Group 3). Restricts search bounds to avoid overlap.
            pattern_upcoming = r'([^\n]+)\s*\n\s*(Summative|Formative)(?:(?!(?:Summative|Formative)).)*?Not Due(?:(?!(?:Summative|Formative)).)*?([\d\.]+)\s*Points'
            matches = re.findall(pattern_upcoming, c_data["paste"], flags=re.IGNORECASE | re.DOTALL)
            
            if matches:
                count = 0
                for name, cat, pts in matches:
                    # Avoid adding duplicates if clicked twice
                    if not any(a["Name"] == name.strip() for a in c_data["upcoming"]):
                        c_data["upcoming"].append({"Name": name.strip(), "Category": cat.capitalize(), "Points": float(pts)})
                        count += 1
                
                if count > 0:
                    st.success(f"Added {count} new upcoming assignment(s)!")
                else:
                    st.info("Assignments were found, but they are already in your list below.")
                save_data()
                st.rerun()
            else:
                st.warning("No upcoming assignments found. Make sure they say 'Not Due' and 'Points Possible'.")
    
    with col_clear:
        if st.button("🗑️ Clear Upcoming List"):
            c_data["upcoming"] = []
            save_data()
            st.rerun()

    # Manual Add Form
    with st.expander("➕ Manually Add an Upcoming Assignment"):
        c_cat, c_name, c_pts, c_btn = st.columns([1.5, 2, 1, 1])
        with c_cat: m_cat = st.selectbox("Category", ["Summative", "Formative"], key=f"m_cat_{active_class}")
        with c_name: m_name = st.text_input("Name", value="New Assignment", key=f"m_name_{active_class}")
        with c_pts: m_pts = st.number_input("Points", min_value=1.0, value=100.0, step=1.0, key=f"m_pts_{active_class}")
        with c_btn:
            st.write("") 
            st.write("") 
            if st.button("Add", key=f"m_btn_{active_class}", use_container_width=True):
                c_data["upcoming"].append({"Name": m_name, "Category": m_cat, "Points": m_pts})
                save_data()
                st.rerun()
    
    edited_upcoming = st.data_editor(
        c_data["upcoming"],
        num_rows="dynamic",
        column_config={
            "Name": st.column_config.TextColumn("Assignment Name", required=True),
            "Category": st.column_config.SelectboxColumn("Category", options=["Summative", "Formative"], required=True),
            "Points": st.column_config.NumberColumn("Points Possible", min_value=0.1, required=True)
        },
        use_container_width=True,
        key=f"editor_{active_class}"
    )
    
    if edited_upcoming != c_data["upcoming"]:
        c_data["upcoming"] = edited_upcoming
        save_data()
        
    if len(edited_upcoming) > 0:
        st.write("---")
        st.markdown("#### 🎯 Target Calculator")
        target_grade = st.number_input("What is your Target Overall Grade? (%)", min_value=0.0, max_value=150.0, value=90.0, step=1.0)
        
        assumed_scores = []
        
        if len(edited_upcoming) > 1:
            st.info("💡 **Tip:** You have multiple upcoming assignments. Use the sliders below to estimate what you'll get on the earlier assignments to see how it changes the requirement for the **final** assignment.")
            
            for i in range(len(edited_upcoming) - 1):
                item = edited_upcoming[i]
                cat, pts, name = item.get("Category"), float(item.get("Points", 1.0)), item.get("Name", "Assignment")
                
                pct = st.slider(f"Expected Score for: {name} ({pts} pts)", 0.0, 100.0, 90.0, step=1.0, key=f"sl_{active_class}_{i}")
                assumed_scores.append(pct / 100.0 * pts)
                
        # --- THE MATH: Solve for the LAST assignment ---
        last_ast = edited_upcoming[-1]
        last_cat, last_pts, last_name = last_ast.get("Category", "Summative"), float(last_ast.get("Points", 1.0)), last_ast.get("Name", "Final Assignment")
        
        # Sum up current totals + assumed slider totals
        s_earned_new, s_pos_new = s_earned, s_pos
        f_earned_new, f_pos_new = f_earned, f_pos
        
        for i in range(len(edited_upcoming) - 1):
            cat = edited_upcoming[i].get("Category")
            pts = float(edited_upcoming[i].get("Points", 1.0))
            e = assumed_scores[i]
            
            if cat == "Summative":
                s_earned_new += e
                s_pos_new += pts
            else:
                f_earned_new += e
                f_pos_new += pts

        # Add the possible points of the final assignment
        if last_cat == "Summative":
            s_pos_new += last_pts
        else:
            f_pos_new += last_pts
            
        target_dec = target_grade / 100.0
        w_s, w_f = c_data["s_weight"] / 100.0, c_data["f_weight"] / 100.0
        
        active_w_s = w_s if (f_pos_new > 0) else 1.0
        active_w_f = w_f if (s_pos_new > 0) else 1.0
        
        needed_points = 0.0
        
        if last_cat == "Summative":
            f_pct_new = (f_earned_new / f_pos_new) if f_pos_new > 0 else 0.0
            f_contribution = f_pct_new * active_w_f if f_pos_new > 0 else 0.0
            
            if active_w_s > 0:
                needed_s_pct = (target_dec - f_contribution) / active_w_s
                needed_s_earned = needed_s_pct * s_pos_new
                needed_points = needed_s_earned - s_earned_new
        else:
            s_pct_new = (s_earned_new / s_pos_new) if s_pos_new > 0 else 0.0
            s_contribution = s_pct_new * active_w_s if s_pos_new > 0 else 0.0
            
            if active_w_f > 0:
                needed_f_pct = (target_dec - s_contribution) / active_w_f
                needed_f_earned = needed_f_pct * f_pos_new
                needed_points = needed_f_earned - f_earned_new

        # Display Result
        st.markdown(f"#### Requirement for your final assignment: **{last_name}**")
        if needed_points > last_pts:
            st.error(f"You need **{needed_points:.1f} / {last_pts}** (**{needed_points/last_pts*100:.1f}%**) — This requires extra credit!")
        elif needed_points <= 0:
            st.success(f"You need **{needed_points:.1f} / {last_pts}** — You're safe even with a 0!")
        else:
            st.success(f"You need **{needed_points:.1f} / {last_pts}** (**{needed_points/last_pts*100:.1f}%**)")

# ==========================================
# TAB 3: GPA PLANNER
# ==========================================
with tab_gpa:
    st.markdown("### 🎯 GPA Planner")
    with st.expander("⚙️ Customize Your GPA Scale"):
        edited_scale = st.data_editor(st.session_state.gpa_scale, num_rows="dynamic", use_container_width=True)
        try:
            gpa_dict = {str(row["Grade"]): {"Standard": float(row["Standard"]), "Honors": float(row["Honors"]), "AP/IB/DE": float(row["AP/IB/DE"])} for row in edited_scale if row.get("Grade")}
        except ValueError:
            st.error("Invalid scale data. Please ensure all GPA values are numbers.")
            gpa_dict = {}

    c1, c2 = st.columns(2)
    with c1:
        num_classes = st.number_input("How many classes are you taking?", min_value=1, value=6, step=1)
    with c2:
        gpa_mode = st.radio("Calculation Mode", ["Weighted", "Unweighted"])
    
    total_gpa_points, total_credits = 0.0, 0.0
    
    if gpa_dict:
        letter_options = list(gpa_dict.keys())
        for i in range(num_classes):
            c_name, c_grade, c_lvl, c_cred = st.columns([2, 1, 1, 1])
            with c_name: st.text_input(f"Class {i+1}", placeholder=f"Class {i+1} Name", key=f"n_{i}")
            with c_grade: grade = st.selectbox("Grade", letter_options, key=f"g_{i}", index=1 if len(letter_options) > 1 else 0)
            with c_lvl: level = st.selectbox("Level", ["Standard", "Honors", "AP/IB/DE"], key=f"l_{i}")
            with c_cred: credits = st.number_input("Credits", min_value=0.0, value=1.0, step=0.5, key=f"c_{i}")
                
            active_level = "Standard" if gpa_mode == "Unweighted" else level
            total_gpa_points += (gpa_dict[grade][active_level] * credits)
            total_credits += credits
            
        current_gpa = (total_gpa_points / total_credits) if total_credits > 0 else 0.0
        
        st.write("---")
        st.metric(f"Your Current {gpa_mode} GPA", f"{current_gpa:.3f}")
        
        st.write("---")
        st.markdown("#### 🚀 GPA Goal Calculator")
        target_gpa = st.number_input("Target GPA", min_value=0.0, max_value=6.0, value=round(current_gpa + 0.1, 2), step=0.05)
        
        if st.button("Calculate Upgrades Needed", type="primary"):
            target_total_points = target_gpa * total_credits
            points_deficit = target_total_points - total_gpa_points
            
            if points_deficit <= 0:
                st.success("🎉 You are already at or above your Target GPA!")
            else:
                st.error(f"You are currently short by **{points_deficit:.2f} total GPA points** across your schedule.")
                st.info("To reach your goal, look at your current classes and see which ones you can raise a letter grade in. (A jump from a B to an A in a standard 1-credit class usually earns you 1.0 extra GPA point).")

# Save data automatically at the end of every interaction
save_data()
