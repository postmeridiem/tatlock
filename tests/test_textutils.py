"""
Tests for stem.textutils module.
"""

import pytest
from stem.textutils import normalize_text, truncate_text


class TestNormalizeText:
    """Test text normalization function."""
    
    def test_normalize_simple_text(self):
        """Test normalizing simple text."""
        result = normalize_text("Hello World")
        assert result == "hello world"
    
    def test_normalize_with_whitespace(self):
        """Test normalizing text with extra whitespace."""
        result = normalize_text("  Hello   World  ")
        assert result == "hello   world"  # strip() only removes leading/trailing whitespace
    
    def test_normalize_mixed_case(self):
        """Test normalizing text with mixed case."""
        result = normalize_text("HeLLo WoRLd")
        assert result == "hello world"
    
    def test_normalize_empty_string(self):
        """Test normalizing empty string."""
        result = normalize_text("")
        assert result == ""
    
    def test_normalize_whitespace_only(self):
        """Test normalizing whitespace-only string."""
        result = normalize_text("   \t\n   ")
        assert result == ""
    
    def test_normalize_single_character(self):
        """Test normalizing single character."""
        result = normalize_text("A")
        assert result == "a"
    
    def test_normalize_numbers(self):
        """Test normalizing text with numbers."""
        result = normalize_text("Hello 123 World")
        assert result == "hello 123 world"
    
    def test_normalize_special_characters(self):
        """Test normalizing text with special characters."""
        result = normalize_text("Hello! @#$%^&*() World")
        assert result == "hello! @#$%^&*() world"
    
    def test_normalize_unicode(self):
        """Test normalizing text with unicode characters."""
        result = normalize_text("Héllö Wörld")
        assert result == "héllö wörld"
    
    def test_normalize_none_input(self):
        """Test normalizing None input."""
        result = normalize_text(None)  # type: ignore
        assert result == ""
    
    def test_normalize_integer_input(self):
        """Test normalizing integer input."""
        result = normalize_text(123)  # type: ignore
        assert result == ""
    
    def test_normalize_list_input(self):
        """Test normalizing list input."""
        result = normalize_text(["hello", "world"])  # type: ignore
        assert result == ""


class TestTruncateText:
    """Test text truncation function."""
    
    def test_truncate_short_text(self):
        """Test truncating text shorter than max length."""
        result = truncate_text("Hello World", 20)
        assert result == "Hello World"
    
    def test_truncate_exact_length(self):
        """Test truncating text exactly at max length."""
        result = truncate_text("Exactly twenty chars", 20)
        assert result == "Exactly twenty chars"
    
    def test_truncate_long_text(self):
        """Test truncating text longer than max length."""
        result = truncate_text("This is a very long text that needs to be truncated", 20)
        assert result == "This is a very long ..."  # Function adds space before ellipsis
    
    def test_truncate_with_default_length(self):
        """Test truncating with default max length."""
        long_text = "x" * 201
        result = truncate_text(long_text)
        assert len(result) == 203  # 200 chars + "..."
        assert result.endswith("...")
    
    def test_truncate_empty_string(self):
        """Test truncating empty string."""
        result = truncate_text("")
        assert result == ""
    
    def test_truncate_whitespace_only(self):
        """Test truncating whitespace-only string."""
        result = truncate_text("   \t\n   ")
        assert result == "   \t\n   "
    
    def test_truncate_single_character(self):
        """Test truncating single character."""
        result = truncate_text("A", 1)
        assert result == "A"
    
    def test_truncate_at_boundary(self):
        """Test truncating at word boundary."""
        result = truncate_text("Hello World", 5)
        assert result == "Hello..."
    
    def test_truncate_very_short_max_length(self):
        """Test truncating with very short max length."""
        result = truncate_text("Hello World", 3)
        assert result == "Hel..."
    
    def test_truncate_zero_max_length(self):
        """Test truncating with zero max length."""
        result = truncate_text("Hello World", 0)
        assert result == "..."
    
    def test_truncate_negative_max_length(self):
        """Test truncating with negative max length."""
        result = truncate_text("Hello World", -5)
        assert result == "Hello ..."  # Function doesn't handle negative lengths specially
    
    def test_truncate_unicode_text(self):
        """Test truncating text with unicode characters."""
        result = truncate_text("Héllö Wörld", 5)
        assert result == "Héllö..."
    
    def test_truncate_none_input(self):
        """Test truncating None input."""
        result = truncate_text(None)  # type: ignore
        assert result == ""
    
    def test_truncate_integer_input(self):
        """Test truncating integer input."""
        result = truncate_text(123)  # type: ignore
        assert result == ""
    
    def test_truncate_list_input(self):
        """Test truncating list input."""
        result = truncate_text(["hello", "world"])  # type: ignore
        assert result == ""


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_normalize_very_long_text(self):
        """Test normalizing very long text."""
        long_text = "A" * 10000
        result = normalize_text(long_text)
        
        assert result == "a" * 10000
        assert len(result) == 10000
    
    def test_truncate_very_long_text(self):
        """Test truncating very long text."""
        long_text = "A" * 10000
        result = truncate_text(long_text, 100)
        
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")
    
    def test_normalize_mixed_types(self):
        """Test normalizing text with mixed types."""
        result = normalize_text("Hello123World")
        assert result == "hello123world"
    
    def test_truncate_preserves_original(self):
        """Test that truncate doesn't modify original string."""
        original = "Hello World"
        result = truncate_text(original, 5)
        
        assert original == "Hello World"  # Original unchanged
        assert result == "Hello..."
    
    def test_normalize_preserves_original(self):
        """Test that normalize doesn't modify original string."""
        original = "  Hello World  "
        result = normalize_text(original)
        
        assert original == "  Hello World  "  # Original unchanged
        assert result == "hello world"
    
    def test_truncate_with_ellipsis_in_text(self):
        """Test truncating text that already contains ellipsis."""
        result = truncate_text("Hello...World", 8)
        assert result == "Hello......"  # Function adds ellipsis regardless of existing ones
    
    def test_normalize_with_control_characters(self):
        """Test normalizing text with control characters."""
        result = normalize_text("Hello\tWorld\n")
        assert result == "hello\tworld"  # strip() removes newlines but not tabs
    
    def test_truncate_with_control_characters(self):
        """Test truncating text with control characters."""
        result = truncate_text("Hello\tWorld\n", 8)
        assert result == "Hello\tWo..."
        assert len(result) == 11  # 8 + "..." 