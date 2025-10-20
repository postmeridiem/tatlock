"""
cortex/tatlock.py

Core agent logic for Tatlock implementing Multi-phase prompt architecture.
Handles chat interaction, tool dispatch, and butler personality.
"""

import ollama
import json
import re
import logging
import time
from datetime import date, datetime
import uuid
import asyncio
import inspect
from typing import List, Literal
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any
import re

# Import from our new, organized modules
from config import OLLAMA_MODEL
from hippocampus.database import get_base_instructions
from hippocampus.reference_frame import get_tool_catalog_for_selection, get_selected_tools
from stem.tools import AVAILABLE_TOOLS, execute_tool
from hippocampus.remember import save_interaction
from hippocampus.conversation_compact import trigger_compact_if_needed, get_conversation_context
from hippocampus.user_database import ensure_user_database
from cortex.response_parser import response_parser, response_formatter
from stem.debug_logger import get_debug_logger, reset_debug_logger

# Set up logging for this module
logger = logging.getLogger(__name__)

# Module reload marker
print("MODULE RELOAD: cortex.tatlock module loaded with debug functionality")

# --- Tool Dispatcher ---
# AVAILABLE_TOOLS now provided by dynamic tool system in stem/tools.py

# === NEW Multi-PHASE ARCHITECTURE CLASSES ===

class PromptPhase(Enum):
    """Enum representing the different phases of prompt processing"""
    INITIAL_ASSESSMENT = "initial_assessment"
    TOOL_SELECTION = "tool_selection"
    TOOL_EXECUTION = "tool_execution"
    RESPONSE_FORMATTING = "response_formatting"
    QUALITY_GATE = "quality_gate"

class CapabilityGuardReason(Enum):
    """Reasons why CAPABILITY_GUARD might be triggered"""
    IDENTITY = "IDENTITY"
    CAPABILITIES = "CAPABILITIES"
    TEMPORAL = "TEMPORAL"
    SECURITY = "SECURITY"
    MIXED = "MIXED"

class AssessmentResult(BaseModel):
    """Result from Phase 1 initial assessment"""
    assessment_type: Literal["DIRECT", "TOOLS_NEEDED", "CAPABILITY_GUARD"] = Field(
        description="Type of assessment result"
    )
    guard_reason: Optional[CapabilityGuardReason] = Field(
        default=None,
        description="Reason for capability guard trigger if applicable"
    )
    tools_needed: List[str] = Field(
        default=[],
        description="List of specific tool keys needed"
    )
    direct_response: Optional[str] = Field(
        default=None,
        description="Direct answer if assessment is DIRECT"
    )
    tool_query: Optional[str] = Field(
        default=None,
        description="Description of what tools are needed if TOOLS_NEEDED"
    )

class ToolSelectionResult(BaseModel):
    """Result from Phase 2 tool selection"""
    selected_tools: List[str] = Field(
        description="List of selected tool names"
    )
    usage_instructions: str = Field(
        description="Instructions for how to use the selected tools"
    )

class QualityResult(BaseModel):
    """Result from Phase Multi quality gate"""
    approved: bool = Field(
        description="Whether the response is approved for delivery"
    )
    needs_fallback: bool = Field(
        default=False,
        description="Whether a fallback response is needed"
    )
    fallback_type: Optional[str] = Field(
        default=None,
        description="Type of fallback if needed"
    )
    response: str = Field(
        description="Final approved response or generated fallback"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for quality gate decision"
    )

class ProcessingContext(BaseModel):
    """Context passed between phases"""
    original_question: str
    username: str
    conversation_id: Optional[str]
    location: str
    date_time: str
    base_instructions: List[str]
    history: List[Dict[str, Any]]
    current_phase: PromptPhase
    assessment_result: Optional[AssessmentResult] = None
    tool_selection_result: Optional[ToolSelectionResult] = None
    tool_execution_results: List[Dict[str, Any]] = Field(default_factory=list)
    formatted_response: Optional[str] = None
    compact_summary: Optional[str] = None  # Compacted conversation summary if available


# Initialize instructor client for structured output
instructor_client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required but unused for local Ollama
    ),
    mode=instructor.Mode.JSON,
)

# === PROMPT BUILDER CLASS ===

