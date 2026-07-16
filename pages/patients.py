import streamlit as st
import uuid
import datetime
import pandas as pd
from utils.auth import check_auth
from utils.database import load_data, save_data, insert_record, update_record, delete_record
from utils.styles import inject_custom_css
from utils.helper import render_header, render_badge
from utils.validation import (
    validate_non_empty,
    validate_age,
    validate_weight,
    validate_phone
)

# Protect access
check_auth()

# Inject styling
inject_custom_css()

# Header
render_header("Patient Records")

# Load data
patients = load_data("patients")
doctors = load_data("doctors")

# Helper for doctor names
doctor_names = [d.get("name") for d in doctors]
if not doctor_names:
    doctor_names = ["Unassigned / General Admission"]

# Tabs for CRUD
tab_view, tab_add, tab_edit, tab_delete = st.tabs([
    "📂 Patient Directory",
    "➕ Register Patient",
    "✏️ Edit Record",
    "❌ Discharge / Delete"
])

# ================= TAB 1: VIEW & SEARCH PATIENTS =================
with tab_view:
    st.markdown("### 📂 Patient Directory")
    
    if not patients:
        st.info("No patients currently registered in the database.")
    else:
        # Search & Filter controls
        col_search, col_doc, col_date = st.columns([2, 1, 1])
        with col_search:
            search_query = st.text_input("Search patients by Name, Disease or ID", placeholder="Search...", key="p_search")
        with col_doc:
            doc_filter = st.selectbox("Filter by Doctor", ["All Doctors"] + doctor_names, key="p_filter_doc")
        with col_date:
            date_filter = st.date_input("Filter by Registration Date", None, key="p_filter_date")

        # Apply filtering
        filtered_patients = patients.copy()
        
        if search_query:
            sq = search_query.lower()
            filtered_patients = [
                p for p in filtered_patients 
                if sq in p.get("name", "").lower() or sq in p.get("disease", "").lower() or sq in p.get("id", "").lower()
            ]
            
        if doc_filter != "All Doctors":
            filtered_patients = [p for p in filtered_patients if p.get("doctor_assigned") == doc_filter]
            
        if date_filter is not None:
            date_str = date_filter.isoformat()
            # Streamlit date_input might be null, check if we actually have a date
            if date_filter:
                filtered_patients = [p for p in filtered_patients if p.get("date") == date_str]

        # Display list of patients
        if not filtered_patients:
            st.info("No patients found matching the search criteria.")
        else:
            # Convert to Pandas for display
            df = pd.DataFrame(filtered_patients)
            
            # Select columns to display in grid
            display_df = df[["id", "name", "age", "gender", "blood_group", "disease", "doctor_assigned", "date"]]
            
            # Rename columns for cleaner UI
            display_df.columns = ["Patient ID", "Full Name", "Age", "Gender", "Blood Group", "Diagnosis", "Assigned Doctor", "Date Registered"]
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("#### 🔍 Select Patient for Detailed Health Sheet")
            patient_id_select = st.selectbox(
                "Choose patient to view full health records", 
                options=[p.get("id") for p in filtered_patients],
                format_func=lambda x: f"{x} - {next((p.get('name') for p in filtered_patients if p.get('id') == x), '')}"
            )
            
            if patient_id_select:
                selected_patient = next((p for p in filtered_patients if p.get("id") == patient_id_select), None)
                if selected_patient:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4 style="color: var(--accent-color); margin-top:0;">📋 Patient Health Profile: {selected_patient.get('name')}</h4>
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                            <tr style="border-bottom: 1px solid var(--card-border);">
                                <td style="padding: 8px; font-weight: 600; width: 30%;">Patient ID:</td>
                                <td style="padding: 8px;">{selected_patient.get('id')}</td>
                                <td style="padding: 8px; font-weight: 600; width: 30%;">Blood Group:</td>
                                <td style="padding: 8px;">{selected_patient.get('blood_group')}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--card-border);">
                                <td style="padding: 8px; font-weight: 600;">Age / Gender:</td>
                                <td style="padding: 8px;">{selected_patient.get('age')} Yrs / {selected_patient.get('gender')}</td>
                                <td style="padding: 8px; font-weight: 600;">Weight:</td>
                                <td style="padding: 8px;">{selected_patient.get('weight')} kg</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--card-border);">
                                <td style="padding: 8px; font-weight: 600;">Contact Phone:</td>
                                <td style="padding: 8px;">{selected_patient.get('phone')}</td>
                                <td style="padding: 8px; font-weight: 600;">Date Admitted:</td>
                                <td style="padding: 8px;">{selected_patient.get('date')}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--card-border);">
                                <td style="padding: 8px; font-weight: 600;">Home Address:</td>
                                <td colspan="3" style="padding: 8px;">{selected_patient.get('address')}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--card-border);">
                                <td style="padding: 8px; font-weight: 600;">Primary Diagnosis:</td>
                                <td colspan="3" style="padding: 8px; font-weight:bold; color: var(--danger-color);">{selected_patient.get('disease')}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--card-border);">
                                <td style="padding: 8px; font-weight: 600;">Key Symptoms:</td>
                                <td colspan="3" style="padding: 8px;">{selected_patient.get('symptoms')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: 600;">Attending Clinician:</td>
                                <td colspan="3" style="padding: 8px; font-weight:bold; color: var(--accent-color);">{selected_patient.get('doctor_assigned')}</td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)


