import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Activity & ME Tracker", layout="wide")

# File paths
activity_file = "upcoming_activities.csv"
automation_file = "automations.csv"
me_file = "sample_me_hours.csv"

# Load CSV files
@st.cache_data
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception:
        return pd.DataFrame()

df_activities = load_csv(activity_file)
df_automations = load_csv(automation_file)
df_me = load_csv(me_file)

# Convert date columns and extract month
if "Scheduled Date" in df_activities.columns:
    df_activities["Scheduled Date"] = pd.to_datetime(df_activities["Scheduled Date"], errors="coerce")
    df_activities["Month"] = df_activities["Scheduled Date"].dt.strftime("%B %Y")

if "ME Month" in df_me.columns:
    df_me["ME Month"] = pd.to_datetime(df_me["ME Month"], errors="coerce")
    df_me["Month"] = df_me["ME Month"].dt.strftime("%B %Y")

# Tabs for navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Activity Dashboard", "Automations", "ME Hours", "Charts Dashboard", "MOM Dashboard"])

# ---------------- Activity Dashboard ----------------
with tab1:
    st.title("📅 Activity Dashboard")
    uploaded_file = st.file_uploader("Upload Activities File (CSV or Excel)", type=["csv", "xlsx"], key="activities")
    if uploaded_file:
        if uploaded_file.name.endswith('.xlsx'):
            df_activities = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df_activities = pd.read_csv(uploaded_file)
        df_activities["Scheduled Date"] = pd.to_datetime(df_activities["Scheduled Date"], errors="coerce")
        df_activities["Month"] = df_activities["Scheduled Date"].dt.strftime("%B %Y")

    if not df_activities.empty:
        st.subheader("📆 Monthly Dashboard")
        months = df_activities["Month"].dropna().unique()
        selected_month_dashboard = st.selectbox("Select Month to View Activities", sorted(months), key="dashboard_month")
        filtered_df = df_activities[df_activities["Month"] == selected_month_dashboard]
        st.dataframe(filtered_df.drop(columns=["Month"], errors="ignore"), use_container_width=True)

        st.subheader("✏️ Edit Activities")
        editable_df = df_activities.copy()
        if "Scheduled Date" in editable_df.columns:
            editable_df["Scheduled Date"] = pd.to_datetime(editable_df["Scheduled Date"], errors="coerce")
        if "Month" in editable_df.columns:
            editable_df.drop(columns=["Month"], inplace=True)
        if "Status" in editable_df.columns:
            editable_df["Status"] = editable_df["Status"].astype(str)
        if "Implemented Servers" not in editable_df.columns:
            editable_df["Implemented Servers"] = ""

        edited_df = st.data_editor(
            editable_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Scheduled Date": st.column_config.DateColumn("Scheduled Date"),
                "Status": st.column_config.SelectboxColumn("Status", options=["Planned", "Inprogress", "Completed"]),
                "Implemented Servers": st.column_config.TextColumn("Implemented Servers")
            }
        )

        if "Scheduled Date" in edited_df.columns:
            edited_df["Month"] = pd.to_datetime(edited_df["Scheduled Date"], errors="coerce").dt.strftime("%B %Y")

        if st.button("Save Changes", key="save_activities"):
            edited_df.to_csv(activity_file, index=False)
            st.success("Changes saved to upcoming_activities.csv")

# ---------------- Automations ----------------
with tab2:
    st.title("🤖 Automation Details")
    uploaded_file = st.file_uploader("Upload Automations File (CSV or Excel)", type=["csv", "xlsx"], key="automations")
    if uploaded_file:
        if uploaded_file.name.endswith('.xlsx'):
            df_automations = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df_automations = pd.read_csv(uploaded_file)

    edited_df = st.data_editor(df_automations, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes", key="save_automations"):
        edited_df.to_csv(automation_file, index=False)
        st.success("Changes saved to automations.csv")

# ---------------- ME Hours ----------------
with tab3:
    st.title("🧮 ME Hours Tracker")
    uploaded_file = st.file_uploader("Upload ME Hours File (CSV or Excel)", type=["csv", "xlsx"], key="me_hours")
    if uploaded_file:
        if uploaded_file.name.endswith('.xlsx'):
            df_me = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df_me = pd.read_csv(uploaded_file)

    for col in ["Resource 1 Hours", "Resource 2 Hours", "Resource 3 Hours"]:
        if col not in df_me.columns:
            df_me[col] = 0

    df_me["Total ME Hours"] = df_me[["Resource 1 Hours", "Resource 2 Hours", "Resource 3 Hours"]].sum(axis=1)
    edited_df = st.data_editor(
        df_me,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Total ME Hours": st.column_config.NumberColumn("Total ME Hours", disabled=True)
        }
    )

    edited_df["Total ME Hours"] = edited_df[["Resource 1 Hours", "Resource 2 Hours", "Resource 3 Hours"]].sum(axis=1)
    if "ME Month" in edited_df.columns:
        edited_df["ME Month"] = pd.to_datetime(edited_df["ME Month"], errors="coerce")
        edited_df["Month"] = edited_df["ME Month"].dt.strftime("%B %Y")

    if st.button("Save Changes", key="save_me_hours"):
        edited_df.to_csv(me_file, index=False)
        st.success("Changes saved to sample_me_hours.csv")

