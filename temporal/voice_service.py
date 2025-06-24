"""
Voice Service

Main service for coordinating voice processing, speech recognition,
temporal context, and language understanding.

Note: Voice processing has been removed from this version.
Voice features are not available.
"""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from .temporal_context import TemporalContext
from .language_processor import LanguageProcessor

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self, context_window_hours: int = 24):
        self.temporal_context = TemporalContext(context_window_hours)
        self.language_processor = LanguageProcessor()
        self.websocket_server = None
        self.audio_callbacks = []
        self.is_initialized = False
        
        logger.info("VoiceService initialized (voice processing not available)")
        
    async def initialize(self) -> bool:
        """Initialize the voice service"""
        logger.info("VoiceService initialized in text-only mode")
        return False
            
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Convert audio to text"""
        logger.warning("Voice transcription is not available")
        return None

    async def process_voice_command(self, text: str, websocket=None) -> Dict[str, Any]:
        """Process voice command through temporal context"""
        if not text:
            return {"error": "No text to process"}
            
        # Add to temporal context
        self.temporal_context.add_interaction(text)
        
        # Get current context
        context = self.temporal_context.get_current_context()
        
        # Process through language processor
        processed_text = self.language_processor.process_with_context(text, context)
        intent = self.language_processor.extract_intent(text)
        
        # Prepare response
        response = {
            "original_text": text,
            "processed_text": processed_text,
            "intent": intent,
            "temporal_context": context,
            "timestamp": context["current_time"].isoformat()
        }
        
        logger.info(f"Processed voice command: {intent}")
        
        # Send to cortex agent for processing (placeholder)
        # This will be integrated with the existing agent system
        agent_response = await self.send_to_cortex(processed_text, intent)
        response["agent_response"] = agent_response
        
        # Send response back to client if websocket provided
        if websocket:
            await self.send_response_to_client(websocket, response)
            
        return response
        
    async def send_to_cortex(self, text: str, intent: Dict[str, Any]) -> str:
        """Send processed text to cortex agent for processing"""
        # Placeholder - this will be integrated with existing agent system
        logger.info(f"Sending to cortex: '{text}' with intent: {intent}")
        
        # For now, return a simple response
        if intent.get("urgency") == "high":
            return f"Urgent request processed: {text}"
        elif "weather" in intent.get("categories", []):
            return f"Weather query detected: {text}"
        elif "time" in intent.get("categories", []):
            return f"Time query detected: {text}"
        else:
            return f"Voice command processed: {text}"
        
    async def send_response_to_client(self, websocket, response: Dict[str, Any]) -> None:
        """Send response back to client via WebSocket"""
        try:
            import json
            await websocket.send(json.dumps(response))
        except Exception as e:
            logger.error(f"Failed to send response to client: {e}")
        
    def get_temporal_summary(self) -> Dict[str, Any]:
        """Get a summary of temporal context"""
        return self.temporal_context.get_interaction_summary()
        
    def add_audio_callback(self, callback: Callable) -> None:
        """Add callback for audio processing events"""
        self.audio_callbacks.append(callback)
        
    async def handle_websocket_connection(self, websocket, path: str) -> None:
        """Handle WebSocket connection for real-time audio"""
        logger.info(f"New WebSocket connection from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                if isinstance(message, bytes) and message.startswith(b'audio:'):
                    # Voice processing is not available
                    error_response = {
                        "error": "Voice processing is not available",
                        "message": "Voice features have been removed from this version",
                        "status": "disabled"
                    }
                    await self.send_response_to_client(websocket, error_response)
                elif isinstance(message, str):
                    # Handle text messages
                    try:
                        import json
                        data = json.loads(message)
                        if data.get("type") == "text":
                            await self.process_voice_command(data["text"], websocket)
                    except json.JSONDecodeError:
                        # Treat as plain text
                        await self.process_voice_command(message, websocket)
                        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            logger.info(f"WebSocket connection closed: {websocket.remote_address}")
        
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765) -> None:
        """Start WebSocket server for real-time audio"""
        try:
            import websockets
            self.websocket_server = await websockets.serve(
                self.handle_websocket_connection, host, port
            )
            logger.info(f"Voice WebSocket server started on {host}:{port}")
        except ImportError:
            logger.error("WebSockets not available. Install with: pip install websockets")
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
        
    def stop_websocket_server(self) -> None:
        """Stop WebSocket server"""
        if self.websocket_server:
            self.websocket_server.close()
            self.websocket_server = None
            logger.info("Voice WebSocket server stopped") 