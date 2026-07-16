import streamlit as st
import pandas as pd
from utils.auth import check_auth
from utils.database import load_data, save_data
from utils.styles import inject_custom_css
from utils.helper import render_header, render_badge

# Protect access
check_auth()

# Inject styling
inject_custom_css()

# Header
render_header("Issuance History")

# Load history database
history = load_data("history")

# Tabs
tab_log, tab_manage = st.tabs([
    "📜 History Logs",
    "⚙️ Database Cleansing"
])

# ================= TAB 1: HISTORY LOGS =================
with tab_log:
    st.markdown("### 📜 Medication Issuance Logbook")
    
    if not history:
        st.info("No tablet issuance logs found in the database. Transactions will appear here once recommendations are dispensed.")
    else:
        # Search & Filter
        col_sch, col_stat, col_dt = st.columns([2, 1, 1])
        with col_sch:
            h_search = st.text_input("Search logs by Patient Name, Doctor, Medicine, or Disease", placeholder="Search...", key="h_search")
        with col_stat:
            statuses = list(set([h.get("status") for h in history if h.get("status")]))
            status_filter = st.selectbox("Filter Status", ["All Statuses"] + statuses)
        with col_dt:
            # Gather unique dates
            dates = sorted(list(set([h.get("date") for h in history if h.get("date")])), reverse=True)
            date_filter = st.selectbox("Filter Date", ["All Dates"] + dates)
            
        # Apply filters
        filtered_history = history.copy()
        
        if h_search:
            hs = h_search.lower()
            filtered_history = [
                h for h in filtered_history
                if hs in h.get("patient_name", "").lower() or hs in h.get("doctor", "").lower() or hs in h.get("recommended_tablet", "").lower() or hs in h.get("disease", "").lower()
            ]
            
        if status_filter != "All Statuses":
            filtered_history = [h for h in filtered_history if h.get("status") == status_filter]
            
        if date_filter != "All Dates":
            filtered_history = [h for h in filtered_history if h.get("date") == date_filter]
            
        if not filtered_history:
            st.info("No issuance logs matched the search filters.")
        else:
            # Convert to Pandas
            df_hist = pd.DataFrame(filtered_history)
            
            # Format display
            df_display = df_hist[["patient_id", "patient_name", "doctor", "disease", "recommended_tablet", "date", "time", "status"]]
            df_display.columns = ["Patient ID", "Patient Name", "Prescribing Doctor", "Disease Treated", "Medicines Issued", "Date", "Time", "Status"]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Download CSV
            st.markdown("<br>", unsafe_allow_html=True)
            csv_data = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Prescription Logs to CSV",
                data=csv_data,
                file_name=f"prescription_history_{datetime.date.today().isoformat()}.csv",
                mime="text/csv"
            )
            
            # Record detail inspector
            st.markdown("#### 🔎 Inspect Log Record Details")
            inspect_options = []
            for idx, h in enumerate(filtered_history):
                inspect_options.append((idx, f"{h.get('date')} {h.get('time')} - {h.get('patient_name')} ({h.get('recommended_tablet')})"))
                
            selected_idx = st.selectbox(
                "Choose transaction log to inspect",
                options=[opt[0] for opt in inspect_options],
                format_func=lambda x: next((opt[1] for opt in inspect_options if opt[0] == x), "")
            )
            
            if selected_idx is not None:
                record = filtered_history[selected_idx]
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color: var(--accent-color); margin-top:0;">📜 Issuance File: #{selected_idx + 1}</h4>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight:600; width:25%;">Patient Name (ID):</td>
                            <td style="padding: 8px;">{record.get('patient_name')} ({record.get('patient_id')})</td>
                            <td style="padding: 8px; font-weight:600; width:25%;">Attending Doctor:</td>
                            <td style="padding: 8px;">{record.get('doctor')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight:600;">Diagnosis:</td>
                            <td style="padding: 8px;">{record.get('disease')}</td>
                            <td style="padding: 8px; font-weight:600;">Transaction Stamp:</td>
                            <td style="padding: 8px;">{record.get('date')} at {record.get('time')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight:600;">Issued Tablets:</td>
                            <td colspan="3" style="padding: 8px; font-weight:bold; color:var(--accent-color);">{record.get('recommended_tablet')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight:600;">Dosage Protocol:</td>
                            <td colspan="3" style="padding: 8px;">{record.get('dosage')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight:600;">Dispensation Status:</td>
                            <td colspan="3" style="padding: 8px;">{render_badge(record.get('status'))}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)


# ================= TAB 2: DATABASE CLEANSING =================
with tab_manage:
    st.markdown("### ⚙️ Database Cleansing & Maintenance")
    
    is_admin = st.session_state.get("role") == "Admin"
    
    if not is_admin:
        st.warning("🔒 Administrative clearance required. Cleanse operations are locked for clinical provider accounts.")
    elif not history:
        st.info("No records available to cleanse.")
    else:
        # Action 1: Delete individual entry
        st.markdown("#### 🗑️ Delete Single Log Record")
        delete_options = []
        for idx, h in enumerate(history):
            delete_options.append((idx, f"Row #{idx + 1} | {h.get('date')} | Patient: {h.get('patient_name')} | Pill: {h.get('recommended_tablet')}"))
            
        log_to_delete_idx = st.selectbox(
            "Select specific entry to remove permanently",
            options=[opt[0] for opt in delete_options],
            format_func=lambda x: next((opt[1] for opt in delete_options if opt[0] == x), "")
        )
        
        single_delete_btn = st.button("Delete Selected Log Entry", type="primary")
        if single_delete_btn:
            # Remove by index
            record_to_remove = history[log_to_delete_idx]
            history.pop(log_to_delete_idx)
            if save_data("history", history):
                st.success(f"Log entry for patient **{record_to_remove.get('patient_name')}** permanently deleted.")
                st.rerun()
            else:
                st.error("Error updating logs database.")
                
        st.markdown("---")
        
        # Action 2: Wipe Entire History Database
        st.markdown("#### 🚨 Purge Entire Prescription History")
        st.markdown("""
        <div class="glass-card" style="border: 1px solid var(--danger-color) !important;">
            <h5 style="color:var(--danger-color); margin-top:0;">⚠️ CRITICAL OPERATIONS ALERT</h5>
            <p style="font-size:13px; margin:0;">Dispensing the wipe operation deletes ALL records inside <code>history.json</code>. This process is irreversible and cannot be rolled back.</p>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_wipe_check = st.checkbox("I authorize the complete erasure of all medical prescription logs.")
        
        wipe_btn = st.button("Purger Logs Database / Reset History File", type="primary")
        
        if wipe_btn:
            if confirm_wipe_check:
                # Wiping
                if save_data("history", []):
                    st.success("Prescription logs database reset successfully. File is empty.")
                    st.rerun()
                else:
                    st.error("Could not write reset. Check permissions.")
            else:
                st.error("Wipe verification checkbox must be checked to perform this action.")
