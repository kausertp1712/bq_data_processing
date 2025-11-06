import streamlit as st
import pandas as pd
import re
from Crypto.Cipher import AES

st.set_page_config(page_title="Data Tools Suite", layout="wide")
st.title("Data Processing Tools")

app_choice = st.sidebar.selectbox(
    "Choose a tool:",
    ["-- Select --", "📥 Input Validation App", "🧰 Data Post Processing Tool"]
)

# =====================================================================
# APP 1: INPUT VALIDATION APP
# =====================================================================
if app_choice == "📥 Input Validation App":
    st.header("📥 Input Validation App")

    if "show_validation" not in st.session_state:
        st.session_state["show_validation"] = False

    if st.button("Start Input Validation"):
        st.session_state["show_validation"] = True

    if st.session_state["show_validation"]:
        st.subheader("📂 Upload File for Validation")
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.success(f"✅ File loaded successfully — {df.shape[0]} records, {df.shape[1]} columns")
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
                st.stop()

            st.subheader("🔍 Select Column Names (or choose 'Not provided')")
            options = ["Not provided"] + list(df.columns)
            name_col = st.selectbox("Select Name Column", options)
            phone_col = st.selectbox("Select Phone Column", options)
            email_col = st.selectbox("Select Email Column", options)
            pan_col = st.selectbox("Select PAN Column", options)

            # --- Validation Functions ---
            def clean_and_validate_name(name: str) -> bool:
                if pd.isna(name) or not str(name).strip():
                    return None
                cleaned = re.sub(r"[^a-zA-Z0-9\s.\-/,&()]", "", str(name))
                cleaned = re.sub(r"\s+", " ", cleaned).strip()
                if len(cleaned) <= 2:
                    return False
                if re.fullmatch(r'(.)\1+', cleaned, re.IGNORECASE):
                    return False
                if not re.search(r'[a-zA-Z]', cleaned):
                    return False
                return True

            pan_regex = r'^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$'
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

            def validate_pan(pan):
                if pd.isna(pan) or not str(pan).strip():
                    return None
                return bool(re.match(pan_regex, str(pan).upper()))

            def validate_email(email):
                if pd.isna(email) or not str(email).strip():
                    return None
                return bool(re.match(email_regex, str(email).lower()))

            def validate_phone(phone):
                if pd.isna(phone) or str(phone).strip().lower() in ["nan", "none", ""]:
                    return None
                s = re.sub(r'\D', '', str(int(float(phone))) if isinstance(phone, (int, float)) else str(phone))
                if len(s) == 10 and s[0] in "6789":
                    return True
                elif len(s) == 12 and s.startswith("91") and s[2] in "6789":
                    return True
                else:
                    return False

            data = df.copy()

            if name_col != "Not provided":
                data["Valid_Name"] = data[name_col].apply(clean_and_validate_name)
            if phone_col != "Not provided":
                data["Valid_Phone"] = data[phone_col].apply(validate_phone)
            if email_col != "Not provided":
                data["Valid_Email"] = data[email_col].apply(validate_email)
            if pan_col != "Not provided":
                data["Valid_PAN"] = data[pan_col].apply(validate_pan)

            st.subheader("📊 Validation Summary")
            summary_data = []

            def get_summary(field_name, col, valid_col):
                if col == "Not provided":
                    return {"Field": field_name, "Total": "-", "Duplicates": "-", "Missing": "-", "Invalid": "-", "Valid": "-"}
                total = len(data)
                duplicates = data[col].duplicated(keep=False).sum()
                missing = data[col].isna().sum() + (data[col].astype(str).str.strip() == "").sum()
                valid_series = data[valid_col]
                invalid = (valid_series == False).sum()
                valid = (valid_series == True).sum()
                return {"Field": field_name, "Total": int(total), "Duplicates": int(duplicates), "Missing": int(missing), "Invalid": int(invalid), "Valid": int(valid)}

            summary_data.append(get_summary("Name", name_col, "Valid_Name"))
            summary_data.append(get_summary("Phone", phone_col, "Valid_Phone"))
            summary_data.append(get_summary("Email", email_col, "Valid_Email"))
            summary_data.append(get_summary("PAN", pan_col, "Valid_PAN"))

            summary_df = pd.DataFrame(summary_data).astype(str)
            st.dataframe(summary_df, use_container_width=True)

