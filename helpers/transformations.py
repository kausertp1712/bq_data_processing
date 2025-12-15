import re
import pandas as pd

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
