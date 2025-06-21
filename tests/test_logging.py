"""
Tests for stem.logging module.
"""

import pytest
from unittest.mock import patch
from io import StringIO
from stem.logging import log_error, log_info


class TestLogError:
    """Test error logging function."""
    
    def test_log_error_basic(self):
        """Test basic error logging."""
        with patch('builtins.print') as mock_print:
            log_error("Test error message")
            
            # Verify print was called
            mock_print.assert_called_once()
            
            # Get the printed message
            call_args = mock_print.call_args[0][0]
            assert "[ERROR]" in call_args
            assert "Test error message" in call_args
    
    def test_log_error_with_timestamp(self):
        """Test error logging includes timestamp."""
        with patch('builtins.print') as mock_print:
            log_error("Test error message")
            
            call_args = mock_print.call_args[0][0]
            # Check for timestamp format (ISO format)
            assert "T" in call_args  # ISO format separator
            assert "-" in call_args  # Date separator
            assert ":" in call_args  # Time separator
    
    def test_log_error_empty_message(self):
        """Test error logging with empty message."""
        with patch('builtins.print') as mock_print:
            log_error("")
            
            call_args = mock_print.call_args[0][0]
            assert "[ERROR]" in call_args
            assert call_args.endswith(" - ")
    
    def test_log_error_special_characters(self):
        """Test error logging with special characters."""
        with patch('builtins.print') as mock_print:
            log_error("Error with special chars: !@#$%^&*()")
            
            call_args = mock_print.call_args[0][0]
            assert "[ERROR]" in call_args
            assert "Error with special chars: !@#$%^&*()" in call_args
    
    def test_log_error_unicode(self):
        """Test error logging with Unicode characters."""
        with patch('builtins.print') as mock_print:
            log_error("Erreur avec des caractères spéciaux: éàç")
            
            call_args = mock_print.call_args[0][0]
            assert "[ERROR]" in call_args
            assert "Erreur avec des caractères spéciaux: éàç" in call_args
    
    def test_log_error_none_message(self):
        """Test error logging with None message."""
        with patch('builtins.print') as mock_print:
            log_error(None)  # type: ignore
            
            call_args = mock_print.call_args[0][0]
            assert "[ERROR]" in call_args
            assert "None" in call_args


class TestLogInfo:
    """Test info logging function."""
    
    def test_log_info_basic(self):
        """Test basic info logging."""
        with patch('builtins.print') as mock_print:
            log_info("Test info message")
            
            # Verify print was called
            mock_print.assert_called_once()
            
            # Get the printed message
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert "Test info message" in call_args
    
    def test_log_info_with_timestamp(self):
        """Test info logging includes timestamp."""
        with patch('builtins.print') as mock_print:
            log_info("Test info message")
            
            call_args = mock_print.call_args[0][0]
            # Check for timestamp format (ISO format)
            assert "T" in call_args  # ISO format separator
            assert "-" in call_args  # Date separator
            assert ":" in call_args  # Time separator
    
    def test_log_info_empty_message(self):
        """Test info logging with empty message."""
        with patch('builtins.print') as mock_print:
            log_info("")
            
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert call_args.endswith(" - ")
    
    def test_log_info_special_characters(self):
        """Test info logging with special characters."""
        with patch('builtins.print') as mock_print:
            log_info("Info with special chars: !@#$%^&*()")
            
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert "Info with special chars: !@#$%^&*()" in call_args
    
    def test_log_info_unicode(self):
        """Test info logging with Unicode characters."""
        with patch('builtins.print') as mock_print:
            log_info("Information avec des caractères spéciaux: éàç")
            
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert "Information avec des caractères spéciaux: éàç" in call_args
    
    def test_log_info_none_message(self):
        """Test info logging with None message."""
        with patch('builtins.print') as mock_print:
            log_info(None)  # type: ignore
            
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert "None" in call_args


class TestLoggingFormat:
    """Test logging format consistency."""
    
    def test_log_format_consistency(self):
        """Test that error and info logs have consistent format."""
        with patch('builtins.print') as mock_print:
            log_error("Test message")
            log_info("Test message")
            
            # Should have been called twice
            assert mock_print.call_count == 2
            
            error_call = mock_print.call_args_list[0][0][0]
            info_call = mock_print.call_args_list[1][0][0]
            
            # Both should have timestamp and message
            assert "T" in error_call
            assert "T" in info_call
            assert " - " in error_call
            assert " - " in info_call
            assert "Test message" in error_call
            assert "Test message" in info_call
    
    def test_log_level_prefixes(self):
        """Test that logs have correct level prefixes."""
        with patch('builtins.print') as mock_print:
            log_error("Error message")
            log_info("Info message")
            
            error_call = mock_print.call_args_list[0][0][0]
            info_call = mock_print.call_args_list[1][0][0]
            
            assert "[ERROR]" in error_call
            assert "[INFO]" in info_call


class TestLoggingIntegration:
    """Test logging integration scenarios."""
    
    def test_multiple_log_calls(self):
        """Test multiple logging calls."""
        with patch('builtins.print') as mock_print:
            log_info("First message")
            log_error("Second message")
            log_info("Third message")
            
            assert mock_print.call_count == 3
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert "[INFO]" in calls[0]
            assert "[ERROR]" in calls[1]
            assert "[INFO]" in calls[2]
    
    def test_log_with_numbers(self):
        """Test logging with numeric values."""
        with patch('builtins.print') as mock_print:
            log_info("User count: 42")
            log_error("Error code: 500")
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert "User count: 42" in calls[0]
            assert "Error code: 500" in calls[1]
    
    def test_log_with_objects(self):
        """Test logging with object representations."""
        with patch('builtins.print') as mock_print:
            test_dict = {"key": "value", "number": 123}
            log_info(f"Configuration: {test_dict}")
            
            call_args = mock_print.call_args[0][0]
            assert "Configuration:" in call_args
            assert "key" in call_args
            assert "value" in call_args 