# =====================================================================
# APP 2: DATA POST PROCESSING TOOL
# =====================================================================
elif app_choice == "🧰 Data Post Processing Tool":
    st.header("🧰 Data Post Processing Tool")

    # Helper functions (from your QA app)
    def drop_empty_columns(df): return df.dropna(axis=1, how='all')

    def drop_metadata_columns(df):
        keywords = ['requestid', 'timestamp', 'merchantid', 'statuscode']
        return df.drop(columns=[c for c in df.columns if any(k in c.lower() for k in keywords)], errors="ignore")

    def flatten_phone_to_rc(df):
        if "phoneNumber" not in df.columns:
            raise ValueError("❌ Column 'phoneNumber' not found.")
        rc_cols = [c for c in df.columns if "Phone To RC.rcNumber" in c]
        melted = df.melt(id_vars=["phoneNumber"], value_vars=rc_cols, var_name="rc_col", value_name="rcNumber")
        melted = melted.dropna(subset=["rcNumber"]).drop_duplicates(subset=["phoneNumber","rcNumber"])
        return melted[["phoneNumber","rcNumber"]]

    def flatten_pan_to_gst_csv(df):
        result_pattern = re.compile(r'result\.(\d+)\.')
        result_indices = {int(m.group(1)) for col in df.columns if (m := result_pattern.search(col))}
        rows = []
        for _, row in df.iterrows():
            for idx in sorted(result_indices):
                gstin = row.get(f'PAN Based GST Search.result.{idx}.gstinId')
                if pd.notna(gstin) and str(gstin).strip():
                    rows.append({'pan': row.get('pan'), 'gst': gstin})
        return pd.DataFrame(rows)

    # AES constants
    IV = b'#cd\xe0\xcd\xb09>\xa1\x0f\xfe%l\xd5\xbe\xe3'
    KEY = b'Sixteen byte key'
    IV_HEX = IV.hex()

    def _is_hex(s):
        s = str(s or "").strip()
        if len(s) % 2 != 0: return False
        try:
            bytes.fromhex(s)
            return True
        except: return False

    def detokenise(value):
        s = str(value or "").strip()
        if not s or not _is_hex(s):
            return s
        if s.lower().startswith(IV_HEX):
            s = s[32:]
        try:
            cipher = AES.new(KEY, AES.MODE_CFB, IV)
            out = cipher.decrypt(bytes.fromhex(s)).decode("utf-8", errors="ignore").strip()
            return out or value
        except:
            return value

    operation = st.selectbox(
        "⚙️ Choose an operation:",
        [
            "— Select —",
            "Metadata Cleanup",
            "Flatten PAN→GST CSV",
            "Flatten Phone→RC",
            "Decryption Tool"
        ]
    )

    if operation != "— Select —":
        uploaded_file = st.file_uploader("📂 Upload File", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file, dtype=str) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file, dtype=str)
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
                st.stop()

            st.success(f"✅ Loaded file: {uploaded_file.name}")
            st.dataframe(df.head())

            result = None
            if operation == "Metadata Cleanup":
                result = drop_metadata_columns(drop_empty_columns(df))
            elif operation == "Flatten PAN→GST CSV":
                result = flatten_pan_to_gst_csv(df)
            elif operation == "Flatten Phone→RC":
                result = flatten_phone_to_rc(df)
            elif operation == "Decryption Tool":
                column_options = ["— Not Provided —"] + list(df.columns)
                selected_col = st.selectbox("Select column to decrypt", column_options)
                if selected_col != "— Not Provided —":
                    result = df.copy()
                    result[selected_col + "_decrypted"] = df[selected_col].apply(detokenise)

            if result is not None and not result.empty:
                st.success("✅ Processing complete!")
                st.dataframe(result.head())
                csv = result.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Processed CSV",
                    data=csv,
                    file_name=f"{operation.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )

else:
    st.info("👈 Select a tool from the sidebar to begin.")
