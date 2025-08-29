import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Activity & Automation Tracker", layout="wide")

activity_file = "upcoming_activities.csv"
automation_file = "automations.csv"
server_file = "server_list.csv"

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upcoming Activities", "Automations", "Server List Upload", "Charts Dashboard"])

def load_data(uploaded_file, default_file):
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.xlsx'):
                return pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                return pd.read_csv(uploaded_file)
        elif os.path.exists(default_file):
            return pd.read_csv(default_file)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.warning(f"Error loading file: {e}")
        return pd.DataFrame()

def save_csv(df, file_path):
    df.to_csv(file_path, index=False)

# ---------------- Upcoming Activities ----------------
if page == "Upcoming Activities":
    st.title("📅 Upcoming Activities")
    uploaded_file = st.file_uploader("Upload Activities File (CSV or Excel)", type=["csv", "xlsx"], key="activities")
    df_activities = load_data(uploaded_file, activity_file)

    if not df_activities.empty:
        if "Scheduled Date" in df_activities.columns:
            df_activities["Scheduled Date"] = pd.to_datetime(df_activities["Scheduled Date"], errors="coerce")
            df_activities["Month"] = df_activities["Scheduled Date"].dt.strftime("%B %Y")

        st.subheader("📆 Monthly Dashboard")
        months = df_activities["Month"].dropna().unique()
        selected_month_dashboard = st.selectbox("Select Month to View Activities", sorted(months), key="dashboard_month")
        filtered_df = df_activities[df_activities["Month"] == selected_month_dashboard]
        st.dataframe(filtered_df.drop(columns=["Month"], errors="ignore"), use_container_width=True)

    st.subheader("✏️ Edit Activities")
    editable_df = df_activities.copy()

    # Ensure Scheduled Date is datetime for editing
    if "Scheduled Date" in editable_df.columns:
        editable_df["Scheduled Date"] = pd.to_datetime(editable_df["Scheduled Date"], errors="coerce")

    # Drop Month column before editing
    if "Month" in editable_df.columns:
        editable_df.drop(columns=["Month"], inplace=True)

    # Ensure Status is string
    if "Status" in editable_df.columns:
        editable_df["Status"] = editable_df["Status"].astype(str)

    edited_df = st.data_editor(
        editable_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Scheduled Date": st.column_config.DateColumn("Scheduled Date"),
            "Status": st.column_config.SelectboxColumn("Status", options=["Planned", "Inprogress", "Completed"])
        }
    )

    # Recalculate Month column
    if "Scheduled Date" in edited_df.columns:
        edited_df["Month"] = edited_df["Scheduled Date"].dt.strftime("%B %Y")

    if st.button("Save Changes", key="save_activities"):
        save_csv(edited_df, activity_file)
        st.success("Changes saved to upcoming_activities.csv")

# ---------------- Automations ----------------
elif page == "Automations":
    st.title("🤖 Automation Details")
    uploaded_file = st.file_uploader("Upload Automations File (CSV or Excel)", type=["csv", "xlsx"], key="automations")
    df_automations = load_data(uploaded_file, automation_file)
    edited_df = st.data_editor(df_automations, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes", key="save_automations"):
        save_csv(edited_df, automation_file)
        st.success("Changes saved to automations.csv")

# ---------------- Server List Upload ----------------
elif page == "Server List Upload":
    st.title("🖥️ Server List Upload")
    uploaded_file = st.file_uploader("Upload Server List File (CSV or Excel)", type=["csv", "xlsx"], key="servers")
    df_servers = load_data(uploaded_file, server_file)
    edited_df = st.data_editor(df_servers, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes", key="save_servers"):
        save_csv(edited_df, server_file)
        st.success("Changes saved to server_list.csv")

# ---------------- Charts Dashboard ----------------
elif page == "Charts Dashboard":
    st.title("📊 Charts Dashboard")
    df_activities = load_data(None, activity_file)

    if not df_activities.empty and "Scheduled Date" in df_activities.columns:
        df_activities["Scheduled Date"] = pd.to_datetime(df_activities["Scheduled Date"], errors="coerce")
        df_activities["Month"] = df_activities["Scheduled Date"].dt.strftime("%B %Y")

        if "Status" in df_activities.columns:
            st.subheader("Task Status Distribution")
            status_counts = df_activities["Status"].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90)
            ax1.axis("equal")
            st.pyplot(fig1)

        if "Month" in df_activities.columns:
            st.subheader("Tasks per Month")
            task_counts = df_activities["Month"].value_counts().sort_index()
            st.bar_chart(task_counts)

        if "Estimated Hours" in df_activities.columns and "Actual Hours" in df_activities.columns:
            st.subheader("Estimated vs Actual Hours per Activity")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            activities = df_activities["Activity Name"].astype(str)
            estimated = df_activities["Estimated Hours"]
            actual = df_activities["Actual Hours"]
            ax2.bar(activities, estimated, label="Estimated Hours", alpha=0.7)
            ax2.bar(activities, actual, label="Actual Hours", alpha=0.7)
            ax2.set_ylabel("Hours")
            ax2.set_title("Estimated vs Actual Hours per Activity")
            ax2.legend()
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig2)

        if "Resource Name" in df_activities.columns:
            st.subheader("Resource Hours")
            months = df_activities["Month"].dropna().unique()
            selected_month = st.selectbox("Select Month for Resource Hours", sorted(months), key="resource_month")
            filtered_data = df_activities[df_activities["Month"] == selected_month]
            grouped = filtered_data.groupby("Resource Name")[["Estimated Hours", "Actual Hours"]].sum().reset_index()
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            x = grouped["Resource Name"].astype(str)
            ax3.bar(x, grouped["Estimated Hours"], label="Estimated Hours", alpha=0.7)
            ax3.bar(x, grouped["Actual Hours"], label="Actual Hours", alpha=0.7)
            ax3.set_ylabel("Hours")
            ax3.set_title(f"Resource Hours - {selected_month}")
            ax3.legend()
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig3)
    else:
        st.info("No valid activity data found. Please upload a file with a 'Scheduled Date' column.")
