"""
Base LLM-powered qualifier bot using LiveKit Voice Agents.
All conversation flow is handled by the LLM.
"""

from __future__ import annotations

import logging

from livekit import rtc
from livekit.agents.voice import Agent

from src.config import get_bot_prompt

logger = logging.getLogger(__name__)


class QualifierAgent(Agent):
    """
    Base class for lead qualification voice bots.

    This agent:
    - Uses a real LLM
    - Asks questions one by one
    - Handles yes/no understanding
    - Decides qualified vs not qualified
    - Ends the conversation cleanly

    Child bots ONLY specify bot_type.
    """

    def __init__(
        self,
        *,
        room: rtc.Room,
        bot_type: str,
    ):
        self.room = room
        self.bot_type = bot_type

        # Load system prompt from template file
        system_prompt = get_bot_prompt(bot_type)

        logger.info("Initializing QualifierAgent (LLM mode): %s", bot_type)

        super().__init__(
            instructions=system_prompt,
        )

    async def on_enter(self) -> None:
        """
        Called when the agent becomes active.
        We trigger the first LLM turn.
        """
        logger.info("Agent entered – starting LLM-driven qualification flow")
        # This kicks off the first assistant response (greeting)
        await self.session.say("")
