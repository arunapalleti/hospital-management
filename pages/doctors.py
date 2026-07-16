import streamlit as st
import pandas as pd
from utils.auth import check_auth
from utils.database import load_data, save_data, insert_record, update_record, delete_record
from utils.styles import inject_custom_css, render_metric_card
from utils.helper import render_header, render_badge
from utils.validation import validate_non_empty, validate_email, validate_phone

# Protect access
check_auth()

# Inject styling
inject_custom_css()

# Header
render_header("Doctor Specialists")

# Load data
doctors = load_data("doctors")

# 13 required Specializations
SPECIALIZATIONS = [
    "General Physician",
    "Cardiologist",
    "Dermatologist",
    "Neurologist",
    "Orthopedic",
    "Pediatrician",
    "ENT",
    "Psychiatrist",
    "Dentist",
    "Gynecologist",
    "Oncologist",
    "Pulmonologist",
    "Nephrologist"
]

DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Admin role check
is_admin = st.session_state.get("role") == "Admin"

# Separate display: directory is public, modifications are admin-only
if is_admin:
    tab_dir, tab_add, tab_edit, tab_delete = st.tabs([
        "📂 Specialists Directory",
        "👨‍⚕️ Register Specialist",
        "✏️ Edit Profile",
        "❌ Remove Specialist"
    ])
else:
    tab_dir, = st.tabs(["📂 Specialists Directory"])

