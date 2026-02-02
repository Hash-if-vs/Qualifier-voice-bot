"""Home Renovation Lead Qualifier Bot - Case Study 1."""

import logging

from livekit import rtc

from src.bots.base_bot import QualifierAgent

logger = logging.getLogger(__name__)


class HomeRenovationBot(QualifierAgent):
    """
    Voice bot for qualifying home renovation leads.

    Asks three questions:
    1. Do you own your home?
    2. Is your budget over $10,000?
    3. Are you looking to start within 3 months?

    If all answers are YES -> Hot Lead (offer transfer to agent)
    If any answer is NO -> Thank them and end call

    """

    def __init__(self, *, room: rtc.Room):
        """Initialize the home renovation bot."""
        super().__init__(room=room, bot_type="home_renovation")
        logger.info("HomeRenovationBot initialized")
