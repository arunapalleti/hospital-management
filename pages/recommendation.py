import streamlit as st
import datetime
import uuid
from utils.auth import check_auth
from utils.database import load_data, save_data, insert_record, get_record, update_record
from utils.recommendation_engine import get_recommendations
from utils.styles import inject_custom_css
from utils.helper import render_header, render_badge
from utils.validation import validate_non_empty, validate_age, validate_weight

# Protect access
check_auth()

# Inject styling
inject_custom_css()

# Header
render_header("Clinical Recommendations")

# Load necessary data
patients = load_data("patients")
doctors = load_data("doctors")
tablets = load_data("tablets")

# Doctor names list
doctor_names = [d.get("name") for d in doctors]
if not doctor_names:
    doctor_names = ["Unassigned / General Admission"]

st.markdown("### 🩺 Diagnostic Tablet Advisor & Dispensing Console")
st.markdown("Enter patient clinical diagnostic markers or select an existing inpatient file to receive tablet matches and trigger pharmacy dispensing.")

# Choose patient selection mode
patient_mode = st.radio("Patient Selection Mode", ["Select Inpatient", "Manual Input"], horizontal=True)

# Form variables
selected_p_id = ""
p_name = ""
p_age = ""
p_weight = ""
p_disease = ""
p_symptoms = ""

if patient_mode == "Select Inpatient":
    if not patients:
        st.warning("No registered patients found. Please switch to manual input or add a patient.")
    else:
        # Patient selectbox
        p_sel = st.selectbox(
            "Select Registered Patient Profile",
            options=[p.get("id") for p in patients],
            format_func=lambda x: f"{x} - {next((p.get('name') for p in patients if p.get('id') == x), '')}"
        )
        
        patient_obj = next((p for p in patients if p.get("id") == p_sel), None)
        if patient_obj:
            selected_p_id = patient_obj.get("id")
            p_name = patient_obj.get("name")
            p_age = str(patient_obj.get("age"))
            p_weight = str(patient_obj.get("weight"))
            p_disease = patient_obj.get("disease")
            p_symptoms = patient_obj.get("symptoms")
            
            # Show static patient sheet
            st.info(f"📁 **Loaded Patient File**: {p_name} | Age: {p_age} yrs | Weight: {p_weight} kg | Active Diagnosis: {p_disease}")
else:
    # Manual Input
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        p_name = st.text_input("Patient Full Name", placeholder="e.g. Samuel Green")
        p_age = st.text_input("Patient Age", placeholder="e.g. 38")
    with col_in2:
        p_weight = st.text_input("Patient Weight (kg)", placeholder="e.g. 68.0")
        p_disease = st.text_input("Reported Disease / Pathology", placeholder="e.g. Cold")
    p_symptoms = st.text_area("Patient Symptoms Description", placeholder="e.g. runny nose, sneezing, cough")

# Action trigger
st.markdown("<br>", unsafe_allow_html=True)
run_diag = st.button("Evaluate Symptoms & Find Recommendations", type="primary")

