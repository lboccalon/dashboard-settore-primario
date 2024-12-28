import streamlit as st


def filter_data_by_year(data, allow_none=True):
    selectable_years = data.index.year.unique().tolist()
    if allow_none:
        selectable_years = [None] + selectable_years
    selected_year = st.selectbox(
        "Chose a year to filter the table or leave None to display all:",
        selectable_years,
    )
    if selected_year is not None:
        data = data.loc[data.index.year == selected_year]
    return data
