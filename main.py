"""Main entry point for the voice bot application."""

import logging
import os
import sys

from dotenv import load_dotenv
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli
from livekit.agents.voice import room_io
from livekit.plugins import elevenlabs, noise_cancellation, openai, silero

from src.bots import HomeRenovationBot, LoanQualifierBot
from src.config import get_bot_config, validate_env
from src.utils import make_deepgram_stt

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args(argv: list[str]) -> tuple[str, list[str]]:
    """
    Parse command line arguments.

    Args:
        argv: Command line arguments

    Returns:
        Tuple of (bot_type, remaining_argv)
    """
    bot_type = os.getenv("BOT_TYPE", "home_renovation")
    remaining = []

    i = 0
    while i < len(argv):
        if argv[i] == "--bot-type" and i + 1 < len(argv):
            bot_type = argv[i + 1]
            i += 2
        else:
            remaining.append(argv[i])
            i += 1

    return bot_type, remaining


async def entrypoint(ctx: JobContext):
    """
    Entry point for the LiveKit agent.

    This function is called when a new participant joins a room.
    Creates the voice pipeline and starts the conversation.
    """
    logger.info(f"Entrypoint called - Room: {ctx.room.name}")

    # Get bot type from environment
    bot_type = os.getenv("BOT_TYPE", "home_renovation")
    logger.info(f"Starting bot type: {bot_type}")

    # Load bot configuration
    bot_config = get_bot_config(bot_type)
    stt_config = bot_config.get("stt", {})
    tts_config = bot_config.get("tts", {})
    llm_cfg = bot_config.get("llm", {})

    # Create STT (Deepgram) with keyterms for yes/no detection
    stt = make_deepgram_stt(
        language=stt_config.get("language", "en-US"),
        model=stt_config.get("model", "nova-2"),
        endpointing_ms=stt_config.get("endpointing_ms", 300),
    )

    # Create TTS (ElevenLabs)
    tts = elevenlabs.TTS(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id=tts_config.get("voice_id", "21m00Tcm4TlvDq8ikWAM"),
        model=tts_config.get("model", "eleven_turbo_v2_5"),
    )

    llm = openai.LLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=llm_cfg.get("model", "gpt-4o-mini"),
        temperature=llm_cfg.get("temperature", 0.2),
    )

    # Create VAD (Voice Activity Detection)
    vad = silero.VAD.load()

    # Connect to the room
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name}")

    # Create the appropriate bot agent
    if bot_type == "loan_qualifier":
        agent = LoanQualifierBot(room=ctx.room)
    else:
        agent = HomeRenovationBot(room=ctx.room)

    # Create the agent session
    session = AgentSession(
        stt=stt,
        tts=tts,
        vad=vad,
        llm=llm,
    )

    # Start the session with the agent
    # User speech is handled in agent.stt_node()
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=room_io.RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
        room_output_options=room_io.RoomOutputOptions(
            transcription_enabled=True,
        ),
    )

    logger.info("Agent session started")


def main():
    """Main function to start the voice bot worker."""
    try:
        # Parse command line arguments
        bot_type, remaining_argv = parse_args(sys.argv[1:])
        os.environ["BOT_TYPE"] = bot_type

        # Validate configuration
        logger.info("Validating configuration...")
        validate_env()
        logger.info("Configuration validated successfully")

        logger.info(f"Starting voice bot with type: {bot_type}")

        # Reconstruct argv for LiveKit CLI
        sys.argv = [sys.argv[0]] + remaining_argv

        # Create worker options and start
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
            )
        )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error(
            "Please check your .env file and ensure all required variables are set"
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting voice bot: {e}")
        raise


if __name__ == "__main__":
    main()
