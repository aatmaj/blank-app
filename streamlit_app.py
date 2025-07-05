import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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
    }
    .divider-line {
        border-top: 2px solid #6e48aa;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'exec_data' not in st.session_state:
    # Sample dataset
    st.session_state.exec_data = {
        "plan": [
            {"Time": "9:00", "Doctor": "Dr. Mehta", "Objective": "Get 5 Rx", "Brand": "A", "Status": "Planned"},
            {"Time": "10:30", "Doctor": "Dr. Verma", "Objective": "Product Demo", "Brand": "B", "Status": "Planned"},
            {"Time": "12:00", "Doctor": "Dr. Joshi", "Objective": "Follow-up", "Brand": "A", "Status": "Planned"}
        ],
        "actual": [
            {"Time": "9:25", "Doctor": "Dr. Mehta", "Outcome": "3 Rx", "Notes": "Price concern", "Status": "Partial"},
            {"Time": "11:00", "Doctor": "Dr. Verma", "Outcome": "Canceled", "Notes": "Emergency", "Status": "Failed"},
            {"Time": "12:15", "Doctor": "Dr. Joshi", "Outcome": "2 Rx", "Notes": "Will order more", "Status": "Success"}
        ]
    }

# --- HEADER ---
st.title("FieldForce Optimizer Pro")
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

# --- SECTION 1: TODAY'S PLAN ---
with st.container():
    st.header("📅 Today's Battle Plan")
    
    # Interactive plan editor
    with st.expander("✏️ Edit Plan", expanded=True):
        edited_plan = st.data_editor(
            pd.DataFrame(st.session_state.exec_data["plan"]),
            column_config={
                "Time": st.column_config.TimeColumn("Time"),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Planned", "In Progress", "Completed"]
                )
            },
            use_container_width=True,
            height=250
        )
    
    # Plan metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card">📌 <b>Total Visits</b><br>3 Planned</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card">⏱️ <b>Travel Time</b><br>2.5 Hours</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card">🎯 <b>Target Potential</b><br>12 Rx</div>', unsafe_allow_html=True)

# --- SECTION 2: EXECUTION TRACKER ---
with st.container():
    st.header("📝 Live Execution")
    
    # Real-time updates
    tab1, tab2 = st.tabs(["Visits", "Map View"])
    
    with tab1:
        exec_df = pd.DataFrame(st.session_state.exec_data["actual"])
        st.dataframe(
            exec_df.style.applymap(
                lambda x: "background-color: #ffcccc" if x == "Failed" else (
                    "#ccffcc" if x == "Success" else "#ffffcc"),
                subset=["Status"]
            ),
            use_container_width=True,
            height=300
        )
    
    with tab2:
        # Interactive map
        map_df = pd.DataFrame({
            "lat": [19.0760, 19.2183, 18.9667],
            "lon": [72.8777, 72.9781, 72.8333],
            "size": [10, 5, 8],
            "status": ["Partial", "Failed", "Success"]
        })
        fig = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            size="size",
            color="status",
            zoom=10
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)

# --- SECTION 3: INTELLIGENT INSIGHTS ---
with st.container():
    st.header("🔍 AI-Powered Insights")
    
    # Dynamic insights
    insight_cols = st.columns(2)
    
    with insight_cols[0]:
        st.subheader("Performance Alerts")
        st.error("🚨 Dr. Verma: 3 cancellations this month")
        st.warning("⚠️ Brand A: Price objections up 20%")
        st.success("✅ Dr. Joshi: Conversion rate 75%")
    
    with insight_cols[1]:
        st.subheader("Trend Analysis")
        trend_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu"],
            "Rx": [12, 15, 8, 14],
            "Visits": [5, 6, 4, 7]
        })
        st.line_chart(trend_data.set_index("Day"))

# --- SECTION 4: TOMORROW'S PLAN ---
with st.container():
    st.header("🔄 Smart Replanning")
    
    # AI recommendations
    rec_cols = st.columns([2, 1])
    
    with rec_cols[0]:
        st.subheader("AI Recommendations")
        rec_df = pd.DataFrame({
            "Priority": ["High", "Medium", "Low"],
            "Action": [
                "Reschedule Dr. Verma with samples",
                "Morning visit to Chemist Ratan",
                "Follow-up with Dr. Mehta's clinic staff"
            ]
        })
        st.dataframe(rec_df, use_container_width=True)
    
    with rec_cols[1]:
        st.subheader("Quick Actions")
        st.button("📅 Sync with Calendar")
        st.button("📱 Notify Team")
        st.button("📊 Generate Report")

# --- FOOTER ---
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.caption("© 2024 FieldForce Optimizer Pro | v2.1")