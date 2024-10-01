import logging
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

def verify_required_params(data, required_params, case_insensitive=False, allow_empty=False):
    
    missing_params = []
    
    data_keys = data.keys()
    if case_insensitive:
        data_keys = [key.lower() for key in data_keys]
        required_params = [param.lower() for key in required_params]

    for param in required_params:
        if param not in data_keys:
            missing_params.append(param)
        elif not allow_empty and (data.get(param) in [None, '', []]):
            missing_params.append(param)
    
    if missing_params:
        missing_params_str = ', '.join(missing_params) 
        error_message = f"Missing or invalid parameters: {missing_params_str}"
        logger.error(f"Missing required parameters: {missing_params_str}")
        raise ValidationError(error_message)

    logger.debug(f"All required parameters are present: {required_params}")
