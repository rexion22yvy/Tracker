import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(page_title="Activity & Automation Tracker", layout="wide")

# Define file paths
activity_file = "upcoming_activities.csv"
automation_file = "automations.csv"
server_file = "server_list.csv"

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upcoming Activities", "Automations", "Server List Upload"])

# Function to load CSV with error handling
def load_csv(uploaded_file, default_file):
    try:
        if uploaded_file is not None:
            return pd.read_csv(uploaded_file)
        elif os.path.exists(default_file):
            return pd.read_csv(default_file)
        else:
            return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.warning("The uploaded file is empty or invalid. Showing empty table.")
        return pd.DataFrame()

# Function to save CSV
def save_csv(df, file_path):
    df.to_csv(file_path, index=False)

# Page 1: Upcoming Activities
if page == "Upcoming Activities":
    st.title("📅 Upcoming Activities")
    st.markdown("Upload a CSV file or edit the existing data. Click 'Save Changes' to store updates.")
    uploaded_file = st.file_uploader("Upload Activities CSV", type="csv", key="activities")
    df_activities = load_csv(uploaded_file, activity_file)
    edited_df = st.data_editor(df_activities, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes", key="save_activities"):
        save_csv(edited_df, activity_file)
        st.success("Changes saved to upcoming_activities.csv")

# Page 2: Automations
elif page == "Automations":
    st.title("🤖 Automation Details")
    st.markdown("Upload a CSV file or edit the existing data. Click 'Save Changes' to store updates.")
    uploaded_file = st.file_uploader("Upload Automations CSV", type="csv", key="automations")
    df_automations = load_csv(uploaded_file, automation_file)
    edited_df = st.data_editor(df_automations, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes", key="save_automations"):
        save_csv(edited_df, automation_file)
        st.success("Changes saved to automations.csv")

# Page 3: Server List Upload
elif page == "Server List Upload":
    st.title("🖥️ Server List Upload")
    st.markdown("Upload a CSV file or edit the existing data. Click 'Save Changes' to store updates.")
    uploaded_file = st.file_uploader("Upload Server List CSV", type="csv", key="servers")
    df_servers = load_csv(uploaded_file, server_file)
    edited_df = st.data_editor(df_servers, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes", key="save_servers"):
        save_csv(edited_df, server_file)
        st.success("Changes saved to server_list.csv")
