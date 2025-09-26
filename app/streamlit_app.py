import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Streamlit Example",
    page_icon="🚗",
)

# ---------------- TITLE ----------------
st.write("# IND320 Dashboard")

# ---------------- DESCRIPTION ----------------
st.markdown(
    """
    Project work,part 1: Open Meteo Data Analysis.
    - Load the dataset from the provided CSV file.
    - Parse the 'time' column as datetime and set it as the index.
    - Plot each numeric column separately as a function of time.
    - Plot all columns together. 
    """
)