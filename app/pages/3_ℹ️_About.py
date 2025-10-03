import streamlit as st

st.set_page_config(page_title="About", layout="wide")

def main():
    st.title("About")
    st.caption("Lise Rochat – 2025")
    st.divider()

    st.markdown(
        """
        **IND320 – Data to Decision**  
        ***03 october 2025:*** Part 1 – Dashboard basics 

        - Multipage layout scaffold
        - Sidebar-ready controls
        - Utils module placeholder for shared functions
        """
    )

    with st.sidebar:
        st.header("About")
        st.write("Project roadmap")

if __name__ == "__main__":
    main()
