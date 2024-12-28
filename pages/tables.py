import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from simulator import data
from common import filter_data_by_year

title = "# Data Tables :clipboard:"
st.markdown(title)
st.sidebar.markdown(title)


data = filter_data_by_year(data=data)

# hottest days
hottest_days = pd.Series(
    data[data["temperature"] == data["temperature"].max()].index.date,
    name=data["temperature"].max(),
)

# coldest days
coldest_days = pd.Series(
    data[data["temperature"] == data["temperature"].min()].index.date,
    name=data["temperature"].min(),
)


# Function to calculate the longest streak
def find_longest_streak(df, column, value):
    max_streak = 0
    current_streak = 0
    streak_indices = []
    max_indices = []

    for i, val in enumerate(df[column]):
        if val == value:
            current_streak += 1
            streak_indices.append(i)
        else:
            if current_streak > max_streak:
                max_streak = current_streak
                max_indices = streak_indices.copy()
            current_streak = 0
            streak_indices = []

    # Final check in case the longest streak ends at the last row
    if current_streak > max_streak:
        max_streak = current_streak
        max_indices = streak_indices

    return max_streak, max_indices


# Find longest streak for 100
longest_100_streak, indices_100 = find_longest_streak(data, "cloud_coverage", 100)
# Find longest streak for 0
longest_0_streak, indices_0 = find_longest_streak(data, "cloud_coverage", 0)


[col] = st.columns(1, vertical_alignment="center")
with col:
    st.dataframe(data, use_container_width=False)
    st.dataframe(data.describe())
    st.write("Hottest days:")
    st.write(hottest_days)
    st.write("Coldest days:")
    st.write(coldest_days)
    st.write(f"Longest streak of rain days: {longest_100_streak}")
    st.write(data.iloc[indices_100])
    st.write(f"Longest streak of perfectly sunny days: {longest_0_streak}")
    st.write(data.iloc[indices_0])
