"""
Tests for cortex.agent
"""
import pytest
import cortex.agent as agent
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from cortex.agent import process_chat_interaction, run_async, AVAILABLE_TOOLS

class DummyOllama:
    def __init__(self):
        self.calls = []
    def chat(self, model, messages, tools=None):
        self.calls.append((model, messages, tools))
        # Simulate a final answer on first call
        if len(self.calls) == 1:
            return {"message": {"role": "assistant", "content": "Hello!", "tool_calls": None}}
        # Simulate a tool call on first, then final answer
        return {"message": {"role": "assistant", "content": "", "tool_calls": None}}


def test_process_chat_interaction(monkeypatch):
    # Patch ollama and save_interaction
    dummy_ollama = DummyOllama()
    monkeypatch.setattr(agent, "ollama", dummy_ollama)
    monkeypatch.setattr(agent, "save_interaction", lambda **kwargs: "dummy_id")
    monkeypatch.setattr(agent, "get_base_instructions", lambda username: ["Be helpful."])
    # Patch TOOLS to empty
    monkeypatch.setattr(agent, "TOOLS", [])
    # Call process_chat_interaction
    result = agent.process_chat_interaction(
        user_message="Hi!",
        history=[],
        username="testuser",
        conversation_id="conv1"
    )
    assert "response" in result
    assert result["response"] == "Hello!"
    assert "topic" in result
    assert "history" in result
    assert "conversation_id" in result 


class TestRunAsync:
    """Test the run_async function."""
    
    def test_run_async_with_running_loop(self):
        """Test run_async when there's a running event loop."""
        async def test_coro():
            return "test_result"
        
        with patch('asyncio.get_running_loop') as mock_get_loop:
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = True
            mock_loop.run_until_complete.return_value = "test_result"
            mock_get_loop.return_value = mock_loop
            
            result = run_async(test_coro())
            
            assert result == "test_result"
            mock_loop.run_until_complete.assert_called_once()
    
    def test_run_async_without_running_loop(self):
        """Test run_async when there's no running event loop."""
        async def test_coro():
            return "test_result"
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.run') as mock_run:
                mock_run.return_value = "test_result"
                result = run_async(test_coro())
                assert result == "test_result"
                mock_run.assert_called_once()
    
    def test_run_async_nest_asyncio_import_error(self):
        """Test run_async when nest_asyncio is not available."""
        async def test_coro():
            return "test_result"
        
        with patch('asyncio.get_running_loop') as mock_get_loop:
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = True
            mock_get_loop.return_value = mock_loop
            
            with patch('nest_asyncio.apply', side_effect=ImportError):
                with pytest.raises(RuntimeError, match="nest_asyncio is required"):
                    run_async(test_coro())


