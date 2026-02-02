"""QuickRupee Loan Eligibility Screener Bot - Case Study 2."""
import logging

from livekit import rtc

from src.bots.base_bot import QualifierAgent

logger = logging.getLogger(__name__)


class LoanQualifierBot(QualifierAgent):
    """
    Voice bot for screening personal loan applicants for QuickRupee.

    Asks three eligibility questions:
    1. Are you a salaried employee?
    2. Is your monthly in-hand salary above ₹25,000?
    3. Do you reside in a metro city (Delhi, Mumbai, or Bangalore)?

    If all answers are YES -> Eligible (agent callback message)
    If any answer is NO -> Does not meet criteria (end call)

    Configuration is loaded from src/config/bots.yaml
    """

    def __init__(self, *, room: rtc.Room):
        """Initialize the loan qualifier bot."""
        super().__init__(room=room, bot_type="loan_qualifier")
        logger.info("LoanQualifierBot initialized")
