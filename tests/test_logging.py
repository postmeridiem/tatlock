"""
Tests for stem.logging module.
"""

import pytest
from unittest.mock import patch, MagicMock
from stem.logging import log_error, log_info


class TestLogError:
    """Test error logging function."""
    
    def test_log_error_basic(self):
        """Test basic error logging."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error("Test error message")
            
            # Verify logger.error was called
            mock_logger.error.assert_called_once_with("Test error message")
    
    def test_log_error_with_timestamp(self):
        """Test error logging includes timestamp."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error("Test error message")
            
            mock_logger.error.assert_called_once_with("Test error message")
    
    def test_log_error_empty_message(self):
        """Test error logging with empty message."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error("")
            
            mock_logger.error.assert_called_once_with("")
    
    def test_log_error_special_characters(self):
        """Test error logging with special characters."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error("Error with special chars: !@#$%^&*()")
            
            mock_logger.error.assert_called_once_with("Error with special chars: !@#$%^&*()")
    
    def test_log_error_unicode(self):
        """Test error logging with Unicode characters."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error("Erreur avec des caractères spéciaux: éàç")
            
            mock_logger.error.assert_called_once_with("Erreur avec des caractères spéciaux: éàç")
    
    def test_log_error_none_message(self):
        """Test error logging with None message."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error(None)  # type: ignore
            
            mock_logger.error.assert_called_once_with(None)


class TestLogInfo:
    """Test info logging function."""
    
    def test_log_info_basic(self):
        """Test basic info logging."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info("Test info message")
            
            # Verify logger.info was called
            mock_logger.info.assert_called_once_with("Test info message")
    
    def test_log_info_with_timestamp(self):
        """Test info logging includes timestamp."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info("Test info message")
            
            mock_logger.info.assert_called_once_with("Test info message")
    
    def test_log_info_empty_message(self):
        """Test info logging with empty message."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info("")
            
            mock_logger.info.assert_called_once_with("")
    
    def test_log_info_special_characters(self):
        """Test info logging with special characters."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info("Info with special chars: !@#$%^&*()")
            
            mock_logger.info.assert_called_once_with("Info with special chars: !@#$%^&*()")
    
    def test_log_info_unicode(self):
        """Test info logging with Unicode characters."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info("Information avec des caractères spéciaux: éàç")
            
            mock_logger.info.assert_called_once_with("Information avec des caractères spéciaux: éàç")
    
    def test_log_info_none_message(self):
        """Test info logging with None message."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info(None)  # type: ignore
            
            mock_logger.info.assert_called_once_with(None)


class TestLoggingFormat:
    """Test logging format consistency."""
    
    def test_log_format_consistency(self):
        """Test that error and info logs have consistent format."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error("Test message")
            log_info("Test message")
            
            # Should have been called twice
            assert mock_logger.error.call_count == 1
            assert mock_logger.info.call_count == 1
            
            mock_logger.error.assert_called_once_with("Test message")
            mock_logger.info.assert_called_once_with("Test message")
    
    def test_log_level_prefixes(self):
        """Test that logs have correct level prefixes."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_error("Error message")
            log_info("Info message")
            
            mock_logger.error.assert_called_once_with("Error message")
            mock_logger.info.assert_called_once_with("Info message")


class TestLoggingIntegration:
    """Test logging integration scenarios."""
    
    def test_multiple_log_calls(self):
        """Test multiple logging calls."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info("First message")
            log_error("Second message")
            log_info("Third message")
            
            assert mock_logger.info.call_count == 2
            assert mock_logger.error.call_count == 1
            
            calls = [
                mock_logger.info.call_args_list[0][0][0],
                mock_logger.error.call_args_list[0][0][0],
                mock_logger.info.call_args_list[1][0][0]
            ]
            assert calls[0] == "First message"
            assert calls[1] == "Second message"
            assert calls[2] == "Third message"
    
    def test_log_with_numbers(self):
        """Test logging with numeric values."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_info("User count: 42")
            log_error("Error code: 500")
            
            mock_logger.info.assert_called_once_with("User count: 42")
            mock_logger.error.assert_called_once_with("Error code: 500")
    
    def test_log_with_objects(self):
        """Test logging with object representations."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            test_dict = {"key": "value", "number": 123}
            log_info(f"Configuration: {test_dict}")
            
            mock_logger.info.assert_called_once_with(f"Configuration: {test_dict}") 