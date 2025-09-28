"""
cortex/response_parser.py

Model-agnostic response parsing and formatting system for Tatlock.
Handles different LLM tool calling formats and ensures consistent, polished responses.
"""

import json
import re
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ToolCall:
    """Standardized tool call representation."""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class ParsedResponse:
    """Standardized parsed response representation."""
    content: str
    tool_calls: List[ToolCall]
    needs_tool_execution: bool
    raw_response: str

class ResponseParser:
    """
    Model-agnostic response parser that can handle various LLM output formats
    and standardize them into a consistent internal representation.
    """

    def __init__(self):
        self.parsers = [
            self._parse_ollama_native,
            self._parse_openai_format,
            self._parse_text_based_tools,
            self._parse_bracket_format,
            self._parse_xml_format,
            self._parse_json_format
        ]

    def parse_response(self, response: Dict[str, Any]) -> ParsedResponse:
        """
        Parse an LLM response using multiple fallback strategies.

        Args:
            response: Raw response from LLM

        Returns:
            ParsedResponse: Standardized parsed response
        """
        message = response.get('message', {})
        content = message.get('content', '')

        logger.debug(f"Parsing response with content length: {len(content)}")

        # Try each parser in order
        for parser in self.parsers:
            try:
                parsed = parser(message, content)
                if parsed:
                    logger.debug(f"Successfully parsed with {parser.__name__}")
                    return parsed
            except Exception as e:
                logger.debug(f"Parser {parser.__name__} failed: {e}")
                continue

        # Fallback: treat as plain text response
        logger.debug("All parsers failed, treating as plain text")
        return ParsedResponse(
            content=content,
            tool_calls=[],
            needs_tool_execution=False,
            raw_response=str(response)
        )

    def _parse_ollama_native(self, message: Dict, content: str) -> Optional[ParsedResponse]:
        """Parse Ollama's native tool calling format."""
        if not message.get('tool_calls'):
            return None

        tool_calls = []
        for tool_call in message['tool_calls']:
            tool_calls.append(ToolCall(
                id=tool_call.get('id', f"call_{uuid.uuid4().hex[:8]}"),
                name=tool_call.get('function', {}).get('name', ''),
                arguments=tool_call.get('function', {}).get('arguments', {})
            ))

        return ParsedResponse(
            content=content,
            tool_calls=tool_calls,
            needs_tool_execution=len(tool_calls) > 0,
            raw_response=str(message)
        )

    def _parse_openai_format(self, message: Dict, content: str) -> Optional[ParsedResponse]:
        """Parse OpenAI-style tool calling format."""
        # Check for tool_calls array format
        if 'tool_calls' in content or 'function_call' in content:
            # Look for embedded JSON tool calls
            tool_pattern = r'"tool_calls":\s*(\[.*?\])'
            match = re.search(tool_pattern, content, re.DOTALL)
            if match:
                try:
                    tool_calls_json = json.loads(match.group(1))
                    tool_calls = []
                    for tc in tool_calls_json:
                        tool_calls.append(ToolCall(
                            id=tc.get('id', f"call_{uuid.uuid4().hex[:8]}"),
                            name=tc.get('function', {}).get('name', ''),
                            arguments=tc.get('function', {}).get('arguments', {})
                        ))

                    # Remove tool call JSON from content
                    clean_content = re.sub(tool_pattern, '', content, flags=re.DOTALL).strip()

                    return ParsedResponse(
                        content=clean_content,
                        tool_calls=tool_calls,
                        needs_tool_execution=len(tool_calls) > 0,
                        raw_response=str(message)
                    )
                except json.JSONDecodeError:
                    pass

        return None

    def _parse_text_based_tools(self, message: Dict, content: str) -> Optional[ParsedResponse]:
        """Parse text-based tool calling formats like your weather example."""
        # Pattern 1: [{"name": "tool_name", "arguments": {...}}]
        pattern1 = r'\[{"name":\s*"([^"]+)",\s*"arguments":\s*({[^}]*})\s*}\]'
        match1 = re.search(pattern1, content)

        if match1:
            tool_name = match1.group(1)
            try:
                arguments = json.loads(match1.group(2))
                tool_calls = [ToolCall(
                    id=f"call_{uuid.uuid4().hex[:8]}",
                    name=tool_name,
                    arguments=arguments
                )]

                # Remove the tool call from content
                clean_content = re.sub(pattern1, '', content).strip()
                # Remove tool call markers
                clean_content = re.sub(r'<\|.*?\|>', '', clean_content).strip()

                return ParsedResponse(
                    content=clean_content,
                    tool_calls=tool_calls,
                    needs_tool_execution=True,
                    raw_response=str(message)
                )
            except json.JSONDecodeError:
                pass

        # Pattern 2: Multiple tools in array format
        pattern2 = r'\[({"name":\s*"[^"]+",\s*"arguments":\s*{[^}]*}\s*}(?:,\s*{"name":\s*"[^"]+",\s*"arguments":\s*{[^}]*}\s*})*)\]'
        match2 = re.search(pattern2, content, re.DOTALL)

        if match2:
            try:
                tools_json = f"[{match2.group(1)}]"
                tools_data = json.loads(tools_json)
                tool_calls = []
                for tool in tools_data:
                    tool_calls.append(ToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        name=tool.get('name', ''),
                        arguments=tool.get('arguments', {})
                    ))

                clean_content = re.sub(pattern2, '', content, flags=re.DOTALL).strip()
                clean_content = re.sub(r'<\|.*?\|>', '', clean_content).strip()

                return ParsedResponse(
                    content=clean_content,
                    tool_calls=tool_calls,
                    needs_tool_execution=len(tool_calls) > 0,
                    raw_response=str(message)
                )
            except json.JSONDecodeError:
                pass

        return None

    def _parse_bracket_format(self, message: Dict, content: str) -> Optional[ParsedResponse]:
        """Parse bracket-based tool calling format."""
        # Look for [TOOL:tool_name:arguments] format
        pattern = r'\[TOOL:([^:]+):({.*?})\]'
        matches = re.findall(pattern, content, re.DOTALL)

        if matches:
            tool_calls = []
            for tool_name, args_str in matches:
                try:
                    arguments = json.loads(args_str)
                    tool_calls.append(ToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        name=tool_name.strip(),
                        arguments=arguments
                    ))
                except json.JSONDecodeError:
                    continue

            if tool_calls:
                clean_content = re.sub(pattern, '', content, flags=re.DOTALL).strip()
                return ParsedResponse(
                    content=clean_content,
                    tool_calls=tool_calls,
                    needs_tool_execution=True,
                    raw_response=str(message)
                )

        return None

    def _parse_xml_format(self, message: Dict, content: str) -> Optional[ParsedResponse]:
        """Parse XML-based tool calling format."""
        # Look for <tool_call>...</tool_call> format
        pattern = r'<tool_call>\s*({.*?})\s*</tool_call>'
        matches = re.findall(pattern, content, re.DOTALL)

        if matches:
            tool_calls = []
            for match in matches:
                try:
                    tool_data = json.loads(match.strip())
                    tool_calls.append(ToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        name=tool_data.get('name', ''),
                        arguments=tool_data.get('parameters', tool_data.get('arguments', {}))
                    ))
                except json.JSONDecodeError:
                    continue

            if tool_calls:
                clean_content = re.sub(pattern, '', content, flags=re.DOTALL).strip()
                return ParsedResponse(
                    content=clean_content,
                    tool_calls=tool_calls,
                    needs_tool_execution=True,
                    raw_response=str(message)
                )

        return None

    def _parse_json_format(self, message: Dict, content: str) -> Optional[ParsedResponse]:
        """Parse pure JSON tool calling format."""
        # Look for JSON objects that might be tool calls
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, content, re.DOTALL)

        if matches:
            tool_calls = []
            for match in matches:
                try:
                    data = json.loads(match)
                    if 'name' in data or 'tool_name' in data:
                        tool_calls.append(ToolCall(
                            id=f"call_{uuid.uuid4().hex[:8]}",
                            name=data.get('name', data.get('tool_name', '')),
                            arguments=data.get('arguments', data.get('parameters', {}))
                        ))
                except json.JSONDecodeError:
                    continue

            if tool_calls:
                clean_content = re.sub(json_pattern, '', content, flags=re.DOTALL).strip()
                return ParsedResponse(
                    content=clean_content,
                    tool_calls=tool_calls,
                    needs_tool_execution=True,
                    raw_response=str(message)
                )

        return None

