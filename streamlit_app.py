import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- APP CONFIG ---
st.set_page_config(
    page_title="FieldForce Optimizer Pro",
    page_icon="🚀",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'plan' not in st.session_state:
    st.session_state.plan = {
        "9:00 AM": {"Doctor": "Dr. Mehta", "Objective": "5 Rx Brand A", "Status": "Planned"},
        "10:30 AM": {"Doctor": "Dr. Verma", "Objective": "New Product Sampling", "Status": "Planned"},
        "12:00 PM": {"Doctor": "Dr. Joshi", "Objective": "3 Rx Brand B", "Status": "Planned"},
        "2:00 PM": {"Doctor": "Sai Pharma", "Objective": "Stock Replenishment", "Status": "Planned"}
    }
    st.session_state.execution = {}
    st.session_state.insights = []
    st.session_state.replan = {}
    st.session_state.day_completed = False

# --- SIMULATE DAY COMPLETION FUNCTION ---
def simulate_day_completion():
    # Generate realistic execution data
    st.session_state.execution = {
        "Dr. Mehta": {
            "Actual Time": "9:20 AM",
            "Outcome": "2 Rx",
            "Notes": "Price objection raised",
            "Duration": "28 mins",
            "Status": "Partial"
        },
        "Dr. Verma": {
            "Actual Time": "10:30 AM",
            "Outcome": "Canceled",
            "Notes": "Emergency OPD",
            "Duration": "0 mins",
            "Status": "Failed"
        },
        "Dr. Joshi": {
            "Actual Time": "12:15 PM",
            "Outcome": "2 Rx",
            "Notes": "Will prescribe more next week",
            "Duration": "45 mins",
            "Status": "Success"
        },
        "Sai Pharma": {
            "Actual Time": "2:30 PM",
            "Outcome": "Order placed",
            "Notes": "Brand A x200 units",
            "Duration": "35 mins",
            "Status": "Success"
        },
        "Chemist Ratan": {
            "Actual Time": "3:00 PM",
            "Outcome": "Stock-out",
            "Notes": "Brand B unavailable",
            "Duration": "15 mins",
            "Status": "Partial"
        }
    }
    
    # Generate insights
    st.session_state.insights = [
        {"type": "error", "text": "🚨 Price objections increased 20% in North 2"},
        {"type": "warning", "text": "⚠️ Dr. Verma has canceled 3 visits this month"},
        {"type": "success", "text": "✅ Dr. Joshi shows high Rx potential (follow-up recommended)"},
        {"type": "info", "text": "ℹ️ Chemist visits before 11 AM have 30% higher success rate"}
    ]
    
    # Generate replan
    st.session_state.replan = {
        "8:30 AM": {"Task": "Chemist Ratan", "Priority": "Critical", "Reason": "Brand B stock-out"},
        "9:30 AM": {"Task": "Dr. Mehta", "Priority": "High", "Reason": "Price objection handling"},
        "11:00 AM": {"Task": "Dr. Joshi", "Priority": "High", "Reason": "Rx reinforcement"},
        "3:00 PM": {"Task": "Dr. Verma", "Priority": "Medium", "Reason": "Reschedule attempt"}
    }
    
    st.session_state.day_completed = True
    st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    rep_name = st.selectbox("Medical Rep", ["MR Ravi", "MR Priya", "MR Ajay"])
    territory = st.selectbox("Territory", ["North 2", "West 1", "South 3"])
    sim_date = st.date_input("Date", datetime.today())
    
    if not st.session_state.day_completed:
        if st.button("🔄 Simulate Day Completion", use_container_width=True):
            simulate_day_completion()
    else:
        if st.button("🔄 Reset Simulation", use_container_width=True):
            st.session_state.day_completed = False
            st.rerun()
    
    st.divider()
    st.download_button(
        "📥 Export Today's Report",
        data=pd.DataFrame(st.session_state.execution).to_csv().encode('utf-8'),
        file_name=f"sfe_report_{sim_date}.csv",
        mime="text/csv"
    )

# --- MAIN DASHBOARD ---
st.title("FieldForce Optimizer Pro")
st.caption("Plan → Execute → Learn → Replan")

# SECTION 1: TODAY'S PLAN
with st.container():
    st.header("📅 Today's Plan")
    plan_df = pd.DataFrame.from_dict(st.session_state.plan, orient="index")
    st.dataframe(
        plan_df,
        use_container_width=True,
        height=300,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Planned", "In Progress", "Completed", "Canceled"]
            )
        }
    )
    
    # Plan metrics
    cols = st.columns(3)
    with cols[0]:
        st.metric("Total Planned Visits", len(st.session_state.plan))
    with cols[1]:
        target_rx = sum(int(v["Objective"].split()[0]) for v in st.session_state.plan.values() if "Rx" in v["Objective"])
        st.metric("Target Rx", target_rx)
    with cols[2]:
        st.metric("Estimated Travel Time", "2.5 hours")

