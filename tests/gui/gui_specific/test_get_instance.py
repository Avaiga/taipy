import pytest
from taipy.gui.data.data_accessor import _DataAccessors, _InvalidDataAccessor
from taipy.gui import Gui


def test__get_instance_with_valid_data(gui: Gui):
    """Test if __get_instance returns the correct accessor for valid data."""
    data_accessors = _DataAccessors(gui)

    # Simulate valid data being passed
    data_accessors._DataAccessors__access_4_type = {int: "valid_accessor"} # type: ignore

    result = data_accessors._DataAccessors__get_instance(123) # type: ignore
    assert result == "valid_accessor"  # Valid accessor should be returned


def test__get_instance_with_invalid_data(gui: Gui):
    """Test if __get_instance handles invalid data correctly."""
    data_accessors = _DataAccessors(gui)

    # No valid data accessor, should return None
    gui.handle_invalid_data = lambda x: None # type: ignore
    result = data_accessors._DataAccessors__get_instance("invalid_data") # type: ignore

    assert isinstance(result, _InvalidDataAccessor)  # Should return InvalidDataAccessor


def test__get_instance_transformation_successful(gui: Gui):
    """Test if __get_instance transforms invalid data correctly when callback is set."""
    data_accessors = _DataAccessors(gui)

    # Mock invalid data transformation to return valid data
    gui.handle_invalid_data = lambda x: 123  # type: ignore # Transformation success
    data_accessors._DataAccessors__access_4_type = {int: "valid_accessor"} # type: ignore

    result = data_accessors._DataAccessors__get_instance("invalid_data") # type: ignore
    assert (
        result == "valid_accessor"
    )  # Transformed data should now return the valid accessor
