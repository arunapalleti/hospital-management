import streamlit as st
import datetime
import pandas as pd
from utils.auth import check_auth
from utils.database import load_data
from utils.styles import inject_custom_css, render_metric_card
from utils.helper import render_header, render_badge

# Protect page access
check_auth()

# Inject styling
inject_custom_css()

# Render header
render_header("Dashboard")

# Load databases
patients = load_data("patients")
doctors = load_data("doctors")
tablets = load_data("tablets")
recommendations = load_data("recommendations")
history = load_data("history")

# Prepare statistics
total_patients = len(patients)
total_doctors = len(doctors)

# Calculate Today's patients
today_str = datetime.date.today().isoformat()
todays_patients = sum(1 for p in patients if p.get("date") == today_str)

# Calculate tablets count and alerts
total_tablets = len(tablets)
low_stock_count = sum(1 for t in tablets if int(t.get("stock", 0)) < 20)

# Calculate history issues
tablets_issued = len(history)
total_rules = len(recommendations)

# Expiry warning check (expiry date within 30 days)
expiring_soon_count = 0
today = datetime.date.today()
for t in tablets:
    try:
        exp_date = datetime.datetime.strptime(t.get("expiry_date", ""), "%Y-%m-%d").date()
        if (exp_date - today).days <= 30 and (exp_date - today).days >= 0:
            expiring_soon_count += 1
    except:
        pass

# Global Search System
search_query = st.text_input("🔍 Global Search (Search across Patients, Doctors, Tablets, and History)", placeholder="Type a name, specialization, disease, or tablet ID...", key="global_search")

if search_query:
    q = search_query.lower().strip()
    st.markdown(f"### Search Results for: *\"{search_query}\"*")
    
    found_any = False
    
    # 1. Search Patients
    matching_patients = []
    for p in patients:
        if q in p.get("name", "").lower() or q in p.get("disease", "").lower() or q in p.get("id", "").lower():
            matching_patients.append(p)
    if matching_patients:
        found_any = True
        st.markdown("#### 👤 Patients Matched")
        df_p = pd.DataFrame(matching_patients)
        st.dataframe(df_p[["id", "name", "age", "gender", "disease", "doctor_assigned", "date"]], use_container_width=True)
        
    # 2. Search Doctors
    matching_doctors = []
    for d in doctors:
        if q in d.get("name", "").lower() or q in d.get("specialization", "").lower() or q in d.get("id", "").lower():
            matching_doctors.append(d)
    if matching_doctors:
        found_any = True
        st.markdown("#### 👨‍⚕️ Doctors Matched")
        df_d = pd.DataFrame(matching_doctors)
        st.dataframe(df_d[["id", "name", "specialization", "consultation_time", "status", "email"]], use_container_width=True)

    # 3. Search Tablets
    matching_tablets = []
    for t in tablets:
        if q in t.get("name", "").lower() or q in t.get("category", "").lower() or q in t.get("id", "").lower() or q in t.get("uses", "").lower():
            matching_tablets.append(t)
    if matching_tablets:
        found_any = True
        st.markdown("#### 💊 Tablets Matched")
        df_t = pd.DataFrame(matching_tablets)
        st.dataframe(df_t[["id", "name", "category", "strength", "stock", "expiry_date", "price"]], use_container_width=True)

    # 4. Search History
    matching_history = []
    for h in history:
        if q in h.get("patient_name", "").lower() or q in h.get("recommended_tablet", "").lower() or q in h.get("disease", "").lower() or q in h.get("doctor", "").lower():
            matching_history.append(h)
    if matching_history:
        found_any = True
        st.markdown("#### 📜 Issuance Logs Matched")
        df_h = pd.DataFrame(matching_history)
        st.dataframe(df_h[["patient_id", "patient_name", "recommended_tablet", "dosage", "doctor", "date", "status"]], use_container_width=True)
        
    if not found_any:
        st.info("No matching records found in patients, doctors, tablets, or logs database.")
        