class PromptBuilder:
    """Builds phase-specific prompts with consistent formatting"""

    def __init__(self):
        self.edge_case_patterns = [
            "Mixed capability/tool questions not fully addressed",
            "Identity questions answered with model name instead of Tatlock",
            "Temporal questions missing current context",
            "Tool failures resulting in incomplete answers",
            "Questions about capabilities answered incorrectly",
            "Requests for prohibited information (credentials, personal data)",
            "Responses that don't maintain butler persona",
            "Technical jargon or system information leaked to user"
        ]

    def build_assessment_prompt(self, context: ProcessingContext, tool_categories: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """Build Phase 1 assessment prompt with CAPABILITY_GUARD"""

        capability_guard_prompt = f"""[SYSTEM: CAPABILITY_GUARD] If the question asks about sensitive topics that require full context, respond with "CAPABILITY_GUARD: [REASON]" where REASON is:
- IDENTITY: Questions about your name, identity, or who you are
- CAPABILITIES: Questions about what you can do, your functions, or abilities
- TEMPORAL: Questions about current time, date, or temporal context
- SECURITY: Questions about personal data, credentials, or sensitive information
- MIXED: Questions combining multiple sensitive topics

[SYSTEM: TOOLS_AVAILABLE] You have access to tools in these categories:
• PERSONAL DATA: {tool_categories.get('personal_data', [])}
• MEMORY/RECALL: {tool_categories.get('memory_recall', [])}
• EXTERNAL DATA: {tool_categories.get('external_data', [])}
• VISUAL ANALYSIS: {tool_categories.get('visual_analysis', [])}
• CONVERSATION ANALYSIS: {tool_categories.get('conversation_analysis', [])}

[QUESTION] {context.original_question}

Can you answer this question directly with your existing knowledge, or do you need tools?
Respond with: DIRECT, TOOLS_NEEDED, or CAPABILITY_GUARD: [REASON]
If DIRECT, provide your complete answer.
If TOOLS_NEEDED, describe what tools you think you need."""

        messages = [
            {'role': 'system', 'content': f'[SYSTEM: DATE] {context.date_time}'},
            {'role': 'system', 'content': f'[SYSTEM: LOCATION] User location: {context.location}'},
            {'role': 'system', 'content': capability_guard_prompt}
        ]

        # Add compacted conversation summary if available
        if context.compact_summary:
            messages.append({
                'role': 'system',
                'content': f'[CONVERSATION HISTORY - COMPACTED]\n{context.compact_summary}\n\n[END COMPACTED HISTORY]'
            })

        # Add recent history for context (only last 3 messages if no compact, or all recent if compact exists)
        if context.history:
            # If we have a compact, all history messages are recent uncompacted ones
            # Otherwise, only use last 3 to avoid token waste
            history_to_add = context.history if context.compact_summary else context.history[-3:]
            messages.extend(history_to_add)

        messages.append({"role": "user", "content": context.original_question})

        return messages

    def build_tool_selection_prompt(self, context: ProcessingContext, available_tools: List[Dict]) -> List[Dict[str, str]]:
        """Build Phase 2 tool selection prompt"""

        tool_descriptions = []
        for tool in available_tools:
            tool_descriptions.append(f"• {tool['name']}: {tool['description']}")
            if 'parameters' in tool:
                tool_descriptions.append(f"  - Parameters: {', '.join(tool['parameters'])}")
            tool_descriptions.append(f"  - Usage: {tool.get('usage', 'No usage description')}")

        tools_text = '\n'.join(tool_descriptions)

        selection_prompt = f"""[SYSTEM: DATE] {context.date_time}
[SYSTEM: LOCATION] User location: {context.location}

[QUESTION] {context.original_question}

[BACKGROUND: TOOL_QUERY] {context.assessment_result.tool_query}

[SYSTEM: AVAILABLE_TOOLS] Here are the specific tools available:
{tools_text}

Select only the tools needed and provide usage instructions:"""

        messages = [
            {'role': 'system', 'content': selection_prompt}
        ]

        return messages

    def build_formatting_prompt(self, context: ProcessingContext, is_capability_guard: bool = False) -> List[Dict[str, str]]:
        """Build Phase 4 response formatting prompt"""

        if is_capability_guard:
            # Use full rise_and_shine context for capability guard scenarios
            messages = [
                {'role': 'system', 'content': f'[SYSTEM: DATE] {context.date_time}'},
                {'role': 'system', 'content': f'[SYSTEM: LOCATION] User location: {context.location}'}
            ]

            # Add all base instructions (rise_and_shine)
            for instruction in context.base_instructions:
                messages.append({'role': 'system', 'content': f'[SYSTEM: RISE_AND_SHINE] {instruction}'})

            messages.extend([
                {'role': 'system', 'content': '[SYSTEM: FORMATTING_REQUIREMENTS] Answer the original question directly using your identity from the rise_and_shine instructions above.'},
                {'role': 'system', 'content': f'[QUESTION] {context.original_question}'},
                {'role': 'system', 'content': f'[BACKGROUND: CAPABILITY_GUARD_TRIGGERED] True'},
                {'role': 'system', 'content': f'[BACKGROUND: GUARD_REASON] {context.assessment_result.guard_reason.value if context.assessment_result else "UNKNOWN"}'},
                {'role': 'system', 'content': '[BACKGROUND: INSTRUCTION] Answer the original question using your rise_and_shine context'},
                {'role': 'user', 'content': 'Provide your response:'}
            ])
        else:
            # Standard butler formatting
            background_sections = []

            if context.assessment_result and context.assessment_result.tool_query:
                background_sections.append(f'[BACKGROUND: TOOL_SELECTION_PHASE] {context.assessment_result.tool_query}')

            if context.tool_execution_results:
                background_sections.append('[BACKGROUND: TOOL_EXECUTION]')
                for result in context.tool_execution_results:
                    background_sections.append(f"Called {result.get('tool_name', 'unknown')} with results: {result.get('status', 'unknown')}")

            if context.tool_execution_results:
                background_sections.append('[BACKGROUND: TOOL_RESULTS]')
                results_summary = []
                for result in context.tool_execution_results:
                    if result.get('status') == 'success':
                        results_summary.append(f"{result.get('tool_name', 'tool')}: {str(result.get('data', 'No data'))[:100]}")
                    else:
                        results_summary.append(f"{result.get('tool_name', 'tool')}: {result.get('message', 'Failed')}")
                background_sections.extend(results_summary)

            background_text = '\n'.join(background_sections) if background_sections else 'Direct answer path, no tools used'

            butler_prompt = f"""[SYSTEM: BUTLER_ROLE] You are Tatlock, a British butler. Format a response according to these requirements:
- Keep responses concise (under 50 words) unless specified otherwise
- Use proper British butler speech
- Always end with ", sir."
- Be helpful but formal
- Remove any technical jargon
- Synthesize information naturally

[QUESTION] {context.original_question}

{background_text}

Provide the properly formatted butler response:"""

            messages = [
                {'role': 'system', 'content': butler_prompt}
            ]

        return messages

    def build_quality_gate_prompt(self, context: ProcessingContext, proposed_response: str) -> List[Dict[str, str]]:
        """Build Phase Multi quality gate prompt"""

        edge_case_list = '\n'.join([f"- {pattern}" for pattern in self.edge_case_patterns])

        context_summary = []
        if context.assessment_result:
            if context.assessment_result.assessment_type == "CAPABILITY_GUARD":
                context_summary.append(f"CAPABILITY_GUARD triggered: {context.assessment_result.guard_reason.value}")
            elif context.assessment_result.assessment_type == "TOOLS_NEEDED":
                context_summary.append(f"Tool execution: {len(context.tool_execution_results)} tools used")
            else:
                context_summary.append("Direct answer path, no tools used, no guards triggered")

        context_text = ', '.join(context_summary) if context_summary else 'Unknown processing path'

        quality_prompt = f"""[SYSTEM: QUALITY_GATE] Review this response against known issues:

EDGE CASE PATTERNS:
{edge_case_list}

EDGE CASE CHECKS:
- Does this answer the original question completely?
- Is the butler persona maintained (formal, ends with "sir")?
- Are there any inappropriate elements or system leaks?
- Does this match any known problematic patterns?

[ORIGINAL_QUESTION] {context.original_question}
[PROPOSED_ANSWER] {proposed_response}
[CONTEXT] {context_text}

Quality assessment: APPROVED or FALLBACK: [TYPE with reason]
If FALLBACK needed, provide the corrected response."""

        messages = [
            {'role': 'system', 'content': quality_prompt}
        ]

        return messages


# === QUALITY GATE CLASS ===

class QualityGate:
    """Validates response quality and handles edge cases before delivery"""

    def __init__(self, prompt_builder: PromptBuilder):
        self.prompt_builder = prompt_builder
        self.fallback_responses = {
            "INCOMPLETE": "I apologize, sir, but I believe I may have missed part of your question. Could you please rephrase it so I can assist you properly?",
            "TOOL_FAILURE": "I apologize, sir, but I'm currently unable to retrieve that information due to a technical issue. Please try again in a moment.",
            "IDENTITY_LEAK": "My name is Tatlock, sir. How may I assist you today?",
            "CAPABILITY_ERROR": "I can help with various tasks including answering questions, searching information, and recalling our conversation history, sir.",
            "DOUBLE_PROCESSING": None,  # Will use original if detected
            "SAFETY_VIOLATION": "I'm not able to help with that request, sir.",
            "UNKNOWN": "I apologize, sir, but I encountered an issue processing your request. Please try again."
        }

    def evaluate_response(self, context: ProcessingContext, proposed_response: str) -> QualityResult:
        """Evaluate if proposed answer adequately addresses the original question"""

        # Step 1: Quick safety checks
        safety_result = self._check_safety(context.original_question, proposed_response)
        if safety_result.needs_fallback:
            return safety_result

        # Step 2: Completeness validation
        completeness_result = self._check_completeness(context, proposed_response)
        if completeness_result.needs_fallback:
            return completeness_result

        # Step 3: Edge case detection
        edge_case_result = self._check_edge_cases(context, proposed_response)
        if edge_case_result.needs_fallback:
            return edge_case_result

        # Step 4: Use LLM for final quality assessment
        llm_result = self._llm_quality_check(context, proposed_response)
        return llm_result

    def _check_safety(self, original_question: str, proposed_response: str) -> QualityResult:
        """Quick safety validation for obvious violations"""

        # Check for obvious security violations
        security_triggers = ["password", "credit card", "ssn", "social security", "bank account"]
        question_lower = original_question.lower()

        if any(trigger in question_lower for trigger in security_triggers):
            return QualityResult(
                approved=False,
                needs_fallback=True,
                fallback_type="SAFETY_VIOLATION",
                response=self.fallback_responses["SAFETY_VIOLATION"],
                reasoning="Question requests sensitive information"
            )

        # Check for system information leaks
        system_leaks = ["ollama", "llama", "gemma", "model", "AI assistant", "language model"]
        response_lower = proposed_response.lower()

        if any(leak in response_lower for leak in system_leaks):
            return QualityResult(
                approved=False,
                needs_fallback=True,
                fallback_type="IDENTITY_LEAK",
                response=self.fallback_responses["IDENTITY_LEAK"],
                reasoning="Response contains system information leak"
            )

        return QualityResult(approved=True, response=proposed_response, reasoning="Safety checks passed")

    def _check_completeness(self, context: ProcessingContext, proposed_response: str) -> QualityResult:
        """Validate response completeness"""

        # Check for tool failure scenarios
        if context.tool_execution_results:
            failed_tools = [r for r in context.tool_execution_results if r.get('status') != 'success']
            if failed_tools and "successfully" in proposed_response.lower():
                return QualityResult(
                    approved=False,
                    needs_fallback=True,
                    fallback_type="TOOL_FAILURE",
                    response=self.fallback_responses["TOOL_FAILURE"],
                    reasoning="Response claims success but tools failed"
                )

        # Check for empty or generic responses
        generic_responses = ["processing completed", "i apologize", "i cannot", "i don't know"]
        if len(proposed_response.strip()) < 10 or any(generic in proposed_response.lower() for generic in generic_responses):
            if context.assessment_result and context.assessment_result.assessment_type == "DIRECT":
                return QualityResult(
                    approved=False,
                    needs_fallback=True,
                    fallback_type="INCOMPLETE",
                    response=self.fallback_responses["INCOMPLETE"],
                    reasoning="Response is too generic for direct question"
                )

        return QualityResult(approved=True, response=proposed_response, reasoning="Completeness checks passed")

    def _check_edge_cases(self, context: ProcessingContext, proposed_response: str) -> QualityResult:
        """Check for known edge case patterns"""

        # Edge case: Mixed questions not fully addressed
        if context.assessment_result and context.assessment_result.guard_reason == CapabilityGuardReason.MIXED:
            # Check if response addresses all parts of a mixed question
            question_parts = self._count_question_parts(context.original_question)
            if question_parts > 1 and len(proposed_response.split('.')) < question_parts:
                return QualityResult(
                    approved=False,
                    needs_fallback=True,
                    fallback_type="INCOMPLETE",
                    response=self.fallback_responses["INCOMPLETE"],
                    reasoning="Mixed question not fully addressed"
                )

        # Edge case: Identity questions without proper context
        identity_keywords = ["name", "who are you", "what are you", "identity"]
        if any(keyword in context.original_question.lower() for keyword in identity_keywords):
            if "tatlock" not in proposed_response.lower():
                return QualityResult(
                    approved=False,
                    needs_fallback=True,
                    fallback_type="IDENTITY_LEAK",
                    response=self.fallback_responses["IDENTITY_LEAK"],
                    reasoning="Identity question didn't mention Tatlock"
                )

        # Edge case: Capability questions
        capability_keywords = ["what can you do", "capabilities", "abilities", "help with"]
        if any(keyword in context.original_question.lower() for keyword in capability_keywords):
            if len(proposed_response) < 30:  # Too short for capability explanation
                return QualityResult(
                    approved=False,
                    needs_fallback=True,
                    fallback_type="CAPABILITY_ERROR",
                    response=self.fallback_responses["CAPABILITY_ERROR"],
                    reasoning="Capability question needs more detailed response"
                )

        return QualityResult(approved=True, response=proposed_response, reasoning="Edge case checks passed")

    def _count_question_parts(self, question: str) -> int:
        """Count distinct parts in a question (rough heuristic)"""
        and_count = question.lower().count(' and ')
        question_marks = question.count('?')
        return max(1, and_count + 1, question_marks)

    def _llm_quality_check(self, context: ProcessingContext, proposed_response: str) -> QualityResult:
        """Use LLM for final quality assessment"""

        try:
            # Build quality gate prompt
            messages = self.prompt_builder.build_quality_gate_prompt(context, proposed_response)

            # Get LLM evaluation
            quality_response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=[])
            quality_content = quality_response['message']['content']

            # Parse quality response
            if "APPROVED" in quality_content.upper():
                return QualityResult(
                    approved=True,
                    response=proposed_response,
                    reasoning="LLM quality check approved"
                )
            elif "FALLBACK:" in quality_content.upper():
                # Extract fallback type and reason
                fallback_lines = [line.strip() for line in quality_content.split('\n') if 'FALLBACK:' in line.upper()]
                if fallback_lines:
                    fallback_info = fallback_lines[0].split('FALLBACK:')[1].strip()
                    fallback_type = fallback_info.split(' ')[0] if fallback_info else "UNKNOWN"

                    # Try to extract corrected response if provided
                    corrected_response = None
                    lines = quality_content.split('\n')
                    for i, line in enumerate(lines):
                        if 'corrected response' in line.lower() and i + 1 < len(lines):
                            corrected_response = lines[i + 1].strip()
                            break

                    return QualityResult(
                        approved=False,
                        needs_fallback=True,
                        fallback_type=fallback_type,
                        response=corrected_response or self.fallback_responses.get(fallback_type, self.fallback_responses["UNKNOWN"]),
                        reasoning=f"LLM detected issue: {fallback_info}"
                    )

            # Fallback if parsing fails
            return QualityResult(
                approved=True,
                response=proposed_response,
                reasoning="LLM quality check completed (parse unclear)"
            )

        except Exception as e:
            logger.warning(f"Quality gate LLM check failed: {e}")
            # Default to approval if quality check fails
            return QualityResult(
                approved=True,
                response=proposed_response,
                reasoning=f"Quality check failed, defaulting to approval: {str(e)}"
            )

    def generate_fallback_response(self, context: ProcessingContext, fallback_type: str, custom_message: str = None) -> str:
        """Generate appropriate fallback response"""

        if custom_message:
            return custom_message

        return self.fallback_responses.get(fallback_type, self.fallback_responses["UNKNOWN"])