# ================= TAB 2: REGISTER PATIENT =================
with tab_add:
    st.markdown("### ➕ Register New Patient")
    
    with st.form("add_patient_form"):
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            name = st.text_input("Patient Full Name", placeholder="e.g., John Doe")
            age = st.text_input("Age", placeholder="e.g., 45")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        with col_n2:
            weight = st.text_input("Weight (kg)", placeholder="e.g., 72.5")
            phone = st.text_input("Phone Number", placeholder="e.g., +15551234")
            doctor_assigned = st.selectbox("Attending Doctor Specialists", doctor_names)
            date_adm = st.date_input("Registration Date", datetime.date.today())
            
        address = st.text_area("Home Address", placeholder="e.g., 123 Main St, New York")
        disease = st.text_input("Primary Disease / Clinical Diagnosis", placeholder="e.g., Hypertension")
        symptoms = st.text_area("Patient Symptoms", placeholder="e.g., Frequent headaches, dizziness, shortness of breath")
        
        submit_btn = st.form_submit_button("Register Patient")
        
        if submit_btn:
            # Validations
            n_ok, n_msg = validate_non_empty(name, "Patient Name")
            a_ok, a_msg = validate_age(age)
            w_ok, w_msg = validate_weight(weight)
            p_ok, p_msg = validate_phone(phone)
            ad_ok, ad_msg = validate_non_empty(address, "Address")
            d_ok, d_msg = validate_non_empty(disease, "Disease")
            
            if not n_ok:
                st.error(n_msg)
            elif not a_ok:
                st.error(a_msg)
            elif not w_ok:
                st.error(w_msg)
            elif not p_ok:
                st.error(p_msg)
            elif not ad_ok:
                st.error(ad_msg)
            elif not d_ok:
                st.error(d_msg)
            else:
                # Auto-generate custom short ID
                patient_id = f"PAT-{uuid.uuid4().hex[:6].upper()}"
                
                new_patient = {
                    "id": patient_id,
                    "name": name.strip(),
                    "age": int(age),
                    "gender": gender,
                    "blood_group": blood_group,
                    "weight": float(weight),
                    "phone": phone.strip(),
                    "address": address.strip(),
                    "disease": disease.strip(),
                    "symptoms": symptoms.strip(),
                    "doctor_assigned": doctor_assigned,
                    "date": date_adm.isoformat()
                }
                
                insert_record("patients", new_patient)
                st.success(f"Successfully registered patient {name} with ID **{patient_id}**!")
                st.rerun()


