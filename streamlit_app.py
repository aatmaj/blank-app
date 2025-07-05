import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- SETUP ---
st.set_page_config(layout="wide")
st.title("🚀 SFE Simulation Dashboard - InField AI")
st.caption("Plan → Execute → Learn → Replan")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Simulation Controls")
    rep_name = st.selectbox("Medical Rep", ["MR Ravi", "MR Priya", "MR Ajay"])
    territory = st.selectbox("Territory", ["North 2", "West 1", "South 3"])
    sim_date = st.date_input("Date", datetime.today())
    sim_speed = st.slider("Simulation Speed", 1, 5, 1)
    
    if st.button("🔁 Inject Disruption"):
        st.session_state.disruption = "Dr. Verma canceled (Emergency)"
    
    st.divider()
    st.download_button("📥 Export Today's Plan", data="csv_data", file_name="sfe_plan.csv")

# --- INITIALIZE SESSION STATE ---
if "plan" not in st.session_state:
    st.session_state.plan = {
        "Dr. Mehta": {"Time": "9:00 AM", "Objective": "5 Rx", "Status": "Planned"},
        "Dr. Verma": {"Time": "10:30 AM", "Objective": "Sampling", "Status": "Planned"},
        "Dr. Joshi": {"Time": "12:00 PM", "Objective": "3 Rx", "Status": "Planned"},
        "Sai Pharma": {"Time": "2:00 PM", "Objective": "Order", "Status": "Planned"}
    }

# --- DASHBOARD LAYOUT ---
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.subheader("📌 Original Plan")
    plan_df = pd.DataFrame.from_dict(st.session_state.plan, orient="index")
    st.dataframe(plan_df, use_container_width=True)

with col2:
    st.subheader("🧾 Execution Reality")
    
    # Simulate execution updates
    reality = {
        "Dr. Mehta": {"Time": "9:20 AM", "Outcome": "2 Rx", "Notes": "Price objection"},
        "Dr. Verma": {"Time": "10:30 AM", "Outcome": "Canceled", "Notes": "Emergency OPD"},
        "Dr. Joshi": {"Time": "12:15 PM", "Outcome": "2 Rx", "Notes": "Stockist referral"},
        "Sai Pharma": {"Time": "2:30 PM", "Outcome": "Order placed", "Notes": "Brand A x200 units"},
        "Chemist Ratan": {"Time": "3:00 PM", "Outcome": "Stock-out", "Notes": "Brand B"}
    }
    
    if "disruption" in st.session_state:
        reality["Dr. Verma"]["Notes"] = st.session_state.disruption
    
    reality_df = pd.DataFrame.from_dict(reality, orient="index")
    st.dataframe(reality_df, use_container_width=True)

with col3:
    st.subheader("🎯 Goal Tracking")
    
    goals = {
        "Metric": ["Brand A Rx", "Brand B Rx", "Visits Completed"],
        "Target": [200, 150, 25],
        "Achieved": [70, 45, 18],
        "% Complete": [35, 30, 72]
    }
    
    st.dataframe(pd.DataFrame(goals), use_container_width=True)
    
    # Progress bars
    for goal in goals["Metric"]:
        idx = goals["Metric"].index(goal)
        st.progress(goals["% Complete"][idx]/100, text=f"{goal}: {goals['Achieved'][idx]}/{goals['Target'][idx]}")

with col4:
    st.subheader("🔮 AI Replan (Tomorrow)")
    
    replan = {
        "8:30 AM": {"Task": "Chemist Ratan", "Priority": "Urgent", "Reason": "Brand B stock-out"},
        "9:30 AM": {"Task": "Dr. Mehta", "Priority": "High", "Reason": "Price objection follow-up"},
        "11:00 AM": {"Task": "Dr. Joshi", "Priority": "Medium", "Reason": "Reinforce Rx"},
        "3:00 PM": {"Task": "Dr. Verma", "Priority": "High", "Reason": "Reschedule attempt"}
    }
    
    replan_df = pd.DataFrame.from_dict(replan, orient="index")
    st.dataframe(replan_df, use_container_width=True)
    
    if st.button("🔄 Generate New Plan"):
        st.success("AI replan completed!")

# --- SIMULATION FOOTER ---
st.divider()
st.write("**Insights & Recommendations**")
st.info("🚨 Price objections increased 20% in North 2 - Trigger objection handling training")
st.warning("⏳ Dr. Verma has missed 3 visits this month - Consider alternate contact method")

# --- HIDDEN DATA EXPORT ---
csv_data = plan_df.to_csv().encode('utf-8')
