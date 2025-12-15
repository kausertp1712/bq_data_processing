import streamlit as st
from helpers.io import load_file
from helpers.validation import validate_pan, validate_email

def render():
    st.header("📥 Input Validation App")

    uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])
    if not uploaded_file:
        return

    df = load_file(uploaded_file)
    st.success("File loaded successfully")
    st.dataframe(df.head())

    options = ["Not provided"] + list(df.columns)

    name_col = st.selectbox("Name column", options)
    phone_col = st.selectbox("Phone column", options)
    email_col = st.selectbox("Email column", options)
    pan_col = st.selectbox("PAN column", options)

    result = df.copy()

    if pan_col != "Not provided":
        result["Valid_PAN"] = result[pan_col].apply(validate_pan)

    if email_col != "Not provided":
        result["Valid_Email"] = result[email_col].apply(validate_email)

    st.dataframe(result.head())
