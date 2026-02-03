import pytest
from src.utils.helpers import map_dict_to_pydantic
from pydantic import ValidationError



def test_map_dict_to_pydantic_valid_schema():
    schema = {
        "name": {"type": "str", "default": "John", "description": "User's name"},
        "age": {"type": "int", "default": 30, "description": "User's age"},
    }
    Model = map_dict_to_pydantic(schema)
    instance = Model(name="Alice", age=25)
    assert instance.name == "Alice"
    assert instance.age == 25



def test_map_dict_to_pydantic_invalid_type():
    schema = {
        "name": {"type": "unsupported_type", "default": "John"},
    }
    with pytest.raises(ValueError, match="Unsupported type 'unsupported_type' for field 'name'"):
        map_dict_to_pydantic(schema)



def test_map_dict_to_pydantic_missing_field():
    schema = {
        "name": "str",
    }
    Model = map_dict_to_pydantic(schema)
    with pytest.raises(ValidationError):
        Model()