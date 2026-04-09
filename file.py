import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(layout="wide")

# =========================
# LOAD DATA
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
    df = df.copy()
    df["match_score"] = df["full_name"].astype(str).apply(
        lambda x: fuzz.token_sort_ratio(name, x)
    )
    return df[df["match_score"] > 70].sort_values(by="match_score", ascending=False)


# =========================
# ML MODEL
# =========================
@st.cache_resource
def train_model(screenings):
    df = screenings.dropna(subset=["risk_level"]).copy()

    df["risk_encoded"] = df["risk_level"].map({
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2
    })

    X = df[["risk_score"]]
    y = df["risk_encoded"]

    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)

    return model


model = train_model(screenings)


def predict_risk(score):
    pred = model.predict([[score]])[0]
    return ["LOW", "MEDIUM", "HIGH"][pred]


# =========================
# ALERT ENGINE
# =========================
def generate_alerts(df):
    df = df.copy()

    df["auto_alert"] = df["risk_score"].apply(
        lambda x: "🚨 HIGH RISK ALERT" if x > 80 else
                  "⚠️ MEDIUM RISK ALERT" if x > 60 else
                  "🟢 LOW RISK"
    )
    return df


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
    st.title("📊 AML Intelligence Dashboard")

    total_customers = len(customers)
    total_screenings = len(screenings)
    total_alerts = len(alerts)
    high_risk = screenings[screenings["risk_level"] == "HIGH"].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Customers", total_customers)
    col2.metric("Screenings", total_screenings)
    col3.metric("Alerts", total_alerts)
    col4.metric("High Risk", high_risk)

    st.markdown("---")

    # Filters
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

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(df, x="risk_level", color="risk_level", title="Risk Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(df, names="status", title="Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Time trend
    df["screening_date"] = pd.to_datetime(df["screening_date"])
    trend = df.groupby(df["screening_date"].dt.date).size().reset_index(name="count")

    fig = px.line(trend, x="screening_date", y="count", title="Screening Trend")
    st.plotly_chart(fig, use_container_width=True)

    # AML Hits
    fig = px.bar(aml_hits, x="list_type", color="list_type", title="AML Hit Types")
    st.plotly_chart(fig, use_container_width=True)

    # Geo Map
    st.subheader("🌍 Geo Risk Map")
    geo_df = customers.merge(screenings, on="customer_id")
    country_risk = geo_df.groupby("country")["risk_score"].mean().reset_index()

    fig = px.choropleth(
        country_risk,
        locations="country",
        locationmode="country names",
        color="risk_score",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig, use_container_width=True)


# =========================
# MANUAL LOOKUP
# =========================
elif menu == "Manual Lookup":

    st.title("🔎 New Manual Lookup")

    tabs = st.tabs(["Email", "Phone", "IP", "Card BIN", "AML", "Transaction"])

    with tabs[0]:
        email = st.text_input("Email")
        if st.button("Check Email"):
            st.error("🔴 Risky Email") if "fraud" in email else st.success("Safe")

    with tabs[1]:
        phone = st.text_input("Phone")
        if st.button("Check Phone"):
            st.warning("Medium Risk") if phone.startswith("+234") else st.success("Safe")

    with tabs[2]:
        ip = st.text_input("IP")
        if st.button("Check IP"):
            st.error("Suspicious") if not ip.startswith("192") else st.success("Internal")

    with tabs[3]:
        bin = st.text_input("Card BIN")
        if st.button("Check BIN"):
            st.success("VISA") if bin.startswith("4") else st.warning("Unknown")

    with tabs[4]:
        name = st.text_input("Full Name")

        if st.button("Run AML Lookup"):

            results = fuzzy_search(name, customers)

            if results.empty:
                st.error("No match found")
            else:
                merged = results.merge(screenings, on="customer_id", how="left")\
                                .merge(aml_hits, on="screening_id", how="left")

                merged["predicted_risk"] = merged["risk_score"].apply(predict_risk)
                merged = generate_alerts(merged)

                merged["HIT"] = merged["hit_id"].notna().apply(label_hit)
                merged["STATUS"] = merged["status"].apply(status_color)

                st.dataframe(merged.head(50))

                if merged.iloc[0]["risk_score"] > 80:
                    st.error("🚨 HIGH RISK ALERT GENERATED")

    with tabs[5]:
        amt = st.number_input("Amount", min_value=0)
        if st.button("Analyze"):
            st.error("HIGH RISK") if amt > 1000000 else st.success("LOW RISK")


# =========================
# MONITORING
# =========================
elif menu == "Monitoring":
    st.title("📡 Monitoring")
    st.dataframe(screenings.head(100))


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
    st.title("📁 Cases")
    st.dataframe(cases.head(100))