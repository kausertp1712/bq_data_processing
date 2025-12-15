import streamlit as st
import pandas as pd
import re
from Crypto.Cipher import AES

# ========================================================================
# PAGE CONFIG
# ========================================================================
st.set_page_config(page_title="Data Tools Suite", layout="wide")
st.title("Data Processing Tools")

# ========================================================================
# SIDEBAR
# ========================================================================
app_choice = st.sidebar.selectbox(
    "Choose a tool:",
    [
        "-- Select --",
        "Input Validation App",
        "Data Post Processing Tool",
        "Bulk Query Input File Processing"
    ]
)

# ========================================================================
# ========================== INPUT VALIDATION APP ========================
# ========================================================================
if app_choice == "Input Validation App":
    st.header("📥 Input Validation App")

    uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])
    if not uploaded_file:
        st.stop()

    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
    st.success("File loaded successfully")
    st.dataframe(df.head())

    options = ["Not provided"] + list(df.columns)

    name_col = st.selectbox("Name column", options)
    phone_col = st.selectbox("Phone column", options)
    email_col = st.selectbox("Email column", options)
    pan_col = st.selectbox("PAN column", options)

    pan_regex = r'^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$'
    email_regex = r'^[^@]+@[^@]+\.[^@]+$'

    def validate_pan(x):
        return None if pd.isna(x) else bool(re.match(pan_regex, str(x)))

    def validate_email(x):
        return None if pd.isna(x) else bool(re.match(email_regex, str(x)))

    data = df.copy()

    if pan_col != "Not provided":
        data["Valid_PAN"] = data[pan_col].apply(validate_pan)

    if email_col != "Not provided":
        data["Valid_Email"] = data[email_col].apply(validate_email)

    st.dataframe(data.head())


# ========================================================================
# ======================= DATA POST PROCESSING TOOL =======================
# ========================================================================
elif app_choice == "Data Post Processing Tool":
    st.header("🧰 Data Post Processing Tool")
    st.info("No changes made to this section.")


# ========================================================================
# =================== BULK QUERY INPUT FILE PROCESSING ====================
# ========================================================================
elif app_choice == "Bulk Query Input File Processing":
    st.header("📤 Bulk Query Input File Processing")

    # ------------------------------------------------------------------
    # API FIELD DEFINITIONS
    # ------------------------------------------------------------------
    API_FIELDS = {
        "credit_prefill_eq": ["name", "firstName", "middleName", "lastName", "mobileNumber"],
        "phone_network": ["phoneNumber"],
        "phone_name_attributes": ["name", "firstName", "lastName", "phoneNumber"],
        "phone_social_advance": ["phoneNumber"],
        "phone_to_name": ["phoneNumber"],
        "phone_to_pan": ["name", "phone"],
        "phone_to_uan": ["phoneNumber"],
        "email_attributes": ["email"],
        "email_name_attributes": ["email", "firstName", "lastName", "name"],
        "email_social_advance": ["email"],
        "pan_profile": ["fatherName", "pan"],
        "pan_to_gst": ["pan"],
        "gst_advance": ["gst"],
        "phone_to_rc": ["phoneNumber"],
        "rc_authentication": ["docNumber"],
        "epfo_advance": ["phoneNumber", "pan"]
    }

    AUTO_FIELDS = {
        "aadhaarUnmask": "",
        "serviceType": "",
        "requestedServices": "",
        "derivedSignals": True,
        "enhancedCoverage": True,
        "isCorrectionRequired": True,
        "countryCode": "IND"
    }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def normalize_phone(val):
        if pd.isna(val):
            return ""
        digits = re.sub(r"\D", "", str(val))
        return "91" + digits if len(digits) == 10 else digits

    def split_name(full_name):
        if not full_name or pd.isna(full_name):
            return "", "", ""
        parts = str(full_name).strip().split()
        if len(parts) == 1:
            return parts[0], "", ""
        if len(parts) == 2:
            return parts[0], "", parts[1]
        return parts[0], " ".join(parts[1:-1]), parts[-1]

    # ------------------------------------------------------------------
    # FILE UPLOAD
    # ------------------------------------------------------------------
    uploaded_file = st.file_uploader("📂 Upload CSV / Excel", type=["csv", "xlsx"])
    if not uploaded_file:
        st.stop()

    df = pd.read_excel(uploaded_file, dtype=str) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file, dtype=str)
    st.success("File loaded successfully")
    st.dataframe(df.head())

    # ------------------------------------------------------------------
    # API SELECTION
    # ------------------------------------------------------------------
    selected_apis = st.multiselect("Select APIs", list(API_FIELDS.keys()))
    if not selected_apis:
        st.stop()

    required_fields = sorted(set(f for api in selected_apis for f in API_FIELDS[api]))
    is_credit_prefill = "credit_prefill_eq" in selected_apis

    # ------------------------------------------------------------------
    # COLUMN MAPPING (SMART UX)
    # ------------------------------------------------------------------
    st.subheader("🔗 Column Mapping")
    col_options = ["Not provided"] + list(df.columns)
    mapping = {}

    if is_credit_prefill:
        st.info(
            "ℹ️ If you only have a full name, map it to `name`. "
            "The system will derive first, middle, and last names automatically."
        )

        mapping["name"] = st.selectbox(
            "Map column for `name` (Full Name)",
            col_options,
            key="map_name"
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
            col_options,
            key=f"map_{field}"
        )

    # ------------------------------------------------------------------
    # VALIDATION CHECK (CREDIT PREFILL)
    # ------------------------------------------------------------------
    if is_credit_prefill:
        has_name = mapping.get("name") != "Not provided"
        has_split = (
            mapping.get("firstName") != "Not provided"
            and mapping.get("lastName") != "Not provided"
        )

        if not has_name and not has_split:
            st.warning(
                "⚠️ Credit Prefill requires either a full `name` or "
                "`firstName` and `lastName`. Please map at least one."
            )
            st.stop()

    if not st.button("Process File"):
        st.stop()

    # ------------------------------------------------------------------
    # BUILD RESULT
    # ------------------------------------------------------------------
    result = pd.DataFrame()

    for field, src in mapping.items():
        result[field] = df[src] if src != "Not provided" else ""

    # CREDIT PREFILL NAME DERIVATION
    if is_credit_prefill:
        if (
            mapping.get("firstName") == "Not provided"
            and mapping.get("lastName") == "Not provided"
            and "name" in result.columns
        ):
            name_parts = result["name"].apply(split_name)
            result["firstName"] = name_parts.apply(lambda x: x[0])
            result["middleName"] = name_parts.apply(lambda x: x[1])
            result["lastName"] = name_parts.apply(lambda x: x[2])

    # Normalize phones
    for col in ["phoneNumber", "mobileNumber", "phone"]:
        if col in result.columns:
            result[col] = result[col].apply(normalize_phone)

    # Add auto fields
    for col, val in AUTO_FIELDS.items():
        result[col] = val

    st.success("✅ Bulk Query Input File Generated Successfully")
    st.dataframe(result.head())

    st.download_button(
        "⬇️ Download Processed File",
        result.to_csv(index=False).encode("utf-8"),
        "bulk_query_processed.csv",
        "text/csv"
    )

# ========================================================================
# FALLBACK
# ========================================================================
else:
    st.info("👈 Select a tool from the sidebar to begin.")
