import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Set page config
st.set_page_config(page_title="PennyWise", layout="wide")

# Load dataset or initialize
def load_data():
    try:
        return pd.read_csv("budget_data.csv", parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Notes", "Section"])

df = load_data()

st.markdown("## 💰 PennyWise")
st.markdown("### _Where your money meets mastery — Simple. Smart. Saving._")

# TABS Layout
tabs = st.tabs(["📊 Dashboard", "📝 Entries", "🏖️ Holiday Budget", "👶 Child Expenses", "⚙️ Settings"])

# --- Dashboard Tab ---
with tabs[0]:
    st.subheader("📊 Dashboard Overview")

    if df.empty:
        st.info("No data yet. Add entries in the Entries tab.")
    else:
        col1, col2, col3 = st.columns(3)
        total_income = df[df["Type"] == "Income"]["Amount"].sum()
        total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
        total_saving = df[df["Type"] == "Saving"]["Amount"].sum()
        balance = total_income - total_expense

        col1.metric("Total Income", f"${total_income:,.2f}")
        col2.metric("Total Expenses", f"${total_expense:,.2f}")
        col3.metric("Balance", f"${balance:,.2f}")

        # 3D Chart: Pie by Type
        st.plotly_chart(
            px.pie(df, names="Type", values="Amount", title="Expense Breakdown by Type", hole=0.3).update_traces(textinfo='percent+label'),
            use_container_width=True
        )

        # 3D Chart: Bar by Category
        st.plotly_chart(
            px.bar_3d(df, x="Category", y="Amount", z="Type", title="Spending by Category and Type").update_layout(height=400),
            use_container_width=True
        )

# --- Entries Tab ---
with tabs[1]:
    st.subheader("📝 Add/Edit Entries")
    num_rows = st.number_input("Rows to add", min_value=1, max_value=30, value=5)

    # Prepare new empty rows
    new_data = pd.DataFrame({
        "#": list(range(1, num_rows + 1)),
        "Date": [date.today()] * num_rows,
        "Type": ["Expense"] * num_rows,
        "Category": ["" for _ in range(num_rows)],
        "Amount": [0.0] * num_rows,
        "Notes": ["" for _ in range(num_rows)],
        "Section": ["Main"] * num_rows,
    })

    edited = st.data_editor(
        new_data,
        hide_index=True,
        use_container_width=True,
        column_config={
            "#": st.column_config.NumberColumn(label="#", disabled=True),
            "Date": st.column_config.DateColumn("Date", default=date.today()),
            "Type": st.column_config.SelectboxColumn("Type", options=["Income", "Expense", "Saving"]),
            "Category": st.column_config.TextColumn("Category"),
            "Amount": st.column_config.NumberColumn("Amount", min_value=0.0, step=0.01),
            "Notes": st.column_config.TextColumn("Notes"),
            "Section": st.column_config.SelectboxColumn("Section", options=["Main", "Holiday", "Child"]),
        }
    )

    if st.button("💾 Save Entries"):
        valid = edited.dropna(subset=["Date", "Type", "Category", "Amount"])
        if not valid.empty:
            df = pd.concat([df, valid], ignore_index=True)
            df.to_csv("budget_data.csv", index=False)
            st.success("✅ Entries saved.")
        else:
            st.warning("⚠️ Please complete required fields.")

    # Optional Edit Existing
    st.divider()
    st.subheader("🔁 Existing Entries")
    if not df.empty:
        edited_existing = st.data_editor(df, key="edit_existing", use_container_width=True)
        if st.button("💾 Save Edits"):
            edited_existing.to_csv("budget_data.csv", index=False)
            st.success("✅ Updates saved.")
    else:
        st.info("No existing entries.")

# --- Holiday Budget Tab ---
with tabs[2]:
    st.subheader("🏖️ Holiday Budget Tracker")
    holiday_df = df[df["Section"] == "Holiday"]
    st.write("Total Allocated:", f"${holiday_df['Amount'].sum():,.2f}")
    st.dataframe(holiday_df, use_container_width=True)

# --- Child Expenses Tab ---
with tabs[3]:
    st.subheader("👶 Child Expenses Tracker")
    child_df = df[df["Section"] == "Child"]
    st.write("Total Allocated:", f"${child_df['Amount'].sum():,.2f}")
    st.dataframe(child_df, use_container_width=True)

# --- Settings Tab ---
with tabs[4]:
    st.subheader("⚙️ App Settings & Info")
    st.info("✔️ This version of PennyWise supports editable tables, graph analytics, and separate budget sections.")
    st.markdown("App version: **V5 - PennyWise**")
    st.markdown("Data stored locally in `budget_data.csv`. Backup regularly!")