# ================= TAB 1: VIEW & SEARCH DOCTORS =================
with tab_dir:
    st.markdown("### 📂 Specialists Directory")
    
    # Simple Doctor Stats
    total_docs = len(doctors)
    available_docs = sum(1 for d in doctors if d.get("status") == "Available")
    on_leave_docs = total_docs - available_docs
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        render_metric_card("Total Specialists", f"{total_docs} onboard", "👨‍⚕️")
    with sc2:
        render_metric_card("Available Today", f"{available_docs} active", "🟢")
    with sc3:
        render_metric_card("On Leave", f"{on_leave_docs} profiles", "🔴")
        
    st.markdown("---")
    
    # Search and Filter
    col_search, col_spec = st.columns([2, 1])
    with col_search:
        doc_search = st.text_input("Search doctors by Name, Email or ID", placeholder="Search...", key="d_search")
    with col_spec:
        spec_filter = st.selectbox("Filter by Specialization", ["All Specializations"] + SPECIALIZATIONS, key="d_filter_spec")

    # Apply filters
    filtered_docs = doctors.copy()
    if doc_search:
        ds = doc_search.lower()
        filtered_docs = [
            d for d in filtered_docs 
            if ds in d.get("name", "").lower() or ds in d.get("email", "").lower() or ds in d.get("id", "").lower()
        ]
    if spec_filter != "All Specializations":
        filtered_docs = [d for d in filtered_docs if d.get("specialization") == spec_filter]

    # Display doctor profiles
    if not filtered_docs:
        st.info("No doctor specialists found matching the criteria.")
    else:
        # Render a grid of profile cards
        # 2 cards per row
        for i in range(0, len(filtered_docs), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(filtered_docs):
                    doc = filtered_docs[i + j]
                    
                    days_str = ", ".join(doc.get("available_days", []))
                    status_badge_html = render_badge(doc.get("status", "Available"))
                    
                    cols[j].markdown(f"""
                    <div class="glass-card" style="margin-bottom: 15px !important;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                            <div>
                                <h4 style="color: var(--accent-color); margin: 0; font-size:18px;">{doc.get('name')}</h4>
                                <span style="font-size:12px; color: var(--text-muted); font-weight: 500;">ID: {doc.get('id')}</span>
                            </div>
                            {status_badge_html}
                        </div>
                        <p style="margin: 4px 0; font-size:14px;"><strong>Specialty:</strong> {doc.get('specialization')}</p>
                        <p style="margin: 4px 0; font-size:14px;"><strong>Qualification:</strong> {doc.get('qualification')}</p>
                        <p style="margin: 4px 0; font-size:14px;"><strong>Experience:</strong> {doc.get('experience')} Years</p>
                        <hr style="border: 0; border-top: 1px solid var(--card-border); margin: 10px 0;">
                        <p style="margin: 4px 0; font-size:13px; color: var(--text-muted);">🗓 <strong>Availability:</strong> {days_str}</p>
                        <p style="margin: 4px 0; font-size:13px; color: var(--text-muted);">🕒 <strong>Hours:</strong> {doc.get('consultation_time')}</p>
                        <hr style="border: 0; border-top: 1px solid var(--card-border); margin: 10px 0;">
                        <p style="margin: 4px 0; font-size:13px;">📞 {doc.get('phone')} | 📧 {doc.get('email')}</p>
                    </div>
                    """, unsafe_allow_html=True)


# ================= ADM-ONLY TABS =================
if is_admin:
    # ================= TAB 2: ADD DOCTOR =================
    with tab_add:
        st.markdown("### 👨‍⚕️ Register Doctor Profile")
        
        with st.form("add_doctor_form"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                doc_id = st.text_input("Doctor ID (Custom unique code)", placeholder="e.g., DOC-105")
                doc_name = st.text_input("Doctor Full Name", placeholder="e.g., Dr. Alice Brown")
                specialization = st.selectbox("Specialization Area", SPECIALIZATIONS)
                qualification = st.text_input("Qualifications", placeholder="e.g., MBBS, MD (Cardiology)")
                experience = st.slider("Years of Experience", min_value=1, max_value=50, value=5)
            with col_a2:
                available_days = st.multiselect("Available Clinic Days", DAYS_OF_WEEK, default=["Mon", "Wed", "Fri"])
                consultation_time = st.text_input("Consultation Hours", placeholder="e.g., 09:00 - 12:00")
                phone = st.text_input("Contact Phone", placeholder="e.g., +15550201")
                email = st.text_input("Email Address", placeholder="e.g., alice.brown@hospital.com")
                status = st.selectbox("Initial Availability Status", ["Available", "On Leave"])
                
            submit_btn = st.form_submit_button("Register Specialist Profile")
            
            if submit_btn:
                # Validations
                id_ok, id_msg = validate_non_empty(doc_id, "Doctor ID")
                n_ok, n_msg = validate_non_empty(doc_name, "Doctor Name")
                q_ok, q_msg = validate_non_empty(qualification, "Qualification")
                time_ok, time_msg = validate_non_empty(consultation_time, "Consultation Time")
                p_ok, p_msg = validate_phone(phone)
                e_ok, e_msg = validate_email(email)
                
                # Check duplicate ID
                id_exists = any(d.get("id").upper() == doc_id.upper() for d in doctors)
                
                if not id_ok:
                    st.error(id_msg)
                elif id_exists:
                    st.error(f"Doctor ID '{doc_id}' is already registered. Please choose a unique ID.")
                elif not n_ok:
                    st.error(n_msg)
                elif not q_ok:
                    st.error(q_msg)
                elif not time_ok:
                    st.error(time_msg)
                elif not p_ok:
                    st.error(p_msg)
                elif not e_ok:
                    st.error(e_msg)
                else:
                    new_doc = {
                        "id": doc_id.strip().upper(),
                        "name": doc_name.strip(),
                        "specialization": specialization,
                        "qualification": qualification.strip(),
                        "experience": int(experience),
                        "available_days": available_days,
                        "consultation_time": consultation_time.strip(),
                        "phone": phone.strip(),
                        "email": email.strip(),
                        "status": status
                    }
                    
                    insert_record("doctors", new_doc)
                    st.success(f"Profile for {doc_name} successfully registered under ID: **{doc_id}**!")
                    st.rerun()

    # ================= TAB 3: EDIT DOCTOR =================
    with tab_edit:
        st.markdown("### ✏️ Edit Doctor Profile")
        
        if not doctors:
            st.info("No doctor profiles available to edit.")
        else:
            edit_id = st.selectbox(
                "Select Specialist to Edit",
                options=[d.get("id") for d in doctors],
                format_func=lambda x: f"{x} - {next((d.get('name') for d in doctors if d.get('id') == x), '')}",
                key="d_edit_selectbox"
            )
            
            doc_to_edit = next((d for d in doctors if d.get("id") == edit_id), None)
            
            if doc_to_edit:
                with st.form("edit_doctor_form"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        e_name = st.text_input("Doctor Full Name", value=doc_to_edit.get("name"))
                        e_spec = st.selectbox("Specialization Area", SPECIALIZATIONS, index=SPECIALIZATIONS.index(doc_to_edit.get("specialization")))
                        e_qual = st.text_input("Qualifications", value=doc_to_edit.get("qualification"))
                        e_exp = st.slider("Years of Experience", min_value=1, max_value=50, value=int(doc_to_edit.get("experience")))
                    with col_e2:
                        e_days = st.multiselect("Available Clinic Days", DAYS_OF_WEEK, default=doc_to_edit.get("available_days", []))
                        e_time = st.text_input("Consultation Hours", value=doc_to_edit.get("consultation_time"))
                        e_phone = st.text_input("Contact Phone", value=doc_to_edit.get("phone"))
                        e_email = st.text_input("Email Address", value=doc_to_edit.get("email"))
                        e_status = st.selectbox("Availability Status", ["Available", "On Leave"], index=["Available", "On Leave"].index(doc_to_edit.get("status")))
                        
                    edit_btn = st.form_submit_button("Update Specialist Profile")
                    
                    if edit_btn:
                        n_ok, n_msg = validate_non_empty(e_name, "Doctor Name")
                        q_ok, q_msg = validate_non_empty(e_qual, "Qualification")
                        time_ok, time_msg = validate_non_empty(e_time, "Consultation Time")
                        p_ok, p_msg = validate_phone(e_phone)
                        e_ok, e_msg = validate_email(e_email)
                        
                        if not n_ok:
                            st.error(n_msg)
                        elif not q_ok:
                            st.error(q_msg)
                        elif not time_ok:
                            st.error(time_msg)
                        elif not p_ok:
                            st.error(p_msg)
                        elif not e_ok:
                            st.error(e_msg)
                        else:
                            updated_fields = {
                                "name": e_name.strip(),
                                "specialization": e_spec,
                                "qualification": e_qual.strip(),
                                "experience": int(e_exp),
                                "available_days": e_days,
                                "consultation_time": e_time.strip(),
                                "phone": e_phone.strip(),
                                "email": e_email.strip(),
                                "status": e_status
                            }
                            
                            success = update_record("doctors", edit_id, updated_fields, key_name="id")
                            if success:
                                st.success(f"Profile for {e_name} [ID: {edit_id}] updated successfully!")
                                st.rerun()
                            else:
                                st.error("Error updating doctor profile.")

    # ================= TAB 4: DELETE DOCTOR =================
    with tab_delete:
        st.markdown("### ❌ De-register Doctor Profile")
        
        if not doctors:
            st.info("No doctor profiles in directory.")
        else:
            delete_id = st.selectbox(
                "Select Profile to Delete",
                options=[d.get("id") for d in doctors],
                format_func=lambda x: f"{x} - {next((d.get('name') for d in doctors if d.get('id') == x), '')}",
                key="d_delete_selectbox"
            )
            
            doc_to_delete = next((d for d in doctors if d.get("id") == delete_id), None)
            
            if doc_to_delete:
                st.markdown(f"""
                <div class="glass-card" style="border: 1px solid var(--danger-color) !important;">
                    <h4 style="color: var(--danger-color); margin-top:0;">⚠️ Profile De-registration Warning</h4>
                    <p>Are you sure you want to permanently delete the clinical profile for <strong>{doc_to_delete.get('name')}</strong> (ID: {doc_to_delete.get('id')})?</p>
                </div>
                """, unsafe_allow_html=True)
                
                confirm_code = st.text_input("Type the Specialist ID to confirm deletion", placeholder=doc_to_delete.get("id"))
                
                delete_btn = st.button("Permanently Delete Profile", type="primary")
                
                if delete_btn:
                    if confirm_code == doc_to_delete.get("id"):
                        success = delete_record("doctors", delete_id, key_name="id")
                        if success:
                            st.success(f"Specialist profile {doc_to_delete.get('name')} deleted successfully.")
                            st.rerun()
                        else:
                            st.error("Error deleting specialist profile.")
                    else:
                        st.error("Confirmation ID mismatch. Please enter the correct Specialist ID.")
