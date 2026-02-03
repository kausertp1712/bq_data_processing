import re
import pandas as pd
from config import PAN_REGEX, EMAIL_REGEX


# ---------------- PAN ----------------
def validate_pan(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    return bool(re.match(PAN_REGEX, str(val).upper()))


# ---------------- EMAIL ----------------
def validate_email(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    return bool(re.match(EMAIL_REGEX, str(val).lower()))


# ---------------- NAME ----------------
def validate_name(val):
    if pd.isna(val) or not str(val).strip():
        return None

    s = str(val).strip()

    # too short
    if len(s) <= 2:
        return False

    # noise like AAAAA or 11111
    if re.fullmatch(r'(.)\1+', s):
        return False

    # must contain at least one alphabet
    if not re.search(r'[A-Za-z]', s):
        return False

    return True


# ---------------- PHONE ----------------
def validate_phone(val):
    if pd.isna(val) or str(val).strip() == "":
        return None

    s = re.sub(r'\D', '', str(val))

    # 10-digit Indian mobile
    if len(s) == 10 and s[0] in "6789":
        return True

    # 12-digit with country code
    if len(s) == 12 and s.startswith("91") and s[2] in "6789":
        return True

    return False


# ---------------- SUMMARY ----------------
def compute_validation_summary(df, raw_col, valid_col):
    total = len(df)

    missing = (
        df[raw_col].isna().sum()
        + (df[raw_col].astype(str).str.strip() == "").sum()
    )

    duplicates = (
        df[df[raw_col].notna()][raw_col]
        .duplicated()
        .sum()
    )

    valid = (df[valid_col] == True).sum()
    invalid = (df[valid_col] == False).sum()

    return {
        "Total": total,
        "Missing": missing,
        "Invalid": invalid,
        "Duplicates": duplicates,
        "Valid": valid
    }
