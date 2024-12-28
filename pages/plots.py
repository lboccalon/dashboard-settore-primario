import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import plotly.express as px


from simulator import data

title = "# Plots :bar_chart:"
st.markdown(title)
st.sidebar.markdown(title)


data["year"] = data.index.year
data["month"] = data.index.month
data["day_of_year"] = data.index.dayofyear

st.markdown("# Annual Temperature Report")
agg_month = st.checkbox("Aggregate by month")

if agg_month:
    fig = px.line(
        data.groupby(["month", "year"])["temperature"].mean().reset_index(),
        x="month",
        y="temperature",
        color="year",
        labels={
            "month": "Month of Year",
            "temperature": "Temperature (°C)",
            "year": "Year",
        },
        title="Average Monthly Temperature by Year",
    )
else:
    fig = px.line(
        data,
        x="day_of_year",
        y="temperature",
        color="year",
        labels={
            "day_of_year": "Day of Year",
            "temperature": "Temperature (°C)",
            "year": "Year",
        },
        title="Daily Temperature by Year",
    )

st.plotly_chart(fig)

st.markdown("# Annual Rain Report")
data["cumulative_rain"] = data.groupby("year")["rain_mm"].transform("cumsum")


fig = px.line(
    data,
    x="day_of_year",
    y="cumulative_rain",
    color="year",
    labels={
        "day_of_year": "Day of Year",
        "cumulative_rain": "Cumulative Rain (mm)",
        "year": "Year",
    },
    title="Cumulative Rain by Year",
)
st.plotly_chart(fig)
