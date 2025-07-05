import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- SETUP ---
st.set_page_config(layout="wide", page_title="SFE Daily Cycle")
st.title("🔄 SFE Daily Control Tower")
st.caption("Plan → Execute → Learn → Replan")

# --- INITIALIZE DATA ---
if 'execution' not in st.session_state:
    # Sample data structure
    st.session_state.plan = {
        "9:00 AM": {"Doctor": "Dr. Mehta", "Objective": "5 Rx Brand A", "Status": "Planned"},
        "10:30 AM": {"Doctor": "Dr. Verma", "Objective": "New Product Sampling", "Status": "Planned"},
        "12:00 PM": {"Doctor": "Dr. Joshi", "Objective": "3 Rx Brand B", "Status": "Planned"},
        "2:00 PM": {"Doctor": "Sai Pharma", "Objective": "Stock Replenishment", "Status": "Planned"}
    }
    
    st.session_state.execution = {}
    st.session_state.insights = []
    st.session_state.replan = {}

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Controls")
    rep = st.selectbox("Medical Rep", ["MR Ravi", "MR Priya", "MR Ajay"])
    territory = st.selectbox("Territory", ["North 2", "West 1", "South 3"])
    
    if st.button("🔄 Simulate Day Completion"):
        # Simulate execution data
        st.session_state.execution = {
            "Dr. Mehta": {"Actual Time": "9:20 AM", "Outcome": "2 Rx", "Notes": "Price objection"},
            "Dr. Verma": {"Actual Time": "10:30 AM", "Outcome": "Canceled", "Notes": "Emergency OPD"},
            "Dr. Joshi": {"Actual Time": "12:15 PM", "Outcome": "2 Rx", "Notes": "Will prescribe more next week"},
            "Sai Pharma": {"Actual Time": "2:30 PM", "Outcome": "Order placed", "Notes": "Brand A x200 units"},
            "Chemist Ratan": {"Actual Time": "3:00 PM", "Outcome": "Stock-out", "Notes": "Brand B unavailable"}
        }
        
        # Generate insights
        st.session_state.insights = [
            "🚨 Price objections increased 20% in North 2",
            "⚠️ Dr. Verma has canceled 3 visits this month",
            "📈 Dr. Joshi shows high Rx potential (follow-up recommended)"
        ]
        
        # Generate replan
        st.session_state.replan = {
            "8:30 AM": {"Task": "Chemist Ratan", "Priority": "Critical", "Reason": "Brand B stock-out"},
            "9:30 AM": {"Task": "Dr. Mehta", "Priority": "High", "Reason": "Price objection handling"},
            "11:00 AM": {"Task": "Dr. Joshi", "Priority": "High", "Reason": "Rx reinforcement"},
            "3:00 PM": {"Task": "Dr. Verma", "Priority": "Medium", "Reason": "Reschedule attempt"}
        }
        st.success("Day simulation complete!")

# --- DASHBOARD LAYOUT ---
tab1, tab2, tab3, tab4 = st.tabs(["📅 Today's Plan", "📝 Execution", "🔍 Insights", "🔄 Tomorrow's Plan"])

# TAB 1: TODAY'S PLAN
with tab1:
    st.subheader(f"Morning Plan for {datetime.today().strftime('%d %b %Y')}")
    plan_df = pd.DataFrame.from_dict(st.session_state.plan, orient="index")
    st.dataframe(plan_df, use_container_width=True, height=300)
    
    # Plan completion stats
    if st.session_state.execution:
        completed = len([v for v in st.session_state.execution.values() if v["Outcome"] not in ["Canceled", "Missed"]])
        completion_rate = int((completed / len(st.session_state.plan)) * 100)
        st.metric("Plan Completion Rate", f"{completion_rate}%")

# TAB 2: EXECUTION
with tab2:
    if st.session_state.execution:
        st.subheader("Actual Visit Outcomes")
        exec_df = pd.DataFrame.from_dict(st.session_state.execution, orient="index")
        st.dataframe(exec_df, use_container_width=True, height=300)
        
        # Execution metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Visits", len(st.session_state.execution))
        col2.metric("Successful Visits", len([v for v in st.session_state.execution.values() if "Rx" in v["Outcome"]]))
        col3.metric("Cancellations", len([v for v in st.session_state.execution.values() if v["Outcome"] == "Canceled"]))
    else:
        st.info("No execution data yet. Simulate day completion from sidebar.")

# TAB 3: INSIGHTS
with tab3:
    if st.session_state.insights:
        st.subheader("Key Learnings from Today")
        
        # Insights cards
        for insight in st.session_state.insights:
            if "🚨" in insight:
                st.error(insight)
            elif "⚠️" in insight:
                st.warning(insight)
            else:
                st.success(insight)
        
        # Trend visualization
        st.subheader("Performance Trends")
        trend_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "Rx Target": [18, 22, 15, 20, 25],
            "Actual Rx": [15, 20, 12, 18, 22]
        })
        st.line_chart(trend_data.set_index("Day"))
    else:
        st.info("Complete a day's execution to generate insights")

# TAB 4: TOMORROW'S PLAN
with tab4:
    if st.session_state.replan:
        st.subheader("AI-Generated Plan for Tomorrow")
        replan_df = pd.DataFrame.from_dict(st.session_state.replan, orient="index")
        st.dataframe(replan_df, use_container_width=True, height=300)
        
        # Priority distribution
        priorities = pd.DataFrame({
            "Priority": ["Critical", "High", "Medium", "Low"],
            "Count": [1, 2, 1, 0]  # These would be calculated in real usage
        })
        st.bar_chart(priorities.set_index("Priority"))
        
        if st.button("✅ Approve Tomorrow's Plan"):
            st.session_state.plan = {
                time: {"Doctor": task["Task"], "Objective": task["Reason"], "Status": "Planned"}
                for time, task in st.session_state.replan.items()
            }
            st.success("Plan approved! Ready for tomorrow.")
    else:
        st.info("Complete today's execution to generate tomorrow's plan")

# --- FOOTER ---
st.divider()
st.caption("InField AI v1.0 | Real-time SFE Optimization")