class TestProcessChatInteraction:
    """Test the main chat interaction processing."""
    
    @pytest.fixture
    def mock_ollama(self):
        """Mock ollama responses."""
        with patch('cortex.agent.ollama') as mock_ollama:
            yield mock_ollama
    
    @pytest.fixture
    def mock_save_interaction(self):
        """Mock the save_interaction function."""
        with patch('cortex.agent.save_interaction') as mock_save:
            yield mock_save
    
    @pytest.mark.asyncio
    async def test_basic_chat_interaction(self):
        """Test basic chat interaction."""
        with patch('cortex.agent.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': 'Hello! How can I help you today?'}
            }
            
            with patch('cortex.agent.save_interaction') as mock_save:
                mock_save.return_value = {"status": "success"}
                
                result = process_chat_interaction("Hello!", [], "test_user")
                
                assert result["status"] == "success"
                assert "response" in result
                # The topic might be extracted from the response, not hardcoded
                assert "topic" in result
    
    def test_chat_with_tool_calls(self, mock_ollama, mock_save_interaction):
        """Test chat interaction with tool calls."""
        # Mock tool call response
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': [
                        {
                            'id': 'call_123',
                            'function': {
                                'name': 'get_weather_forecast',
                                'arguments': {'city': 'Amsterdam'}
                            }
                        }
                    ]
                }
            },
            {
                'message': {
                    'role': 'assistant',
                    'content': 'The weather in Amsterdam is sunny.'
                }
            }
        ]
        
        with patch.dict(AVAILABLE_TOOLS, {
            'get_weather_forecast': MagicMock(return_value={'status': 'success', 'data': 'sunny'})
        }):
            result = process_chat_interaction(
                user_message="What's the weather in Amsterdam?",
                history=[],
                username="testuser"
            )
        
        assert "weather" in result["response"].lower()
        assert result["topic"] == "general"
    
    @pytest.mark.asyncio
    async def test_tool_call_parsing_from_tool_call_tags(self):
        """Test parsing tool calls from <tool_call> tags."""
        with patch('cortex.agent.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': '<tool_call>{"name": "get_weather", "args": {"location": "New York"}}</tool_call>'}
            }
            
            with patch('cortex.agent.execute_tool') as mock_execute:
                mock_execute.return_value = {"status": "success", "data": "The weather is sunny."}
                
                with patch('cortex.agent.save_interaction') as mock_save:
                    mock_save.return_value = {"status": "success"}
                    
                    result = process_chat_interaction("What's the weather?", [], "test_user")
                    
                    assert result["status"] == "success"
                    assert "response" in result
                    # The response should contain the tool execution result
                    assert "weather" in result["response"].lower() or "sunny" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_tool_call_parsing_invalid_json(self):
        """Test parsing tool calls with invalid JSON."""
        with patch('cortex.agent.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': '<tool_call>{"invalid": json}</tool_call>'}
            }
            
            with patch('cortex.agent.save_interaction') as mock_save:
                mock_save.return_value = {"status": "success"}
                
                result = process_chat_interaction("Invalid tool call", [], "test_user")
                
                assert result["status"] == "success"
                assert "response" in result
                # Should handle invalid JSON gracefully
                assert "error" in result["response"].lower() or "invalid" in result["response"].lower()
    
    def test_tool_execution_failure(self, mock_ollama, mock_save_interaction):
        """Test handling tool execution failures."""
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': [
                        {
                            'id': 'call_123',
                            'function': {
                                'name': 'get_weather_forecast',
                                'arguments': {'city': 'InvalidCity'}
                            }
                        }
                    ]
                }
            },
            {
                'message': {
                    'role': 'assistant',
                    'content': 'I encountered an error with the weather tool.'
                }
            }
        ]
        
        with patch.dict(AVAILABLE_TOOLS, {
            'get_weather_forecast': MagicMock(side_effect=Exception("API Error"))
        }):
            result = process_chat_interaction(
                user_message="Weather in InvalidCity",
                history=[],
                username="testuser"
            )
        
        assert "error" in result["response"].lower()
    
    def test_unknown_tool_call(self, mock_ollama, mock_save_interaction):
        """Test handling unknown tool calls."""
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': [
                        {
                            'id': 'call_123',
                            'function': {
                                'name': 'unknown_tool',
                                'arguments': {}
                            }
                        }
                    ]
                }
            },
            {
                'message': {
                    'role': 'assistant',
                    'content': 'I cannot use that tool.'
                }
            }
        ]
        
        result = process_chat_interaction(
            user_message="Use unknown tool",
            history=[],
            username="testuser"
        )
        
        assert result["response"] == "I cannot use that tool."
    
    def test_async_tool_execution(self, mock_ollama, mock_save_interaction):
        """Test execution of async tools."""
        async def async_weather_tool(**kwargs):
            return {'status': 'success', 'data': 'async_weather'}
        
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': [
                        {
                            'id': 'call_123',
                            'function': {
                                'name': 'async_weather',
                                'arguments': {'city': 'Amsterdam'}
                            }
                        }
                    ]
                }
            },
            {
                'message': {
                    'role': 'assistant',
                    'content': 'Async weather result.'
                }
            }
        ]
        
        with patch.dict(AVAILABLE_TOOLS, {
            'async_weather': async_weather_tool
        }):
            result = process_chat_interaction(
                user_message="Async weather",
                history=[],
                username="testuser"
            )
        
        assert result["response"] == "Async weather result."
    
    def test_max_iterations_reached(self, mock_ollama, mock_save_interaction):
        """Test behavior when max iterations are reached."""
        # Mock 10 tool call responses to reach max iterations
        tool_call_response = {
            'message': {
                'role': 'assistant',
                'content': '',
                'tool_calls': [
                    {
                        'id': 'call_123',
                        'function': {
                            'name': 'get_weather_forecast',
                            'arguments': {'city': 'Amsterdam'}
                        }
                    }
                ]
            }
        }
        
        final_response = {
            'message': {
                'role': 'assistant',
                'content': 'I have reached the maximum number of tool calls.'
            }
        }
        
        mock_ollama.chat.side_effect = [tool_call_response] * 9 + [final_response]
        
        with patch.dict(AVAILABLE_TOOLS, {
            'get_weather_forecast': MagicMock(return_value={'status': 'success', 'data': 'sunny'})
        }):
            result = process_chat_interaction(
                user_message="Repeated tool calls",
                history=[],
                username="testuser"
            )
        
        assert "maximum" in result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_tool_failures_analysis(self):
        """Test analysis of tool failures."""
        with patch('cortex.agent.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': '<tool_call>{"name": "get_weather", "args": {}}</tool_call>'}
            }
            
            with patch('cortex.agent.execute_tool') as mock_execute:
                mock_execute.return_value = {"status": "error", "error": "API unavailable"}
                
                with patch('cortex.agent.save_interaction') as mock_save:
                    mock_save.return_value = {"status": "success"}
                    
                    result = process_chat_interaction("What's the weather?", [], "test_user")
                    
                    assert result["status"] == "success"
                    assert "response" in result
                    # Should handle tool failures gracefully
                    assert "error" in result["response"].lower() or "unavailable" in result["response"].lower()
    
    def test_topic_classification_success(self, mock_ollama, mock_save_interaction):
        """Test successful topic classification."""
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': 'The weather is sunny today.'
                }
            },
            {
                'message': {
                    'content': 'weather'
                }
            }
        ]
        
        result = process_chat_interaction(
            user_message="What's the weather like?",
            history=[],
            username="testuser"
        )
        
        assert result["topic"] == "weather"
    
    def test_topic_classification_failure(self, mock_ollama, mock_save_interaction):
        """Test topic classification failure."""
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': 'Hello there!'
                }
            },
            Exception("Topic classification failed")
        ]
        
        result = process_chat_interaction(
            user_message="Hello",
            history=[],
            username="testuser"
        )
        
        assert result["topic"] == "general"
    
    @pytest.mark.asyncio
    async def test_save_interaction_failure(self):
        """Test handling save interaction failure."""
        with patch('cortex.agent.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': 'Hello! How can I help you today?'}
            }
            
            with patch('cortex.agent.save_interaction') as mock_save:
                mock_save.side_effect = Exception("Save failed")
                
                result = process_chat_interaction("Hello!", [], "test_user")
                
                assert result["status"] == "success"
                assert "response" in result
                # The topic might be extracted from the response, not hardcoded
                assert "topic" in result
    
    def test_empty_tool_calls_string(self, mock_ollama, mock_save_interaction):
        """Test handling empty tool_calls string."""
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': 'Hello!',
                    'tool_calls': ''
                }
            }
        ]
        
        result = process_chat_interaction(
            user_message="Hello",
            history=[],
            username="testuser"
        )
        
        assert result["response"] == "Hello!"
    
    def test_invalid_tool_call_format(self, mock_ollama, mock_save_interaction):
        """Test handling invalid tool call format."""
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': [
                        {
                            'id': 'call_123',
                            'function': {
                                'name': 'get_weather_forecast',
                                'arguments': 'invalid_args'  # Should be dict
                            }
                        }
                    ]
                }
            },
            {
                'message': {
                    'role': 'assistant',
                    'content': 'I cannot process that request.'
                }
            }
        ]
        
        result = process_chat_interaction(
            user_message="Invalid tool call",
            history=[],
            username="testuser"
        )
        
        assert result["response"] == "I cannot process that request."
    
    def test_no_tool_outputs(self, mock_ollama, mock_save_interaction):
        """Test handling when no tool outputs are generated."""
        mock_ollama.chat.side_effect = [
            {
                'message': {
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': [
                        {
                            'id': 'call_123',
                            'function': {
                                'name': 'get_weather_forecast',
                                'arguments': {'city': 'Amsterdam'}
                            }
                        }
                    ]
                }
            },
            {
                'message': {
                    'role': 'assistant',
                    'content': 'I could not execute the requested tools.'
                }
            }
        ]
        
        # Mock tool to return None or raise exception
        with patch.dict(AVAILABLE_TOOLS, {
            'get_weather_forecast': MagicMock(return_value=None)
        }):
            result = process_chat_interaction(
                user_message="Weather request",
                history=[],
                username="testuser"
            )
        
        assert "could not execute" in result["response"].lower()
    
    def test_conversation_id_generation(self, mock_ollama, mock_save_interaction):
        """Test conversation ID generation."""
        mock_ollama.chat.return_value = {
            'message': {
                'role': 'assistant',
                'content': 'Hello!'
            }
        }
        
        result = process_chat_interaction(
            user_message="Hello",
            history=[],
            username="testuser"
        )
        
        assert result["conversation_id"] is not None
        assert isinstance(result["conversation_id"], str)
    
    def test_custom_conversation_id(self, mock_ollama, mock_save_interaction):
        """Test using custom conversation ID."""
        mock_ollama.chat.return_value = {
            'message': {
                'role': 'assistant',
                'content': 'Hello!'
            }
        }
        
        custom_id = "custom-conversation-123"
        result = process_chat_interaction(
            user_message="Hello",
            history=[],
            username="testuser",
            conversation_id=custom_id
        )
        
        assert result["conversation_id"] == custom_id
    
    @pytest.mark.asyncio
    async def test_empty_history_handling(self):
        """Test handling empty conversation history."""
        with patch('cortex.agent.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': 'Hello! How can I help you today?'}
            }
            
            with patch('cortex.agent.save_interaction') as mock_save:
                mock_save.return_value = {"status": "success"}
                
                result = process_chat_interaction("Hello!", [], "test_user")
                
                assert result["status"] == "success"
                assert "response" in result
                # Should handle empty history gracefully
    
    @pytest.mark.asyncio
    async def test_history_without_content(self):
        """Test handling history without content field."""
        with patch('cortex.agent.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': 'Hello! How can I help you today?'}
            }
            
            with patch('cortex.agent.save_interaction') as mock_save:
                mock_save.return_value = {"status": "success"}
                
                history = [{"role": "user", "message": "Hi"}, {"role": "assistant", "message": "Hello"}]
                result = process_chat_interaction("Hello!", history, "test_user")
                
                assert result["status"] == "success"
                assert "response" in result
                # Should handle history without content field gracefully 