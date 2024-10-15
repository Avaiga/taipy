# taipy/validators.py

from datetime import datetime
from taipy.core.exceptions import ValidationError

def validate_time_in_15_min_intervals(datetime_str: str) -> datetime:
    """
    Validates that the time in the given datetime string is in 15-minute intervals.

    Args:
        datetime_str (str): The datetime string to validate.

    Returns:
        datetime: The parsed datetime object if valid.

    Raises:
        ValidationError: If the time is not in 15-minute intervals or format is incorrect.
    """
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        if dt.minute % 15 != 0:
            raise ValidationError("Minutes must be in 15-minute increments (e.g., 00, 15, 30, 45).")
        return dt
    except ValueError:
        raise ValidationError("Invalid datetime format. Expected format: YYYY-MM-DD HH:MM")
