import re

def validate_email(email):
    """Validates email format using regular expressions."""
    if not email:
        return False, "Email cannot be empty."
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(email_regex, email):
        return True, ""
    return False, "Invalid email format (e.g. user@domain.com)."

def validate_phone(phone):
    """Validates phone number format."""
    if not phone:
        return False, "Phone number cannot be empty."
    # Clean phone number (allow +, digits, and spaces/dashes)
    cleaned = re.sub(r"[\s\-()]", "", phone)
    phone_regex = r"^\+?\d{7,15}$"
    if re.match(phone_regex, cleaned):
        return True, ""
    return False, "Invalid phone number. Must contain 7 to 15 digits (optional leading '+')."

def validate_password_strength(password):
    """Validates password strength (length and simple check)."""
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def validate_age(age):
    """Validates that age is a positive integer."""
    try:
        val = int(age)
        if val <= 0 or val > 120:
            return False, "Age must be a valid number between 1 and 120."
        return True, ""
    except (ValueError, TypeError):
        return False, "Age must be an integer."

def validate_weight(weight):
    """Validates that weight is a positive float."""
    try:
        val = float(weight)
        if val <= 0 or val > 500:
            return False, "Weight must be a valid number between 0.1 and 500 kg."
        return True, ""
    except (ValueError, TypeError):
        return False, "Weight must be a decimal number."

def validate_non_empty(val, field_name):
    """Validates that a string value is not empty after stripping whitespace."""
    if not val or not str(val).strip():
        return False, f"{field_name} cannot be empty."
    return True, ""
