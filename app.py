import streamlit as st
import matplotlib.pyplot as plt

from simulator import data


st.dataframe(data)

for dim in ["temperature", "humidity", "sun_hours", "rain_mm", "cloud_coverage"]:
    fig = plt.figure()
    plt.plot(data.index, data[dim])
    st.pyplot(fig)

st.write("Average percentage of complete cloud coverage:")
st.write((data["cloud_coverage"] == 100).mean())