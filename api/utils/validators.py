from rest_framework.exceptions import ValidationError

def verify_required_params(data, required_params):
    """
    Verifies that all required parameters are present in the data.
    Raises a ValidationError if any required parameter is missing.
    """
    missing_params = [param for param in required_params if param not in data]
    if missing_params:
        raise ValidationError(f"Missing required parameters: {', '.join(missing_params)}")
