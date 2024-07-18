import re
from datetime import timedelta
from rest_framework.exceptions import ValidationError

def validate_required_fields(required_fields, data):
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        raise ValidationError({"message": f"Missing fields: {', '.join(missing_fields)}"})


def parse_duration(duration):
    match = re.match(r'(\d+)\s*([DMY])', duration)
    if not match:
        raise ValueError("Invalid duration format")
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'D':
        return timedelta(days=value)
    elif unit == 'M':
        return timedelta(days=30 * value)  
    elif unit == 'Y':
        return timedelta(days=365 * value)
    else:
        raise ValueError("Unsupported duration unit")