# SECTION 2: EXECUTION TRACKING
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
with st.container():
    st.header("📝 Execution Tracking")
    
    if st.session_state.day_completed:
        exec_df = pd.DataFrame.from_dict(st.session_state.execution, orient="index")
        
        # Add color formatting
        def color_status(val):
            if val == "Success":
                return "color: #28a745; font-weight: bold;"
            elif val == "Partial":
                return "color: #ffc107; font-weight: bold;"
            else:
                return "color: #dc3545; font-weight: bold;"
        
        st.dataframe(
            exec_df.style.applymap(color_status, subset=["Status"]),
            use_container_width=True,
            height=350
        )
        
        # Execution metrics
        cols = st.columns(4)
        completed = len([v for v in st.session_state.execution.values() if v["Status"] == "Success"])
        cols[0].metric("Completed", f"{completed}/{len(st.session_state.plan)}")
        cols[1].metric("Rx Obtained", sum(int(v["Outcome"].split()[0]) for v in st.session_state.execution.values() if "Rx" in v["Outcome"]))
        cols[2].metric("Cancellations", len([v for v in st.session_state.execution.values() if v["Status"] == "Failed"]))
        cols[3].metric("Productive Time", "3.2 hours")
    else:
        st.info("Simulate day completion from the sidebar to see execution data")

# SECTION 3: INSIGHTS
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
with st.container():
    st.header("🔍 Insights & Recommendations")
    
    if st.session_state.day_completed:
        cols = st.columns(2)
        
        with cols[0]:
            st.subheader("Key Findings")
            for insight in st.session_state.insights:
                if insight["type"] == "error":
                    st.error(insight["text"])
                elif insight["type"] == "warning":
                    st.warning(insight["text"])
                elif insight["type"] == "success":
                    st.success(insight["text"])
                else:
                    st.info(insight["text"])
        
        with cols[1]:
            st.subheader("Performance Trends")
            trend_data = pd.DataFrame({
                "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "Target Rx": [18, 22, 15, 20, target_rx],
                "Actual Rx": [15, 20, 12, 18, sum(int(v["Outcome"].split()[0]) for v in st.session_state.execution.values() if "Rx" in v["Outcome"])]
            })
            st.line_chart(trend_data.set_index("Day"))
    else:
        st.warning("Complete a day's execution to generate insights")

# SECTION 4: TOMORROW'S PLAN
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
with st.container():
    st.header("🔄 Tomorrow's Plan")
    
    if st.session_state.day_completed:
        replan_df = pd.DataFrame.from_dict(st.session_state.replan, orient="index")
        st.dataframe(
            replan_df,
            use_container_width=True,
            height=300,
            column_config={
                "Priority": st.column_config.SelectboxColumn(
                    "Priority",
                    options=["Critical", "High", "Medium", "Low"]
                )
            }
        )
        
        if st.button("✅ Approve Tomorrow's Plan", type="primary"):
            st.session_state.plan = {
                time: {
                    "Doctor": task["Task"],
                    "Objective": task["Reason"],
                    "Status": "Planned"
                }
                for time, task in st.session_state.replan.items()
            }
            st.session_state.day_completed = False
            st.success("Plan approved! Ready for tomorrow.")
            st.rerun()
    else:
        st.info("Complete today's execution to generate tomorrow's plan")

# FOOTER
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.caption(f"© {datetime.now().year} FieldForce Optimizer Pro | v2.1 | {rep_name} | {territory}")