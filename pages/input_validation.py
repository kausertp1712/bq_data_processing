import streamlit as st
import pandas as pd
from helpers.io import load_file
from helpers.validation import (
    validate_pan,
    validate_email,
    compute_validation_summary
)

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

    data = df.copy()
    summary_rows = []

    # ---------------- PAN ----------------
    if pan_col != "Not provided":
        data["Valid_PAN"] = data[pan_col].apply(validate_pan)
        summary = compute_validation_summary(data, pan_col, "Valid_PAN")
        summary_rows.append({"Field": "PAN", **summary})

    # ---------------- EMAIL ----------------
    if email_col != "Not provided":
        data["Valid_Email"] = data[email_col].apply(validate_email)
        summary = compute_validation_summary(data, email_col, "Valid_Email")
        summary_rows.append({"Field": "Email", **summary})

    # ---------------- OUTPUT ----------------
    st.subheader("📊 Validation Summary")
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows))
    else:
        st.info("No fields selected for validation.")

    st.subheader("📄 Data Preview")
    st.dataframe(data.head())
