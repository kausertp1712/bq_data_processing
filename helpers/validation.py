import re
import pandas as pd
from config import PAN_REGEX, EMAIL_REGEX

def validate_pan(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    return bool(re.match(PAN_REGEX, str(val).upper()))

def validate_email(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    return bool(re.match(EMAIL_REGEX, str(val).lower()))

def compute_validation_summary(df, raw_col, valid_col):
    """
    Returns a dict with Total, Missing, Invalid, Duplicate, Valid counts
    """
    total = len(df)

    # Missing = null OR empty string
    missing = df[raw_col].isna().sum() + (df[raw_col].astype(str).str.strip() == "").sum()

    # Duplicates (ignore missing)
    duplicates = (
        df[df[raw_col].notna()][raw_col]
        .duplicated(keep=False)
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
