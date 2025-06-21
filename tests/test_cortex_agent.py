"""
Tests for cortex.agent
"""
import pytest
import cortex.agent as agent

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