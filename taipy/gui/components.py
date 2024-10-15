# taipy/gui/components.py

from taipy.common.config.validators import validate_time_in_15_min_intervals
from taipy.core.exceptions import ValidationError

class DateWithTimeInput():
    def __init__(self, *args, **kwargs):
        # existing initialization
        self.minute_step = 15  # Define step size for minutes

    def validate(self, value: str):
        """
        Validates the input value using the 15-minute interval validator.
        """
        try:
            validated_datetime = validate_time_in_15_min_intervals(value)
            return validated_datetime
        except ValidationError as e:
            self.show_error(str(e))
            return None

    def show_error(self, message: str):
        """
        Displays an error message.
        """
        print(f"Error: {message}")

    def render(self):
        """
        Renders the input component with a time picker that increments by 15 minutes.
        """
        return f"""
        <input type="datetime-local" step="900" ... />
        """
