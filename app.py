import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

st.set_page_config(layout="wide")

# =========================
# LOAD DATA (FIXED)
# =========================
@st.cache_data
def load_data():
    file = "full_aml_system_dataset.xlsx"

    customers = pd.read_excel(file, sheet_name="customers")
    screenings = pd.read_excel(file, sheet_name="screenings")
    aml_hits = pd.read_excel(file, sheet_name="aml_hits")
    sanctions_details = pd.read_excel(file, sheet_name="sanctions_details")
    transactions = pd.read_excel(file, sheet_name="transactions")
    monitoring = pd.read_excel(file, sheet_name="monitoring")
    alerts = pd.read_excel(file, sheet_name="alerts")
    cases = pd.read_excel(file, sheet_name="cases")

    return customers, screenings, aml_hits, sanctions_details, transactions, monitoring, alerts, cases


# =========================
# LOAD ON START (IMPORTANT FIX)
# =========================
customers, screenings, aml_hits, sanctions_details, transactions, monitoring, alerts, cases = load_data()


# =========================
# HELPERS
# =========================
def label_hit(x):
    return "🔴 HIT" if x else "🟢 NO HIT"


def status_color(status):
    if status == "REVIEWED":
        return "🟢 REVIEWED"
    elif status == "NEW":
        return "🟡 NEW"
    elif status == "ESCALATED":
        return "🔴 ESCALATED"
    return status


def fuzzy_search(name, df):
    df = df.copy()  # prevent mutation error
    df["match_score"] = df["full_name"].astype(str).apply(
        lambda x: fuzz.token_sort_ratio(name, x)
    )
    return df[df["match_score"] > 70].sort_values(by="match_score", ascending=False)


# =========================
# SIDEBAR
# =========================
st.sidebar.title("🏦 AML Monitoring System")
menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Manual Lookup",
    "Monitoring",
    "Transactions",
    "Cases"
])


# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Anti-Money Laundering Intelligence Dashboard")

    # ================= KPIs =================
    total_customers = len(customers)
    total_screenings = len(screenings)
    total_alerts = len(alerts)
    high_risk = screenings[screenings["risk_level"] == "HIGH"].shape[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", total_customers)
    col2.metric("Screenings", total_screenings)
    col3.metric("Alerts", total_alerts)
    col4.metric("High Risk Cases", high_risk)

    st.markdown("---")

    # ================= FILTERS =================
    st.subheader("🔍 Filters")

    col1, col2 = st.columns(2)

    with col1:
        risk_filter = st.selectbox("Risk Level", ["All", "LOW", "MEDIUM", "HIGH"])

    with col2:
        status_filter = st.selectbox("Status", ["All", "NEW", "REVIEWED", "ESCALATED"])

    df = screenings.copy()

    if risk_filter != "All":
        df = df[df["risk_level"] == risk_filter]

    if status_filter != "All":
        df = df[df["status"] == status_filter]

    st.markdown("---")

    # ================= CHARTS =================
    col1, col2 = st.columns(2)

    # Risk Distribution
    with col1:
        st.subheader("📊 Risk Level Distribution")
        risk_counts = df["risk_level"].value_counts()
        st.bar_chart(risk_counts)

    # Status Distribution
    with col2:
        st.subheader("📌 Status Distribution")
        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

    # ================= TIME SERIES =================
    st.subheader("📈 Screening Trend Over Time")

    df["screening_date"] = pd.to_datetime(df["screening_date"])
    trend = df.groupby(df["screening_date"].dt.date).size()

    st.line_chart(trend)

    # ================= AML HIT ANALYSIS =================
    st.subheader("🚨 AML Hits by Type")

    hit_counts = aml_hits["list_type"].value_counts()
    st.bar_chart(hit_counts)

    # ================= TOP HIGH RISK CUSTOMERS =================
    st.subheader("🔥 Top High-Risk Customers")

    merged = customers.merge(screenings, on="customer_id", how="inner")
    high_risk_df = merged[merged["risk_level"] == "HIGH"]

    st.dataframe(high_risk_df[[
        "customer_id",
        "full_name",
        "country",
        "risk_level",
        "risk_score"
    ]].head(20))

    # ================= ALERT TABLE =================
    st.subheader("🚨 Recent Alerts")

    st.dataframe(alerts.sort_values(by="created_at", ascending=False).head(20))

# =========================
# MANUAL LOOKUP
# =========================
elif menu == "Manual Lookup":

    st.title("🔎 New Manual Lookup")

    tabs = st.tabs(["Email", "Phone", "IP", "Card BIN", "AML", "Transaction"])

    # ================= EMAIL =================
    with tabs[0]:
        email = st.text_input("Enter Email")

        if st.button("Check Email"):
            if "fraud" in email.lower():
                st.error("🔴 High Risk Email Detected")
            else:
                st.success("🟢 Email Looks Safe")

    # ================= PHONE =================
    with tabs[1]:
        phone = st.text_input("Enter Phone Number")

        if st.button("Check Phone"):
            if phone.startswith("+234"):
                st.warning("🟡 Medium Risk Region")
            else:
                st.success("🟢 Phone Looks Safe")

    # ================= IP =================
    with tabs[2]:
        ip = st.text_input("Enter IP Address")

        if st.button("Check IP"):
            if ip.startswith("192."):
                st.success("🟢 Internal IP")
            else:
                st.error("🔴 Suspicious IP")

    # ================= CARD BIN =================
    with tabs[3]:
        bin_number = st.text_input("Enter Card BIN")

        if st.button("Check BIN"):
            if bin_number.startswith("4"):
                st.success("🟢 VISA Card")
            else:
                st.warning("🟡 Unknown BIN")

    # ================= AML =================
    with tabs[4]:
        name = st.text_input("Full Name")

        if st.button("Run AML Lookup"):

            results = fuzzy_search(name, customers)

            if results.empty:
                st.error("No customer found")
            else:
                st.success("Customer Found")

                merged = results.merge(screenings, on="customer_id", how="left") \
                                .merge(aml_hits, on="screening_id", how="left")

                # FILTERS
                col1, col2 = st.columns(2)

                with col1:
                    type_filter = st.selectbox("Select type", ["All", "SANCTION", "CRIME", "PEP", "WATCHLIST"])

                with col2:
                    status_filter = st.selectbox("Select status", ["All", "NEW", "REVIEWED", "ESCALATED"])

                if type_filter != "All":
                    merged = merged[merged["list_type"].str.contains(type_filter, case=False, na=False)]

                if status_filter != "All":
                    merged = merged[merged["status"] == status_filter]

                # ADD FLAGS
                merged["HIT"] = merged["hit_id"].notna().apply(label_hit)
                merged["STATUS"] = merged["status"].apply(status_color)

                st.subheader("AML Results")
                st.dataframe(merged.head(50))

                # DETAILS PANEL
                if not merged.empty:
                    row = merged.iloc[0]

                    st.subheader("Details")
                    st.write(f"**Name:** {row.get('full_name', '')}")
                    st.write(f"**Risk Level:** {row.get('risk_level', '')}")
                    st.write(f"**Source:** {row.get('source', '')}")
                    st.write(f"**Match Score:** {row.get('match_score', 'N/A')}")

                    if st.button("Mark as False Match"):
                        st.warning("Marked as False Match")

                    st.toggle("Monitoring", value=True)

    # ================= TRANSACTION =================
    with tabs[5]:
        amount = st.number_input("Transaction Amount", min_value=0)

        if st.button("Analyze Transaction"):
            if amount > 1000000:
                st.error("🚨 HIGH RISK TRANSACTION")
            elif amount > 500000:
                st.warning("⚠️ Medium Risk Transaction")
            else:
                st.success("🟢 Low Risk Transaction")


# =========================
# MONITORING
# =========================
elif menu == "Monitoring":
    st.title("📡 Monitoring Dashboard")

    df = screenings.copy()
    df["STATUS"] = df["status"].apply(status_color)

    st.dataframe(df[[
        "customer_id",
        "screening_date",
        "risk_score",
        "STATUS"
    ]].head(100))


# =========================
# TRANSACTIONS
# =========================
elif menu == "Transactions":
    st.title("💳 Transactions")

    st.dataframe(transactions.head(100))


# =========================
# CASES
# =========================
elif menu == "Cases":
    st.title("📁 Case Management")

    st.dataframe(cases.head(100))