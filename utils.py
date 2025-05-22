
import streamlit as st
import plotly.express as px

def show_project_charts(df):
    st.subheader("📊 Progress Histogram")
    if "Progress (%)" in df.columns:
        fig1 = px.histogram(
            df,
            x="Progress (%)",
            nbins=10,
            title="Distribution of Progress (%)",
            color_discrete_sequence=["#1f77b4"]
        )
        st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🧩 Overall Progress Pie Chart")
    if "Length (m)" in df.columns and "Done (m)" in df.columns:
        total = df["Length (m)"].sum()
        done = df["Done (m)"].sum()
        remaining = max(total - done, 0)
        fig2 = px.pie(
            names=["Done", "Remaining"],
            values=[done, remaining],
            title="Total Progress (by Length)",
            color_discrete_sequence=["green", "lightgray"]
        )
        st.plotly_chart(fig2, use_container_width=True)
