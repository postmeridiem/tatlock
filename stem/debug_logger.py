"""
stem/debug_logger.py

Debug logging system for LLM prompts and responses when DEBUG_MODE is enabled.
Creates detailed logs of all LLM interactions for debugging timing, tool usage, and responses.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid

from config import DEBUG_MODE

class DebugLogger:
    """
    Debug logger for LLM interactions that creates session-based log files
    when DEBUG_MODE is enabled.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.session_start = datetime.now()
        self.log_file_path = None
        self.step_counter = 0
        self.iteration_counter = 0

        if DEBUG_MODE:
            self._initialize_log_file()

    def _initialize_log_file(self):
        """Initialize the debug log file for this session."""
        try:
            # Create logs/conversations directory if it doesn't exist
            log_dir = Path("logs/conversations")
            log_dir.mkdir(parents=True, exist_ok=True)

            # Create filename with session ID and timestamp
            timestamp = self.session_start.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{self.session_id}_{timestamp}.log"
            self.log_file_path = log_dir / filename

            # Write session header
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write(f"TATLOCK DEBUG SESSION LOG\n")
                f.write(f"Session ID: {self.session_id}\n")
                f.write(f"Started: {self.session_start.isoformat()}\n")
                f.write("="*80 + "\n\n")

        except Exception as e:
            # Log error and set to None so other methods will skip logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize debug log file: {e}")
            self.log_file_path = None

    def log_phase_start(self, phase_name: str, description: str = ""):
        """Log the start of a processing phase."""
        if not DEBUG_MODE or not self.log_file_path:
            return

        self.step_counter += 1
        self.iteration_counter = 0
        timestamp = datetime.now().isoformat()

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"PHASE {self.step_counter}: {phase_name.upper()}\n")
            if description:
                f.write(f"Description: {description}\n")
            f.write(f"Started: {timestamp}\n")
            f.write(f"{'='*60}\n")

    def log_llm_request(self, model: str, messages: List[Dict], tools: Optional[List] = None,
                       iteration_type: str = "main"):
        """Log an LLM request with full prompt details."""
        if not DEBUG_MODE or not self.log_file_path:
            return

        self.iteration_counter += 1
        timestamp = datetime.now().isoformat()

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'-'*40}\n")
            f.write(f"LLM REQUEST #{self.iteration_counter} ({iteration_type})\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Step: {self.step_counter}, Iteration: {self.iteration_counter}\n")
            f.write(f"{'-'*40}\n")

            # Log messages (prompts)
            f.write("MESSAGES:\n")
            for i, msg in enumerate(messages):
                f.write(f"\n[{i+1}] Role: {msg.get('role', 'unknown')}\n")
                content = msg.get('content', '')
                if len(content) > 1000:
                    f.write(f"Content (truncated): {content[:1000]}...\n")
                else:
                    f.write(f"Content: {content}\n")

                # Log tool calls if present
                if 'tool_calls' in msg:
                    f.write(f"Tool Calls: {json.dumps(msg['tool_calls'], indent=2)}\n")

            # Log available tools
            if tools:
                f.write(f"\nAVAILABLE TOOLS ({len(tools)}):\n")
                for tool in tools:
                    tool_name = tool.get('function', {}).get('name', 'unknown')
                    f.write(f"  - {tool_name}\n")
            else:
                f.write("\nAVAILABLE TOOLS: None\n")

    def log_llm_response(self, response: Dict[str, Any], duration_seconds: float,
                        tool_calls_made: Optional[List] = None):
        """Log an LLM response with timing and tool usage details."""
        if not DEBUG_MODE or not self.log_file_path:
            return

        timestamp = datetime.now().isoformat()

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\nLLM RESPONSE #{self.iteration_counter}\n")
            f.write(f"Completed: {timestamp}\n")
            f.write(f"Duration: {duration_seconds:.3f}s\n")
            f.write(f"{'-'*40}\n")

            # Log response content
            if isinstance(response, dict):
                content = response.get('content', '')
                if content:
                    if len(content) > 500:
                        f.write(f"Response (truncated): {content[:500]}...\n")
                    else:
                        f.write(f"Response: {content}\n")

                # Log tool calls in response
                if 'tool_calls' in response:
                    f.write(f"Tool Calls Requested: {len(response['tool_calls'])}\n")
                    for i, tool_call in enumerate(response['tool_calls']):
                        f.write(f"  [{i+1}] {tool_call.get('function', {}).get('name', 'unknown')}\n")
            else:
                f.write(f"Response: {str(response)}\n")

            # Log actual tool executions
            if tool_calls_made:
                f.write(f"\nTOOL EXECUTIONS ({len(tool_calls_made)}):\n")
                for tool_exec in tool_calls_made:
                    f.write(f"  - {tool_exec.get('name', 'unknown')}: {tool_exec.get('status', 'unknown')}\n")

    def log_tool_execution(self, tool_name: str, args: Dict, result: Dict, duration_seconds: float):
        """Log individual tool execution details."""
        if not DEBUG_MODE or not self.log_file_path:
            return

        timestamp = datetime.now().isoformat()

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\nTOOL EXECUTION: {tool_name}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Duration: {duration_seconds:.3f}s\n")
            f.write(f"Arguments: {json.dumps(args, indent=2)}\n")

            status = result.get('status', 'unknown')
            f.write(f"Status: {status}\n")

            if status == 'error':
                f.write(f"Error: {result.get('message', 'No error message')}\n")
            else:
                data = result.get('data', result)
                if isinstance(data, (dict, list)) and len(str(data)) > 200:
                    f.write(f"Result (truncated): {str(data)[:200]}...\n")
                else:
                    f.write(f"Result: {json.dumps(data, indent=2)}\n")

    def log_phase_summary(self, phase_name: str, duration_seconds: float,
                         iterations: int, success: bool, notes: str = ""):
        """Log a summary of a completed phase."""
        if not DEBUG_MODE or not self.log_file_path:
            return

        timestamp = datetime.now().isoformat()

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\nPHASE {self.step_counter} SUMMARY\n")
            f.write(f"Name: {phase_name}\n")
            f.write(f"Completed: {timestamp}\n")
            f.write(f"Duration: {duration_seconds:.3f}s\n")
            f.write(f"Iterations: {iterations}\n")
            f.write(f"Success: {success}\n")
            if notes:
                f.write(f"Notes: {notes}\n")
            f.write(f"{'='*60}\n")

    def log_session_end(self, total_duration_seconds: float):
        """Log session completion summary."""
        if not DEBUG_MODE or not self.log_file_path:
            return

        timestamp = datetime.now().isoformat()

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"SESSION COMPLETED\n")
            f.write(f"Ended: {timestamp}\n")
            f.write(f"Total Duration: {total_duration_seconds:.3f}s\n")
            f.write(f"Total Steps: {self.step_counter}\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"{'='*80}\n")

# Global debug logger instance - will be created per request/session
_debug_logger: Optional[DebugLogger] = None

def get_debug_logger(session_id: Optional[str] = None) -> DebugLogger:
    """Get or create a debug logger for the current session."""
    global _debug_logger
    if _debug_logger is None or session_id:
        _debug_logger = DebugLogger(session_id)
    return _debug_logger

def reset_debug_logger():
    """Reset the global debug logger (for new sessions)."""
    global _debug_logger
    _debug_logger = None