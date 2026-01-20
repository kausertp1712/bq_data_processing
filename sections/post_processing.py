import streamlit as st
import pandas as pd
import re
from Crypto.Cipher import AES


def render():
    st.header("🧰 Data Post Processing Tool")
    st.caption("Clean, flatten, and decrypt enriched API response files")

    def drop_empty_columns(df):
        """Remove columns that are completely empty"""
        return df.dropna(axis=1, how="all")

    def drop_metadata_columns(df):
        """Remove system-generated metadata columns"""
        keywords = ["requestid", "timestamp", "merchantid", "statuscode"]
        cols_to_drop = [
            col for col in df.columns
            if any(k in col.lower() for k in keywords)
        ]
        return df.drop(columns=cols_to_drop, errors="ignore")

    def flatten_phone_to_rc(df):
        """Flatten Phone → RC response into two-column output"""
        if "phoneNumber" not in df.columns:
            raise ValueError("Column 'phoneNumber' not found in file")

        rc_cols = [c for c in df.columns if "Phone To RC.rcNumber" in c]

        melted = df.melt(
            id_vars=["phoneNumber"],
            value_vars=rc_cols,
            var_name="source",
            value_name="rcNumber"
        )

        melted = (
            melted
            .dropna(subset=["rcNumber"])
            .drop_duplicates(subset=["phoneNumber", "rcNumber"])
        )

        return melted[["phoneNumber", "rcNumber"]]

    def flatten_pan_to_gst_csv(df):
        """Flatten PAN → GST response into two-column output"""
        result_pattern = re.compile(r"result\.(\d+)\.")
        indices = {
            int(m.group(1))
            for col in df.columns
            if (m := result_pattern.search(col))
        }

        rows = []
        for _, row in df.iterrows():
            for idx in sorted(indices):
                gstin = row.get(f"PAN Based GST Search.result.{idx}.gstinId")
                if pd.notna(gstin) and str(gstin).strip():
                    rows.append({
                        "pan": row.get("pan"),
                        "gst": gstin
                    })

        return pd.DataFrame(rows)

    IV = b"#cd\xe0\xcd\xb09>\xa1\x0f\xfe%l\xd5\xbe\xe3"
    KEY = b"Sixteen byte key"
    IV_HEX = IV.hex()

    def _is_hex(value):
        value = str(value).strip()
        if len(value) % 2 != 0:
            return False
        try:
            bytes.fromhex(value)
            return True
        except Exception:
            return False

    def detokenise(value):
        value = str(value or "").strip()
        if not _is_hex(value):
            return value

        if value.lower().startswith(IV_HEX):
            value = value[32:]

        try:
            cipher = AES.new(KEY, AES.MODE_CFB, IV)
            return cipher.decrypt(bytes.fromhex(value)).decode("utf-8").strip()
        except Exception:
            return value

    operation = st.selectbox(
        "Choose an operation",
        [
            "— Select —",
            "Metadata Cleanup",
            "Flatten PAN → GST",
            "Flatten Phone → RC",
            "Decryption Tool"
        ]
    )

    if operation == "— Select —":
        st.info("Select an operation to continue")
        return

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx"]
    )

    if not uploaded_file:
        return

    try:
        df = (
            pd.read_excel(uploaded_file, dtype=str)
            if uploaded_file.name.endswith(".xlsx")
            else pd.read_csv(uploaded_file, dtype=str)
        )
        st.success("File loaded successfully")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return

    result = None

    try:
        if operation == "Metadata Cleanup":
            result = drop_metadata_columns(drop_empty_columns(df))

        elif operation == "Flatten PAN → GST":
            result = flatten_pan_to_gst_csv(df)

        elif operation == "Flatten Phone → RC":
            result = flatten_phone_to_rc(df)

        elif operation == "Decryption Tool":
            col = st.selectbox(
                "Select column to decrypt",
                ["— Select —"] + list(df.columns)
            )
            if col != "— Select —":
                result = df.copy()
                result[f"{col}_decrypted"] = result[col].apply(detokenise)

    except Exception as e:
        st.error(str(e))
        return
        
    if result is not None:
        st.success("Processing complete")
        st.dataframe(result.head())

        st.download_button(
            "⬇️ Download Processed CSV",
            result.to_csv(index=False).encode("utf-8"),
            file_name="post_processed_output.csv",
            mime="text/csv"
        )
