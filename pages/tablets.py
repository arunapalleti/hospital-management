import streamlit as st
import datetime
import pandas as pd
from utils.auth import check_auth
from utils.database import load_data, save_data, insert_record, update_record, delete_record
from utils.styles import inject_custom_css, render_metric_card
from utils.helper import render_header, render_badge
from utils.validation import validate_non_empty

# Protect access
check_auth()

# Inject styling
inject_custom_css()

# Header
render_header("Tablet Inventory")

# Load data
tablets = load_data("tablets")

# Low stock threshold
LOW_STOCK_LIMIT = 20

# Admin check
is_admin = st.session_state.get("role") == "Admin"

# Tabs
if is_admin:
    tab_inv, tab_add, tab_edit, tab_delete = st.tabs([
        "📦 Pharmacy Stock",
        "💊 Add Medicine",
        "✏️ Edit Medicine",
        "❌ Delete Medicine"
    ])
else:
    tab_inv, = st.tabs(["📦 Pharmacy Stock"])

# ================= TAB 1: VIEW & FILTER INVENTORY =================
with tab_inv:
    st.markdown("### 📦 Pharmacy Stock")
    
    # Calculate stats
    total_formulations = len(tablets)
    total_units = sum(int(t.get("stock", 0)) for t in tablets)
    
    # Expiry and Low stock warnings
    today = datetime.date.today()
    low_stock_count = 0
    expiring_soon_count = 0
    
    for t in tablets:
        stock_val = int(t.get("stock", 0))
        if stock_val < LOW_STOCK_LIMIT:
            low_stock_count += 1
            
        try:
            exp_date = datetime.datetime.strptime(t.get("expiry_date", ""), "%Y-%m-%d").date()
            days_left = (exp_date - today).days
            if days_left <= 30 and days_left >= 0:
                expiring_soon_count += 1
        except:
            pass
            
    # Metric rows
    col_st1, col_st2, col_st3, col_st4 = st.columns(4)
    with col_st1:
        render_metric_card("Total Formulas", f"{total_formulations} chemical types", "💊")
    with col_st2:
        render_metric_card("Total Units Stocked", f"{total_units} units", "📦")
    with col_st3:
        render_metric_card("Low Stock Alerts", f"{low_stock_count} medicines", "⚠️")
    with col_st4:
        render_metric_card("Expiring Soon (30d)", f"{expiring_soon_count} chemical types", "⏳")
        
    st.markdown("---")
    
    # Filters
    col_s, col_cat, col_al = st.columns([2, 1, 1])
    with col_s:
        search_q = st.text_input("Search inventory by Name, Uses or ID", placeholder="Search...", key="t_search")
    with col_cat:
        # Dynamic categories list
        categories = list(set([t.get("category") for t in tablets if t.get("category")]))
        cat_filter = st.selectbox("Category Filter", ["All Categories"] + categories)
    with col_al:
        alert_filter = st.selectbox("Status Filter", ["All Items", "Low Stock (<20)", "Expiring Soon (<=30 Days)"])

    # Apply filters
    filtered_tablets = tablets.copy()
    
    if search_q:
        sq = search_q.lower()
        filtered_tablets = [
            t for t in filtered_tablets
            if sq in t.get("name", "").lower() or sq in t.get("uses", "").lower() or sq in t.get("id", "").lower() or sq in t.get("manufacturer", "").lower()
        ]
        
    if cat_filter != "All Categories":
        filtered_tablets = [t for t in filtered_tablets if t.get("category") == cat_filter]
        
    if alert_filter == "Low Stock (<20)":
        filtered_tablets = [t for t in filtered_tablets if int(t.get("stock", 0)) < LOW_STOCK_LIMIT]
    elif alert_filter == "Expiring Soon (<=30 Days)":
        valid_tablets = []
        for t in filtered_tablets:
            try:
                exp_date = datetime.datetime.strptime(t.get("expiry_date", ""), "%Y-%m-%d").date()
                if (exp_date - today).days <= 30 and (exp_date - today).days >= 0:
                    valid_tablets.append(t)
            except:
                pass
        filtered_tablets = valid_tablets

    # Show items
    if not filtered_tablets:
        st.info("No medicines found matching the filters.")
    else:
        # Create a table list
        table_rows = []
        for t in filtered_tablets:
            stock_val = int(t.get("stock", 0))
            
            # Stock badge
            if stock_val == 0:
                stock_status = "Out of Stock"
            elif stock_val < LOW_STOCK_LIMIT:
                stock_status = "Low Stock"
            else:
                stock_status = "In Stock"
                
            # Expiry status
            try:
                exp_date = datetime.datetime.strptime(t.get("expiry_date", ""), "%Y-%m-%d").date()
                days_left = (exp_date - today).days
                if days_left < 0:
                    exp_status = "Expired"
                elif days_left <= 30:
                    exp_status = "Expiring Soon"
                else:
                    exp_status = "Valid"
            except:
                exp_status = "Valid"
                
            table_rows.append({
                "ID": t.get("id"),
                "Name": t.get("name"),
                "Category": t.get("category"),
                "Strength": t.get("strength"),
                "Stock Quantity": stock_val,
                "Stock Status": stock_status,
                "Expiry Date": t.get("expiry_date"),
                "Expiry Status": exp_status,
                "Price ($)": f"${float(t.get('price', 0)):.2f}",
                "Manufacturer": t.get("manufacturer")
            })
            
        df_inv = pd.DataFrame(table_rows)
        
        # Color coding highlighting helper
        def highlight_statuses(val):
            if val in ["Low Stock", "Expiring Soon"]:
                return "background-color: rgba(245, 158, 11, 0.2); color: #d97706; font-weight: bold;"
            elif val in ["Out of Stock", "Expired"]:
                return "background-color: rgba(239, 68, 68, 0.2); color: #dc2626; font-weight: bold;"
            elif val in ["In Stock", "Valid"]:
                return "background-color: rgba(16, 185, 129, 0.2); color: #10b981; font-weight: bold;"
            return ""
            
        styled_df = df_inv.style.map(highlight_statuses, subset=["Stock Status", "Expiry Status"])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Details Drawer / Card selection
        st.markdown("#### 🔍 Select Tablet to View Detailed Leaflet")
        tab_id_select = st.selectbox(
            "Choose a chemical formula to inspect details",
            options=[t.get("id") for t in filtered_tablets],
            format_func=lambda x: f"{x} - {next((t.get('name') for t in filtered_tablets if t.get('id') == x), '')}"
        )
        
        if tab_id_select:
            selected_tab = next((t for t in filtered_tablets if t.get("id") == tab_id_select), None)
            if selected_tab:
                # Calculate days remaining
                exp_msg = selected_tab.get("expiry_date")
                try:
                    exp_date = datetime.datetime.strptime(selected_tab.get("expiry_date", ""), "%Y-%m-%d").date()
                    days_left = (exp_date - today).days
                    if days_left < 0:
                        exp_msg += f" (Expired {abs(days_left)} days ago!)"
                    else:
                        exp_msg += f" (Expiring in {days_left} days)"
                except:
                    pass
                    
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color: var(--accent-color); margin-top:0;">💊 Medicine Leaflet: {selected_tab.get('name')} {selected_tab.get('strength')}</h4>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight: 600; width: 25%;">Tablet ID:</td>
                            <td style="padding: 8px;">{selected_tab.get('id')}</td>
                            <td style="padding: 8px; font-weight: 600; width: 25%;">Manufacturer:</td>
                            <td style="padding: 8px;">{selected_tab.get('manufacturer')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight: 600;">Category:</td>
                            <td style="padding: 8px;">{selected_tab.get('category')}</td>
                            <td style="padding: 8px; font-weight: 600;">Dosage Guideline:</td>
                            <td style="padding: 8px;">{selected_tab.get('dosage')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight: 600;">Stock Units:</td>
                            <td style="padding: 8px; font-weight: bold; color: {'var(--danger-color)' if int(selected_tab.get('stock')) < LOW_STOCK_LIMIT else 'var(--success-color)'};">{selected_tab.get('stock')} units</td>
                            <td style="padding: 8px; font-weight: 600;">Unit Price:</td>
                            <td style="padding: 8px;">${float(selected_tab.get('price')):.2f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight: 600;">Expiry Date:</td>
                            <td colspan="3" style="padding: 8px;">{exp_msg}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid var(--card-border);">
                            <td style="padding: 8px; font-weight: 600;">Therapeutic Uses:</td>
                            <td colspan="3" style="padding: 8px;">{selected_tab.get('uses')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: 600;">Known Side Effects:</td>
                            <td colspan="3" style="padding: 8px; color: var(--warning-color);">{selected_tab.get('side_effects')}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)


# ================= ADM-ONLY CRUD =================
if is_admin:
    # ================= TAB 2: ADD MEDICINE =================
    with tab_add:
        st.markdown("### ➕ Register New Tablet / Medicine")
        
        with st.form("add_medicine_form"):
            col_ad1, col_ad2 = st.columns(2)
            with col_ad1:
                t_id = st.text_input("Tablet ID (Custom unique code)", placeholder="e.g., TAB-006")
                t_name = st.text_input("Tablet Name", placeholder="e.g., Ibuprofen")
                t_man = st.text_input("Manufacturer", placeholder="e.g., MediLabs Inc.")
                t_cat = st.text_input("Category / Class", placeholder="e.g., NSAID / Analgesic")
                t_dos = st.text_input("Standard Dosage Instruction", placeholder="e.g., 1 tablet after food twice daily")
            with col_ad2:
                t_str = st.text_input("Strength (mg / ml)", placeholder="e.g., 400mg")
                t_prc = st.number_input("Unit Price ($)", min_value=0.01, max_value=500.0, value=0.20, step=0.01)
                t_stk = st.number_input("Initial Stock Quantity", min_value=0, max_value=10000, value=100, step=10)
                t_exp = st.date_input("Expiry Date", datetime.date.today() + datetime.timedelta(days=365))
                
            t_uses = st.text_area("Therapeutic Uses", placeholder="e.g., Treatment of fever, muscle aches, and general inflammation.")
            t_side = st.text_area("Common Side Effects", placeholder="e.g., Heartburn, stomach distress, mild dizziness.")
            
            submit_btn = st.form_submit_button("Add Tablet to Inventory")
            
            if submit_btn:
                # Validations
                id_ok, id_msg = validate_non_empty(t_id, "Tablet ID")
                n_ok, n_msg = validate_non_empty(t_name, "Tablet Name")
                man_ok, man_msg = validate_non_empty(t_man, "Manufacturer")
                
                # Check duplicate
                id_exists = any(item.get("id").upper() == t_id.upper() for item in tablets)
                
                if not id_ok:
                    st.error(id_msg)
                elif id_exists:
                    st.error(f"Tablet ID '{t_id}' already exists in inventory database.")
                elif not n_ok:
                    st.error(n_msg)
                elif not man_ok:
                    st.error(man_msg)
                else:
                    new_tablet = {
                        "id": t_id.strip().upper(),
                        "name": t_name.strip(),
                        "manufacturer": t_man.strip(),
                        "category": t_cat.strip(),
                        "dosage": t_dos.strip(),
                        "strength": t_str.strip(),
                        "price": float(t_prc),
                        "stock": int(t_stk),
                        "expiry_date": t_exp.isoformat(),
                        "uses": t_uses.strip(),
                        "side_effects": t_side.strip()
                    }
                    
                    insert_record("tablets", new_tablet)
                    st.success(f"Medicine **{t_name}** added to inventory list under ID: **{t_id}**!")
                    st.rerun()

    # ================= TAB 3: EDIT MEDICINE =================
    with tab_edit:
        st.markdown("### ✏️ Edit Tablet Record")
        
        if not tablets:
            st.info("No medicine files available to edit.")
        else:
            edit_id = st.selectbox(
                "Select Medicine to Edit",
                options=[t.get("id") for t in tablets],
                format_func=lambda x: f"{x} - {next((t.get('name') for t in tablets if t.get('id') == x), '')}",
                key="t_edit_selectbox"
            )
            
            tab_to_edit = next((t for t in tablets if t.get("id") == edit_id), None)
            
            if tab_to_edit:
                with st.form("edit_tablet_form"):
                    col_ed1, col_ed2 = st.columns(2)
                    with col_ed1:
                        e_name = st.text_input("Tablet Name", value=tab_to_edit.get("name"))
                        e_man = st.text_input("Manufacturer", value=tab_to_edit.get("manufacturer"))
                        e_cat = st.text_input("Category / Class", value=tab_to_edit.get("category"))
                        e_dos = st.text_input("Standard Dosage Instruction", value=tab_to_edit.get("dosage"))
                    with col_ed2:
                        e_str = st.text_input("Strength (mg / ml)", value=tab_to_edit.get("strength"))
                        e_prc = st.number_input("Unit Price ($)", min_value=0.01, max_value=500.0, value=float(tab_to_edit.get("price")), step=0.01)
                        e_stk = st.number_input("Stock Quantity", min_value=0, max_value=10000, value=int(tab_to_edit.get("stock")), step=10)
                        
                        # Parse date
                        try:
                            parsed_date = datetime.datetime.strptime(tab_to_edit.get("expiry_date"), "%Y-%m-%d").date()
                        except:
                            parsed_date = datetime.date.today()
                        e_exp = st.date_input("Expiry Date", parsed_date)
                        
                    e_uses = st.text_area("Therapeutic Uses", value=tab_to_edit.get("uses"))
                    e_side = st.text_area("Common Side Effects", value=tab_to_edit.get("side_effects"))
                    
                    edit_btn = st.form_submit_button("Update Tablet Info")
                    
                    if edit_btn:
                        n_ok, n_msg = validate_non_empty(e_name, "Tablet Name")
                        man_ok, man_msg = validate_non_empty(e_man, "Manufacturer")
                        
                        if not n_ok:
                            st.error(n_msg)
                        elif not man_ok:
                            st.error(man_msg)
                        else:
                            updated_fields = {
                                "name": e_name.strip(),
                                "manufacturer": e_man.strip(),
                                "category": e_cat.strip(),
                                "dosage": e_dos.strip(),
                                "strength": e_str.strip(),
                                "price": float(e_prc),
                                "stock": int(e_stk),
                                "expiry_date": e_exp.isoformat(),
                                "uses": e_uses.strip(),
                                "side_effects": e_side.strip()
                            }
                            
                            success = update_record("tablets", edit_id, updated_fields, key_name="id")
                            if success:
                                st.success(f"Medicine **{e_name}** [ID: {edit_id}] updated successfully!")
                                st.rerun()
                            else:
                                st.error("Error updating medicine details.")

    # ================= TAB 4: DELETE MEDICINE =================
    with tab_delete:
        st.markdown("### ❌ De-register Medicine File")
        
        if not tablets:
            st.info("No medicine files in inventory.")
        else:
            delete_id = st.selectbox(
                "Select Medicine to Delete",
                options=[t.get("id") for t in tablets],
                format_func=lambda x: f"{x} - {next((t.get('name') for t in tablets if t.get('id') == x), '')}",
                key="t_delete_selectbox"
            )
            
            tab_to_delete = next((t for t in tablets if t.get("id") == delete_id), None)
            
            if tab_to_delete:
                st.markdown(f"""
                <div class="glass-card" style="border: 1px solid var(--danger-color) !important;">
                    <h4 style="color: var(--danger-color); margin-top:0;">⚠️ Inventory Deletion Warning</h4>
                    <p>Are you sure you want to permanently delete <strong>{tab_to_delete.get('name')}</strong> (ID: {tab_to_delete.get('id')}) from database?</p>
                </div>
                """, unsafe_allow_html=True)
                
                confirm_code = st.text_input("Type the Tablet ID to confirm deletion", placeholder=tab_to_delete.get("id"))
                
                delete_btn = st.button("Permanently Delete Medicine", type="primary")
                
                if delete_btn:
                    if confirm_code == tab_to_delete.get("id"):
                        success = delete_record("tablets", delete_id, key_name="id")
                        if success:
                            st.success(f"Medicine {tab_to_delete.get('name')} deleted from database inventory.")
                            st.rerun()
                        else:
                            st.error("Error deleting medicine profile.")
                    else:
                        st.error("Confirmation ID mismatch. Please enter the correct Tablet ID.")
