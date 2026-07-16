import streamlit as st
import pandas as pd
from utils.auth import check_auth
from utils.database import load_data
from utils.styles import inject_custom_css, render_metric_card
from utils.helper import render_header

# Protect access
check_auth()

# Inject styling
inject_custom_css()

# Header
render_header("Analytical Reports")

# Load databases
patients = load_data("patients")
doctors = load_data("doctors")
tablets = load_data("tablets")
history = load_data("history")

st.markdown("### 📊 Clinical Intelligence & Reports Dashboard")
st.markdown("Generate summaries, plot health analytics, and extract clinical logs as CSV files.")

# Report Category selection
report_cat = st.selectbox(
    "Select Report Analytics Panel",
    ["👤 Patient Registry Reports", "👨‍⚕️ Clinician Roster Reports", "💊 Pharmacy Inventory Reports", "📜 Prescription Activity Reports"]
)

st.markdown("---")

# ================= CATEGORY 1: PATIENTS =================
if report_cat == "👤 Patient Registry Reports":
    st.markdown("### 👤 Patient Registry Analytics")
    
    if not patients:
        st.info("No patient records registered yet. Generate reports after adding patients.")
    else:
        df_p = pd.DataFrame(patients)
        
        # Summary metrics
        total_p = len(df_p)
        avg_age = df_p["age"].mean()
        male_cnt = sum(1 for g in df_p["gender"] if g.lower() == "male")
        female_cnt = sum(1 for g in df_p["gender"] if g.lower() == "female")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Total Patients", f"{total_p} admitted", "👤")
        with c2:
            render_metric_card("Average Age", f"{avg_age:.1f} years", "⏳")
        with c3:
            render_metric_card("Male Patients", f"{male_cnt} patients", "👨")
        with c4:
            render_metric_card("Female Patients", f"{female_cnt} patients", "👩")
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_ch1, col_ch2 = st.columns(2)
        
        with col_ch1:
            st.markdown("#### Patient Distribution by Blood Group")
            # Bar Chart
            blood_counts = df_p["blood_group"].value_counts()
            st.bar_chart(blood_counts)
            
        with col_ch2:
            st.markdown("#### Patient Distribution by Gender")
            gender_counts = df_p["gender"].value_counts()
            st.bar_chart(gender_counts)
            
        st.markdown("#### Age Profile Distribution")
        # Line Chart of age counts
        age_counts = df_p["age"].value_counts().sort_index()
        st.line_chart(age_counts)
        
        st.markdown("---")
        st.markdown("#### 📥 Raw Patient Registry Download")
        st.dataframe(df_p[["id", "name", "age", "gender", "blood_group", "disease", "phone", "date"]], use_container_width=True, hide_index=True)
        
        csv_p = df_p.to_csv(index=False).encode('utf-8')
        st.download_button("Download Raw Patient Directory (CSV)", csv_p, "patients_report.csv", "text/csv")


# ================= CATEGORY 2: DOCTORS =================
elif report_cat == "👨‍⚕️ Clinician Roster Reports":
    st.markdown("### 👨‍⚕️ Clinician Roster Analytics")
    
    if not doctors:
        st.info("No doctor profiles loaded in database.")
    else:
        df_d = pd.DataFrame(doctors)
        
        total_d = len(df_d)
        avg_exp = df_d["experience"].mean()
        active_d = sum(1 for s in df_d["status"] if s.lower() == "available")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric_card("Total Specialists", f"{total_d} clinicians", "👨‍⚕️")
        with c2:
            render_metric_card("Average Experience", f"{avg_exp:.1f} years", "⭐")
        with c3:
            render_metric_card("On Clinic Duty", f"{active_d} active", "🟢")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### Doctor Specializations Breakdown")
        spec_counts = df_d["specialization"].value_counts()
        st.bar_chart(spec_counts)
        
        st.markdown("#### Years of Experience by Doctor")
        exp_df = df_d[["name", "experience"]].set_index("name")
        st.bar_chart(exp_df)
        
        st.markdown("---")
        st.markdown("#### 📥 Raw Specialist Roster Download")
        st.dataframe(df_d[["id", "name", "specialization", "qualification", "experience", "consultation_time", "status"]], use_container_width=True, hide_index=True)
        
        csv_d = df_d.to_csv(index=False).encode('utf-8')
        st.download_button("Download Clinician Roster (CSV)", csv_d, "doctors_roster.csv", "text/csv")


# ================= CATEGORY 3: TABLETS =================
elif report_cat == "💊 Pharmacy Inventory Reports":
    st.markdown("### 💊 Pharmacy Inventory Analytics")
    
    if not tablets:
        st.info("No medicines loaded in inventory database.")
    else:
        df_t = pd.DataFrame(tablets)
        
        total_t = len(df_t)
        total_stock_qty = df_t["stock"].sum()
        avg_price = df_t["price"].mean()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric_card("Total Medicine Formulations", f"{total_t} formulas", "💊")
        with c2:
            render_metric_card("Total Stock Volume", f"{total_stock_qty} tablets", "📦")
        with c3:
            render_metric_card("Average Unit Cost", f"${avg_price:.2f}", "💵")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### Tablet Unit Stock Level by Medicine")
        stock_df = df_t[["name", "stock"]].set_index("name")
        st.bar_chart(stock_df)
        
        st.markdown("#### Unit Price Distribution ($)")
        price_df = df_t[["name", "price"]].set_index("name")
        st.bar_chart(price_df)
        
        st.markdown("---")
        st.markdown("#### 📥 Raw Inventory Catalog Download")
        st.dataframe(df_t[["id", "name", "manufacturer", "category", "strength", "stock", "price", "expiry_date"]], use_container_width=True, hide_index=True)
        
        csv_t = df_t.to_csv(index=False).encode('utf-8')
        st.download_button("Download Pharmacy Catalog (CSV)", csv_t, "pharmacy_catalog.csv", "text/csv")


# ================= CATEGORY 4: HISTORY =================
elif report_cat == "📜 Prescription Activity Reports":
    st.markdown("### 📜 Prescription Issuance Log Analytics")
    
    if not history:
        st.info("No transaction logs in issuance database.")
    else:
        df_h = pd.DataFrame(history)
        
        total_issued = len(df_h)
        unique_patients = df_h["patient_id"].nunique()
        active_docs = df_h["doctor"].nunique()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric_card("Total Pills Dispensed", f"{total_issued} logs", "💊")
        with c2:
            render_metric_card("Unique Patients Served", f"{unique_patients} profiles", "👤")
        with c3:
            render_metric_card("Active Prescribers", f"{active_docs} clinicians", "✍️")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### Prescription Volume Over Time (Timeline)")
        # Count by date
        timeline_counts = df_h["date"].value_counts().sort_index()
        st.line_chart(timeline_counts)
        
        st.markdown("#### Prescriptions Dispensed by Doctor")
        doc_counts = df_h["doctor"].value_counts()
        st.bar_chart(doc_counts)
        
        st.markdown("---")
        st.markdown("#### 📥 Raw Prescription History Logs Download")
        st.dataframe(df_h[["patient_id", "patient_name", "doctor", "disease", "recommended_tablet", "date", "time", "status"]], use_container_width=True, hide_index=True)
        
        csv_h = df_h.to_csv(index=False).encode('utf-8')
        st.download_button("Download Prescription History Logs (CSV)", csv_h, "prescription_history_report.csv", "text/csv")
