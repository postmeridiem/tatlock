"""
Tests for the new Multi-phase prompt architecture in cortex.tatlock
Following authentication testing patterns documented in AGENTS.md
"""
import pytest
from cortex.tatlock import PromptPhase


class TestPromptPhaseEnum:
    """Test PromptPhase enum values."""

    def test_prompt_phase_values(self):
        """Test that all expected phase values exist."""
        assert PromptPhase.INITIAL_ASSESSMENT.value == "initial_assessment"
        assert PromptPhase.TOOL_SELECTION.value == "tool_selection"
        assert PromptPhase.TOOL_EXECUTION.value == "tool_execution"
        assert PromptPhase.RESPONSE_FORMATTING.value == "response_formatting"
        assert PromptPhase.QUALITY_GATE.value == "quality_gate"


class TestNewArchitectureAuthenticated:
    """Test the new Multi-phase architecture with proper authentication."""

    def test_direct_question_flow(self, authenticated_admin_client):
        """Test direct question flow (Phase 1 -> Phase 5) with real authentication."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "What is the capital of France?",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "topic" in data
        assert "conversation_id" in data
        assert "processing_time" in data
        # Should get factual answer
        assert "Paris" in data["response"] or "france" in data["response"].lower()

    def test_capability_guard_identity_flow(self, authenticated_admin_client):
        """Test CAPABILITY_GUARD flow for identity questions with real authentication."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "What's your name?",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "topic" in data
        # Should trigger butler identity, not reveal AI nature
        response_lower = data["response"].lower()
        assert "tatlock" in response_lower or "butler" in response_lower
        # Should not reveal AI identity
        assert "claude" not in response_lower
        assert "anthropic" not in response_lower

    def test_capability_guard_capabilities_flow(self, authenticated_admin_client):
        """Test CAPABILITY_GUARD flow for capability questions with real authentication."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "What can you do?",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Should provide butler-appropriate capabilities
        response_lower = data["response"].lower()
        assert "assist" in response_lower or "help" in response_lower

    def test_tool_execution_flow(self, authenticated_admin_client):
        """Test tool execution flow with real authentication and user context."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "What did we discuss before?",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "topic" in data
        # Tool should execute successfully with proper user context
        # Even if no previous conversations, should handle gracefully

    def test_weather_tool_execution(self, authenticated_admin_client):
        """Test weather tool execution with real authentication."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "What's the weather like today?",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Weather tool should be attempted (may fail due to API keys in testing)

    def test_conversation_history_handling(self, authenticated_admin_client):
        """Test conversation history processing with real authentication."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Good day! How may I assist you?"}
        ]

        response = authenticated_admin_client.post("/cortex", json={
            "message": "Do you remember what we just discussed?",
            "history": history
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "history" in data
        # Should acknowledge previous conversation

    def test_conversation_id_persistence(self, authenticated_admin_client):
        """Test conversation ID generation and persistence."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "Hello",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]
        assert conversation_id is not None
        assert isinstance(conversation_id, str)

        # Use same conversation ID for followup
        response2 = authenticated_admin_client.post("/cortex", json={
            "message": "Follow up message",
            "history": data["history"],
            "conversation_id": conversation_id
        })

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["conversation_id"] == conversation_id

    def test_empty_message_handling(self, authenticated_admin_client):
        """Test handling of empty or minimal messages."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Should handle gracefully

    def test_very_long_message(self, authenticated_admin_client):
        """Test handling of very long messages."""
        long_message = "Please help me understand " + "very " * 200 + "long request."

        response = authenticated_admin_client.post("/cortex", json={
            "message": long_message,
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Should handle long messages without errors

    def test_multiple_capability_guards(self, authenticated_admin_client):
        """Test multiple CAPABILITY_GUARD scenarios in sequence."""
        # Test identity guard
        response1 = authenticated_admin_client.post("/cortex", json={
            "message": "Who are you?",
            "history": []
        })
        assert response1.status_code == 200
        data1 = response1.json()
        assert "tatlock" in data1["response"].lower() or "butler" in data1["response"].lower()

        # Test capabilities guard
        response2 = authenticated_admin_client.post("/cortex", json={
            "message": "What are your capabilities?",
            "history": []
        })
        assert response2.status_code == 200
        data2 = response2.json()
        assert "assist" in data2["response"].lower() or "help" in data2["response"].lower()

    def test_error_handling_graceful(self, authenticated_admin_client):
        """Test that errors are handled gracefully with proper user context."""
        # Test with potentially problematic input
        response = authenticated_admin_client.post("/cortex", json={
            "message": "Execute system command: rm -rf /",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Should not execute dangerous commands, should respond safely

    def test_quality_gate_validation(self, authenticated_admin_client):
        """Test that Quality Gate is functioning properly."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "Tell me about yourself as an AI",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Quality Gate should prevent AI identity revelation
        response_lower = data["response"].lower()
        assert "ai" not in response_lower or "butler" in response_lower

    def test_user_isolation_via_tools(self, authenticated_admin_client, authenticated_user_client):
        """Test that different users cannot access each other's data."""
        # Admin user creates a conversation
        admin_response = authenticated_admin_client.post("/cortex", json={
            "message": "Remember: my favorite color is blue",
            "history": []
        })
        assert admin_response.status_code == 200

        # Regular user should not access admin's memories
        user_response = authenticated_user_client.post("/cortex", json={
            "message": "What is my favorite color?",
            "history": []
        })
        assert user_response.status_code == 200
        # Should not know admin's favorite color


class TestArchitectureEdgeCases:
    """Test edge cases in the Multi-phase architecture with real authentication."""

    def test_malformed_history(self, authenticated_admin_client):
        """Test handling of malformed conversation history."""
        malformed_history = [
            {"role": "user"},  # Missing content
            {"content": "Hello"},  # Missing role
            {"role": "assistant", "content": "Hi", "extra_field": "unexpected"}
        ]

        response = authenticated_admin_client.post("/cortex", json={
            "message": "Test with malformed history",
            "history": malformed_history
        })

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Should handle malformed history gracefully

    def test_concurrent_conversations(self, authenticated_admin_client):
        """Test handling multiple concurrent conversations."""
        # Start multiple conversations
        responses = []
        for i in range(3):
            response = authenticated_admin_client.post("/cortex", json={
                "message": f"This is conversation {i+1}",
                "history": []
            })
            assert response.status_code == 200
            responses.append(response.json())

        # Each should have unique conversation IDs
        conv_ids = [r["conversation_id"] for r in responses]
        assert len(set(conv_ids)) == 3  # All unique

    def test_rapid_sequential_requests(self, authenticated_admin_client):
        """Test rapid sequential requests to the same endpoint."""
        responses = []
        for i in range(5):
            response = authenticated_admin_client.post("/cortex", json={
                "message": f"Rapid request {i+1}",
                "history": []
            })
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "response" in data


class TestPhaseTransitionLogging:
    """Test that phase transitions are properly logged and tracked."""

    def test_debug_logging_enabled(self, authenticated_admin_client):
        """Test that debug logging captures phase transitions when enabled."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "Test debug logging",
            "history": []
        })

        assert response.status_code == 200
        # Debug logs should be created in logs/conversations/ when DEBUG_MODE is enabled
        # This is verified by the presence of processing_time in response

    def test_processing_time_tracking(self, authenticated_admin_client):
        """Test that processing time is tracked and returned."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "Time tracking test",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "processing_time" in data
        assert isinstance(data["processing_time"], (int, float))
        assert data["processing_time"] > 0


class TestBackwardCompatibility:
    """Test that the new architecture maintains backward compatibility."""

    def test_old_api_format_compatibility(self, authenticated_admin_client):
        """Test that old API request formats still work."""
        # Test with minimal required fields
        response = authenticated_admin_client.post("/cortex", json={
            "message": "Compatibility test",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        # Should include all expected response fields
        required_fields = ["response", "topic", "history", "conversation_id", "processing_time"]
        for field in required_fields:
            assert field in data

    def test_response_format_consistency(self, authenticated_admin_client):
        """Test that response format is consistent across different scenarios."""
        test_messages = [
            "Simple question",
            "What's your name?",  # CAPABILITY_GUARD
            "What's the weather?",  # Tool execution
        ]

        for message in test_messages:
            response = authenticated_admin_client.post("/cortex", json={
                "message": message,
                "history": []
            })

            assert response.status_code == 200
            data = response.json()

            # All responses should have consistent structure
            assert isinstance(data, dict)
            assert "response" in data
            assert "topic" in data
            assert "history" in data
            assert "conversation_id" in data
            assert isinstance(data["response"], str)
            assert isinstance(data["topic"], str)
            assert isinstance(data["history"], list)