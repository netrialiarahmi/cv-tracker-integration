"""
Login page for authentication.
Supports HR Superadmin, HR Admin, and Division user login.
"""

import streamlit as st
from utils.helpers import get_logo_base64
from core.auth import get_hr_roles
from core.session_manager import qp_clear, qp_update


def render() -> None:
    """
    Render the login page with role-based authentication.
    """
    hr_roles = get_hr_roles()
    logo_base64 = get_logo_base64()
    
    st.markdown(f"""
    <div style="
        max-width: 420px;
        margin: 6rem auto;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 2.5rem 2rem;
        border-top: 4px solid #2563eb;
    ">
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        ">
            <img src="data:image/webp;base64,{logo_base64}" 
                 style="width: 70px; height: auto; border-radius: 8px;" 
                 alt="Kompas.com Logo" />
            <div style="text-align: left;">
                <h2 style="font-weight:700; color:#1e293b; margin:0;">
                    Kompas.com Hiring Tracker
                </h2>
                <p style="color:#64748b; font-size:0.9rem; margin:0;">
                    Streamline your recruitment process with efficiency and transparency.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    role_choice = st.selectbox("Select Access Type", ["", "Human Resource", "Division"], index=0)
    
    if role_choice == "Human Resource":
        hr_role = st.radio("Select HR Role", ["Superadmin", "Admin"], horizontal=True)
        if hr_role == "Superadmin":
            hr_user = st.text_input("Superadmin Username", placeholder="Enter your Username", key="super_user")
            hr_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="super_pass")
            if st.button("Sign In", use_container_width=True, key="super_login"):
                superadmin_user = hr_roles.get("superadmin", {}).get("username", "")
                superadmin_pass = hr_roles.get("superadmin", {}).get("password", "")
                if not superadmin_user or not superadmin_pass:
                    st.error("⚠️ Superadmin credentials not configured properly.")
                    st.stop()
                if hr_user == superadmin_user and hr_pass == superadmin_pass:
                    # Clear any existing state first
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    qp_clear()
                    # Set new state
                    st.session_state.logged_in = True
                    st.session_state.user_division = "Human Resource"
                    st.session_state.role = "HR Superadmin"
                    st.session_state.hr_admin = None
                    # Set new query params
                    qp_update({
                        "logged_in": "1",
                        "user_division": "Human Resource",
                        "role": "HR Superadmin",
                        "role_type": "HR Superadmin",
                        "hr_admin": ""
                    })
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Superadmin credentials.")
        elif hr_role == "Admin":
            admin_options = list(hr_roles.get("admins", {}).keys())
            admin_user = st.selectbox("Select HR Admin", options=[""] + admin_options, index=0, key="admin_user")
            admin_pass = st.text_input("Password", type="password", key="admin_pass")
            if st.button("Sign In", use_container_width=True, key="admin_login"):
                if admin_user and admin_pass == hr_roles.get("admins", {}).get(admin_user, {}).get("password", ""):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    qp_clear()
                    st.session_state.logged_in = True
                    st.session_state.user_division = "Human Resource"
                    st.session_state.role = "HR Admin"
                    st.session_state.hr_admin = admin_user
                    qp_update({
                        "logged_in": "1",
                        "user_division": "Human Resource",
                        "role": "HR Admin",
                        "role_type": "HR Admin",
                        "hr_admin": admin_user
                    })
                    st.success(f"✅ Login successful! Welcome {admin_user}")
                    st.rerun()
                else:
                    st.error("❌ Invalid HR Admin credentials.")
    elif role_choice == "Division":
        available_divs = [d for d in st.session_state.credentials.keys() if d != "Human Resource"]
        if not available_divs:
            st.warning("⚠️ No divisions available yet. HR Superadmin needs to create divisions first.")
        else:
            division = st.selectbox("Division", options=[""] + available_divs, index=0, key="div_select")
            password = st.text_input("Password", type="password", placeholder="Enter your secure password", key="div_pass")
            if st.button("Sign In", use_container_width=True, key="div_login"):
                if division == "":
                    st.error("❌ Please select a division.")
                elif division not in st.session_state.credentials:
                    st.error(f"❌ Division '{division}' not found in system.")
                elif password == st.session_state.credentials.get(division, ""):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    qp_clear()
                    qp_update({
                        "logged_in": "1",
                        "user_division": division,
                        "role": "Division",
                        "role_type": "Division",
                        "hr_admin": ""
                    })
                    st.session_state.logged_in = True
                    st.session_state.user_division = division
                    st.session_state.role = "Division"
                    st.session_state.hr_admin = None
                    st.success(f"✅ Login successful! Welcome {division}")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please check your password.")
    
    st.markdown("""
        <p style='text-align:center; margin-top:2rem; color:#94a3b8; font-size:0.8rem;'>
            © 2025 Kompas.com — Human Resource Division
        </p>
    </div>
    """, unsafe_allow_html=True)
