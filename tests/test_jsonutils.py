"""
Tests for stem.jsonutils module.
"""

import pytest
import json
from stem.jsonutils import to_json, from_json


class TestToJson:
    """Test JSON serialization function."""
    
    def test_simple_dict(self):
        """Test serializing a simple dictionary."""
        data = {"name": "John", "age": 30}
        result = to_json(data)
        
        assert result == '{"name": "John", "age": 30}'
        # Verify it's valid JSON
        assert json.loads(result) == data
    
    def test_simple_list(self):
        """Test serializing a simple list."""
        data = [1, 2, 3, "test"]
        result = to_json(data)
        
        assert result == '[1, 2, 3, "test"]'
        # Verify it's valid JSON
        assert json.loads(result) == data
    
    def test_nested_structure(self):
        """Test serializing nested data structures."""
        data = {
            "user": {
                "name": "John",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown"
                }
            },
            "items": [1, 2, {"id": 3, "name": "item3"}]
        }
        result = to_json(data)
        
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == data
        assert parsed["user"]["address"]["city"] == "Anytown"
        assert parsed["items"][2]["name"] == "item3"
    
    def test_string_input(self):
        """Test serializing a string."""
        data = "Hello, World!"
        result = to_json(data)
        
        assert result == '"Hello, World!"'
        # Verify it's valid JSON
        assert json.loads(result) == data
    
    def test_number_input(self):
        """Test serializing numbers."""
        # Integer
        result = to_json(42)
        assert result == "42"
        assert json.loads(result) == 42
        
        # Float
        result = to_json(3.14)
        assert result == "3.14"
        assert json.loads(result) == 3.14
    
    def test_boolean_input(self):
        """Test serializing booleans."""
        # True
        result = to_json(True)
        assert result == "true"
        assert json.loads(result) is True
        
        # False
        result = to_json(False)
        assert result == "false"
        assert json.loads(result) is False
    
    def test_none_input(self):
        """Test serializing None."""
        result = to_json(None)
        assert result == "null"
        assert json.loads(result) is None
    
    def test_empty_structures(self):
        """Test serializing empty data structures."""
        # Empty dict
        result = to_json({})
        assert result == "{}"
        assert json.loads(result) == {}
        
        # Empty list
        result = to_json([])
        assert result == "[]"
        assert json.loads(result) == []
    
    def test_unicode_characters(self):
        """Test serializing Unicode characters."""
        data = {"message": "Hello, 世界! 🌍"}
        result = to_json(data)
        
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == data
        assert parsed["message"] == "Hello, 世界! 🌍"


class TestToJsonErrorHandling:
    """Test JSON serialization error handling."""
    
    def test_circular_reference(self):
        """Test handling circular references."""
        data = {}
        data["self"] = data  # Circular reference
        
        result = to_json(data)
        
        # Should return empty string on error
        assert result == ""
    
    def test_function_object(self):
        """Test handling non-serializable objects."""
        def test_function():
            pass
        
        result = to_json(test_function)
        
        # Should return empty string on error
        assert result == ""
    
    def test_class_instance(self):
        """Test handling class instances."""
        class TestClass:
            def __init__(self):
                self.value = "test"
        
        instance = TestClass()
        result = to_json(instance)
        
        # Should return empty string on error
        assert result == ""


class TestFromJson:
    """Test JSON deserialization function."""
    
    def test_simple_dict(self):
        """Test deserializing a simple dictionary."""
        json_str = '{"name": "John", "age": 30}'
        result = from_json(json_str)
        
        assert result == {"name": "John", "age": 30}
    
    def test_simple_list(self):
        """Test deserializing a simple list."""
        json_str = '[1, 2, 3, "test"]'
        result = from_json(json_str)
        
        assert result == [1, 2, 3, "test"]
    
    def test_nested_structure(self):
        """Test deserializing nested data structures."""
        json_str = '{"user": {"name": "John", "address": {"street": "123 Main St", "city": "Anytown"}}, "items": [1, 2, {"id": 3, "name": "item3"}]}'
        result = from_json(json_str)
        
        assert result is not None
        assert result["user"]["name"] == "John"
        assert result["user"]["address"]["city"] == "Anytown"
        assert result["items"][2]["name"] == "item3"
    
    def test_string_input(self):
        """Test deserializing a string."""
        json_str = '"Hello, World!"'
        result = from_json(json_str)
        
        assert result == "Hello, World!"
    
    def test_number_input(self):
        """Test deserializing numbers."""
        # Integer
        result = from_json("42")
        assert result == 42
        
        # Float
        result = from_json("3.14")
        assert result == 3.14
    
    def test_boolean_input(self):
        """Test deserializing booleans."""
        # True
        result = from_json("true")
        assert result is True
        
        # False
        result = from_json("false")
        assert result is False
    
    def test_none_input(self):
        """Test deserializing null."""
        result = from_json("null")
        assert result is None
    
    def test_empty_structures(self):
        """Test deserializing empty data structures."""
        # Empty dict
        result = from_json("{}")
        assert result == {}
        
        # Empty list
        result = from_json("[]")
        assert result == []
    
    def test_unicode_characters(self):
        """Test deserializing Unicode characters."""
        json_str = '{"message": "Hello, 世界! 🌍"}'
        result = from_json(json_str)
        
        assert result is not None
        assert result["message"] == "Hello, 世界! 🌍"


class TestFromJsonErrorHandling:
    """Test JSON deserialization error handling."""
    
    def test_invalid_json_syntax(self):
        """Test handling invalid JSON syntax."""
        invalid_json = '{"name": "John", "age": 30,}'  # Trailing comma
        
        result = from_json(invalid_json)
        
        # Should return None on error
        assert result is None
    
    def test_missing_quotes(self):
        """Test handling missing quotes around keys."""
        invalid_json = '{name: "John", "age": 30}'  # Missing quotes around key
        
        result = from_json(invalid_json)
        
        # Should return None on error
        assert result is None
    
    def test_unclosed_brackets(self):
        """Test handling unclosed brackets."""
        invalid_json = '{"name": "John", "items": [1, 2, 3'  # Unclosed array
        
        result = from_json(invalid_json)
        
        # Should return None on error
        assert result is None
    
    def test_empty_string(self):
        """Test handling empty string."""
        result = from_json("")
        
        # Should return None on error
        assert result is None
    
    def test_whitespace_only(self):
        """Test handling whitespace-only string."""
        result = from_json("   ")
        
        # Should return None on error
        assert result is None
    
    def test_none_input(self):
        """Test handling None input."""
        result = from_json(None)  # type: ignore
        
        # Should return None on error
        assert result is None


class TestRoundTrip:
    """Test round-trip serialization and deserialization."""
    
    def test_dict_round_trip(self):
        """Test round-trip for dictionary."""
        original = {"name": "John", "age": 30, "active": True}
        
        json_str = to_json(original)
        result = from_json(json_str)
        
        assert result == original
    
    def test_list_round_trip(self):
        """Test round-trip for list."""
        original = [1, "test", {"nested": True}, None]
        
        json_str = to_json(original)
        result = from_json(json_str)
        
        assert result == original
    
    def test_nested_structure_round_trip(self):
        """Test round-trip for nested structure."""
        original = {
            "users": [
                {"id": 1, "name": "John", "roles": ["admin", "user"]},
                {"id": 2, "name": "Jane", "roles": ["user"]}
            ],
            "metadata": {
                "total": 2,
                "active": True,
                "last_updated": "2023-01-01"
            }
        }
        
        json_str = to_json(original)
        result = from_json(json_str)
        
        assert result == original 