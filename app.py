import streamlit as st
import pandas as pd
import os
import shutil
from datetime import datetime
from utils import show_project_charts

# User credentials
users = {
    "Nenad": {"password": "srbija88", "role": "Editor", "projects": ["Moskva"]},
    "Jovan": {"password": "srbija88", "role": "Viewer", "projects": ["Moskva", "Ust-Luga", "Sankt Peterburg"]}
}

# Login logic
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.session_state["role"] = users[username]["role"]
            st.session_state["projects"] = users[username]["projects"]
            st.rerun()
        else:
            st.error("Incorrect username or password.")
    st.stop()

# Sidebar
st.sidebar.title("User Info")
st.sidebar.write(f"👤 {st.session_state['user']} ({st.session_state['role']})")

if st.sidebar.button("🚪 Log Out"):
    st.session_state.clear()
    st.rerun()

# Main
st.title("🗺️ Project Map – Russia")
st.write("Select a project to view details:")

for project in st.session_state["projects"]:
    if st.button(f"📍 {project}"):
        st.session_state["active_project"] = project
        st.rerun()

project = st.session_state.get("active_project", None)
if project:
    st.header(f"📊 Project Details: {project}")

    folder = f"data/{project.lower().replace(' ', '-')}"
    filepath = f"{folder}/tabela_glavna.xlsx"
    backup_folder = os.path.join(folder, "backups")
    os.makedirs(backup_folder, exist_ok=True)

    if os.path.exists(filepath):
        df_main = pd.read_excel(filepath)
    else:
        df_main = None

    if st.session_state["role"] == "Editor":
        st.subheader("📤 Upload New Data (Editor Only)")
        uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.write("✅ Uploaded file preview:")
            st.dataframe(df)

            if st.button("🔄 Update Main Table with Uploaded Data"):
                today = datetime.now().strftime("%Y-%m-%d")
                backup_path = os.path.join(backup_folder, f"tabela_{today}.xlsx")
                shutil.copy(filepath, backup_path)

                updated = 0
                df_main = pd.read_excel(filepath)

                for _, row in df.iterrows():
                    mask = df_main["Pipe Name"] == row["Pipe Name"]
                    if mask.any():
                        df_main.loc[mask, "Done (m)"] += row["Done (m)"]
                        df_main.loc[mask, "Progress (%)"] = (
                            df_main.loc[mask, "Done (m)"] / df_main.loc[mask, "Length (m)"]
                        ) * 100
                        updated += 1

                df_main.to_excel(filepath, index=False)
                st.success(f"Main table updated successfully ({updated} rows). Daily backup saved.")

    # Load backups and show dropdown
    if os.path.exists(filepath):
        backup_files = sorted([
            f for f in os.listdir(backup_folder)
            if f.endswith(".xlsx")
        ], reverse=True)

        today_label = datetime.now().strftime("%Y-%m-%d")
        version_labels = [f.replace("tabela_", "").replace(".xlsx", "") for f in backup_files]
        version_options = [today_label] + [v for v in version_labels if v != today_label]

        selected_version = st.selectbox("📂 Select table version to view:", version_options)

        if selected_version == today_label:
            selected_df = df_main
            st.info(f"Showing current table (updated on {today_label}).")
        else:
            selected_path = os.path.join(backup_folder, f"tabela_{selected_version}.xlsx")
            selected_df = pd.read_excel(selected_path)
            st.info(f"Showing backup version: {selected_version}")

            if st.session_state["role"] == "Editor":
                if st.button("♻️ Restore this version"):
                    shutil.copy(selected_path, filepath)
                    st.success("This version has been restored as the main table.")
                    st.rerun()

        st.subheader("📋 Selected Table Version")
        st.dataframe(selected_df)

        if "Done (m)" in selected_df.columns and "Progress (%)" in selected_df.columns:
            show_project_charts(selected_df)
    else:
        st.warning("Main table has not been uploaded yet.")

    if st.session_state["role"] == "Editor":
        st.info("As an Editor, you can upload, update, and restore table versions.")
    else:
        st.info("As a Viewer, you can view current and past versions of the data.")






