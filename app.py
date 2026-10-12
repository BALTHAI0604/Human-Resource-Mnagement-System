import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# ==============================================================================
# DATABASE CONNECTION & SCHEMA SETUP
# ==============================================================================

conn = sqlite3.connect("dayflow.db", check_same_thread=False)
cursor = conn.cursor()

# Employees Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL
)
""")

# Attendance Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT NOT NULL,
    check_in TEXT,
    check_out TEXT,
    attendance_date TEXT
)
""")

# Leaves Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT NOT NULL,
    leave_type TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

# Payroll Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS payroll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT NOT NULL,
    salary REAL NOT NULL,
    created_date TEXT
)
""")

conn.commit()


# ==============================================================================
# PAGE CONFIGURATION & RICH AESTHETICS (CUSTOM CSS)
# ==============================================================================

st.set_page_config(
    page_title="Dayflow HRMS | Modern Workforce Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Modern CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 95%;
    }

    /* Vibrant Gradient Header Banner */
    .banner-container {
        background: linear-gradient(135deg, #4338ca 0%, #6366f1 35%, #8b5cf6 70%, #ec4899 100%);
        padding: 24px 32px;
        border-radius: 18px;
        color: #ffffff;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.28);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .banner-title {
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .banner-sub {
        font-size: 14px;
        opacity: 0.92;
        margin-top: 4px;
        font-weight: 500;
    }
    .banner-pill {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 8px 18px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.35);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Modern Direct Top Tabs Styling */
    div[data-baseweb="tab-list"] {
        gap: 10px;
        padding: 6px 4px 14px 4px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 20px;
    }
    button[data-baseweb="tab"] {
        background: #f8fafc;
        border-radius: 12px;
        padding: 10px 22px;
        font-weight: 600;
        font-size: 14px;
        color: #475569;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    button[data-baseweb="tab"]:hover {
        background: #e2e8f0;
        color: #1e293b;
        transform: translateY(-1px);
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
        border-color: transparent !important;
    }

    /* Vibrant Stat KPI Cards */
    .stat-card {
        border-radius: 16px;
        padding: 22px 24px;
        color: #ffffff;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
    }
    .stat-card-blue {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    }
    .stat-card-green {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    .stat-card-amber {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    .stat-card-purple {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
    }
    .stat-number {
        font-size: 32px;
        font-weight: 800;
        line-height: 1.1;
        margin: 6px 0 2px 0;
    }
    .stat-label {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.9;
    }
    .stat-icon {
        font-size: 26px;
        float: right;
        opacity: 0.9;
    }

    /* Content Cards / Containers */
    .content-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px 26px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }
    .box-title {
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Primary Gradient Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 9px 24px;
        border: none;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
        transform: translateY(-2px);
        color: white;
    }

    /* Status Badges */
    .badge-pending {
        background: #fef3c7;
        color: #b45309;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-approved {
        background: #d1fae5;
        color: #047857;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-rejected {
        background: #fee2e2;
        color: #b91c1c;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# HEADER BANNER (DIRECTLY VISIBLE)
# ==============================================================================

today_str = date.today().strftime("%B %d, %Y")
now_time_str = datetime.now().strftime("%I:%M %p")

st.markdown(f"""
<div class="banner-container">
    <div>
        <div class="banner-title">⚡ Dayflow HRMS Portal</div>
        <div class="banner-sub">Smart Employee Management, Real-time Attendance & Payroll Dashboard</div>
    </div>
    <div class="banner-pill">
        <span>📅 {today_str}</span>
        <span>•</span>
        <span>🕒 {now_time_str}</span>
        <span>•</span>
        <span>🟢 System Active</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# DIRECT TOP TABS NAVIGATION (NO SIDEBAR REQUIRED)
# ==============================================================================

tab_home, tab_emp, tab_att, tab_leave, tab_pay = st.tabs([
    "🏠 Dashboard Overview",
    "👥 Employees",
    "⏱️ Attendance",
    "🌴 Leave Management",
    "💰 Payroll"
])