class ResponseFormatter:
    """
    Formats responses to ensure consistent, polished output that matches
    Tatlock's British butler personality regardless of the underlying model.
    Uses LLM-based polishing for all response types.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name
        self.butler_phrases = [
            "Very good, sir.",
            "Certainly, sir.",
            "At your service, sir.",
            "Right away, sir.",
            "Indeed, sir.",
            "As you wish, sir."
        ]

    def format_response(self, content: str, tool_results: List[Dict] = None) -> str:
        """
        Format a response to ensure it matches Tatlock's personality and style.
        Uses LLM-based polishing to convert any verbose/computerized output into proper butler speech.

        Args:
            content: Raw content from LLM
            tool_results: Results from tool execution

        Returns:
            str: Formatted response in Tatlock's voice
        """
        if not content and tool_results:
            # Generate response from tool results
            content = self._generate_response_from_tools(tool_results)

        if not content:
            return "I apologize, sir, but I seem to have encountered a brief malfunction. Might I suggest rephrasing your request?"

        # Clean up any remaining tool artifacts first
        content = self._clean_tool_artifacts(content)

        # Check if response needs polishing (verbose, computerized, or non-butler-like)
        if self._needs_polishing(content):
            content = self._polish_with_llm(content)

        # Final cleanup and butler voice check
        content = self._ensure_butler_voice(content)
        content = self._clean_formatting(content)

        return content

    def _needs_polishing(self, content: str) -> bool:
        """
        Determine if a response needs LLM-based polishing.

        Args:
            content: The response content to check

        Returns:
            bool: True if content needs polishing
        """
        # Check for signs that indicate need for polishing
        polishing_indicators = [
            len(content) > 200,  # Very long responses
            'weather forecast indicates' in content.lower(),  # Weather responses
            'precipitation' in content.lower(),  # Technical weather terms
            'temperature' in content.lower() and len(content) > 100,  # Long weather responses
            content.count('.') > 3,  # Many sentences
            'approximately' in content.lower(),  # Technical language
            'expected' in content.lower() and 'temperature' in content.lower(),  # Weather patterns
            not content.lower().endswith(', sir.') and not content.lower().endswith(', sir!'),  # Missing butler ending
            '{' in content or '}' in content,  # JSON artifacts
            'data' in content.lower() and 'retrieved' in content.lower()  # Technical language
        ]

        return any(polishing_indicators)

    def _polish_with_llm(self, content: str) -> str:
        """
        Use the LLM to polish a response into proper Tatlock butler speech.

        Args:
            content: The response content to polish

        Returns:
            str: Polished response in butler voice
        """
        try:
            import ollama
            from config import OLLAMA_MODEL

            polishing_prompt = f"""You are Tatlock, a British butler. Convert this response into a concise, natural butler response.

