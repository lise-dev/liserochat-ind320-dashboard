import streamlit as st
from pathlib import Path

st.set_page_config(page_title="IND320 – Dashboard Basics", layout="wide")

def main():
    st.title("IND320 – Dashboard Basics")

    # CSV 
    project_root_directory = Path(__file__).resolve().parent.parent
    csv_file_path = project_root_directory / "data" / "open-meteo-subset.csv"

if __name__ == "__main__":
    main()