# ==============================================================================
# 1. DASHBOARD OVERVIEW (HOME) - ALL-IN-ONE DIRECT VIEW
# ==============================================================================

with tab_home:
    # Fetch Core Metrics
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    today_iso = str(date.today())
    cursor.execute("""
    SELECT COUNT(DISTINCT employee_name)
    FROM attendance
    WHERE attendance_date=?
    """, (today_iso,))
    present_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leaves WHERE status='Pending'")
    pending_leaves = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(salary), 0) FROM payroll")
    total_payroll_val = cursor.fetchone()[0]

    # 4 Vibrant Colorful KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card stat-card-blue">
            <span class="stat-icon">👥</span>
            <div class="stat-label">Total Staff</div>
            <div class="stat-number">{total_employees}</div>
            <div style="font-size: 12px; opacity: 0.85;">Registered Employees</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card stat-card-green">
            <span class="stat-icon">⏱️</span>
            <div class="stat-label">Present Today</div>
            <div class="stat-number">{present_today}</div>
            <div style="font-size: 12px; opacity: 0.85;">Checked-in On Duty</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card stat-card-amber">
            <span class="stat-icon">📋</span>
            <div class="stat-label">Pending Leaves</div>
            <div class="stat-number">{pending_leaves}</div>
            <div style="font-size: 12px; opacity: 0.85;">Awaiting Approval</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card stat-card-purple">
            <span class="stat-icon">💰</span>
            <div class="stat-label">Monthly Payroll</div>
            <div class="stat-number">₹{total_payroll_val:,.0f}</div>
            <div style="font-size: 12px; opacity: 0.85;">Total Salary Pool</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Direct Dashboard Actions (Quick Attendance + Live Feed)
    dash_col_left, dash_col_right = st.columns([1, 1])

    with dash_col_left:
        st.markdown("""
        <div class="content-box">
            <div class="box-title">⚡ Quick Daily Attendance</div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 15px;">
                Check in or check out directly from the dashboard.
            </div>
        """, unsafe_allow_html=True)

        cursor.execute("SELECT name FROM employees")
        all_emps = [row[0] for row in cursor.fetchall()]

        if all_emps:
            quick_emp = st.selectbox("Select Employee for Quick Punch", all_emps, key="dash_quick_emp")

            cursor.execute("""
            SELECT id, check_in, check_out FROM attendance
            WHERE employee_name=? AND attendance_date=?
            """, (quick_emp, today_iso))
            att_rec = cursor.fetchone()

            if not att_rec:
                st.info(f"📍 **{quick_emp}** has not checked in today.")
                if st.button("🟢 Check In Now", key="dash_btn_in"):
                    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("""
                    INSERT INTO attendance (employee_name, check_in, attendance_date)
                    VALUES (?, ?, ?)
                    """, (quick_emp, curr_time, today_iso))
                    conn.commit()
                    st.success(f"✅ {quick_emp} successfully checked in at {curr_time.split()[1]}!")
                    st.rerun()
            else:
                st.success(f"🕒 Checked in at: **{att_rec[1]}**")
                if att_rec[2] is None:
                    if st.button("🔴 Check Out Now", key="dash_btn_out"):
                        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("""
                        UPDATE attendance SET check_out=? WHERE id=?
                        """, (curr_time, att_rec[0]))
                        conn.commit()
                        st.success(f"✅ {quick_emp} checked out at {curr_time.split()[1]}!")
                        st.rerun()
                else:
                    st.info(f"🏁 Checked out at: **{att_rec[2]}**")
        else:
            st.warning("No employees in system yet. Switch to the 'Employees' tab to add staff members.")

        st.markdown("</div>", unsafe_allow_html=True)

    with dash_col_right:
        st.markdown("""
        <div class="content-box">
            <div class="box-title">📅 Today's Live Attendance Feed</div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 12px;">
                Staff currently clocked in for today.
            </div>
        """, unsafe_allow_html=True)

        cursor.execute("""
        SELECT employee_name, check_in, check_out
        FROM attendance
        WHERE attendance_date=?
        ORDER BY id DESC
        """, (today_iso,))
        today_records = cursor.fetchall()

        if today_records:
            today_df = pd.DataFrame(today_records, columns=["Employee", "Check In", "Check Out"])
            today_df["Check Out"] = today_df["Check Out"].fillna("🟢 On Duty")
            st.dataframe(today_df, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance records logged for today yet.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Pending Leaves Direct Section on Dashboard
    if pending_leaves > 0:
        st.markdown("""
        <div class="content-box">
            <div class="box-title">⚠️ Pending Leave Approvals Required</div>
        """, unsafe_allow_html=True)

        cursor.execute("""
        SELECT id, employee_name, leave_type, reason, status
        FROM leaves
        WHERE status='Pending'
        """)
        pending_list = cursor.fetchall()

        for pleave in pending_list:
            l_id, l_name, l_type, l_reason, _ = pleave
            p_col1, p_col2, p_col3, p_col4 = st.columns([2, 2, 4, 2])
            with p_col1:
                st.write(f"**👤 {l_name}**")
            with p_col2:
                st.write(f"🏷️ `{l_type}`")
            with p_col3:
                st.write(f"💬 *{l_reason}*")
            with p_col4:
                btn_app, btn_rej = st.columns(2)
                with btn_app:
                    if st.button("✔", key=f"dash_app_{l_id}", help="Approve Leave"):
                        cursor.execute("UPDATE leaves SET status='Approved' WHERE id=?", (l_id,))
                        conn.commit()
                        st.success("Approved!")
                        st.rerun()
                with btn_rej:
                    if st.button("✖", key=f"dash_rej_{l_id}", help="Reject Leave"):
                        cursor.execute("UPDATE leaves SET status='Rejected' WHERE id=?", (l_id,))
                        conn.commit()
                        st.warning("Rejected!")
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 2. EMPLOYEES TAB
# ==============================================================================

with tab_emp:
    st.markdown("""
    <div class="content-box">
        <div class="box-title">👥 Employee Directory & Staff Management</div>
    """, unsafe_allow_html=True)

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.subheader("➕ Add New Employee")
        emp_name = st.text_input("Full Name", placeholder="e.g. John Doe", key="emp_add_name")
        emp_dept = st.selectbox(
            "Department",
            ["Engineering", "Human Resources", "Marketing", "Sales", "Finance", "Operations", "Design"],
            key="emp_add_dept"
        )

        if st.button("Add Employee", key="btn_add_emp"):
            if emp_name.strip():
                cursor.execute("INSERT INTO employees (name, department) VALUES (?, ?)", (emp_name.strip(), emp_dept))
                conn.commit()
                st.success(f"🎉 **{emp_name}** has been added to {emp_dept}!")
                st.rerun()
            else:
                st.warning("Please enter employee name.")

    with col_list:
        st.subheader("📋 Registered Staff List")
        cursor.execute("SELECT id, name, department FROM employees ORDER BY id DESC")
        emp_records = cursor.fetchall()

        if emp_records:
            emp_df = pd.DataFrame(emp_records, columns=["Employee ID", "Full Name", "Department"])
            st.dataframe(emp_df, use_container_width=True, hide_index=True)

            # Option to delete
            with st.expander("🗑️ Delete Employee Record"):
                del_emp_id = st.selectbox(
                    "Select Employee to Remove",
                    options=[f"{r[0]} - {r[1]} ({r[2]})" for r in emp_records],
                    key="del_emp_select"
                )
                if st.button("Confirm Delete", key="btn_del_emp"):
                    target_id = int(del_emp_id.split(" - ")[0])
                    cursor.execute("DELETE FROM employees WHERE id=?", (target_id,))
                    conn.commit()
                    st.warning("Employee record deleted successfully.")
                    st.rerun()
        else:
            st.info("No employees registered yet. Add your first employee using the form on the left.")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 3. ATTENDANCE TAB
# ==============================================================================

with tab_att:
    st.markdown("""
    <div class="content-box">
        <div class="box-title">⏱️ Real-time Attendance Tracker</div>
    """, unsafe_allow_html=True)

    cursor.execute("SELECT name FROM employees")
    att_emp_list = [row[0] for row in cursor.fetchall()]

    if att_emp_list:
        att_c1, att_c2 = st.columns([1, 2])

        with att_c1:
            st.subheader("Clock In / Out")
            sel_worker = st.selectbox("Select Employee", att_emp_list, key="att_tab_sel_emp")
            today_str_db = str(date.today())

            cursor.execute("""
            SELECT id, employee_name, check_in, check_out FROM attendance
            WHERE employee_name=? AND attendance_date=?
            """, (sel_worker, today_str_db))
            today_log = cursor.fetchone()

            if not today_log:
                st.info(f"⏳ **{sel_worker}** has not checked in today.")
                if st.button("Check In", key="att_tab_in_btn"):
                    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("""
                    INSERT INTO attendance (employee_name, check_in, attendance_date)
                    VALUES (?, ?, ?)
                    """, (sel_worker, stamp, today_str_db))
                    conn.commit()
                    st.success(f"Checked in successfully at {stamp}!")
                    st.rerun()
            else:
                st.success(f"🟢 **Check In Time:** {today_log[2]}")
                if today_log[3] is None:
                    if st.button("Check Out", key="att_tab_out_btn"):
                        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("UPDATE attendance SET check_out=? WHERE id=?", (stamp, today_log[0]))
                        conn.commit()
                        st.success(f"Checked out successfully at {stamp}!")
                        st.rerun()
                else:
                    st.info(f"🏁 **Check Out Time:** {today_log[3]}")

        with att_c2:
            st.subheader("📜 Attendance History")
            cursor.execute("""
            SELECT employee_name, attendance_date, check_in, check_out
            FROM attendance
            ORDER BY id DESC
            """)
            all_att_data = cursor.fetchall()

            if all_att_data:
                att_df = pd.DataFrame(all_att_data, columns=["Employee", "Date", "Check In", "Check Out"])
                att_df["Check Out"] = att_df["Check Out"].fillna("🟢 Active Now")
                st.dataframe(att_df, use_container_width=True, hide_index=True)
            else:
                st.info("No attendance records found.")
    else:
        st.warning("Please add employees first in the 'Employees' tab.")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 4. LEAVE MANAGEMENT TAB
# ==============================================================================

with tab_leave:
    st.markdown("""
    <div class="content-box">
        <div class="box-title">🌴 Leave Application & Approval Management</div>
    """, unsafe_allow_html=True)

    cursor.execute("SELECT name FROM employees")
    leave_emps = [r[0] for r in cursor.fetchall()]

    if leave_emps:
        l_col1, l_col2 = st.columns([1, 2])

        with l_col1:
            st.subheader("📝 Apply for Leave")
            l_employee = st.selectbox("Employee Name", leave_emps, key="leave_tab_emp")
            l_type = st.selectbox(
                "Leave Category",
                ["Casual Leave", "Sick Leave", "Paid Time Off (PTO)", "Maternity/Paternity", "Emergency Leave"],
                key="leave_tab_type"
            )
            l_reason = st.text_area("Reason / Description", placeholder="Briefly specify reason...", key="leave_tab_reason")

            if st.button("Submit Leave Request", key="btn_submit_leave"):
                if l_reason.strip():
                    cursor.execute("""
                    INSERT INTO leaves (employee_name, leave_type, reason, status)
                    VALUES (?, ?, ?, 'Pending')
                    """, (l_employee, l_type, l_reason.strip()))
                    conn.commit()
                    st.success("✅ Leave application submitted with 'Pending' status!")
                    st.rerun()
                else:
                    st.warning("Please provide a reason for the leave.")

        with l_col2:
            st.subheader("📋 Leave Applications & Actions")
            cursor.execute("SELECT id, employee_name, leave_type, reason, status FROM leaves ORDER BY id DESC")
            all_leaves = cursor.fetchall()

            if all_leaves:
                leaves_df = pd.DataFrame(all_leaves, columns=["ID", "Employee", "Type", "Reason", "Status"])
                st.dataframe(leaves_df, use_container_width=True, hide_index=True)

                st.write("")
                st.write("##### ⚡ Quick Status Update")
                pendings = [row for row in all_leaves if row[4] == 'Pending']
                if pendings:
                    act_col1, act_col2, act_col3 = st.columns([2, 1, 1])
                    with act_col1:
                        selected_req = st.selectbox(
                            "Select Pending Request",
                            options=[f"{p[0]} - {p[1]} ({p[2]})" for p in pendings],
                            key="quick_leave_select"
                        )
                    target_leave_id = int(selected_req.split(" - ")[0])
                    with act_col2:
                        if st.button("Approve ✅", key="btn_app_req"):
                            cursor.execute("UPDATE leaves SET status='Approved' WHERE id=?", (target_leave_id,))
                            conn.commit()
                            st.success("Leave Approved!")
                            st.rerun()
                    with act_col3:
                        if st.button("Reject ❌", key="btn_rej_req"):
                            cursor.execute("UPDATE leaves SET status='Rejected' WHERE id=?", (target_leave_id,))
                            conn.commit()
                            st.warning("Leave Rejected.")
                            st.rerun()
            else:
                st.info("No leave applications recorded yet.")
    else:
        st.warning("Please add employees first in the 'Employees' tab.")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 5. PAYROLL TAB
# ==============================================================================

with tab_pay:
    st.markdown("""
    <div class="content-box">
        <div class="box-title">💰 Payroll & Compensation Management</div>
    """, unsafe_allow_html=True)

    cursor.execute("SELECT name FROM employees")
    pay_emps = [r[0] for r in cursor.fetchall()]

    if pay_emps:
        p_c1, p_c2 = st.columns([1, 2])

        with p_c1:
            st.subheader("💵 Record Salary")
            p_employee = st.selectbox("Employee Name", pay_emps, key="pay_tab_emp")
            p_salary = st.number_input(
                "Monthly Salary (₹)",
                min_value=0.0,
                step=5000.0,
                value=35000.0,
                key="pay_tab_amount"
            )

            if st.button("Save Payroll Record", key="btn_save_pay"):
                cursor.execute("""
                INSERT INTO payroll (employee_name, salary, created_date)
                VALUES (?, ?, ?)
                """, (p_employee, p_salary, str(date.today())))
                conn.commit()
                st.success(f"💰 Payroll entry of ₹{p_salary:,.2f} recorded for {p_employee}!")
                st.rerun()

        with p_c2:
            st.subheader("📊 Payroll History & Summary")
            cursor.execute("SELECT employee_name, salary, created_date FROM payroll ORDER BY id DESC")
            pay_records = cursor.fetchall()

            if pay_records:
                pay_df = pd.DataFrame(pay_records, columns=["Employee", "Salary (₹)", "Date Recorded"])
                pay_df["Salary (₹)"] = pay_df["Salary (₹)"].apply(lambda x: f"₹{x:,.2f}")
                st.dataframe(pay_df, use_container_width=True, hide_index=True)
            else:
                st.info("No payroll entries recorded yet.")
    else:
        st.warning("Please add employees first in the 'Employees' tab.")

    st.markdown("</div>", unsafe_allow_html=True)
