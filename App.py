import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="HSE AI Agent", layout="wide")

st.title("🧠 HSE AI Decision Support Agent")

# ==============================
# FILE UPLOAD
# ==============================
uploaded_file = st.file_uploader("Upload Incident Excel File", type=["xlsx"])

if uploaded_file:

    # Show file name
    st.success(f"Loaded File: {uploaded_file.name}")

    # ==============================
    # READ EXCEL (ONLY XLSX - STABLE)
    # ==============================
    df = pd.read_excel(uploaded_file, engine='openpyxl')

    # ==============================
    # DATA CLEANING
    # ==============================
    df.columns = df.columns.str.strip()

    # Convert Date
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Month'] = df['Date'].dt.month_name()
        df['Year'] = df['Date'].dt.year

    # Create Age Band
    if 'Age' in df.columns:
        bins = [18, 25, 35, 45, 60]
        labels = ['18-25', '26-35', '36-45', '46+']
        df['Age Band'] = pd.cut(df['Age'], bins=bins, labels=labels)

    # ==============================
    # SIDEBAR FILTERS
    # ==============================
    st.sidebar.header("Filters")

    if 'Department' in df.columns:
        dept = st.sidebar.multiselect("Department", df['Department'].dropna().unique())
        if dept:
            df = df[df['Department'].isin(dept)]

    if 'Age Band' in df.columns:
        age_band = st.sidebar.multiselect("Age Band", df['Age Band'].dropna().unique())
        if age_band:
            df = df[df['Age Band'].isin(age_band)]

    if 'Year' in df.columns:
        year = st.sidebar.multiselect("Year", df['Year'].dropna().unique())
        if year:
            df = df[df['Year'].isin(year)]

    # ==============================
    # KPIs
    # ==============================
    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    total_incidents = len(df)

    if 'RA Score' in df.columns:
        high_risk = df[df['RA Score'] >= 10].shape[0]
    else:
        high_risk = 0

    if 'Department' in df.columns and not df['Department'].isna().all():
        top_dept = df['Department'].value_counts().idxmax()
    else:
        top_dept = "N/A"

    if 'Nature of Injury' in df.columns and not df['Nature of Injury'].isna().all():
        top_injury = df['Nature of Injury'].value_counts().idxmax()
    else:
        top_injury = "N/A"

    col1.metric("Total Incidents", total_incidents)
    col2.metric("High Risk Incidents", high_risk)
    col3.metric("Top Department", top_dept)
    col4.metric("Top Injury Type", top_injury)

    # ==============================
    # CHARTS
    # ==============================
    st.subheader("📈 Analysis Dashboard")

    col1, col2 = st.columns(2)

    if 'Department' in df.columns:
        dept_counts = df['Department'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Count']
        fig1 = px.bar(dept_counts, x='Count', y='Department',
                      orientation='h', title="Incidents by Department")
        col1.plotly_chart(fig1, use_container_width=True)

    if 'Month' in df.columns:
        month_counts = df['Month'].value_counts().reset_index()
        month_counts.columns = ['Month', 'Count']
        fig2 = px.line(month_counts, x='Month', y='Count',
                       title="Incidents by Month")
        col2.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    if 'RA Score' in df.columns:
        fig3 = px.histogram(df, x='RA Score', title="Risk Score Distribution")
        col3.plotly_chart(fig3, use_container_width=True)

    if 'Root Cause Category' in df.columns:
        cause_counts = df['Root Cause Category'].value_counts().head(10).reset_index()
        cause_counts.columns = ['Root Cause', 'Count']
        fig4 = px.bar(cause_counts, x='Count', y='Root Cause',
                      orientation='h', title="Top Root Causes")
        col4.plotly_chart(fig4, use_container_width=True)

    # ==============================
    # AI INSIGHTS
    # ==============================
    st.subheader("🤖 AI Insights & Recommendations")

    insights = []

    if 'Department' in df.columns:
        top_dept = df['Department'].value_counts().idxmax()
        insights.append(f"🔍 Highest incidents recorded in {top_dept} department.")

    if 'Nature of Injury' in df.columns:
        injury = df['Nature of Injury'].value_counts().idxmax()
        insights.append(f"⚠️ Most common injury type is {injury}.")

    if 'RA Score' in df.columns:
        avg_risk = df['RA Score'].mean()
        if avg_risk > 8:
            insights.append("🚨 Overall risk level is high. Immediate action required.")
        else:
            insights.append("✅ Risk levels are generally moderate.")

    if 'Root Cause Category' in df.columns:
        cause = df['Root Cause Category'].value_counts().idxmax()
        insights.append(f"📌 Main root cause identified: {cause}.")

    insights.append("✅ Recommendation: Conduct targeted safety training.")
    insights.append("✅ Recommendation: Review high-risk activities.")
    insights.append("✅ Recommendation: Improve PPE compliance monitoring.")

    for i in insights:
        st.write(i)

    # ==============================
    # DATA PREVIEW
    # ==============================
    st.subheader("📄 Data Preview")
    st.dataframe(df)

else:
    st.info("Please upload your Excel (.xlsx) file to start analysis.")
