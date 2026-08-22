import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# =====================================
# DATABASE CONNECTION
# =====================================

conn = sqlite3.connect("dayflow.db", check_same_thread=False)
cursor = conn.cursor()


# =====================================
# CREATE TABLES
# =====================================

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

# Leave Table
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


# =====================================
# PAGE SETTINGS
# =====================================

st.set_page_config(
    page_title="Dayflow HRMS",
    page_icon="👨‍💼",
    layout="wide"
)

st.title("🌊 Dayflow HRMS")
st.subheader("Human Resource Management System")


# =====================================
# SIDEBAR
# =====================================

menu = st.sidebar.selectbox(
    "Select Menu",
    [
        "Home",
        "Employees",
        "Attendance",
        "Leave",
        "Payroll"
    ]
)


# =====================================
# HOME
# =====================================

if menu == "Home":

    st.header("Welcome to Dayflow HRMS 👋")

    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(DISTINCT employee_name)
    FROM attendance
    WHERE attendance_date=?
    """, (str(date.today()),))

    present_today = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM leaves
    WHERE status='Pending'
    """)

    pending_leaves = cursor.fetchone()[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Employees", total_employees)
    col2.metric("Present Today", present_today)
    col3.metric("Pending Leaves", pending_leaves)

    st.success("HRMS System is Running Successfully! ✅")


# =====================================
# EMPLOYEES
# =====================================

elif menu == "Employees":

    st.header("👥 Employee Management")

    st.subheader("Add New Employee")

    name = st.text_input("Employee Name")
    department = st.text_input("Department")

    if st.button("Add Employee"):

        if name and department:

            cursor.execute("""
            INSERT INTO employees (name, department)
            VALUES (?, ?)
            """, (name, department))

            conn.commit()

            st.success(f"{name} added successfully! ✅")
            st.rerun()

        else:
            st.warning("Please enter all details.")

    st.subheader("Employee List")

    cursor.execute("""
    SELECT * FROM employees
    """)

    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=["ID", "Name", "Department"]
        )

        st.dataframe(df, use_container_width=True)

    else:
        st.info("No employees added yet.")


# =====================================
# ATTENDANCE
# =====================================

elif menu == "Attendance":

    st.header("📅 Attendance Management")

    cursor.execute("SELECT name FROM employees")
    employees = cursor.fetchall()

    if employees:

        employee_names = [emp[0] for emp in employees]

        selected_employee = st.selectbox(
            "Select Employee",
            employee_names
        )

        today = str(date.today())

        cursor.execute("""
        SELECT * FROM attendance
        WHERE employee_name=?
        AND attendance_date=?
        """, (selected_employee, today))

        record = cursor.fetchone()

        if not record:

            if st.button("Check In"):

                current_time = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                cursor.execute("""
                INSERT INTO attendance
                (employee_name, check_in, attendance_date)
                VALUES (?, ?, ?)
                """, (
                    selected_employee,
                    current_time,
                    today
                ))

                conn.commit()

                st.success(
                    f"{selected_employee} checked in successfully! ✅"
                )

                st.rerun()

        else:

            st.info(
                f"Check In Time: {record[2]}"
            )

            if record[3] is None:

                if st.button("Check Out"):

                    current_time = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    cursor.execute("""
                    UPDATE attendance
                    SET check_out=?
                    WHERE id=?
                    """, (
                        current_time,
                        record[0]
                    ))

                    conn.commit()

                    st.success("Checked out successfully! ✅")
                    st.rerun()

            else:

                st.success(
                    f"Check Out Time: {record[3]}"
                )

        # Attendance History
        st.subheader("Attendance History")

        cursor.execute("""
        SELECT employee_name,
               attendance_date,
               check_in,
               check_out
        FROM attendance
        ORDER BY id DESC
        """)

        attendance_data = cursor.fetchall()

        if attendance_data:

            df = pd.DataFrame(
                attendance_data,
                columns=[
                    "Employee",
                    "Date",
                    "Check In",
                    "Check Out"
                ]
            )

            st.dataframe(df, use_container_width=True)

    else:
        st.warning(
            "First add an employee in Employee Management."
        )


# =====================================
# LEAVE
# =====================================

elif menu == "Leave":

    st.header("📝 Leave Management")

    cursor.execute("SELECT name FROM employees")
    employees = cursor.fetchall()

    if employees:

        employee_names = [emp[0] for emp in employees]

        selected_employee = st.selectbox(
            "Select Employee",
            employee_names
        )

        leave_type = st.selectbox(
            "Leave Type",
            [
                "Sick Leave",
                "Casual Leave",
                "Paid Leave"
            ]
        )

        reason = st.text_area("Reason")

        if st.button("Apply Leave"):

            if reason:

                cursor.execute("""
                INSERT INTO leaves
                (employee_name, leave_type, reason, status)
                VALUES (?, ?, ?, ?)
                """, (
                    selected_employee,
                    leave_type,
                    reason,
                    "Pending"
                ))

                conn.commit()

                st.success(
                    "Leave application saved successfully! ✅"
                )

                st.rerun()

            else:
                st.warning("Please enter a reason.")

        # Show Leave History
        st.subheader("Leave Requests")

        cursor.execute("""
        SELECT employee_name,
               leave_type,
               reason,
               status
        FROM leaves
        ORDER BY id DESC
        """)

        leave_data = cursor.fetchall()

        if leave_data:

            df = pd.DataFrame(
                leave_data,
                columns=[
                    "Employee",
                    "Leave Type",
                    "Reason",
                    "Status"
                ]
            )

            st.dataframe(df, use_container_width=True)

        else:
            st.info("No leave requests yet.")

    else:
        st.warning("First add an employee.")


# =====================================
# PAYROLL
# =====================================

elif menu == "Payroll":

    st.header("💰 Payroll Management")

    cursor.execute("SELECT name FROM employees")
    employees = cursor.fetchall()

    if employees:

        employee_names = [emp[0] for emp in employees]

        selected_employee = st.selectbox(
            "Select Employee",
            employee_names
        )

        salary = st.number_input(
            "Monthly Salary",
            min_value=0.0,
            step=1000.0
        )

        if st.button("Save Payroll"):

            cursor.execute("""
            INSERT INTO payroll
            (employee_name, salary, created_date)
            VALUES (?, ?, ?)
            """, (
                selected_employee,
                salary,
                str(date.today())
            ))

            conn.commit()

            st.success(
                f"Payroll for {selected_employee} saved successfully! 💰"
            )

            st.rerun()

        # Payroll History
        st.subheader("Payroll History")

        cursor.execute("""
        SELECT employee_name,
               salary,
               created_date
        FROM payroll
        ORDER BY id DESC
        """)

        payroll_data = cursor.fetchall()

        if payroll_data:

            df = pd.DataFrame(
                payroll_data,
                columns=[
                    "Employee",
                    "Salary",
                    "Date"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True
            )

        else:
            st.info("No payroll records yet.")

    else:
        st.warning("First add an employee.")