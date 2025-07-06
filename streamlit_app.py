import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# --- APP CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Pharma Field Force AI Assistant", page_icon="💊")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main container padding */
    .stApp > header { visibility: hidden; } /* Hide Streamlit header */
    .stApp { margin-top: -50px; } /* Pull content up */
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem; /* Adjust tab font size */
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; /* Space between tabs */
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #1A73E8; /* Highlight active tab */
        color: #1A73E8; /* Active tab text color */
    }
    /* Headers */
    h1 { color: #1A73E8; } /* Google Blue */
    h2, h3 { color: #3c4043; } /* Darker gray for subheadings */

    /* Buttons */
    .stButton > button {
        color: #FFFFFF;
        background-color: #1A73E8;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0F5EBC;
    }
    /* Primary button (if type="primary") */
    .stButton > button[data-testid="stFormSubmitButton"] {
        background-color: #1A73E8;
    }
    .stButton > button[data-testid="stFormSubmitButton"]:hover {
        background-color: #0F5EBC;
    }

    /* Metrics */
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background-color: #ffffff;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2em; /* Slightly smaller for better fit */
        font-weight: bold;
        color: #1A73E8;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 0.9em; /* Slightly smaller for better fit */
        color: #555555;
    }

    /* Spinners and Alerts */
    .stSpinner > div > span {
        font-size: 1.2em;
        color: #1A73E8;
    }
    .stAlert {
        border-radius: 8px;
    }

    /* DataFrame styling for better readability */
    .stDataFrame {
        font-size: 0.9em;
    }
    
    /* Specific status colors for text within dataframes (if applied via style.applymap) */
    .status-success { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-danger { color: #dc3545; font-weight: bold; }

    /* Custom insight card styles */
    .insight-card {
        border-left: 4px solid;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 5px;
        background-color: #f8f9fa; /* Light background for all insights */
    }
    .insight-success { border-color: #28a745; background-color: #e6ffe6; }
    .insight-warning { border-color: #ffc107; background-color: #fffacd; }
    .insight-error { border-color: #dc3545; background-color: #ffe6e6; }
    .insight-info { border-color: #17a2b8; background-color: #e6f7ff; }

</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
def initialize_session_state_for_date(target_date):
    """
    Initializes or resets session state variables for a given target date.
    This ensures that data is specific to the selected day.
    """
    st.session_state.current_date = target_date.strftime("%Y-%m-%d")

    # Define a default plan. This will be the starting point for any new day.
    default_plan = pd.DataFrame({
        "Time Slot": ["9:00 AM", "10:30 AM", "12:00 PM", "2:00 PM", "4:00 PM"],
        "Doctor": ["Dr. Mehta", "Dr. Verma", "Dr. Joshi", "Sai Pharma", "Dr. Kumar"],
        "Objective": ["Target 5 Rx", "New Product Sampling", "Achieve 3 Rx", "Stock Replenishment", "Secure 4 Rx"],
        "Brand": ["A", "B", "A", "B", "A"]
    })

    # Initialize plan (either default or from saved data if multi-day persistence was desired)
    # For this demo, we reset to default plan if the date changes.
    st.session_state.plan = default_plan.copy()
    
    # Initialize execution data (always empty at start of a new day)
    st.session_state.execution_data = pd.DataFrame(columns=[
        "Time Slot", "Doctor", "Planned Objective", "Actual Time", "Outcome", 
        "Notes", "Duration", "Actual Status", "Brand"
    ])
    
    # Reset insights and replan
    st.session_state.insights_text = "No insights available yet. Run today's simulation to generate."
    st.session_state.replan_text = "No replan generated yet."
    
    # --- NEW: Initialize next_day_plan data frame ---
    st.session_state.next_day_plan = pd.DataFrame(columns=["Time Slot", "Doctor", "Objective", "Brand", "Priority"])
    
    # --- CRITICAL: Reset day_completed for the new day ---
    st.session_state.day_completed = False

# --- Initial setup on first run or full refresh ---
if 'current_date' not in st.session_state:
    initialize_session_state_for_date(datetime.today())

# This part handles date changes from the date_input in sidebar
# It ensures a full reset for the *new* selected date.
selected_date_from_input = datetime.today().date() # Default value
# Use a unique key for the date input to ensure its value is correctly maintained
if 'date_selector_value' in st.session_state:
    selected_date_from_input = st.session_state.date_selector_value

if st.session_state.current_date != selected_date_from_input.strftime("%Y-%m-%d"):
    initialize_session_state_for_date(selected_date_from_input)


# --- HELPER FUNCTIONS ---
def get_rx_count(objective_text):
    """Safely extract Rx count from objective text using regex for better parsing."""
    if pd.isna(objective_text):
        return 0
    try:
        import re
        match = re.search(r'(\d+)\s*Rx', str(objective_text), re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0
    except ValueError:
        return 0

def simulate_day_completion():
    """Simulates a day's execution with pre-defined outcomes for demo purposes."""
    simulated_execution = []
    
    doctor_outcomes = {
        "Dr. Mehta": {"status": "Partial", "outcome": "2 Rx (Brand A)", "notes": "Price objection raised. Follow-up needed with value proposition.", "duration": "28 mins", "delay": 20},
        "Dr. Verma": {"status": "Failed", "outcome": "Canceled - Emergency OPD", "notes": "Doctor unavailable. Needs reschedule due to high patient load.", "duration": "0 mins", "delay": 0},
        "Dr. Joshi": {"status": "Success", "outcome": "4 Rx (Brand A)", "notes": "High potential. Will prescribe more next week. Excellent engagement.", "duration": "45 mins", "delay": 15},
        "Sai Pharma": {"status": "Success", "outcome": "Order placed (Brand B x200 units)", "notes": "Satisfied with stock levels. Discussed promotional offers.", "duration": "35 mins", "delay": 30},
        "Dr. Kumar": {"status": "Success", "outcome": "3 Rx (Brand A)", "notes": "Good discussion on patient benefits. Receptive to new data.", "duration": "30 mins", "delay": 10},
        "New Doctor": {"status": "Success", "outcome": "Introductory Visit", "notes": "Positive first interaction. Follow-up next week.", "duration": "25 mins", "delay": 5}, # Added for custom plan
        "default": {"status": "Success", "outcome": "Visit completed", "notes": "Routine check completed satisfactorily.", "duration": "20 mins", "delay": 10}
    }

    # Ensure st.session_state.plan is not empty before simulating
    if st.session_state.plan.empty:
        st.warning("No plan available for simulation. Please add some visits to the plan first.")
        return

    for _, row in st.session_state.plan.iterrows():
        time_slot = row["Time Slot"]
        doctor = row["Doctor"]
        objective = row["Objective"]
        brand = row["Brand"]
        
        outcome_details = doctor_outcomes.get(doctor, doctor_outcomes["default"])
        
        try:
            planned_time_dt = datetime.strptime(time_slot, "%I:%M %p")
            actual_time = (planned_time_dt + timedelta(minutes=outcome_details["delay"])).strftime("%I:%M %p")
        except ValueError:
            # Fallback if time_slot is not in expected format
            actual_time = "N/A" 

        simulated_execution.append({
            "Time Slot": time_slot,
            "Doctor": doctor,
            "Planned Objective": objective,
            "Actual Time": actual_time,
            "Outcome": outcome_details["outcome"],
            "Notes": outcome_details["notes"],
            "Duration": outcome_details["duration"],
            "Actual Status": outcome_details["status"],
            "Brand": brand
        })
    st.session_state.execution_data = pd.DataFrame(simulated_execution)

    # --- CRITICAL: Generate insights and replan *after* execution data is populated ---
    generate_intelligent_insights()
    generate_intelligent_replan()
    
    # --- CRITICAL: Set day_completed to True once simulation is complete ---
    st.session_state.day_completed = True

def generate_intelligent_insights():
    """Generates AI-like insights based on simulated execution data."""
    execution_df = st.session_state.execution_data
    if execution_df.empty:
        st.session_state.insights_text = "No execution data to generate insights. Run the simulation first."
        return

    total_visits = execution_df.shape[0]
    if total_visits == 0: # Handle case if execution_data somehow becomes empty despite checks
        st.session_state.insights_text = "No visits executed to generate insights."
        return

    success_visits = execution_df[execution_df["Actual Status"] == "Success"].shape[0]
    partial_visits = execution_df[execution_df["Actual Status"] == "Partial"].shape[0]
    failed_visits = execution_df[execution_df["Actual Status"] == "Failed"].shape[0]

    rx_obtained = sum(get_rx_count(outcome) for outcome in execution_df["Outcome"])
    
    brand_performance = execution_df.groupby("Brand")["Actual Status"].apply(
        lambda x: (x == "Success").sum() / len(x) if len(x) > 0 else 0
    ).reset_index()
    brand_performance.columns = ["Brand", "Success Rate"]
    brand_performance_str = "\n".join([f"- **{row['Brand']}**: {row['Success Rate']:.1%} success rate" for index, row in brand_performance.iterrows()])

    # Aggregate notes to avoid duplicates and ensure readability
    all_notes = execution_df["Notes"].dropna().unique()
    notes_summary = "\n".join([f"- {note}" for note in all_notes])

    insights_text = f"""
### Daily Performance Summary for {st.session_state.current_date}:

* **Total Visits Planned:** {st.session_state.plan.shape[0]}
* **Total Visits Executed:** {total_visits}
* **Success Rate:** {success_visits / total_visits:.1%} ({success_visits} successful visits)
* **Partial Success:** {partial_visits} visits
* **Failed Visits:** {failed_visits} visits
* **Total Rx Obtained (Estimated):** {rx_obtained} units across all brands

#### Brand Performance Overview:
{brand_performance_str if brand_performance_str else "- No specific brand performance data."}

#### Key Takeaways from Doctor Interactions:
{notes_summary if notes_summary else "- No specific notes recorded."}

#### Recommendations:
* **Focus on Dr. Verma:** High priority to reschedule due to emergency OPD. Understand their availability better for future planning.
* **Address Price Objections:** For accounts like Dr. Mehta, prepare stronger value propositions or discuss flexible pricing models for Brand A.
* **Leverage Successes:** Identify common factors in successful visits (e.g., Dr. Joshi, Dr. Kumar) and replicate strategies.
* **Proactive Stock Management:** Continue strong engagement with pharmacies like Sai Pharma for Brand B.
"""
    st.session_state.insights_text = insights_text

def generate_intelligent_replan():
    """
    Generates a simple AI-like replan summary and a structured DataFrame
    for the next day's plan based on insights.
    """
    if st.session_state.execution_data.empty:
        st.session_state.replan_text = "Cannot generate replan without simulation data."
        st.session_state.next_day_plan = pd.DataFrame(columns=["Time Slot", "Doctor", "Objective", "Brand", "Priority"])
        return

    # --- Replan Text Summary (as before) ---
    replan_summary = """
### Replan Suggestions for Tomorrow:

Based on today's performance and insights, here are some high-priority suggestions for your next day's plan:

1.  **Reschedule Dr. Verma:** This is critical. Prioritize rescheduling for early morning or late afternoon to avoid peak OPD hours. Objective: Ensure successful product detailing.
2.  **Follow-up with Dr. Mehta:** Address the price objection. Prepare specific data on ROI for Brand A or discuss alternative solutions. Objective: Convert partial success to full Rx.
3.  **Reinforce Success with Dr. Joshi & Dr. Kumar:** Maintain strong relationships and potentially increase frequency of visits or introduce new product lines. Objective: Deepen engagement and increase Rx volume.
4.  **Strategic Pharmacy Visit (Sai Pharma):** Build on the successful order for Brand B. Discuss potential for Brand A or new products.
5.  **Target New Leads (if available):** Allocate 1-2 slots for cold calls or introductory visits to expand reach, especially in areas with lower current success rates.

**Considerations for Time Slots:**
* Avoid peak clinic hours for critical doctor visits identified as 'Failed' or 'Partial'.
* Group geographically close visits to optimize travel time.

This replan focuses on addressing today's challenges and capitalizing on successes to improve overall territory performance.
"""
    st.session_state.replan_text = replan_summary

    # --- NEW: Generate structured data for next day's plan ---
    next_day_visits = []
    
    # Priority 1: Reschedule failed visits
    failed_visits_today = st.session_state.execution_data[st.session_state.execution_data["Actual Status"] == "Failed"]
    for _, row in failed_visits_today.iterrows():
        next_day_visits.append({
            "Time Slot": "09:30 AM", # Suggest an early slot
            "Doctor": row["Doctor"],
            "Objective": f"Reschedule: {row['Planned Objective']}",
            "Brand": row["Brand"],
            "Priority": "High (Failed Today)"
        })
    
    # Priority 2: Follow-up on partial success
    partial_visits_today = st.session_state.execution_data[st.session_state.execution_data["Actual Status"] == "Partial"]
    for _, row in partial_visits_today.iterrows():
        next_day_visits.append({
            "Time Slot": "11:00 AM", # Suggest a mid-morning slot
            "Doctor": row["Doctor"],
            "Objective": f"Follow-up: {row['Planned Objective']}",
            "Brand": row["Brand"],
            "Priority": "High (Partial Today)"
        })

    # Priority 3: Maintain success & explore further
    success_visits_today = st.session_state.execution_data[st.session_state.execution_data["Actual Status"] == "Success"]
    # Exclude those already marked for high priority follow-up
    success_for_next_day = success_visits_today[
        ~success_visits_today['Doctor'].isin(failed_visits_today['Doctor']) &
        ~success_visits_today['Doctor'].isin(partial_visits_today['Doctor'])
    ]
    for _, row in success_for_next_day.sample(min(2, len(success_for_next_day))).iterrows(): # Take up to 2 successful ones
        next_day_visits.append({
            "Time Slot": "01:30 PM", # Suggest afternoon slot
            "Doctor": row["Doctor"],
            "Objective": f"Reinforce: {row['Planned Objective']}",
            "Brand": row["Brand"],
            "Priority": "Medium (Successful Today)"
        })

    # Add a generic new lead if few visits generated
    if len(next_day_visits) < 5:
        next_day_visits.append({
            "Time Slot": "03:00 PM",
            "Doctor": "New Lead Clinic",
            "Objective": "New Introduction",
            "Brand": "Any",
            "Priority": "Low (New Potential)"
        })

    # Convert to DataFrame
    st.session_state.next_day_plan = pd.DataFrame(next_day_visits)
    
    # Optional: Sort the plan by Time Slot or Priority
    st.session_state.next_day_plan["Time Sort"] = st.session_state.next_day_plan["Time Slot"].apply(
        lambda x: datetime.strptime(x, "%I:%M %p").time()
    )
    st.session_state.next_day_plan = st.session_state.next_day_plan.sort_values(
        by=["Priority", "Time Sort"], 
        ascending=[True, True] # High priority first, then by time
    ).drop(columns=["Time Sort"])
    

# --- MAIN DASHBOARD ---
st.title("💊 Pharma Field Force AI Assistant")

st.markdown("""
Welcome to your AI-powered field force assistant!
**Plan** your daily visits, **simulate** execution, and get **intelligent insights** and **replans** to optimize your performance.
""")

st.markdown(f"--- **Medical Rep: MR Ravi** • **Territory: North 2** • **Date: {st.session_state.current_date}** ---")


# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    
    # Date Input
    selected_date_input = st.date_input(
        "📅 Select Simulation Date", 
        value=datetime.strptime(st.session_state.current_date, "%Y-%m-%d").date(),
        key="date_selector" # Add a key to prevent potential issues with state
    )
    # Store the value explicitly
    st.session_state.date_selector_value = selected_date_input


    # --- CRITICAL: Update current_date and re-initialize if the date changes ---
    if selected_date_input.strftime("%Y-%m-%d") != st.session_state.current_date:
        initialize_session_state_for_date(selected_date_input)
        st.rerun() # Trigger rerun immediately after state update

    st.divider()

    # --- SIMULATION BUTTON LOGIC ---
    if not st.session_state.day_completed:
        # Show "Run Simulation" if day is not completed
        if st.button("🚀 Run Today's Simulation", use_container_width=True, type="primary", 
                     help="Automatically fills execution outcomes and generates AI insights/replan."):
            with st.spinner("Simulating today's field operations..."):
                simulate_day_completion()
            st.toast("Simulation complete! Check Execution & Analytics tabs.", icon="✅")
            st.rerun() # --- CRITICAL: Rerun AFTER state is updated ---
    else:
        # Show "Day Completed" message and "Start New Day" button if day is completed
        st.success("🎉 Today's execution simulated!")
        if st.button("🔄 Start New Day", use_container_width=True):
            # Increment date for the new day and re-initialize
            next_day = datetime.strptime(st.session_state.current_date, "%Y-%m-%d") + timedelta(days=1)
            initialize_session_state_for_date(next_day)
            st.toast(f"Ready for {st.session_state.current_date}!", icon="🗓️")
            st.rerun() # Trigger rerun to show the new day's empty plan

    st.divider()

    st.info("💡 **Tip:** Add visits to your plan on the 'Daily Plan' tab before running the simulation!")
    st.info("📊 **Demo Data:** This app uses pre-defined demo data for simulation. In a real scenario, this would integrate with actual CRM data.")


# --- MAIN TABS ---
# --- MODIFIED: Added tab5 ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗓️ Daily Plan", "📊 Execution Data", "📈 Analytics & Insights", "🧠 AI Replan", "🗓️ Next Day's Plan"])

with tab1:
    st.header(f"Daily Visit Plan for {st.session_state.current_date}")
    st.write("Plan your visits for the day. Add doctors, objectives, and brands.")

    # Input form for adding plan entries
    with st.form("add_plan_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            time_slot = st.text_input("Time Slot (e.g., 10:00 AM)", value="09:00 AM")
        with col2:
            doctor = st.text_input("Doctor/Pharmacy Name", value="New Doctor")
        with col3:
            objective = st.text_input("Objective (e.g., 5 Rx Brand A)", value="Introduce New Drug")
        with col4:
            brand = st.text_input("Brand", value="Brand C")
        
        add_button = st.form_submit_button("➕ Add to Plan")

        if add_button:
            if time_slot and doctor and objective and brand:
                new_row = pd.DataFrame([{
                    "Time Slot": time_slot,
                    "Doctor": doctor,
                    "Objective": objective,
                    "Brand": brand
                }])
                st.session_state.plan = pd.concat([st.session_state.plan, new_row], ignore_index=True)
                st.toast("Visit added to plan!", icon="✅")
                st.rerun() # Rerun to update the displayed table
            else:
                st.warning("Please fill all fields to add to the plan.")

    # Display and clear plan
    if not st.session_state.plan.empty:
        st.subheader("Current Daily Plan:")
        st.dataframe(st.session_state.plan, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Clear Plan", type="secondary"):
            st.session_state.plan = pd.DataFrame(columns=["Time Slot", "Doctor", "Objective", "Brand"])
            st.toast("Plan cleared!", icon="🧹")
            st.rerun()
    else:
        st.info("Your daily plan is empty. Use the form above to add visits, or a default plan will be used for simulation.")

with tab2:
    st.header(f"Execution Data for {st.session_state.current_date}")
    st.write("This section shows the simulated outcomes of your daily visits.")

    if not st.session_state.execution_data.empty:
        st.subheader("Simulated Daily Execution:")
        # Apply styling for status column
        def color_status_text(val):
            if val == "Success": return "color: #28a745; font-weight: bold;"
            elif val == "Partial": return "color: #ffc107; font-weight: bold;"
            elif val == "Failed": return "color: #dc3545; font-weight: bold;"
            else: return "" # Default for "Not Visited" or other statuses

        st.dataframe(
            st.session_state.execution_data.style.applymap(color_status_text, subset=['Actual Status']),
            use_container_width=True, 
            hide_index=True
        )
    elif st.session_state.day_completed:
        st.info("Simulation completed, but no execution data was generated. This can happen if your plan was empty before running the simulation.")
    else:
        st.info("Run today's simulation from the sidebar to see the execution data.")

with tab3:
    st.header(f"Analytics & Insights for {st.session_state.current_date}")
    st.write("Get a data-driven overview of your daily performance and key takeaways.")
    if st.session_state.day_completed:
        st.markdown(st.session_state.insights_text, unsafe_allow_html=True)
    else:
        st.info("Run today's simulation from the sidebar to generate analytics and insights.")

with tab4:
    st.header(f"AI Replan for Tomorrow ({datetime.strptime(st.session_state.current_date, '%Y-%m-%d').date() + timedelta(days=1)})")
    st.write("Receive intelligent suggestions for optimizing your next day's plan based on today's performance.")
    if st.session_state.day_completed:
        st.markdown(st.session_state.replan_text, unsafe_allow_html=True)
    else:
        st.info("Run today's simulation from the sidebar to get AI-driven replan suggestions.")

# --- NEW TAB: Next Day's Plan ---
with tab5:
    next_day_date = datetime.strptime(st.session_state.current_date, '%Y-%m-%d').date() + timedelta(days=1)
    st.header(f"AI-Generated Plan for {next_day_date.strftime('%Y-%m-%d')}")
    st.write("Review, edit, and approve the AI-generated plan for tomorrow.")

    if st.session_state.day_completed and not st.session_state.next_day_plan.empty:
        st.info("You can edit the cells in the table below directly.")
        edited_df = st.data_editor(
            st.session_state.next_day_plan,
            num_rows="dynamic", # Allows adding/deleting rows
            column_config={
                "Time Slot": st.column_config.TextColumn("Time Slot (e.g., 10:00 AM)"),
                "Doctor": st.column_config.TextColumn("Doctor/Pharmacy Name"),
                "Objective": st.column_config.TextColumn("Objective"),
                "Brand": st.column_config.TextColumn("Brand"),
                "Priority": st.column_config.SelectboxColumn(
                    "Priority",
                    options=["High (Failed Today)", "High (Partial Today)", "Medium (Successful Today)", "Low (New Potential)"],
                    required=True,
                ),
            },
            use_container_width=True,
            hide_index=True
        )
        st.session_state.next_day_plan = edited_df # Update session state with edited DataFrame

        col_approve, col_clear = st.columns([0.2, 0.8])
        with col_approve:
            if st.button("✅ Approve Plan", type="primary"):
                # Here you would typically save this plan to a database or a persistent file
                st.success("Plan approved! This plan can now be used for the next day's simulation.")
                # You might want to automatically set this as the 'plan' for the next day
                # when 'Start New Day' is clicked. This requires modifying initialize_session_state_for_date
                # to check for an approved next_day_plan.
        with col_clear:
            if st.button("🗑️ Clear Next Day's Plan", type="secondary"):
                st.session_state.next_day_plan = pd.DataFrame(columns=["Time Slot", "Doctor", "Objective", "Brand", "Priority"])
                st.toast("Next day's plan cleared!", icon="🧹")
                st.rerun() # Refresh to show empty table

    elif st.session_state.day_completed:
        st.info("No AI-generated plan available for tomorrow. This might happen if today's simulation had no visits.")
    else:
        st.info("Run today's simulation from the sidebar to generate a plan for tomorrow.")