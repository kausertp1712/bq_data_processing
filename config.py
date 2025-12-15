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

PAN_REGEX = r'^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$'
EMAIL_REGEX = r'^[^@]+@[^@]+\.[^@]+$'
