import pytest

from taipy.core.common._validate_id import _validate_id
from taipy.core.exceptions.exceptions import InvalidConfigurationId


class TestId:
    def test_validate_id(self):
        s = _validate_id("foo")
        assert s == "foo"
        with pytest.raises(InvalidConfigurationId):
            _validate_id("1foo")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("foo bar")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("foo/foo$")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("")
        with pytest.raises(InvalidConfigurationId):
            _validate_id(" ")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("class")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("def")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("with")
