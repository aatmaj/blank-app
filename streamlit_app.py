import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- APP CONFIG ---
st.set_page_config(
    page_title="FieldForce Intelligence - Planner",
    page_icon="🚀",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .st-emotion-cache-z5fcl4 {
        padding-top: 2rem;
    }
    .st-emotion-cache-18ni7ap {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        background: #f0f2f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .divider-line {
        border-top: 2px solid #6e48aa;
        margin: 10px 0;
    }
    .status-success { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }
    .stButton>button {
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    h1, h2, h3 {
        color: #4a2d73;
    }
    /* Style for info, success, warning, error boxes */
    .stAlert {
        border-radius: 8px;
        padding: 10px 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
def initialize_session_state():
    # Initial plan as a DataFrame for easier manipulation with data_editor
    st.session_state.plan = pd.DataFrame({
        "Time Slot": ["9:00 AM", "10:30 AM", "12:00 PM", "2:00 PM"],
        "Doctor": ["Dr. Mehta", "Dr. Verma", "Dr. Joshi", "Sai Pharma"],
        "Objective": ["Get 5 Rx", "New Product Sampling", "3 Rx", "Stock Replenishment"],
        "Brand": ["A", "B", "A", "B"],
        "Planned Status": ["Planned", "Planned", "Planned", "Planned"]
    }).set_index("Time Slot") # Using Time Slot as index for easy lookup

    # Execution data will be built from the editable table
    st.session_state.execution_data = pd.DataFrame(columns=[
        "Time Slot", "Doctor", "Planned Objective", "Actual Time", "Outcome", "Notes", "Duration", "Actual Status"
    ])
    st.session_state.insights = []
    st.session_state.replan_data = pd.DataFrame(columns=[
        "Time Slot", "Task", "Priority", "Reason", "Brand" # Added Brand for replan
    ])
    st.session_state.day_completed = False
    st.session_state.current_date = datetime.today().strftime("%Y-%m-%d") # Store current date

if 'plan' not in st.session_state:
    initialize_session_state()

# --- HELPER FUNCTIONS ---
def get_rx_count(objective_text):
    """Safely extract Rx count from objective text"""
    if pd.isna(objective_text) or "Rx" not in objective_text:
        return 0
    try:
        # Extract digits from the beginning of the string that might contain "Rx"
        # e.g., "5 Rx", "get 10 Rx", "Rx for 20"
        digits = ''.join(filter(str.isdigit, objective_text.split('Rx')[0]))
        if digits:
            return int(digits)
        return 0
    except ValueError:
        return 0

def simulate_day_completion():
    # Create realistic execution data based on the plan
    simulated_execution = []
    for time_slot, row in st.session_state.plan.iterrows():
        doctor = row["Doctor"]
        objective = row["Objective"]
        brand = row["Brand"]

        actual_time = ""
        outcome = ""
        notes = ""
        duration = ""
        status = ""

        if doctor == "Dr. Mehta":
            actual_time = (datetime.strptime(time_slot, "%I:%M %p") + timedelta(minutes=20)).strftime("%I:%M %p")
            outcome = "2 Rx (Brand A)"
            notes = "Price objection raised."
            duration = "28 mins"
            status = "Partial"
        elif doctor == "Dr. Verma":
            actual_time = time_slot # Same planned time, but outcome different
            outcome = "Canceled"
            notes = "Emergency OPD. Needs reschedule."
            duration = "0 mins"
            status = "Failed"
        elif doctor == "Dr. Joshi":
            actual_time = (datetime.strptime(time_slot, "%I:%M %p") + timedelta(minutes=15)).strftime("%I:%M %p")
            outcome = "4 Rx (Brand A)" # Slightly better outcome
            notes = "Will prescribe more next week. High potential."
            duration = "45 mins"
            status = "Success"
        elif doctor == "Sai Pharma":
            actual_time = (datetime.strptime(time_slot, "%I:%M %p") + timedelta(minutes=30)).strftime("%I:%M %p")
            outcome = "Order placed (Brand B x200 units)"
            notes = "Satisfied with stock levels."
            duration = "35 mins"
            status = "Success"
        else: # For any extra tasks if added manually before simulation
            actual_time = (datetime.strptime(time_slot, "%I:%M %p") + timedelta(minutes=10)).strftime("%I:%M %p")
            outcome = "Visit completed"
            notes = "Routine check."
            duration = "20 mins"
            status = "Success"

        simulated_execution.append({
            "Time Slot": time_slot,
            "Doctor": doctor,
            "Planned Objective": objective,
            "Actual Time": actual_time,
            "Outcome": outcome,
            "Notes": notes,
            "Duration": duration,
            "Actual Status": status
        })
    st.session_state.execution_data = pd.DataFrame(simulated_execution)

    # Generate insights
    st.session_state.insights = [
        {"type": "error", "text": "🚨 Price objections for Brand A increased 20% this week."},
        {"type": "warning", "text": "⚠️ Dr. Verma has canceled 3 visits this month. Requires a different approach."},
        {"type": "success", "text": "✅ Dr. Joshi shows high Rx potential (actual 4Rx vs 3Rx planned). Follow-up recommended."},
        {"type": "info", "text": "ℹ️ Chemist visits before 11 AM have 30% higher success rate."}
    ]

    # Generate replan for tomorrow based on today's outcome
    # Replan as a DataFrame for data_editor
    replan_tasks = []
    # Carry over Dr. Verma
    replan_tasks.append({
        "Time Slot": "9:30 AM", # Suggested new time
        "Task": "Dr. Verma",
        "Priority": "Critical",
        "Reason": "Reschedule attempt after cancellation",
        "Brand": "B"
    })
    # Follow-up with Dr. Mehta for price objection
    replan_tasks.append({
        "Time Slot": "11:00 AM",
        "Task": "Dr. Mehta",
        "Priority": "High",
        "Reason": "Address price objection, reinforce Brand A value",
        "Brand": "A"
    })
    # High potential Dr. Joshi
    replan_tasks.append({
        "Time Slot": "2:00 PM",
        "Task": "Dr. Joshi",
        "Priority": "High",
        "Reason": "Rx reinforcement for Brand A",
        "Brand": "A"
    })
    # Add a new proactive visit
    replan_tasks.append({
        "Time Slot": "4:00 PM",
        "Task": "New Prospect Clinic",
        "Priority": "Medium",
        "Reason": "Introduce Brand B to new clinic",
        "Brand": "B"
    })

    st.session_state.replan_data = pd.DataFrame(replan_tasks)
    st.session_state.day_completed = True
    st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    rep_name = st.selectbox("Medical Rep", ["MR Ravi", "MR Priya", "MR Ajay"])
    territory = st.selectbox("Territory", ["North 2", "West 1", "South 3"])
    
    # Using session state to control the displayed date
    display_date = st.date_input("Current Simulation Date", datetime.today())
    # Update current_date in session state only when changed by user
    if display_date.strftime("%Y-%m-%d") != st.session_state.current_date:
        st.session_state.current_date = display_date.strftime("%Y-%m-%d")
        # If date changes, reset simulation for a new day unless explicitly prevented
        # For this simple demo, we'll reset if date changes
        initialize_session_state() # Resets everything for the new selected day
        st.rerun()

    st.divider()

    if not st.session_state.day_completed:
        if st.button("🔄 Simulate Day Completion", use_container_width=True, help="Automatically fill execution and generate insights/replan."):
            simulate_day_completion()
    else:
        if st.button("🔄 Reset Simulation for New Day", use_container_width=True, help="Clear all executed data and insights. Start fresh."):
            initialize_session_state()
            st.rerun()

    st.divider()
    if not st.session_state.execution_data.empty:
        st.download_button(
            "📥 Export Today's Report",
            data=st.session_state.execution_data.to_csv(index=False).encode('utf-8'),
            file_name=f"sfe_report_{st.session_state.current_date}_{rep_name}.csv",
            mime="text/csv"
        )
    else:
        st.info("No execution data to export yet.")

# --- MAIN DASHBOARD ---
st.title("FieldForce Intelligence - Planner")
st.caption(f"Plan → Execute → Learn → Replan for {rep_name} in {territory} - {st.session_state.current_date}")

# SECTION 1: TODAY'S PLAN
with st.container():
    st.header("📅 Today's Original Plan")
    st.dataframe(
        st.session_state.plan,
        use_container_width=True,
        height=250,
        column_config={
            "Planned Status": st.column_config.SelectboxColumn(
                "Planned Status",
                options=["Planned", "In Progress", "Completed", "Canceled"],
                disabled=True # Original plan is not editable here
            )
        }
    )

    # Plan metrics
    cols = st.columns(3)
    with cols[0]:
        st.metric("Total Planned Visits", len(st.session_state.plan))
    with cols[1]:
        target_rx = sum(get_rx_count(obj) for obj in st.session_state.plan["Objective"].values)
        st.metric("Target Rx (Planned)", target_rx)
    with cols[2]:
        st.metric("Estimated Travel Time", "2.5 hours")

# SECTION 2: EXECUTION TRACKING
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
with st.container():
    st.header("📝 Today's Execution Reality")

    if st.session_state.day_completed:
        st.subheader("Finalized Execution Data")
        # Display execution data as a non-editable table after simulation or manual save
        def color_status(val):
            if val == "Success": return "color: #28a745; font-weight: bold;"
            elif val == "Partial": return "color: #ffc107; font-weight: bold;"
            else: return "color: #dc3545; font-weight: bold;"

        st.dataframe(
            st.session_state.execution_data.style.applymap(color_status, subset=["Actual Status"]),
            use_container_width=True,
            height=300
        )

        # Execution metrics (calculated from final data)
        cols = st.columns(4)
        completed_visits = len(st.session_state.execution_data[st.session_state.execution_data["Actual Status"] == "Success"])
        cols[0].metric("Successfully Completed", f"{completed_visits}/{len(st.session_state.plan)}")

        actual_rx_obtained = sum(get_rx_count(outcome) for outcome in st.session_state.execution_data["Outcome"].values)
        cols[1].metric("Actual Rx Obtained", actual_rx_obtained)

        cancellations = len(st.session_state.execution_data[st.session_state.execution_data["Actual Status"] == "Failed"])
        cols[2].metric("Cancellations/Failures", cancellations)
        cols[3].metric("Productive Time", "3.2 hours") # Placeholder for now

    else:
        st.info("Fill out the execution details below or 'Simulate Day Completion' from sidebar.")

        # Prepare a DataFrame for live editing based on the current plan
        # Add columns for actual data, preserving planned data
        editable_execution_df = st.session_state.plan.copy().reset_index() # Convert index to column for data_editor
        editable_execution_df = editable_execution_df.rename(columns={
            "Objective": "Planned Objective",
            "Planned Status": "Initial Status"
        })
        editable_execution_df['Actual Time'] = ""
        editable_execution_df['Outcome'] = ""
        editable_execution_df['Notes'] = ""
        editable_execution_df['Duration'] = ""
        editable_execution_df['Actual Status'] = "Not Visited" # Default status

        st.subheader("Live Execution Updates (Edit Below)")
        edited_live_execution_df = st.data_editor(
            editable_execution_df,
            column_config={
                "Time Slot": st.column_config.TextColumn("Time Slot", disabled=True),
                "Doctor": st.column_config.TextColumn("Doctor", disabled=True),
                "Planned Objective": st.column_config.TextColumn("Planned Objective", disabled=True),
                "Brand": st.column_config.TextColumn("Brand", disabled=True),
                "Initial Status": st.column_config.TextColumn("Initial Status", disabled=True),
                "Actual Status": st.column_config.SelectboxColumn(
                    "Actual Status",
                    options=["Not Visited", "In Progress", "Success", "Partial", "Failed"],
                    required=True
                ),
                "Actual Time": st.column_config.TextColumn("Actual Time (e.g., 9:15 AM)"),
                "Outcome": st.column_config.TextColumn("Outcome (e.g., 5 Rx, Canceled, Order Placed)"),
                "Notes": st.column_config.TextColumn("Notes"),
                "Duration": st.column_config.TextColumn("Duration (e.g., 30 mins)"),
            },
            num_rows="dynamic", # Allow adding/deleting rows if needed for ad-hoc visits
            use_container_width=True,
            key="live_execution_editor"
        )

        if st.button("💾 Save Live Execution Updates"):
            # Update st.session_state.execution_data from the edited_live_execution_df
            st.session_state.execution_data = edited_live_execution_df.copy()
            st.session_state.day_completed = True # Mark day as completed upon manual save
            st.success("Live execution updates saved! Day marked as completed.")
            st.rerun()

# SECTION 3: EOD GOAL ASSESSMENT
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
with st.container():
    st.header("🎯 EOD Goal Assessment & Variance")

    if st.session_state.day_completed and not st.session_state.execution_data.empty:
        total_planned_visits = len(st.session_state.plan)
        total_actual_visits = len(st.session_state.execution_data[st.session_state.execution_data["Actual Status"] != "Not Visited"])
        actual_rx_obtained = sum(get_rx_count(outcome) for outcome in st.session_state.execution_data["Outcome"].values)
        target_rx = sum(get_rx_count(obj) for obj in st.session_state.plan["Objective"].values)

        st.subheader("Performance Summary")
        col_perf1, col_perf2, col_perf3 = st.columns(3)
        with col_perf1:
            st.metric("Visits (Planned vs. Actual)", f"{total_actual_visits}/{total_planned_visits}",
                      delta=total_actual_visits - total_planned_visits, delta_color="inverse")
        with col_perf2:
            st.metric("Rx (Target vs. Actual)", f"{actual_rx_obtained}/{target_rx}",
                      delta=actual_rx_obtained - target_rx, delta_color="normal")
        with col_perf3:
            # Overall status indicator
            if actual_rx_obtained >= target_rx * 0.9 and total_actual_visits >= total_planned_visits * 0.8:
                st.markdown(f"**Overall Status:** <span class='status-success'>**On Track (Green)**</span>", unsafe_allow_html=True)
            elif actual_rx_obtained >= target_rx * 0.7 or total_actual_visits >= total_planned_visits * 0.6:
                st.markdown(f"**Overall Status:** <span class='status-warning'>**Minor Deviations (Yellow)**</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Overall Status:** <span class='status-danger'>**Significant Issues (Red)**</span>", unsafe_allow_html=True)

        st.subheader("Visit-wise Variance")
        variance_data = []
        for planned_time, planned_row in st.session_state.plan.iterrows():
            doctor = planned_row["Doctor"]
            planned_obj = planned_row["Objective"]
            
            # Find corresponding actual data
            actual_row_match = st.session_state.execution_data[
                (st.session_state.execution_data["Time Slot"] == planned_time) &
                (st.session_state.execution_data["Doctor"] == doctor)
            ]
            
            actual_status = "N/A"
            actual_outcome = "N/A"
            notes = ""
            
            if not actual_row_match.empty:
                actual_row = actual_row_match.iloc[0]
                actual_status = actual_row["Actual Status"]
                actual_outcome = actual_row["Outcome"]
                notes = actual_row["Notes"]

            variance_data.append({
                "Time Slot": planned_time,
                "Doctor": doctor,
                "Planned Objective": planned_obj,
                "Planned Status": planned_row["Planned Status"],
                "Actual Status": actual_status,
                "Actual Outcome": actual_outcome,
                "Notes": notes
            })

        variance_df = pd.DataFrame(variance_data)

        # Apply color based on actual status
        def color_variance_status(val):
            if val == "Success": return "color: #28a745; font-weight: bold;"
            elif val == "Partial": return "color: #ffc107; font-weight: bold;"
            elif val == "Failed" or val == "Not Visited": return "color: #dc3545; font-weight: bold;"
            else: return ""

        st.dataframe(
            variance_df.style.applymap(color_variance_status, subset=["Actual Status"]),
            use_container_width=True,
            height=300
        )

        st.subheader("Key Findings & Learnings")
        for insight in st.session_state.insights:
            if insight["type"] == "error":
                st.error(insight["text"])
            elif insight["type"] == "warning":
                st.warning(insight["text"])
            elif insight["type"] == "success":
                st.success(insight["text"])
            else:
                st.info(insight["text"])

    else:
        st.warning("Complete a day's execution to generate the EOD assessment and insights.")

# SECTION 4: RE-PLAN FOR NEXT DAY
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
with st.container():
    st.header("🔄 Re-Plan for Tomorrow")

    if st.session_state.day_completed:
        st.info("Edit the table below to finalize tomorrow's plan. New rows can be added.")
        edited_replan_df = st.data_editor(
            st.session_state.replan_data,
            column_config={
                "Time Slot": st.column_config.TextColumn("Time Slot (e.g., 9:00 AM)"),
                "Task": st.column_config.TextColumn("Task (Doctor/Chemist Name)", required=True),
                "Priority": st.column_config.SelectboxColumn(
                    "Priority",
                    options=["Critical", "High", "Medium", "Low"],
                    required=True
                ),
                "Reason": st.column_config.TextColumn("Objective/Reason"),
                "Brand": st.column_config.TextColumn("Associated Brand")
            },
            num_rows="dynamic", # Allows adding/deleting rows
            use_container_width=True,
            key="replan_editor"
        )

        if st.button("✅ Approve & Finalize Tomorrow's Plan", type="primary", use_container_width=True):
            # Convert edited_replan_df back to the plan DataFrame structure
            new_plan_dict = {}
            for index, row in edited_replan_df.iterrows():
                # Ensure valid time slot for indexing
                time_slot_val = row["Time Slot"]
                if pd.isna(time_slot_val) or time_slot_val.strip() == "":
                    st.error(f"Error: Time Slot cannot be empty for row {index + 1}. Please provide a time.")
                    st.stop() # Stop execution if validation fails

                new_plan_dict[time_slot_val] = {
                    "Doctor": row["Task"],
                    "Objective": row["Reason"],
                    "Brand": row["Brand"], # Use brand from replan
                    "Planned Status": "Planned"
                }

            st.session_state.plan = pd.DataFrame.from_dict(new_plan_dict, orient="index")

            # Reset other session states for the new day
            st.session_state.day_completed = False
            st.session_state.execution_data = pd.DataFrame(columns=[
                "Time Slot", "Doctor", "Planned Objective", "Actual Time", "Outcome", "Notes", "Duration", "Actual Status"
            ]) # Clear execution
            st.session_state.insights = []
            st.session_state.replan_data = pd.DataFrame(columns=[
                "Time Slot", "Task", "Priority", "Reason", "Brand"
            ]) # Clear replan
            st.session_state.current_date = (datetime.strptime(st.session_state.current_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

            st.success("Plan approved! The dashboard is now ready for tomorrow's operations.")
            st.rerun()
    else:
        st.info("Complete today's execution (or simulate it) to generate and edit tomorrow's plan.")

# FOOTER
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.caption(f"© {datetime.now().year} FieldForce Intelligence - Planner | v 0.2 | {rep_name} | {territory}")