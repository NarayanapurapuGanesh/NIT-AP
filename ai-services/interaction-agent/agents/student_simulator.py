"""Student Simulator Agent — uses Llama 3.2 to generate authentic student responses.
The agent considers: persona type, current understanding, conversation history,
active misconceptions, and Bloom level to produce natural student behavior.
"""

import random
from loguru import logger

from services.ollama_service import OllamaService
from prompts.student_prompts import get_student_system_prompt, get_opening_message_prompt
from prompts.misconception_bank import get_misconceptions_for_subject
from models.schemas import (
    ConversationMessage, ActiveMisconception, NewMisconception
)


class StudentSimulator:
    """Simulates authentic student behavior during teaching interactions."""

    def __init__(self, ollama: OllamaService):
        self.ollama = ollama
        self._used_misconceptions: set[str] = set()

    async def generate_opening_message(
        self, persona_type: str, subject: str, department: str
    ) -> str:
        """Generate the first student message to start the interaction."""
        system = get_student_system_prompt(persona_type, subject, department)
        prompt = get_opening_message_prompt(persona_type, subject)

        response = await self.ollama.generate_student_response(prompt, system)
        logger.info(f"[STUDENT] Generated opening message for {persona_type} persona")
        return response.strip()

    async def generate_response(
        self,
        persona_type: str,
        subject: str,
        department: str,
        faculty_message: str,
        conversation_history: list[ConversationMessage],
        current_bloom: str,
        understanding_estimate: float,
        inject_misconception: bool = False,
        misconception_to_inject: dict | None = None,
    ) -> tuple[str, NewMisconception | None]:
        """Generate a student response to the faculty's explanation.

        Returns:
            Tuple of (student_message, new_misconception_if_injected)
        """
        system = get_student_system_prompt(persona_type, subject, department)

        # Build conversation context (last 6 turns for context window management)
        recent_history = conversation_history[-6:] if conversation_history else []
        context_lines = []
        for msg in recent_history:
            role_label = "Student" if msg.role == "Student" else "Teacher"
            context_lines.append(f"{role_label}: {msg.content}")
        context = "\n".join(context_lines)

        # Build the prompt based on understanding and whether to inject misconception
        prompt_parts = [f"CONVERSATION SO FAR:\n{context}\n"] if context else []
        prompt_parts.append(f"TEACHER'S LATEST RESPONSE:\n{faculty_message}\n")

        if inject_misconception and misconception_to_inject:
            prompt_parts.append(
                f"\n[INTERNAL INSTRUCTION - DO NOT REVEAL THIS TO THE TEACHER]\n"
                f"In your response, express this misconception naturally: "
                f"'{misconception_to_inject['misconception']}'\n"
                f"Make it sound like a genuine misunderstanding, not a direct quote.\n"
            )
        elif understanding_estimate < 0.4:
            prompt_parts.append(
                "\nYou are still quite confused. Express your confusion and ask "
                "for a simpler explanation or a different approach.\n"
            )
        elif understanding_estimate < 0.6:
            prompt_parts.append(
                "\nYou partially understand but have questions. Ask a follow-up "
                "question to deepen your understanding.\n"
            )
        elif understanding_estimate < 0.8:
            prompt_parts.append(
                "\nYou understand most of it. Ask a more advanced question or "
                "request a real-world example or application.\n"
            )
        else:
            prompt_parts.append(
                "\nYou understand this well. Either confirm your understanding "
                "by summarizing, or push to a higher-level question.\n"
            )

        prompt_parts.append(
            f"Current cognitive level: {current_bloom}\n"
            f"Respond as the student. Keep it SHORT and natural (2-4 sentences)."
        )

        prompt = "\n".join(prompt_parts)
        response = await self.ollama.generate_student_response(prompt, system)

        # Track misconception injection
        new_misconception = None
        if inject_misconception and misconception_to_inject:
            new_misconception = NewMisconception(
                misconception_text=misconception_to_inject["misconception"],
                correct_concept=misconception_to_inject["correct_concept"],
                subject_category=misconception_to_inject.get("category", subject),
            )
            self._used_misconceptions.add(misconception_to_inject["misconception"])
            logger.info(f"[STUDENT] Injected misconception: {misconception_to_inject['misconception'][:50]}...")

        return response.strip(), new_misconception

    def should_inject_misconception(
        self,
        persona_type: str,
        turn_number: int,
        total_misconceptions: int,
        max_misconceptions: int = 4,
    ) -> bool:
        """Decide whether to inject a misconception in this turn."""
        if total_misconceptions >= max_misconceptions:
            return False

        if turn_number < 3:
            return False  # Let the conversation warm up first

        # Misconception probability based on persona
        persona_probabilities = {
            "Beginner": 0.35,
            "Confused": 0.45,
            "Curious": 0.15,
            "Average": 0.25,
            "Excellent": 0.05,
            "PracticalLearner": 0.15,
            "ResearchStudent": 0.10,
            "IndustryStudent": 0.15,
            "ExamOriented": 0.30,
            "SlowLearner": 0.40,
            "AdvancedLearner": 0.05,
        }

        probability = persona_probabilities.get(persona_type, 0.20)
        return random.random() < probability

    def select_misconception(self, subject: str) -> dict | None:
        """Select a misconception from the bank that hasn't been used yet."""
        available = get_misconceptions_for_subject(subject)
        unused = [m for m in available if m["misconception"] not in self._used_misconceptions]

        if not unused:
            return None

        return random.choice(unused)
