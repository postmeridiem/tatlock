"""
tests/test_voice_service.py

Tests for the voice service module.
"""

import pytest
import asyncio
import tempfile
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from temporal.voice_service import VoiceService


class TestVoiceService:
    """Test the VoiceService class."""
    
    def test_initialization(self):
        """Test VoiceService initialization."""
        service = VoiceService(context_window_hours=12)
        
        assert service.temporal_context is not None
        assert service.language_processor is not None
        assert service.websocket_server is None
        assert service.audio_callbacks == []
        assert service.whisper_model is None
        assert service.is_initialized is False
    
    def test_initialization_default(self):
        """Test VoiceService initialization with default values."""
        service = VoiceService()
        
        assert service.temporal_context is not None
        assert service.language_processor is not None
        assert service.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful initialization."""
        service = VoiceService()
        
        with patch('builtins.__import__') as mock_import:
            mock_whisper = MagicMock()
            mock_whisper.load_model.return_value = MagicMock()
            mock_import.return_value = mock_whisper
            
            result = await service.initialize()
            
            assert result is True
            assert service.is_initialized is True
            assert service.whisper_model is not None
    
    @pytest.mark.asyncio
    async def test_initialize_import_error(self):
        """Test initialization with import error."""
        service = VoiceService()
        
        with patch('builtins.__import__', side_effect=ImportError("Whisper not available")):
            result = await service.initialize()
            
            assert result is False
            assert service.is_initialized is False
            assert service.whisper_model is None
    
    @pytest.mark.asyncio
    async def test_initialize_other_error(self):
        """Test initialization with other errors."""
        service = VoiceService()
        
        with patch('builtins.__import__') as mock_import:
            mock_whisper = MagicMock()
            mock_whisper.load_model.side_effect = Exception("Model loading failed")
            mock_import.return_value = mock_whisper
            
            result = await service.initialize()
            
            assert result is False
            assert service.is_initialized is False
            assert service.whisper_model is None
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self):
        """Test successful audio transcription."""
        service = VoiceService()
        service.is_initialized = True
        
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Hello world"}
        service.whisper_model = mock_model
        
        audio_data = b"fake_audio_data"
        
        with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            with patch('os.unlink') as mock_unlink:
                result = await service.transcribe_audio(audio_data)
                
                assert result == "Hello world"
                mock_file.write.assert_called_once_with(audio_data)
                mock_model.transcribe.assert_called_once_with("/tmp/test.wav")
                mock_unlink.assert_called_once_with("/tmp/test.wav")
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_not_initialized(self):
        """Test transcription when not initialized."""
        service = VoiceService()
        service.is_initialized = False
        
        result = await service.transcribe_audio(b"audio_data")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_error(self):
        """Test transcription with error."""
        service = VoiceService()
        service.is_initialized = True
    
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        service.whisper_model = mock_model
    
        with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_tempfile.return_value.__enter__.return_value = mock_file
    
            result = await service.transcribe_audio(b"audio_data")
    
            assert result is None
    
    @pytest.mark.asyncio
    async def test_process_voice_command_success(self):
        """Test successful voice command processing."""
        service = VoiceService()
        
        with patch.object(service.language_processor, 'process_with_context') as mock_process:
            with patch.object(service.language_processor, 'extract_intent') as mock_intent:
                with patch.object(service, 'send_to_cortex') as mock_cortex:
                    mock_process.return_value = "Processed text"
                    mock_intent.return_value = {"categories": ["weather"]}
                    mock_cortex.return_value = "Weather response"
                    
                    result = await service.process_voice_command("What's the weather?")
                    
                    assert result["original_text"] == "What's the weather?"
                    assert result["processed_text"] == "Processed text"
                    assert result["intent"] == {"categories": ["weather"]}
                    assert result["agent_response"] == "Weather response"
                    assert "temporal_context" in result
                    assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_process_voice_command_empty_text(self):
        """Test processing empty text."""
        service = VoiceService()
        
        result = await service.process_voice_command("")
        
        assert result["error"] == "No text to process"
    
    @pytest.mark.asyncio
    async def test_process_voice_command_with_websocket(self):
        """Test voice command processing with WebSocket."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        
        with patch.object(service.language_processor, 'process_with_context') as mock_process:
            with patch.object(service.language_processor, 'extract_intent') as mock_intent:
                with patch.object(service, 'send_to_cortex') as mock_cortex:
                    with patch.object(service, 'send_response_to_client') as mock_send:
                        mock_process.return_value = "Processed text"
                        mock_intent.return_value = {"categories": ["time"]}
                        mock_cortex.return_value = "Time response"
                        
                        result = await service.process_voice_command("What time is it?", mock_websocket)
                        
                        assert result["agent_response"] == "Time response"
                        mock_send.assert_called_once_with(mock_websocket, result)
    
    @pytest.mark.asyncio
    async def test_send_to_cortex_urgent(self):
        """Test sending urgent request to cortex."""
        service = VoiceService()
        
        result = await service.send_to_cortex("Emergency!", {"urgency": "high"})
        
        assert "Urgent request processed" in result
    
    @pytest.mark.asyncio
    async def test_send_to_cortex_weather(self):
        """Test sending weather request to cortex."""
        service = VoiceService()
        
        result = await service.send_to_cortex("Weather query", {"categories": ["weather"]})
        
        assert "Weather query detected" in result
    
    @pytest.mark.asyncio
    async def test_send_to_cortex_time(self):
        """Test sending time request to cortex."""
        service = VoiceService()
        
        result = await service.send_to_cortex("Time query", {"categories": ["time"]})
        
        assert "Time query detected" in result
    
    @pytest.mark.asyncio
    async def test_send_to_cortex_general(self):
        """Test sending general request to cortex."""
        service = VoiceService()
        
        result = await service.send_to_cortex("General command", {"categories": ["general"]})
        
        assert "Voice command processed" in result
    
    @pytest.mark.asyncio
    async def test_send_response_to_client_success(self):
        """Test successful response sending to client."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        
        response = {"status": "success", "data": "test"}
        
        await service.send_response_to_client(mock_websocket, response)
        
        mock_websocket.send.assert_called_once_with(json.dumps(response))
    
    @pytest.mark.asyncio
    async def test_send_response_to_client_error(self):
        """Test response sending with error."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.send.side_effect = Exception("Send failed")
        
        response = {"status": "success", "data": "test"}
        
        await service.send_response_to_client(mock_websocket, response)
        
        # Should not raise exception, just log error
        mock_websocket.send.assert_called_once()
    
    def test_get_temporal_summary(self):
        """Test getting temporal summary."""
        service = VoiceService()
        
        summary = service.get_temporal_summary()
        
        assert "message" in summary
        assert summary["message"] == "No interactions recorded"
    
    def test_add_audio_callback(self):
        """Test adding audio callback."""
        service = VoiceService()
        
        def test_callback():
            pass
        
        service.add_audio_callback(test_callback)
        
        assert len(service.audio_callbacks) == 1
        assert service.audio_callbacks[0] == test_callback
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_audio_message(self):
        """Test handling WebSocket audio message."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
    
        with patch.object(service, 'transcribe_audio') as mock_transcribe:
            with patch.object(service, 'process_voice_command') as mock_process:
                mock_transcribe.return_value = "Transcribed text"
    
                # Create a proper async generator for messages
                async def message_generator():
                    yield b'audio:fake_audio_data'
    
                # Set up the async iterator properly
                mock_websocket.__aiter__ = lambda self: message_generator()
    
                await service.handle_websocket_connection(mock_websocket, "/ws/voice")
    
                mock_transcribe.assert_called_once_with(b'fake_audio_data')
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_text_message_json(self):
        """Test handling WebSocket text message with JSON."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
    
        with patch.object(service, 'process_voice_command') as mock_process:
            # Create a proper async generator for messages
            async def message_generator():
                yield '{"type": "text", "text": "Hello world"}'
    
            # Set up the async iterator properly
            mock_websocket.__aiter__ = lambda self: message_generator()
    
            await service.handle_websocket_connection(mock_websocket, "/ws/voice")
    
            mock_process.assert_called_once_with("Hello world", mock_websocket)
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_text_message_plain(self):
        """Test handling WebSocket text message as plain text."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
    
        with patch.object(service, 'process_voice_command') as mock_process:
            # Create a proper async generator for messages
            async def message_generator():
                yield 'Hello world'
    
            # Set up the async iterator properly
            mock_websocket.__aiter__ = lambda self: message_generator()
    
            await service.handle_websocket_connection(mock_websocket, "/ws/voice")
    
            mock_process.assert_called_once_with("Hello world", mock_websocket)
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_invalid_json(self):
        """Test handling WebSocket message with invalid JSON."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
    
        with patch.object(service, 'process_voice_command') as mock_process:
            # Create a proper async generator for messages
            async def message_generator():
                yield '{"invalid": json}'
    
            # Set up the async iterator properly
            mock_websocket.__aiter__ = lambda self: message_generator()
    
            await service.handle_websocket_connection(mock_websocket, "/ws/voice")
    
            mock_process.assert_called_once_with('{"invalid": json}', mock_websocket)
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_error(self):
        """Test handling WebSocket connection error."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
        mock_websocket.__aiter__.side_effect = Exception("Connection error")
        
        await service.handle_websocket_connection(mock_websocket, "/ws/voice")
        
        # Should handle error gracefully
    
    @pytest.mark.asyncio
    async def test_start_websocket_server_success(self):
        """Test successful WebSocket server start."""
        service = VoiceService()
    
        with patch('builtins.__import__') as mock_import:
            mock_websockets = MagicMock()
            mock_server = MagicMock()
            
            # Make the serve method return an awaitable
            async def mock_serve(*args, **kwargs):
                return mock_server
            
            mock_websockets.serve = mock_serve
            mock_import.return_value = mock_websockets
    
            await service.start_websocket_server("localhost", 8765)
    
            assert service.websocket_server == mock_server
    
    @pytest.mark.asyncio
    async def test_start_websocket_server_import_error(self):
        """Test WebSocket server start with import error."""
        service = VoiceService()
        
        with patch('builtins.__import__', side_effect=ImportError("WebSockets not available")):
            await service.start_websocket_server()
            
            assert service.websocket_server is None
    
    @pytest.mark.asyncio
    async def test_start_websocket_server_other_error(self):
        """Test WebSocket server start with other error."""
        service = VoiceService()
        
        with patch('builtins.__import__') as mock_import:
            mock_websockets = MagicMock()
            mock_websockets.serve.side_effect = Exception("Server start failed")
            mock_import.return_value = mock_websockets
            
            await service.start_websocket_server()
            
            assert service.websocket_server is None
    
    def test_stop_websocket_server(self):
        """Test stopping WebSocket server."""
        service = VoiceService()
        mock_server = MagicMock()
        service.websocket_server = mock_server
        
        service.stop_websocket_server()
        
        mock_server.close.assert_called_once()
    
    def test_stop_websocket_server_no_server(self):
        """Test stopping WebSocket server when no server exists."""
        service = VoiceService()
        service.websocket_server = None
        
        # Should not raise exception
        service.stop_websocket_server()
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_with_whitespace(self):
        """Test transcription with whitespace in result."""
        service = VoiceService()
        service.is_initialized = True
        
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "  Hello world  "}
        service.whisper_model = mock_model
        
        with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            with patch('os.unlink'):
                result = await service.transcribe_audio(b"audio_data")
                
                assert result == "Hello world"  # Should be stripped
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_empty_result(self):
        """Test transcription with empty result."""
        service = VoiceService()
        service.is_initialized = True
        
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": ""}
        service.whisper_model = mock_model
        
        with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            with patch('os.unlink'):
                result = await service.transcribe_audio(b"audio_data")
                
                assert result == ""  # Should return empty string
    
    @pytest.mark.asyncio
    async def test_process_voice_command_adds_to_temporal_context(self):
        """Test that voice command is added to temporal context."""
        service = VoiceService()
        
        with patch.object(service.temporal_context, 'add_interaction') as mock_add:
            with patch.object(service.language_processor, 'process_with_context'):
                with patch.object(service.language_processor, 'extract_intent'):
                    with patch.object(service, 'send_to_cortex'):
                        await service.process_voice_command("Test command")
                        
                        mock_add.assert_called_once_with("Test command")
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_multiple_messages(self):
        """Test handling multiple WebSocket messages."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
    
        with patch.object(service, 'transcribe_audio') as mock_transcribe:
            with patch.object(service, 'process_voice_command') as mock_process:
                mock_transcribe.return_value = "Transcribed text"
    
                # Create a proper async generator for multiple messages
                async def message_generator():
                    yield b'audio:audio1'
                    yield b'audio:audio2'
                    yield '{"type": "text", "text": "Hello"}'
    
                # Set up the async iterator properly
                mock_websocket.__aiter__ = lambda self: message_generator()
    
                await service.handle_websocket_connection(mock_websocket, "/ws/voice")
    
                assert mock_transcribe.call_count == 2
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_no_audio_prefix(self):
        """Test handling WebSocket message without audio prefix."""
        service = VoiceService()
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
    
        with patch.object(service, 'process_voice_command') as mock_process:
            # Create a proper async generator for messages
            async def message_generator():
                yield b'not_audio_data'
    
            # Set up the async iterator properly
            mock_websocket.__aiter__ = lambda self: message_generator()
    
            await service.handle_websocket_connection(mock_websocket, "/ws/voice")
    
            # Should treat as text message
            mock_process.assert_called_once_with('not_audio_data', mock_websocket) 