# === CAPABILITY GUARD RESPONSE PARSER ===

class CapabilityGuardParser:
    """Parses LLM responses from Phase 1 assessment for CAPABILITY_GUARD triggers"""

    def parse_assessment_response(self, response_content: str) -> AssessmentResult:
        """Parse LLM response from Phase 1 assessment"""

        response_upper = response_content.upper()

        # Check for CAPABILITY_GUARD trigger (LLM detected sensitive topic)
        if "CAPABILITY_GUARD:" in response_upper:
            guard_line = [line for line in response_content.split('\n') if 'CAPABILITY_GUARD:' in line.upper()]
            if guard_line:
                guard_reason_text = guard_line[0].split('CAPABILITY_GUARD:')[1].strip()
                try:
                    guard_reason = CapabilityGuardReason(guard_reason_text)
                except ValueError:
                    # Invalid reason, default to MIXED
                    guard_reason = CapabilityGuardReason.MIXED

                return AssessmentResult(
                    assessment_type="CAPABILITY_GUARD",
                    guard_reason=guard_reason
                )

        # Check for TOOLS_NEEDED
        elif "TOOLS_NEEDED" in response_upper:
            # Extract tool query from response
            lines = response_content.split('\n')
            tool_query = ""
            for line in lines:
                if line.strip() and not any(keyword in line.upper() for keyword in ['ASSESSMENT:', 'TOOLS:', 'RESPONSE:']):
                    tool_query = line.strip()
                    break

            # Extract tools list if present
            tools_lines = [line for line in lines if 'TOOLS:' in line.upper()]
            tools_needed = []
            if tools_lines:
                tools_text = tools_lines[0].split('TOOLS:')[1].strip()
                if tools_text and tools_text.upper() != "NONE":
                    tools_needed = [tool.strip() for tool in tools_text.split(',')]

            return AssessmentResult(
                assessment_type="TOOLS_NEEDED",
                tools_needed=tools_needed,
                tool_query=tool_query or "Tools needed for this request"
            )

        # Default to DIRECT response
        else:
            return AssessmentResult(
                assessment_type="DIRECT",
                direct_response=response_content.strip()
            )


