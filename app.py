import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai


# ===============================
# LOAD API KEY
# ===============================

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("API Key not found! Check .env file")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"


# ===============================
# SAFE FILE LOADER
# ===============================

def load_file(file):
    if file is None:
        return None

    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)

        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)

        else:
            return None

        # Make Streamlit-safe
        df = df.fillna("")
        for col in df.columns:
            df[col] = df[col].astype(str)

        return df

    except Exception as e:
        st.error(f"File read error: {e}")
        return None


# ===============================
# AI SUMMARY GENERATOR
# ===============================

def generate_summary(data, doc_type):
    if data is None:
        return "No data found."

    prompt = f"""
You are a professional financial analyst.

Document Type: {doc_type}

Analyze this financial data:
{data.to_dict()}

Provide:
• Key Metrics
• Trends
• Risks
• Financial Health
• Recommendations
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"AI Error: {e}"


# ===============================
# VISUALIZATION
# ===============================

def visualize(title, data):
    st.subheader(title)

    if data is not None:
        st.dataframe(data, width="stretch")

        numeric = data.apply(pd.to_numeric, errors="coerce")

        if not numeric.dropna(axis=1, how="all").empty:
            st.line_chart(numeric)
        else:
            st.info("No numeric data available")
    else:
        st.warning("No data uploaded")


# ===============================
# UI
# ===============================

st.set_page_config(
    page_title="AI Financial Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Financial Document Analyzer")
st.markdown("Upload your financial files and get AI-powered insights.")

st.header("📂 Upload Files")

col1, col2, col3 = st.columns(3)

with col1:
    balance_file = st.file_uploader("Balance Sheet", ["csv", "xlsx"])

with col2:
    profit_file = st.file_uploader("Profit & Loss", ["csv", "xlsx"])

with col3:
    cash_file = st.file_uploader("Cash Flow", ["csv", "xlsx"])

st.markdown("---")

if st.button("🚀 Generate Report", width="stretch"):

    with st.spinner("Analyzing financial data..."):

        balance_data = load_file(balance_file)
        profit_data = load_file(profit_file)
        cash_data = load_file(cash_file)

        balance_summary = generate_summary(balance_data, "Balance Sheet")
        profit_summary = generate_summary(profit_data, "Profit and Loss")
        cash_summary = generate_summary(cash_data, "Cash Flow")

        st.success("Analysis Completed ✅")

        tab1, tab2, tab3 = st.tabs([
            "Balance Sheet",
            "Profit & Loss",
            "Cash Flow"
        ])

        with tab1:
            st.write(balance_summary)

        with tab2:
            st.write(profit_summary)

        with tab3:
            st.write(cash_summary)

        st.header("📈 Visualizations")

        visualize("Balance Sheet Data", balance_data)
        visualize("Profit & Loss Data", profit_data)
        visualize("Cash Flow Data", cash_data)

st.markdown("---")
st.markdown(
    "<center>Developed by Appu using Streamlit & Gemini AI ❤️</center>",
    unsafe_allow_html=True
)