else:
    # Render Dashboard Panel
    
    # 1. Image Banner
    col_banner_img, col_banner_text = st.columns([1, 2])
    with col_banner_img:
        st.image("assets/hospital.png", use_container_width=True)
    with col_banner_text:
        st.markdown(f"""
            <div style="padding-top: 10px;">
                <h1 style="color: var(--accent-color); font-weight: 800; margin-bottom: 8px;">Smart Healthcare Operations</h1>
                <p style="color: var(--text-muted); font-size: 16px; line-height: 1.6;">
                    Welcome back to the Medical Console. Streamline operations by viewing stats, issuing prescriptions, matching symptoms, and monitoring pharmacy stocks in real-time.
                </p>
                <div style="display: flex; gap: 12px; margin-top: 16px;">
                    <a href="/?page=Patients" target="_self" style="text-decoration: none;">
                        <span class="status-badge badge-success" style="padding: 8px 16px; cursor: pointer; border-radius: 8px;">Manage Patients</span>
                    </a>
                    <a href="/?page=Recommendations" target="_self" style="text-decoration: none;">
                        <span class="status-badge" style="padding: 8px 16px; cursor: pointer; border-radius: 8px; background: var(--accent-color); color: white;">Diagnostics Matcher</span>
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")

    # 2. Metric Grid (6 cards)
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col4, m_col5, m_col6 = st.columns(3)
    
    with m_col1:
        render_metric_card("Total Patients", f"{total_patients} registered", "👤", "Total patients in hospital database")
    with m_col2:
        render_metric_card("Active Doctors", f"{total_doctors} specialists", "👨‍⚕️", "Active specialist profiles")
    with m_col3:
        render_metric_card("Today's Patients", f"{todays_patients} new today", "📅", "Patients registered today")
    with m_col4:
        render_metric_card("Tablets Issued", f"{tablets_issued} issued logs", "💊", "Total prescriptions completed")
    with m_col5:
        render_metric_card("Recommendations", f"{total_rules} rules loaded", "🩺", "Symptom matching configurations")
    with m_col6:
        # Alert warning on card color if critical items exist
        alert_text = f"{low_stock_count} low / {expiring_soon_count} exp"
        render_metric_card("Inventory Warnings", alert_text, "⚠️", "Medicines with stock < 20 or expiring within 30 days")
        
    st.markdown("---")

    # 3. Two Column Details Layout
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        st.markdown("### 📜 Recent Activities")
        
        # Merge logs of patients and history records to make a unified activity log
        activities = []
        for p in patients:
            activities.append({
                "time": p.get("date", ""),
                "icon": "👤",
                "message": f"New Patient **{p.get('name')}** admitted for **{p.get('disease')}** (Assigned to {p.get('doctor_assigned')})"
            })
        for h in history:
            activities.append({
                "time": f"{h.get('date')} {h.get('time', '')}",
                "icon": "💊",
                "message": f"Issued **{h.get('recommended_tablet')}** to Patient **{h.get('patient_name')}** ({h.get('status')})"
            })
            
        # Sort activities by datetime
        activities = sorted(activities, key=lambda x: x["time"], reverse=True)[:5]
        
        if not activities:
            st.info("No activities recorded yet.")
        else:
            for act in activities:
                st.markdown(f"""
                <div class="glass-card" style="padding: 12px 18px !important; margin-bottom: 10px !important;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 18px; margin-right: 12px;">{act['icon']}</span>
                        <div style="flex-grow: 1; font-size: 14px;">{act['message']}</div>
                        <div style="font-size: 12px; color: var(--text-muted); min-width: 100px; text-align: right;">{act['time']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with right_col:
        st.markdown("### ⚠️ Clinical Alert Center")
        
        # Check alerts
        has_alerts = False
        
        # Expiry Alerts
        expiring_items = []
        for t in tablets:
            try:
                exp_date = datetime.datetime.strptime(t.get("expiry_date", ""), "%Y-%m-%d").date()
                days_left = (exp_date - today).days
                if days_left <= 30 and days_left >= 0:
                    expiring_items.append(f"**{t.get('name')}** (Expiring in {days_left} days on {t.get('expiry_date')})")
            except:
                pass
                
        if expiring_items:
            has_alerts = True
            for alert in expiring_items:
                st.warning(f"⏰ **Expiry Alert**: {alert}")
                
        # Low Stock Alerts
        low_stock_items = [t for t in tablets if int(t.get("stock", 0)) < 20]
        if low_stock_items:
            has_alerts = True
            for item in low_stock_items:
                st.error(f"📦 **Low Stock**: **{item.get('name')}** is running low ({item.get('stock')} remaining)")
                
        if not has_alerts:
            st.success("✅ All system checks nominal. No inventory alerts or expiry issues reported.")
