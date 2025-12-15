import streamlit as st
import pandas as pd
from config import API_FIELDS, AUTO_FIELDS
from helpers.io import load_file
from helpers.transformations import normalize_phone, split_name

def render():
    st.header("📤 Bulk Query Input File Processing")

    uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])
    if not uploaded_file:
        return

    df = load_file(uploaded_file)
    st.success("File loaded successfully")
    st.dataframe(df.head())

    selected_apis = st.multiselect("Select APIs", list(API_FIELDS.keys()))
    if not selected_apis:
        return

    required_fields = sorted(set(f for api in selected_apis for f in API_FIELDS[api]))
    is_credit_prefill = "credit_prefill_eq" in selected_apis

    st.subheader("🔗 Column Mapping")
    col_options = ["Not provided"] + list(df.columns)
    mapping = {}

    if is_credit_prefill:
        st.info(
            "ℹ️ If you only have a full name, map it to `name`. "
            "First, middle, and last names will be derived automatically."
        )

        mapping["name"] = st.selectbox(
            "Map column for `name` (Full Name)",
            col_options
        )
        name_provided = mapping["name"] != "Not provided"
    else:
        name_provided = False

    for field in required_fields:
        if is_credit_prefill:
            if field in {"firstName", "middleName", "lastName"} and name_provided:
                continue
            if field == "name":
                continue

        mapping[field] = st.selectbox(
            f"Map column for `{field}`",
            col_options
        )

    if is_credit_prefill:
        has_name = mapping.get("name") != "Not provided"
        has_split = (
            mapping.get("firstName") != "Not provided"
            and mapping.get("lastName") != "Not provided"
        )
        if not has_name and not has_split:
            st.warning(
                "Credit Prefill requires either a full name or first and last name."
            )
            return

    if not st.button("Process File"):
        return

    result = pd.DataFrame()

    for field, src in mapping.items():
        result[field] = df[src] if src != "Not provided" else ""

    if is_credit_prefill and mapping.get("name") != "Not provided":
        names = result["name"].apply(split_name)
        result["firstName"] = names.apply(lambda x: x[0])
        result["middleName"] = names.apply(lambda x: x[1])
        result["lastName"] = names.apply(lambda x: x[2])

    for col in ["phoneNumber", "mobileNumber", "phone"]:
        if col in result.columns:
            result[col] = result[col].apply(normalize_phone)

    for col, val in AUTO_FIELDS.items():
        result[col] = val

    st.success("Bulk Query Input File Generated")
    st.dataframe(result.head())

    st.download_button(
        "Download CSV",
        result.to_csv(index=False).encode("utf-8"),
        "bulk_query_processed.csv",
        "text/csv"
    )