# === NEW Multi-PHASE PROCESSOR ===

class TatlockProcessor:
    """Main processor implementing the Multi-phase architecture"""

    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.quality_gate = QualityGate(self.prompt_builder)
        self.guard_parser = CapabilityGuardParser()

    def process_question(self, user_message: str, history: List[Dict], username: str = "admin",
                        conversation_id: str = None) -> Dict:
        """Process question through Multi-phase architecture"""

        start_time = time.time()
        logger.info(f"[TIERED LLM ARCHITECTURE] Processing: '{user_message[:50]}...'")

        # Initialize debug logger
        debug_logger = get_debug_logger(conversation_id)
        debug_logger.log_phase_start("NEW Multi-Phase Processing", f"User: {username}, Message: {user_message[:100]}")

        # Build processing context
        context = self._build_context(user_message, history, username, conversation_id)

        try:
            phase1_t0 = time.time()
            # Phase 1: Initial Assessment
            assessment_result = self._phase_1_assessment(context, debug_logger)
            logger.info(f"Phase 1 duration: {round(time.time()-phase1_t0,2)}s")
            context.assessment_result = assessment_result
            context.current_phase = PromptPhase.INITIAL_ASSESSMENT

            # Route based on assessment
            # Force guard if the question clearly matches identity/temporal even if Phase 1 missed it
            if assessment_result.assessment_type == "DIRECT":
                forced_guard_reason = self._detect_guard_reason(context.original_question)
                if forced_guard_reason is not None:
                    assessment_result.assessment_type = "CAPABILITY_GUARD"
                    assessment_result.guard_reason = forced_guard_reason

            if assessment_result.assessment_type == "CAPABILITY_GUARD":
                # Fast path: for CAPABILITY_GUARD, keep processing minimal
                context.current_phase = PromptPhase.RESPONSE_FORMATTING
                phase4_t0 = time.time()
                formatted_response = self._phase_4_formatting(context, debug_logger, is_capability_guard=True)
                logger.info(f"Phase 4 (guard) duration: {round(time.time()-phase4_t0,2)}s")

                # Skip tool selection/execution entirely for guard path
                context.formatted_response = formatted_response
                context.current_phase = PromptPhase.QUALITY_GATE
                phase5_t0 = time.time()
                quality_result = self._phase_5_quality_gate(context, debug_logger)
                logger.info(f"Quality Gate duration: {round(time.time()-phase5_t0,2)}s")

                final_response = quality_result.response
                processing_time = round(time.time() - start_time, 1)

                # Save interaction asynchronously, but do not block
                try:
                    topic_str = self._determine_topic(assessment_result)
                    save_interaction(
                        user_prompt=user_message,
                        llm_reply=final_response,
                        full_llm_history=[],
                        topic=topic_str,
                        username=username,
                        conversation_id=conversation_id
                    )
                    db_path = ensure_user_database(username)
                    import threading
                    threading.Thread(target=trigger_compact_if_needed, args=(username, conversation_id, db_path), daemon=True).start()
                except Exception as e:
                    logger.error(f"Error saving interaction (guard path): {e}")

                return {
                    "response": final_response,
                    "topic": topic_str,
                    "history": context.history + [{"role": "assistant", "content": final_response}],
                    "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                    "processing_time": processing_time
                }

            elif assessment_result.assessment_type == "DIRECT":
                # Direct to Phase 4 for butler formatting, then fast return
                context.current_phase = PromptPhase.RESPONSE_FORMATTING
                phase4_t0 = time.time()
                formatted_response = self._phase_4_formatting(context, debug_logger, is_capability_guard=False)
                logger.info(f"Phase 4 duration: {round(time.time()-phase4_t0,2)}s")

                context.formatted_response = formatted_response
                context.current_phase = PromptPhase.QUALITY_GATE
                phase5_t0 = time.time()
                quality_result = self._phase_5_quality_gate(context, debug_logger)
                logger.info(f"Quality Gate duration: {round(time.time()-phase5_t0,2)}s")

                final_response = quality_result.response
                processing_time = round(time.time() - start_time, 1)

                # Save asynchronously
                try:
                    topic_str = self._determine_topic(assessment_result)
                    save_interaction(
                        user_prompt=user_message,
                        llm_reply=final_response,
                        full_llm_history=[],
                        topic=topic_str,
                        username=username,
                        conversation_id=conversation_id
                    )
                    db_path = ensure_user_database(username)
                    import threading
                    threading.Thread(target=trigger_compact_if_needed, args=(username, conversation_id, db_path), daemon=True).start()
                except Exception as e:
                    logger.error(f"Error saving interaction (direct path): {e}")

                return {
                    "response": final_response,
                    "topic": topic_str,
                    "history": context.history + [{"role": "assistant", "content": final_response}],
                    "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                    "processing_time": processing_time
                }

            elif assessment_result.assessment_type == "TOOLS_NEEDED":
                # Phase 2: Tool Selection
                context.current_phase = PromptPhase.TOOL_SELECTION
                phase2_t0 = time.time()
                tool_selection_result = self._phase_2_tool_selection(context, debug_logger)
                logger.info(f"Phase 2 duration: {round(time.time()-phase2_t0,2)}s")
                context.tool_selection_result = tool_selection_result

                # Phase 3: Tool Execution
                context.current_phase = PromptPhase.TOOL_EXECUTION
                phase3_t0 = time.time()
                tool_results = self._phase_3_tool_execution(context, debug_logger)
                logger.info(f"Phase 3 duration: {round(time.time()-phase3_t0,2)}s")
                context.tool_execution_results = tool_results

                # Phase 4: Response Formatting
                context.current_phase = PromptPhase.RESPONSE_FORMATTING
                phase4_t0 = time.time()
                formatted_response = self._phase_4_formatting(context, debug_logger, is_capability_guard=False)
                logger.info(f"Phase 4 duration: {round(time.time()-phase4_t0,2)}s")
            else:
                # Fallback
                formatted_response = "I apologize, sir, but I encountered an issue processing your request."

            context.formatted_response = formatted_response

            # Phase Multi: Quality Gate
            context.current_phase = PromptPhase.QUALITY_GATE
            phase5_t0 = time.time()
            quality_result = self._phase_5_quality_gate(context, debug_logger)
            logger.info(f"Quality Gate duration: {round(time.time()-phase5_t0,2)}s")

            # Finalize response
            final_response = quality_result.response
            processing_time = round(time.time() - start_time, 1)

            # Save interaction (non-blocking compacting)
            try:
                topic_str = self._determine_topic(assessment_result)
                save_interaction(
                    user_prompt=user_message,
                    llm_reply=final_response,
                    full_llm_history=[],  # Empty - we now use database context loading
                    topic=topic_str,
                    username=username,
                    conversation_id=conversation_id
                )

                # Trigger automatic compacting if threshold reached (every 25 messages)
                # Run in background and do NOT block the response path
                db_path = ensure_user_database(username)
                import threading
                compact_thread = threading.Thread(
                    target=trigger_compact_if_needed,
                    args=(username, conversation_id, db_path),
                    daemon=True
                )
                compact_thread.start()
                # Do not join: avoid blocking response on compacting
                logger.debug("Compacting thread started (non-blocking)")
            except Exception as e:
                logger.error(f"Error saving interaction: {e}")

            # Build final history for response
            final_history = context.history + [{"role": "assistant", "content": final_response}]

            return {
                "response": final_response,
                "topic": topic_str,
                "history": final_history,
                "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"Error in Multi-phase processing: {e}", exc_info=True)
            processing_time = round(time.time() - start_time, 1)
            fallback_response = "I apologize, sir, but I encountered an issue processing your request. Please try again."

            return {
                "response": fallback_response,
                "topic": "error_fallback",
                "history": context.history + [{"role": "assistant", "content": fallback_response}],
                "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                "processing_time": processing_time
            }

    def _detect_guard_reason(self, question: str) -> Optional[CapabilityGuardReason]:
        """Lightweight regex-based guard detection for identity/temporal."""
        q = (question or "").lower()
        if re.search(r"\bwhat'?s your name\b|\bwho are you\b|\byour name\b", q):
            return CapabilityGuardReason.IDENTITY
        if re.search(r"\bwhat time is it\b|\bcurrent time\b|\bwhat'?s the date\b|\btoday'?s date\b", q):
            return CapabilityGuardReason.TEMPORAL
        return None

    

    def _build_context(self, user_message: str, history: List[Dict], username: str, conversation_id: str) -> ProcessingContext:
        """Build initial processing context with compacted conversation awareness"""

        # Get user location
        location = "unknown location"
        try:
            location_result = execute_tool("find_personal_variables", searchkey="location", username=username)
            if location_result.get("status") == "success" and location_result.get("data"):
                location = location_result["data"][0]["value"]
        except Exception as e:
            logger.warning(f"Could not retrieve user location: {e}")

        # Get base instructions
        base_instructions = get_base_instructions(username)

        # Load conversation context from database (replacing client-side history)
        compact_summary = None
        context_history = []

        if conversation_id:
            try:
                db_path = ensure_user_database(username)

                # Get conversation context (uses smart query based on message count)
                compact_summary, recent_messages = get_conversation_context(username, conversation_id, db_path)

                # Always use database context when conversation_id exists
                context_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in recent_messages
                ]

                if compact_summary:
                    logger.info(f"Loaded compacted context: {len(context_history)} recent messages + compact summary")
                else:
                    logger.info(f"Loaded conversation context: {len(context_history)} messages from database")
            except Exception as e:
                logger.error(f"Could not load conversation context: {e}")
                # For existing conversations, we NEED database context
                # Don't fallback to client history as it's unreliable
                context_history = []
        else:
            # New conversation (no conversation_id yet)
            # Client can pass initial history for edge cases, but typically empty
            context_history = history if history else []

        return ProcessingContext(
            original_question=user_message,
            username=username,
            conversation_id=conversation_id,
            location=location,
            date_time=datetime.now().strftime("%A, %B %d, %Y at %I:%M %p"),
            base_instructions=base_instructions,
            history=context_history,
            current_phase=PromptPhase.INITIAL_ASSESSMENT,
            compact_summary=compact_summary  # Add compact summary to context
        )

    def _phase_1_assessment(self, context: ProcessingContext, debug_logger) -> AssessmentResult:
        """Phase 1: Initial Assessment with CAPABILITY_GUARD"""

        debug_logger.log_phase_start("Phase 1: Initial Assessment", "Determine routing with CAPABILITY_GUARD")

        # Get tool categories for prompt
        tool_catalog = get_tool_catalog_for_selection()

        # Build assessment prompt
        messages = self.prompt_builder.build_assessment_prompt(context, tool_catalog)

        # Debug log the request
        debug_logger.log_llm_request(OLLAMA_MODEL, messages, tools=None, iteration_type="assessment")

        try:
            # Call LLM for assessment
            phase1_start = time.time()
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=[], options={"timeout": 20000})
            phase1_end = time.time()

            response_content = response['message']['content']
            logger.debug(f"Phase 1 assessment response: {response_content[:200]}...")

            # Debug log the response
            debug_logger.log_llm_response(response, phase1_end - phase1_start)

            # Parse the response
            assessment_result = self.guard_parser.parse_assessment_response(response_content)
            logger.info(f"Assessment result: {assessment_result.assessment_type}, guard: {assessment_result.guard_reason}")

            return assessment_result

        except Exception as e:
            logger.error(f"Phase 1 assessment failed: {e}")
            # Fallback to direct response
            return AssessmentResult(
                assessment_type="DIRECT",
                direct_response="I apologize, sir, but I encountered an issue with your request."
            )

    def _phase_2_tool_selection(self, context: ProcessingContext, debug_logger) -> ToolSelectionResult:
        """Phase 2: Tool Selection"""

        debug_logger.log_phase_start("Phase 2: Tool Selection", f"Selecting tools for: {context.assessment_result.tool_query}")

        # Get available tools based on assessment
        requested_tools = context.assessment_result.tools_needed
        available_tools = get_selected_tools(requested_tools)

        # Build tool selection prompt
        messages = self.prompt_builder.build_tool_selection_prompt(context, available_tools)

        # Debug log the request
        debug_logger.log_llm_request(OLLAMA_MODEL, messages, tools=None, iteration_type="tool_selection")

        try:
            phase2_start = time.time()
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=[], options={"timeout": 20000})
            phase2_end = time.time()

            response_content = response['message']['content']

            # Debug log the response
            debug_logger.log_llm_response(response, phase2_end - phase2_start)

            # Parse tool selection (simple parsing for now)
            selected_tools = requested_tools  # Use original tools as fallback
            usage_instructions = context.assessment_result.tool_query

            return ToolSelectionResult(
                selected_tools=selected_tools,
                usage_instructions=usage_instructions
            )

        except Exception as e:
            logger.error(f"Phase 2 tool selection failed: {e}")
            return ToolSelectionResult(
                selected_tools=requested_tools,
                usage_instructions="Execute the requested tools"
            )

    def _phase_3_tool_execution(self, context: ProcessingContext, debug_logger) -> List[Dict[str, Any]]:
        """Phase 3: Tool Execution"""

        debug_logger.log_phase_start("Phase 3: Tool Execution", f"Executing: {context.tool_selection_result.selected_tools}")

        # Get tools and execute LLM call with tools
        selected_tools = get_selected_tools(context.tool_selection_result.selected_tools)

        # Build messages for tool execution
        messages = []
        messages.append({'role': 'system', 'content': f'The current date is {context.date_time}. The user is in {context.location}.'})

        for instruction in context.base_instructions:
            messages.append({'role': 'system', 'content': instruction})

        messages.extend(context.history)
        messages.append({"role": "user", "content": context.original_question})
        messages.append({'role': 'system', 'content': f'Use the provided tools as needed to answer the user\'s question. {context.tool_selection_result.usage_instructions}'})

        # Debug log the request
        debug_logger.log_llm_request(OLLAMA_MODEL, messages, tools=selected_tools, iteration_type="tool_execution")

        try:
            phase3_start = time.time()
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=selected_tools)
            phase3_end = time.time()

            # Debug log the response
            debug_logger.log_llm_response(response, phase3_end - phase3_start)

            # Parse and execute tool calls (reuse existing logic)
            parsed_response = response_parser.parse_response(response)
            tool_results = []

            if parsed_response.needs_tool_execution and parsed_response.tool_calls:
                for tool_call in parsed_response.tool_calls:
                    function_name = tool_call.name
                    function_args = tool_call.arguments

                    # Ensure arguments is a dict
                    if isinstance(function_args, str):
                        try:
                            function_args = json.loads(function_args)
                        except json.JSONDecodeError:
                            function_args = {}

                    logger.info(f"Executing tool: {function_name} with args: {function_args}")

                    # Add username to memory-related tools
                    if function_name in ['recall_memories', 'recall_memories_with_time', 'find_personal_variables',
                                       'get_conversations_by_topic', 'get_topics_by_conversation', 'get_conversation_summary',
                                       'get_topic_statistics', 'get_user_conversations', 'get_conversation_details', 'search_conversations']:
                        function_args['username'] = context.username

                    try:
                        tool_start = time.time()
                        output = execute_tool(function_name, **function_args)
                        tool_end = time.time()

                        # Debug log tool execution
                        debug_logger.log_tool_execution(function_name, function_args, output, tool_end - tool_start)

                        tool_results.append({
                            "tool_name": function_name,
                            "status": output.get("status", "success"),
                            "data": output.get("data", output),
                            "message": output.get("message", "")
                        })

                    except Exception as e:
                        logger.error(f"Tool execution failed for {function_name}: {e}")
                        tool_results.append({
                            "tool_name": function_name,
                            "status": "error",
                            "data": None,
                            "message": f"Tool execution failed: {str(e)}"
                        })

            return tool_results

        except Exception as e:
            logger.error(f"Phase 3 tool execution failed: {e}")
            return [{
                "tool_name": "unknown",
                "status": "error",
                "data": None,
                "message": f"Tool execution phase failed: {str(e)}"
            }]

    def _phase_4_formatting(self, context: ProcessingContext, debug_logger, is_capability_guard: bool) -> str:
        """Phase 4: Response Formatting"""

        phase_desc = "CAPABILITY_GUARD formatting" if is_capability_guard else "Standard butler formatting"
        debug_logger.log_phase_start("Phase 4: Response Formatting", phase_desc)

        # Build formatting prompt
        messages = self.prompt_builder.build_formatting_prompt(context, is_capability_guard)

        # Debug log the request
        debug_logger.log_llm_request(OLLAMA_MODEL, messages, tools=None, iteration_type="formatting")

        try:
            phase4_start = time.time()
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=[])
            phase4_end = time.time()

            formatted_response = response['message']['content'].strip()

            # Debug log the response
            debug_logger.log_llm_response(response, phase4_end - phase4_start)

            return formatted_response

        except Exception as e:
            logger.error(f"Phase 4 formatting failed: {e}")
            if is_capability_guard:
                return "My name is Tatlock, sir. How may I assist you today?"
            else:
                return "I apologize, sir, but I encountered an issue processing your request."

    def _phase_5_quality_gate(self, context: ProcessingContext, debug_logger) -> QualityResult:
        """Phase Multi: Quality Gate"""

        debug_logger.log_phase_start("Phase Multi: Quality Gate", f"Validating response quality")

        quality_result = self.quality_gate.evaluate_response(context, context.formatted_response)

        logger.info(f"Quality gate result: approved={quality_result.approved}, type={quality_result.fallback_type}")

        # Debug log quality gate result
        debug_logger.log_quality_gate_result(
            quality_result.approved,
            quality_result.reasoning or "No reasoning provided",
            quality_result.fallback_type
        )

        return quality_result

    def _determine_topic(self, assessment_result: AssessmentResult) -> str:
        """Determine conversation topic based on assessment"""
        if assessment_result.assessment_type == "CAPABILITY_GUARD":
            return f"capability_guard_{assessment_result.guard_reason.value.lower()}"
        elif assessment_result.assessment_type == "TOOLS_NEEDED":
            return "tool_assisted_conversation"
        else:
            return "general_conversation"


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            raise RuntimeError("nest_asyncio is required to run async tools in a running event loop. Please install it with 'pip install nest_asyncio'.")
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)


# === NEW PROCESSOR INTEGRATION ===

# Global processor instance
_tatlock_processor = None

def get_tatlock_processor() -> TatlockProcessor:
    """Get or create the global TatlockProcessor instance"""
    global _tatlock_processor
    if _tatlock_processor is None:
        _tatlock_processor = TatlockProcessor()
    return _tatlock_processor

def process_chat_interaction(user_message: str, history: list[dict], username: str = "admin", conversation_id: str | None = None) -> dict:
    """
    Multi-phase architecture entry point - implements the sample.md specification

    This function uses the complete new architecture:
    - Phase 1: Initial Assessment with CAPABILITY_GUARD
    - Phase 2: Tool Selection (if needed)
    - Phase 3: Tool Execution (if needed)
    - Phase 4: Response Formatting
    - Phase 5: Quality Gate
    """
    processor = get_tatlock_processor()
    return processor.process_question(user_message, history, username, conversation_id)