# ================= TAB 3: EDIT RECORD =================
with tab_edit:
    st.markdown("### ✏️ Edit Patient Record")
    
    if not patients:
        st.info("No patients available to edit.")
    else:
        edit_id_select = st.selectbox(
            "Select Patient to Edit", 
            options=[p.get("id") for p in patients],
            format_func=lambda x: f"{x} - {next((p.get('name') for p in patients if p.get('id') == x), '')}",
            key="p_edit_selectbox"
        )
        
        patient_to_edit = next((p for p in patients if p.get("id") == edit_id_select), None)
        
        if patient_to_edit:
            with st.form("edit_patient_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_name = st.text_input("Patient Full Name", value=patient_to_edit.get("name"))
                    e_age = st.text_input("Age", value=str(patient_to_edit.get("age")))
                    e_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient_to_edit.get("gender")))
                    e_blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(patient_to_edit.get("blood_group")))
                with col_e2:
                    e_weight = st.text_input("Weight (kg)", value=str(patient_to_edit.get("weight")))
                    e_phone = st.text_input("Phone Number", value=patient_to_edit.get("phone"))
                    
                    # Doctor assigned index mapping
                    doc_idx = 0
                    if patient_to_edit.get("doctor_assigned") in doctor_names:
                        doc_idx = doctor_names.index(patient_to_edit.get("doctor_assigned"))
                    e_doctor = st.selectbox("Attending Doctor Specialists", doctor_names, index=doc_idx)
                    
                    # Parse registration date
                    try:
                        parsed_date = datetime.datetime.strptime(patient_to_edit.get("date"), "%Y-%m-%d").date()
                    except:
                        parsed_date = datetime.date.today()
                    e_date = st.date_input("Registration Date", parsed_date)
                    
                e_address = st.text_area("Home Address", value=patient_to_edit.get("address"))
                e_disease = st.text_input("Primary Disease / Clinical Diagnosis", value=patient_to_edit.get("disease"))
                e_symptoms = st.text_area("Patient Symptoms", value=patient_to_edit.get("symptoms"))
                
                edit_btn = st.form_submit_button("Update Patient Record")
                
                if edit_btn:
                    n_ok, n_msg = validate_non_empty(e_name, "Patient Name")
                    a_ok, a_msg = validate_age(e_age)
                    w_ok, w_msg = validate_weight(e_weight)
                    p_ok, p_msg = validate_phone(e_phone)
                    ad_ok, ad_msg = validate_non_empty(e_address, "Address")
                    d_ok, d_msg = validate_non_empty(e_disease, "Disease")
                    
                    if not n_ok:
                        st.error(n_msg)
                    elif not a_ok:
                        st.error(a_msg)
                    elif not w_ok:
                        st.error(w_msg)
                    elif not p_ok:
                        st.error(p_msg)
                    elif not ad_ok:
                        st.error(ad_msg)
                    elif not d_ok:
                        st.error(d_msg)
                    else:
                        updated_fields = {
                            "name": e_name.strip(),
                            "age": int(e_age),
                            "gender": e_gender,
                            "blood_group": e_blood_group,
                            "weight": float(e_weight),
                            "phone": e_phone.strip(),
                            "address": e_address.strip(),
                            "disease": e_disease.strip(),
                            "symptoms": e_symptoms.strip(),
                            "doctor_assigned": e_doctor,
                            "date": e_date.isoformat()
                        }
                        
                        success = update_record("patients", edit_id_select, updated_fields, key_name="id")
                        if success:
                            st.success(f"Patient record {e_name} [ID: {edit_id_select}] updated successfully!")
                            st.rerun()
                        else:
                            st.error("Could not update. An error occurred.")


# ================= TAB 4: DISCHARGE / DELETE =================
with tab_delete:
    st.markdown("### ❌ Patient Discharge & Record Deletion")
    
    if not patients:
        st.info("No patients available in directory.")
    else:
        delete_id_select = st.selectbox(
            "Select Patient to Discharge / Delete",
            options=[p.get("id") for p in patients],
            format_func=lambda x: f"{x} - {next((p.get('name') for p in patients if p.get('id') == x), '')}",
            key="p_delete_selectbox"
        )
        
        patient_to_delete = next((p for p in patients if p.get("id") == delete_id_select), None)
        
        if patient_to_delete:
            st.markdown(f"""
            <div class="glass-card" style="border: 1px solid var(--danger-color) !important;">
                <h4 style="color: var(--danger-color); margin-top:0;">⚠️ Discharge Warning</h4>
                <p>Are you sure you want to discharge Patient <strong>{patient_to_delete.get('name')}</strong> (ID: {patient_to_delete.get('id')})?</p>
                <p style="font-size:12px; color: var(--text-muted);">This action will permanently delete their health registry file from local disk database.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Security Confirmation
            confirm_code = st.text_input("Type the Patient ID to confirm discharge", placeholder=patient_to_delete.get("id"))
            
            delete_btn = st.button("Permanently Discharge Patient", type="primary")
            
            if delete_btn:
                if confirm_code == patient_to_delete.get("id"):
                    success = delete_record("patients", delete_id_select, key_name="id")
                    if success:
                        st.success(f"Patient {patient_to_delete.get('name')} discharged and record deleted successfully.")
                        st.rerun()
                    else:
                        st.error("Error discharging patient.")
                else:
                    st.error("Confirmation ID mismatch. Please enter the correct Patient ID.")
