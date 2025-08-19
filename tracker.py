import streamlit as st
import pandas as pd

st.set_page_config(page_title="Activity & Automation Tracker", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Upcoming Activities", "Automations", "Server List Upload"])

# Load data functions
def load_csv(file):
    return pd.read_csv(file)

# Page 1: Upcoming Activities
if page == "Upcoming Activities":
    st.title("📅 Upcoming Activities")
    uploaded_file = st.file_uploader("Upload Activities CSV", type="csv")
    if uploaded_file:
        df = load_csv(uploaded_file)
        st.data_editor(df, num_rows="dynamic", use_container_width=True)
    else:
        st.info("Please upload a CSV file with activity details.")

# Page 2: Automations
elif page == "Automations":
    st.title("🤖 Automation Details")
    uploaded_file = st.file_uploader("Upload Automations CSV", type="csv")
    if uploaded_file:
        df = load_csv(uploaded_file)
        st.data_editor(df, num_rows="dynamic", use_container_width=True)
    else:
        st.info("Please upload a CSV file with automation details.")

# Page 3: Server List Upload
elif page == "Server List Upload":
    st.title("🖥️ Server List Upload")
    uploaded_file = st.file_uploader("Upload Server List CSV", type="csv")
    if uploaded_file:
        df = load_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)
        st.success("Server list uploaded successfully!")
    else:
        st.info("Please upload a CSV file with server name, environment, and category.")