# Recommendation outputs
if run_diag or st.session_state.get("show_recs", False):
    # Store trigger in state
    st.session_state["show_recs"] = True
    
    # Run validations
    n_ok, n_msg = validate_non_empty(p_name, "Patient Name")
    a_ok, a_msg = validate_age(p_age)
    w_ok, w_msg = validate_weight(p_weight)
    
    if not n_ok:
        st.error(n_msg)
    elif not a_ok:
        st.error(a_msg)
    elif not w_ok:
        st.error(w_msg)
    else:
        # Run recommendation calculations
        rule, warnings = get_recommendations(p_disease, p_age, p_weight, p_symptoms)
        
        if not rule:
            st.warning("🔍 No standard recommendation rule matches this clinical profile. Please consult a specialist directly.")
            st.session_state["show_recs"] = False
        else:
            # Save inputs in session state so they persist on rerun of dispensing action
            st.session_state["diag_p_id"] = selected_p_id if selected_p_id else f"TEMP-{uuid.uuid4().hex[:6].upper()}"
            st.session_state["diag_p_name"] = p_name
            st.session_state["diag_p_disease"] = p_disease if p_disease else rule.get("disease")
            st.session_state["diag_rule"] = rule
            st.session_state["diag_warnings"] = warnings
            
            # Display matching results
            st.markdown("### 📋 Diagnostic Assessment Report")
            
            # Show warnings
            if warnings:
                for w in warnings:
                    st.warning(w)
                    
            # Layout matching card details
            recommended_tabs = rule.get("tablets", [])
            dosage_guideline = rule.get("dosage", "")
            precautions = rule.get("precautions", "")
            side_effects = rule.get("side_effects", "")
            specialist = rule.get("specialist", "")
            
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: var(--accent-color); margin-top:0;">💡 Pre-defined Recommendation Matches</h4>
                <p style="font-size:16px;">Matched Pathology Case: <strong>{rule.get('disease')}</strong></p>
                
                <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-top:15px;">
                    <tr style="border-bottom: 1px solid var(--card-border);">
                        <td style="padding: 10px; font-weight:600; width:25%;">Recommended Pills:</td>
                        <td style="padding: 10px; font-weight:bold; color:var(--accent-color);">{", ".join(recommended_tabs)}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--card-border);">
                        <td style="padding: 10px; font-weight:600;">Dosage Protocol:</td>
                        <td style="padding: 10px;">{dosage_guideline}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--card-border);">
                        <td style="padding: 10px; font-weight:600;">Clinical Precautions:</td>
                        <td style="padding: 10px;">{precautions}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--card-border);">
                        <td style="padding: 10px; font-weight:600;">Potential Side Effects:</td>
                        <td style="padding: 10px; color:var(--warning-color);">{side_effects}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight:600;">Doctor Specialist Routing:</td>
                        <td style="padding: 10px; font-weight:bold; color:var(--success-color);">{specialist} Referrals</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Live Pharmacy Inventory Checks
            st.markdown("### 💊 Live Pharmacy Inventory Availability")
            
            dispense_allowed = True
            tablet_availability_list = []
            
            for tab_name in recommended_tabs:
                # Query stock levels
                matches = [t for t in tablets if t.get("name").lower() == tab_name.lower()]
                
                if not matches:
                    st.error(f"❌ **Missing Formula**: **{tab_name}** is not registered in the pharmacy inventory database.")
                    dispense_allowed = False
                    tablet_availability_list.append({"name": tab_name, "stock": 0, "status": "Not Stocked", "obj": None})
                else:
                    item = matches[0]
                    stock_val = int(item.get("stock", 0))
                    
                    if stock_val <= 0:
                        st.error(f"❌ **Stockout Alert**: **{tab_name}** is out of stock in pharmacy!")
                        dispense_allowed = False
                        tablet_availability_list.append({"name": tab_name, "stock": 0, "status": "Out of Stock", "obj": item})
                    elif stock_val < 20:
                        st.warning(f"⚠️ **Low Stock Warning**: **{tab_name}** has only {stock_val} units left.")
                        tablet_availability_list.append({"name": tab_name, "stock": stock_val, "status": "Low Stock", "obj": item})
                    else:
                        st.success(f"✅ **Stock Level Nominal**: **{tab_name}** has {stock_val} units available.")
                        tablet_availability_list.append({"name": tab_name, "stock": stock_val, "status": "In Stock", "obj": item})
            
            st.session_state["diag_tab_avail"] = tablet_availability_list
            
            # Action interface to issue medication
            st.markdown("### ✍️ Prescription Issuance Console")
            
            # Choose Doctor
            default_doc_idx = 0
            # Try to pre-select matching specialist name if we have a doctor of that specialization
            matching_specialists = [d for d in doctors if d.get("specialization", "").lower() == specialist.lower()]
            if matching_specialists and matching_specialists[0].get("name") in doctor_names:
                default_doc_idx = doctor_names.index(matching_specialists[0].get("name"))
                
            prescribing_doctor = st.selectbox(
                "Select Prescribing Clinician",
                options=doctor_names,
                index=default_doc_idx,
                key="prescribe_doc_select"
            )
            
            # Issue quantity per pill
            issue_qty = 1  # Standard decrement
            
            if dispense_allowed:
                dispense_btn = st.button("Issue Prescription & Dispense Medication", type="primary", key="dispense_medication_btn")
                
                if dispense_btn:
                    with st.spinner("Processing pharmacy inventory write operations..."):
                        # Double check stocks in loop and update
                        tablets_db = load_data("tablets")
                        
                        issued_tabs = []
                        stock_updated = True
                        
                        for tab_avail in st.session_state["diag_tab_avail"]:
                            t_obj = tab_avail["obj"]
                            # Find index in database list
                            for idx, t_db in enumerate(tablets_db):
                                if t_db["id"] == t_obj["id"]:
                                    current_stock = int(t_db["stock"])
                                    if current_stock >= issue_qty:
                                        tablets_db[idx]["stock"] = current_stock - issue_qty
                                        issued_tabs.append(f"{t_db['name']} ({t_db['strength']})")
                                    else:
                                        stock_updated = False
                                        st.error(f"Cannot dispense {t_db['name']}. Low stock occurred mid-transaction.")
                                        break
                                        
                        if stock_updated:
                            # Save updated stock
                            save_data("tablets", tablets_db)
                            
                            # Log to history
                            now = datetime.datetime.now()
                            date_str = now.date().isoformat()
                            time_str = now.time().strftime("%H:%M:%S")
                            
                            history_record = {
                                "patient_id": st.session_state["diag_p_id"],
                                "patient_name": st.session_state["diag_p_name"],
                                "doctor": prescribing_doctor,
                                "disease": st.session_state["diag_p_disease"],
                                "recommended_tablet": ", ".join(issued_tabs),
                                "dosage": dosage_guideline,
                                "date": date_str,
                                "time": time_str,
                                "status": "Issued"
                            }
                            
                            insert_record("history", history_record)
                            
                            st.success(f"Prescription successfully registered! Dispensed: {', '.join(issued_tabs)} to patient **{st.session_state['diag_p_name']}**.")
                            
                            # Reset recommendation triggers
                            st.session_state["show_recs"] = False
                            st.rerun()
            else:
                st.error("❌ Medication dispensing disabled. Please correct missing stocks or out-of-stock items before issuing.")
