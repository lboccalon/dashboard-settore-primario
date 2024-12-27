import streamlit as st
import matplotlib.pyplot as plt

from simulator import data, yield_results


st.dataframe(data)

for dim in ["temperature", "humidity", "sun_hours", "rain_mm", "cloud_coverage"]:
    fig = plt.figure()
    plt.plot(data.index, data[dim])
    st.pyplot(fig)

st.write("Average percentage of complete cloud coverage:")
st.write((data["cloud_coverage"] == 100).mean())

st.write(f"Baseline Yield: {yield_results['baseline_yield_kg']:.0f} kg")
st.write(f"Adjusted Yield: {yield_results['adjusted_yield_kg']:.0f} kg")
st.write(f"Adjustment Factor: {yield_results['adjustment_factor']:.2f}")
st.write(f"Average Temperature: {yield_results['avg_temperature']:.2f} °C")
st.write(f"Total Rainfall: {yield_results['avg_rainfall_mm']:.2f} mm")
st.write(f"Average Sun Hours: {yield_results['avg_sun_hours']:.2f} hours/day")
st.write(f"Average Humidity: {yield_results['avg_humidity']:.2f}%")
forecasted_number_of_bottles = yield_results["adjusted_yield_kg"] * 0.93
st.write(f"Forecasted number of bottles: {forecasted_number_of_bottles:.2f}")
average_sold_price = st.slider("sold price for 1 bottle (€):", 1, 15, 5, 1)
forecasted_gross_revenue = forecasted_number_of_bottles * average_sold_price
st.write(f"Forecasted gross revenue (€): {forecasted_gross_revenue:.2f}")
