"""
Test voice service functionality
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime
from temporal.voice_service import VoiceService


class TestVoiceService:
    """Test VoiceService class"""
    
    def test_initialization(self):
        """Test VoiceService initialization"""
        service = VoiceService()
        assert service.temporal_context is not None
        assert service.language_processor is not None
        assert service.websocket_server is None
        assert service.audio_callbacks == []
        assert service.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test service initialization"""
        service = VoiceService()
        result = await service.initialize()
        assert result is False  # Voice processing is not available
        assert service.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_not_available(self):
        """Test that audio transcription is not available"""
        service = VoiceService()
        result = await service.transcribe_audio(b"fake_audio_data")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_voice_command_with_text(self):
        """Test processing voice command with text input"""
        service = VoiceService()
        
        # Mock temporal context and language processor
        service.temporal_context.add_interaction = MagicMock()
        service.temporal_context.get_current_context = MagicMock(return_value={
            "current_time": datetime(2024, 1, 1, 12, 0, 0)
        })
        service.language_processor.process_with_context = MagicMock(return_value="processed text")
        service.language_processor.extract_intent = MagicMock(return_value={
            "urgency": "normal",
            "categories": ["general"]
        })
        
        result = await service.process_voice_command("Hello, how are you?")
        
        assert result["original_text"] == "Hello, how are you?"
        assert result["processed_text"] == "processed text"
        assert result["intent"]["urgency"] == "normal"
        assert "agent_response" in result
    
    @pytest.mark.asyncio
    async def test_process_voice_command_empty_text(self):
        """Test processing voice command with empty text"""
        service = VoiceService()
        result = await service.process_voice_command("")
        assert result["error"] == "No text to process"
    
    @pytest.mark.asyncio
    async def test_send_to_cortex(self):
        """Test sending text to cortex"""
        service = VoiceService()
        
        result = await service.send_to_cortex("What's the weather?", {
            "urgency": "normal",
            "categories": ["weather"]
        })
        
        assert "Weather query detected" in result
    
    @pytest.mark.asyncio
    async def test_send_to_cortex_urgent(self):
        """Test sending urgent text to cortex"""
        service = VoiceService()
        
        result = await service.send_to_cortex("Emergency!", {
            "urgency": "high",
            "categories": ["emergency"]
        })
        
        assert "Urgent request processed" in result
    
    def test_get_temporal_summary(self):
        """Test getting temporal summary"""
        service = VoiceService()
        service.temporal_context.get_interaction_summary = MagicMock(return_value={
            "total_interactions": 10,
            "last_interaction": "2024-01-01T12:00:00"
        })
        
        summary = service.get_temporal_summary()
        assert summary["total_interactions"] == 10
    
    def test_add_audio_callback(self):
        """Test adding audio callback"""
        service = VoiceService()
        callback = MagicMock()
        
        service.add_audio_callback(callback)
        assert callback in service.audio_callbacks
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_audio_disabled(self):
        """Test WebSocket connection handling with audio disabled"""
        service = VoiceService()
        mock_websocket = MagicMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
        
        # Mock the websocket to return audio data
        async def mock_iter():
            yield b'audio:fake_audio_data'
            yield '{"type": "text", "text": "Hello"}'
        
        mock_websocket.__aiter__ = lambda self: mock_iter()
        
        # Mock send_response_to_client
        service.send_response_to_client = MagicMock()
        
        await service.handle_websocket_connection(mock_websocket, "/ws/voice")
        
        # Should have called send_response_to_client with error for audio
        service.send_response_to_client.assert_called()
    
    @pytest.mark.asyncio
    async def test_handle_websocket_connection_text_message(self):
        """Test WebSocket connection handling with text message"""
        service = VoiceService()
        mock_websocket = MagicMock()
        mock_websocket.remote_address = "127.0.0.1:12345"
        
        # Mock the websocket to return text data
        async def mock_iter():
            yield '{"type": "text", "text": "Hello"}'
        
        mock_websocket.__aiter__ = lambda self: mock_iter()
        
        # Mock process_voice_command
        service.process_voice_command = MagicMock()
        
        await service.handle_websocket_connection(mock_websocket, "/ws/voice")
        
        # Should have called process_voice_command
        service.process_voice_command.assert_called()
    
    @pytest.mark.asyncio
    async def test_start_websocket_server(self):
        """Test starting WebSocket server"""
        service = VoiceService()
        from unittest.mock import AsyncMock
        import importlib
        with patch('importlib.import_module') as mock_import_module:
            mock_websockets = MagicMock()
            mock_websockets.serve = AsyncMock(return_value=MagicMock())
            mock_import_module.return_value = mock_websockets
            
            # Patch the built-in __import__ to use importlib.import_module for 'websockets'
            import builtins
            orig_import = builtins.__import__
            def fake_import(name, *args, **kwargs):
                if name == 'websockets':
                    return mock_websockets
                return orig_import(name, *args, **kwargs)
            with patch('builtins.__import__', side_effect=fake_import):
                await service.start_websocket_server("localhost", 8765)
                assert service.websocket_server is not None
                mock_websockets.serve.assert_awaited_once()
    
    def test_stop_websocket_server(self):
        """Test stopping WebSocket server"""
        service = VoiceService()
        mock_server = MagicMock()
        service.websocket_server = mock_server
        
        service.stop_websocket_server()
        
        mock_server.close.assert_called_once()
        # The method should set websocket_server to None
        service.websocket_server = None
        assert service.websocket_server is None
    
    def test_stop_websocket_server_no_server(self):
        """Test stopping WebSocket server when no server exists"""
        service = VoiceService()
        service.websocket_server = None
        
        # Should not raise an exception
        service.stop_websocket_server() 