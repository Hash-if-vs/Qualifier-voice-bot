"""STT configuration with keyterms for improved yes/no recognition."""
import os
from livekit.plugins import deepgram

# Keyterms to help Deepgram recognize yes/no responses accurately
# Format: (keyword, intensifier) - intensifier boosts recognition
YES_NO_KEYTERMS = [
    # Affirmative
    ("yes", 10),
    ("yeah", 8),
    ("yep", 8),
    ("yup", 8),
    ("sure", 6),
    ("correct", 6),
    ("absolutely", 5),
    ("definitely", 5),
    ("of course", 5),
    ("certainly", 5),
    ("affirmative", 4),
    ("right", 4),
    ("okay", 4),
    ("ok", 4),
    # Negative
    ("no", 10),
    ("nope", 8),
    ("nah", 8),
    ("not", 6),
    ("negative", 5),
    ("never", 5),
    ("incorrect", 4),
    ("wrong", 4),
]


def make_deepgram_stt(
    language: str = "en-US",
    model: str = "nova-2",
    endpointing_ms: int = 300,
) -> deepgram.STT:
    """
    Create a Deepgram STT instance configured for yes/no detection.

    Args:
        language: Language code (e.g., "en-US", "en-IN")
        model: Deepgram model to use
        endpointing_ms: Silence duration to end utterance

    Returns:
        Configured Deepgram STT instance
    """
    return deepgram.STT(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model=model,
        language=language,
        endpointing_ms=endpointing_ms,
        smart_format=True,
        filler_words=True,
        keywords=YES_NO_KEYTERMS,
    )
