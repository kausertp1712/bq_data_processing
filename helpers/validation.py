import re
import pandas as pd
from config import PAN_REGEX, EMAIL_REGEX

def validate_pan(val):
    if pd.isna(val):
        return None
    return bool(re.match(PAN_REGEX, str(val)))

def validate_email(val):
    if pd.isna(val):
        return None
    return bool(re.match(EMAIL_REGEX, str(val)))