IMPORTANT RULES:
- Keep it under 50 words
- Be helpful but concise
- Always end with ", sir."
- Use natural, conversational language
- Remove technical jargon
- Don't repeat information
- Sound like a proper British butler

Original response: "{content}"

Polished response:"""

            response = ollama.chat(
                model=OLLAMA_MODEL or self.model_name,
                messages=[
                    {'role': 'user', 'content': polishing_prompt}
                ],
                tools=[]  # No tools for polishing
            )

            polished = response['message'].get('content', '').strip()

            # Ensure it's not empty and has butler ending
            if polished and len(polished) > 5:
                if not polished.lower().endswith(', sir.') and not polished.lower().endswith(', sir!'):
                    if polished.endswith('.'):
                        polished = polished[:-1] + ', sir.'
                    else:
                        polished += ', sir.'
                return polished
            else:
                # Fallback to original if polishing failed
                return content

        except Exception as e:
            logger.error(f"Error polishing response with LLM: {e}")
            return content

    def _generate_response_from_tools(self, tool_results: List[Dict]) -> str:
        """Generate a natural response from tool execution results."""
        if not tool_results:
            return ""

        # Handle weather results specifically
        for result in tool_results:
            if 'forecast_summary' in str(result):
                return self._format_weather_response(result)
            elif 'memories' in str(result):
                return self._format_memory_response(result)
            elif 'search_results' in str(result):
                return self._format_search_response(result)

        # Generic tool result formatting
        return "I have retrieved the requested information for you, sir."

    def _format_weather_response(self, result: Dict) -> str:
        """Format weather tool results into butler speech."""
        try:
            if isinstance(result, str):
                result = json.loads(result)

            forecast = result.get('forecast_summary', '')
            precipitation = result.get('precipitation_probability', {})
            wind = result.get('wind_speed', '')

            response = f"The weather forecast indicates {forecast.lower()}"

            if precipitation:
                morning_rain = precipitation.get('morning', '0%')
                afternoon_rain = precipitation.get('afternoon', '0%')
                if afternoon_rain != '0%':
                    response += f" with a {afternoon_rain} chance of precipitation in the afternoon"

            if wind:
                response += f" {wind.lower()}"

            response += ", sir."

            # Capitalize first letter properly
            response = response[0].upper() + response[1:]

            return response

        except Exception as e:
            logger.error(f"Error formatting weather response: {e}")
            return "I'm afraid there was an issue retrieving the weather information, sir."

    def _format_memory_response(self, result: Dict) -> str:
        """Format memory tool results into butler speech."""
        return "I have searched through our previous conversations, sir."

    def _format_search_response(self, result: Dict) -> str:
        """Format search tool results into butler speech."""
        return "I have found the relevant information you requested, sir."

    def _clean_tool_artifacts(self, content: str) -> str:
        """Remove any remaining tool call artifacts from content."""
        # Remove tool call markers
        content = re.sub(r'<\|.*?\|>', '', content)
        content = re.sub(r'\[{"name":.*?\]\s*', '', content, flags=re.DOTALL)
        content = re.sub(r'```tool_calls.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'<tool_call>.*?</tool_call>', '', content, flags=re.DOTALL)

        # Remove JSON artifacts
        content = re.sub(r'{"[^"]*":\s*"[^"]*"[^}]*}', '', content)

        return content.strip()

    def _ensure_butler_voice(self, content: str) -> str:
        """Ensure the response matches Tatlock's British butler personality."""
        if not content:
            return content

        # Don't modify if already has butler elements
        butler_indicators = ['sir', 'indeed', 'certainly', 'very good', 'at your service']
        if any(indicator in content.lower() for indicator in butler_indicators):
            return content

        # Add butler ending if missing
        if not content.endswith(('.', '!', '?')):
            content += '.'

        if not any(content.lower().endswith(phrase) for phrase in [', sir.', ', sir!', ', sir?']):
            # Replace final punctuation with butler ending
            if content.endswith('.'):
                content = content[:-1] + ', sir.'
            elif content.endswith('!'):
                content = content[:-1] + ', sir!'
            elif content.endswith('?'):
                content = content[:-1] + ', sir?'

        return content

    def _clean_formatting(self, content: str) -> str:
        """Clean up formatting issues."""
        # Remove multiple spaces
        content = re.sub(r'\s+', ' ', content)

        # Remove leading/trailing whitespace
        content = content.strip()

        # Ensure proper sentence capitalization
        if content and content[0].islower():
            content = content[0].upper() + content[1:]

        return content

# Global instances
response_parser = ResponseParser()

def get_response_formatter():
    """Get response formatter with current model."""
    try:
        from config import OLLAMA_MODEL
        return ResponseFormatter(model_name=OLLAMA_MODEL)
    except ImportError:
        return ResponseFormatter()

response_formatter = get_response_formatter()