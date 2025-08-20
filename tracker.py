import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

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

    if not df_activities.empty:
        # Convert Scheduled Date to datetime
        if 'Scheduled Date' in df_activities.columns:
            df_activities['Scheduled Date'] = pd.to_datetime(df_activities['Scheduled Date'], errors='coerce')
            df_activities['Month'] = df_activities['Scheduled Date'].dt.strftime('%B %Y')

        # Pie Chart: Task Status Distribution
        if 'Status' in df_activities.columns:
            st.subheader("📊 Task Status Distribution")
            status_counts = df_activities['Status'].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)

        # Bar Chart: Tasks per Month
        if 'Month' in df_activities.columns:
            st.subheader("📊 Tasks per Month")
            task_counts = df_activities['Month'].value_counts().sort_index()
            st.bar_chart(task_counts)

        # Bar Chart: Estimated vs Actual Hours
        if 'Estimated Hours' in df_activities.columns and 'Actual Hours' in df_activities.columns:
            st.subheader("📊 Estimated vs Actual Hours per Activity")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            activities = df_activities['Activity Name']
            estimated = df_activities['Estimated Hours']
            actual = df_activities['Actual Hours']
            ax2.bar(activities, estimated, label='Estimated Hours', alpha=0.7)
            ax2.bar(activities, actual, label='Actual Hours', alpha=0.7)
            ax2.set_ylabel("Hours")
            ax2.set_title("Estimated vs Actual Hours per Activity")
            ax2.legend()
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig2)

        # Monthly Dashboard
        if 'Month' in df_activities.columns:
            st.subheader("📆 Monthly Dashboard")
            months = df_activities['Month'].dropna().unique()
            selected_month = st.selectbox("Select Month", sorted(months))
            filtered_df = df_activities[df_activities['Month'] == selected_month]
            st.dataframe(filtered_df.drop(columns=['Month'], errors='ignore'), use_container_width=True)

    # Editable Table and Save
    st.subheader("✏️ Edit Activities")
    edited_df = st.data_editor(df_activities, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes", key="save_activities"):
        save_csv(edited_df.drop(columns=['Month'], errors='ignore'), activity_file)
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
