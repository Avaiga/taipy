import pytest

from taipy.core.common._classproperty import _Classproperty


class TestClassProperty:
    def test_class_property(self):
        class TestClass:
            @_Classproperty
            def test_property(cls):
                return "test_property"

        assert TestClass.test_property == "test_property"
        assert TestClass().test_property == "test_property"
        with pytest.raises(TypeError):
            TestClass.test_property()
