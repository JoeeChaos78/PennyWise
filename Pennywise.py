import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

DATA_FILE = "budget_data.csv"

# Load or create the data file
def load_data():
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Notes"])
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Initialize
st.set_page_config(page_title="PennyWise V5", layout="wide")
st.markdown("## 💰 PennyWise V5")
st.markdown("*Where your money meets mastery. Simple. Smart. Saving.*")

# Load current data
df = load_data()

# Tabs layout
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "📝 Entries", "📈 Reports", "⚙️ Guide"])

# ========== 🏠 DASHBOARD ==========
with tab1:
    st.header("📊 Dashboard Overview")

    if df.empty:
        st.info("No data found. Start by adding entries in the Entries tab.")
    else:
        df["Month"] = df["Date"].dt.strftime('%B')
        df["Year"] = df["Date"].dt.year

        total_income = df[df["Type"] == "Income"]["Amount"].sum()
        total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
        total_saving = df[df["Type"] == "Saving"]["Amount"].sum()
        net_balance = total_income - total_expense

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💵 Total Income", f"${total_income:,.2f}")
        col2.metric("💸 Total Expenses", f"${total_expense:,.2f}")
        col3.metric("💰 Savings", f"${total_saving:,.2f}")
        col4.metric("📈 Net Balance", f"${net_balance:,.2f}", delta=f"${(net_balance - total_saving):,.2f}")

        # Monthly bar chart (3D)
        monthly_summary = df.groupby(["Month", "Type"])["Amount"].sum().reset_index()
        fig = px.bar_3d(monthly_summary, x="Month", y="Type", z="Amount", color="Type", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        # Savings trend
        savings_trend = df[df["Type"] == "Saving"].groupby(["Month"])["Amount"].sum().reset_index()
        fig2 = px.line_3d(savings_trend, x="Month", y="Amount", z=[1]*len(savings_trend), title="Monthly Savings Trend")
        st.plotly_chart(fig2, use_container_width=True)

# ========== 📝 ENTRIES ==========
with tab2:
    st.header("📝 Add or Edit Budget Entries")

    st.markdown("#### ➕ Add Entries")
    num_rows = st.number_input("How many rows to add?", min_value=1, max_value=30, value=5)

    new_data = pd.DataFrame({
        "#": list(range(1, num_rows + 1)),
        "Date": [date.today()] * num_rows,
        "Type": ["Expense"] * num_rows,
        "Category": ["" for _ in range(num_rows)],
        "Amount": [0.0 for _ in range(num_rows)],
        "Notes": ["" for _ in range(num_rows)]
    })

    col_config = {
        "#": st.column_config.NumberColumn(label="#", width="small", disabled=True),
        "Date": st.column_config.DateColumn("Date", default=date.today()),
        "Type": st.column_config.SelectboxColumn("Type", options=["Income", "Expense", "Saving"]),
        "Category": st.column_config.TextColumn("Category"),
        "Amount": st.column_config.NumberColumn("Amount", min_value=0.0, step=0.01),
        "Notes": st.column_config.TextColumn("Notes")
    }

    edited = st.data_editor(new_data, column_config=col_config, hide_index=True, use_container_width=True)

    if st.button("💾 Save Entries"):
        valid = edited.dropna(subset=["Date", "Type", "Category", "Amount"])
        if not valid.empty:
            df = pd.concat([df, valid[["Date", "Type", "Category", "Amount", "Notes"]]], ignore_index=True)
            save_data(df)
            st.success("✅ Entries saved successfully!")

    st.markdown("#### ✏️ Edit Existing Entries")
    if not df.empty:
        edited_data = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("🔁 Update All Entries"):
            save_data(edited_data)
            st.success("✅ All entries updated successfully!")

# ========== 📈 REPORTS ==========
with tab3:
    st.header("📊 Reports & Categories")
    if not df.empty:
        with st.expander("📂 View by Category"):
            category_summary = df.groupby(["Category", "Type"])["Amount"].sum().reset_index()
            st.dataframe(category_summary)

        with st.expander("📅 Yearly Summary"):
            yearly_summary = df.groupby(["Year", "Type"])["Amount"].sum().reset_index()
            st.dataframe(yearly_summary)

        st.download_button("📥 Download Full Report", df.to_csv(index=False), file_name="pennywise_report.csv")

# ========== ⚙️ GUIDE ==========
with tab4:
    st.header("📘 User Guide")
    st.markdown("""
    ### 💡 How to Use PennyWise
    - **Dashboard:** See your income, expenses, savings, and overall budget trend.
    - **Entries Tab:** Log multiple entries at once using the editable table. Default date is today; use the date picker to backdate.
    - **Reports Tab:** Explore breakdowns by category, year, and export reports to CSV.
    - **Edits:** You can correct mistakes by editing the entries directly in the editable table.
    - **Coming Soon:**
      - Cloud-based access
      - Allocations to holiday budgets & child expenses
      - Smart savings target alerts
    """)