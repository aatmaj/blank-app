import streamlit as st
import pandas as pd
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="FieldForce Optimizer",
    page_icon="🚀",
    layout="wide"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* Main card styling */
    .custom-card {
        border-radius: 10px;
        padding: 15px;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    
    /* Status badges */
    .status-success {
        color: #28a745;
        font-weight: bold;
        background-color: #d4edda;
        padding: 3px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
        background-color: #fff3cd;
        padding: 3px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    .status-danger {
        color: #dc3545;
        font-weight: bold;
        background-color: #f8d7da;
        padding: 3px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    
    /* Divider */
    .custom-divider {
        border-top: 2px solid #6e48aa;
        margin: 20px 0;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- SAMPLE DATA ---
if 'plan_data' not in st.session_state:
    st.session_state.plan_data = [
        {"Time": "9:00", "Doctor": "Dr. Mehta", "Objective": "Get 5 Rx", "Brand": "A", "Status": "Planned"},
        {"Time": "10:30", "Doctor": "Dr. Verma", "Objective": "Product Demo", "Brand": "B", "Status": "Planned"},
        {"Time": "12:00", "Doctor": "Dr. Joshi", "Objective": "Follow-up", "Brand": "A", "Status": "Planned"}
    ]

if 'execution_data' not in st.session_state:
    st.session_state.execution_data = [
        {"Time": "9:25", "Doctor": "Dr. Mehta", "Outcome": "3 Rx", "Notes": "Price concern", "Status": "Partial"},
        {"Time": "11:00", "Doctor": "Dr. Verma", "Outcome": "Canceled", "Notes": "Emergency", "Status": "Failed"},
        {"Time": "12:15", "Doctor": "Dr. Joshi", "Outcome": "2 Rx", "Notes": "Will order more", "Status": "Success"}
    ]

# --- HELPER FUNCTIONS ---
def get_status_badge(status):
    if status == "Success":
        return f'<span class="status-success">✓ {status}</span>'
    elif status == "Partial":
        return f'<span class="status-warning">⚠ {status}</span>'
    else:
        return f'<span class="status-danger">✗ {status}</span>'

# --- MAIN APP LAYOUT ---
st.title("FieldForce Optimizer")
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# SECTION 1: TODAY'S PLAN
with st.container():
    st.header("📅 Today's Plan")
    
    # Plan editor
    with st.expander("Edit Daily Plan", expanded=True):
        edited_plan = st.data_editor(
            pd.DataFrame(st.session_state.plan_data),
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Planned", "In Progress", "Completed"]
                )
            },
            use_container_width=True,
            height=250
        )
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="custom-card">📌 <b>Total Visits</b><br>3 Planned</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="custom-card">⏱️ <b>Travel Time</b><br>2.5 Hours</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="custom-card">🎯 <b>Target Rx</b><br>12 Expected</div>', unsafe_allow_html=True)

# SECTION 2: EXECUTION TRACKING
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
with st.container():
    st.header("📝 Execution Tracking")
    
    # Status legend
    st.markdown("""
    <div style="display: flex; gap: 15px; margin-bottom: 15px;">
        <span class="status-success">✓ Success</span>
        <span class="status-warning">⚠ Partial</span>
        <span class="status-danger">✗ Failed</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Execution data with status badges
    exec_df = pd.DataFrame(st.session_state.execution_data)
    exec_df["Status"] = exec_df["Status"].apply(get_status_badge)
    st.write(exec_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# SECTION 3: INSIGHTS & REPLANNING
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🔍 Insights")
        st.error("🚨 Dr. Verma: 3 cancellations this month")
        st.warning("⚠️ Brand A: Price objections up 20%")
        st.success("✅ Dr. Joshi: 75% conversion rate")
        
        # Simple trend visualization
        trend_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu"],
            "Rx": [12, 15, 8, 14]
        }).set_index("Day")
        st.bar_chart(trend_data)
    
    with col2:
        st.header("🔄 Replanning")
        st.markdown('<div class="custom-card">'
                   '🔹 <b>High Priority</b>: Reschedule Dr. Verma<br>'
                   '🔹 <b>Medium Priority</b>: Visit Chemist Ratan<br>'
                   '🔹 <b>Low Priority</b>: Follow-up with Dr. Mehta'
                   '</div>', unsafe_allow_html=True)
        
        if st.button("Generate Tomorrow's Plan", type="primary"):
            st.success("New plan generated successfully!")
            st.session_state.plan_data = [
                {"Time": "8:30", "Doctor": "Chemist Ratan", "Objective": "Stock check", "Brand": "B", "Status": "Planned"},
                {"Time": "9:30", "Doctor": "Dr. Mehta", "Objective": "Price discussion", "Brand": "A", "Status": "Planned"},
                {"Time": "11:00", "Doctor": "Dr. Verma", "Objective": "Rescheduled visit", "Brand": "B", "Status": "Planned"}
            ]

# FOOTER
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.caption("© 2024 FieldForce Optimizer | v1.0")