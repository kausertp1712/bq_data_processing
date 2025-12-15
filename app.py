import streamlit as st
from pages.input_validation import render as render_validation
from pages.bulk_query import render as render_bulk
from pages.post_processing import render as render_post

st.set_page_config(page_title="Data Tools Suite", layout="wide")
st.title("Data Processing Tools")

choice = st.sidebar.selectbox(
    "Choose a tool:",
    [
        "-- Select --",
        "Input Validation App",
        "Bulk Query Input File Processing",
        "Data Post Processing Tool"
    ]
)

if choice == "Input Validation App":
    render_validation()
elif choice == "Bulk Query Input File Processing":
    render_bulk()
elif choice == "Data Post Processing Tool":
    render_post()
else:
    st.info("👈 Select a tool from the sidebar to begin.")