# ---------------- Charts Dashboard ----------------
with tab4:
    st.title("📊 Charts Dashboard")
    chart_options = [
        "Resource Hours by Month",
        "Task Status Distribution",
        "Combined ME + Activity Hours",
        "ME Hours by Resource per Month",
        "Predictive Utilization Forecast"
    ]
    selected_chart = st.selectbox("Select Chart to Display", chart_options)

    if selected_chart == "Resource Hours by Month":
        if not df_activities.empty and "Month" in df_activities.columns:
            st.subheader("Resource Hours by Month")
            months = df_activities["Month"].dropna().unique()
            selected_month = st.selectbox("Select Month", sorted(months), key="monthly_hours")
            filtered_data = df_activities[df_activities["Month"] == selected_month]

            tech_group = filtered_data.groupby("Technical Resource")["Technical Time"].sum().reset_index()
            func_group = filtered_data.groupby("Functional Resource")["Functional Time"].sum().reset_index()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(tech_group["Technical Resource"].astype(str), tech_group["Technical Time"], label="Technical Time", alpha=0.7)
            ax.bar(func_group["Functional Resource"].astype(str), func_group["Functional Time"], label="Functional Time", alpha=0.7)
            ax.set_ylabel("Hours")
            ax.set_title(f"Resource Hours - {selected_month}")
            ax.legend()
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

    elif selected_chart == "Task Status Distribution":
        if not df_activities.empty and "Month" in df_activities.columns and "Status" in df_activities.columns:
            st.subheader("Task Status Distribution per Month")
            status_month = df_activities.groupby(["Month", "Status"]).size().unstack(fill_value=0).sort_index()
            st.bar_chart(status_month)

    elif selected_chart == "Combined ME + Activity Hours":
        if not df_activities.empty and not df_me.empty:
            df_activities["Total Activity Hours"] = df_activities["Technical Time"] + df_activities["Functional Time"]
            activity_hours = df_activities.groupby("Month")["Total Activity Hours"].sum().sort_index()
            me_hours = df_me.groupby("Month")["Total ME Hours"].sum().sort_index()
            combined_df = pd.DataFrame({
                "Activity Hours": activity_hours,
                "ME Hours": me_hours
            }).fillna(0)
            st.subheader("Combined ME and Activity Hours per Month")
            st.bar_chart(combined_df)

    elif selected_chart == "ME Hours by Resource per Month":
        if not df_me.empty and "Month" in df_me.columns:
            st.subheader("ME Hours by Resource per Month")
            months = df_me["Month"].dropna().unique()
            selected_month = st.selectbox("Select Month", sorted(months), key="me_resource_month")
            filtered = df_me[df_me["Month"] == selected_month]
            data = {}
            for i in range(1, 4):
                res_col = f"Resource {i}"
                hrs_col = f"Resource {i} Hours"
                if res_col in filtered.columns and hrs_col in filtered.columns:
                    for res, hrs in zip(filtered[res_col], filtered[hrs_col]):
                        if pd.notna(res):
                            data[res] = data.get(res, 0) + hrs
            if data:
                fig, ax = plt.subplots()
                ax.bar(data.keys(), data.values())
                ax.set_title(f"ME Hours by Resource - {selected_month}")
                ax.set_ylabel("Hours")
                plt.xticks(rotation=45, ha="right")
                st.pyplot(fig)

    elif selected_chart == "Predictive Utilization Forecast":
        st.subheader("Forecasted Utilization for Each Resource")
        combined = []

        if not df_activities.empty and "Month" in df_activities.columns:
            tech_df = df_activities[["Month", "Technical Resource", "Technical Time"]].dropna()
            func_df = df_activities[["Month", "Functional Resource", "Functional Time"]].dropna()
            tech_df.columns = ["Month", "Resource", "Hours"]
            func_df.columns = ["Month", "Resource", "Hours"]
            combined.append(tech_df)
            combined.append(func_df)

        if not df_me.empty and "Month" in df_me.columns:
            for i in range(1, 4):
                res_col = f"Resource {i}"
                hrs_col = f"Resource {i} Hours"
                if res_col in df_me.columns and hrs_col in df_me.columns:
                    temp_df = df_me[["Month", res_col, hrs_col]].dropna()
                    temp_df.columns = ["Month", "Resource", "Hours"]
                    combined.append(temp_df)

        if combined:
            full_df = pd.concat(combined)
            utilization = full_df.groupby(["Month", "Resource"])["Hours"].sum().reset_index()
            month_order = sorted(utilization["Month"].unique())
            month_indices = {month: i for i, month in enumerate(month_order)}

            fig, ax = plt.subplots(figsize=(12, 6))
            for resource in utilization["Resource"].unique():
                resource_data = utilization[utilization["Resource"] == resource]
                X = resource_data["Month"].map(month_indices).values.reshape(-1, 1)
                y = resource_data["Hours"].values
                if len(X) >= 2:
                    model = LinearRegression()
                    model.fit(X, y)
                    future_X = np.array(range(len(month_indices), len(month_indices) + 6)).reshape(-1, 1)
                    future_months = pd.date_range(start=pd.to_datetime(month_order[-1]) + pd.offsets.MonthBegin(1), periods=6, freq='MS').strftime("%B %Y")
                    predictions = model.predict(future_X)
                    utilization_pct = (predictions / 176) * 100
                    ax.plot(future_months, utilization_pct, linestyle='--', marker='o', label=f"{resource}")
            ax.set_title("Forecasted Resource Utilization (%)")
            ax.set_ylabel("Utilization %")
            ax.legend()
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

# ---------------- MOM Dashboard ----------------
with tab5:
    st.title("📋 MOM Dashboard")
    try:
        with open("Momm.html", "r", encoding="utf-8") as file:
            mom_html_content = file.read()
        components.html(mom_html_content, height=800, scrolling=True)
    except FileNotFoundError:
        st.error("Momm.html file not found. Please ensure it is in the same directory as this script.")

