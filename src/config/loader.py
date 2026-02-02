"""Configuration loader for voice bot settings."""

import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global config cache
_CONFIG: dict | None = None


def _load_config() -> dict:
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / "bots.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_config() -> dict:
    """Get the full configuration (cached)."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _load_config()
    return _CONFIG


def get_bot_config(bot_type: str | None = None) -> dict:
    """
    Get configuration for a specific bot type.

    Args:
        bot_type: The bot type ("home_renovation" or "loan_qualifier").
                  If None, uses BOT_TYPE environment variable.

    Returns:
        Bot configuration dictionary
    """
    if bot_type is None:
        bot_type = os.getenv("BOT_TYPE", "home_renovation")

    config = get_config()
    bots = config.get("bots", {})

    if bot_type not in bots:
        raise ValueError(
            f"Unknown bot type: {bot_type}. " f"Available: {list(bots.keys())}"
        )

    return bots[bot_type]


def get_defaults() -> dict:
    """Get default settings."""
    config = get_config()
    return config.get("defaults", {})


def get_env(key: str, default: str | None = None) -> str | None:
    """Get environment variable."""
    return os.getenv(key, default)


def validate_env() -> bool:
    """Validate that all required environment variables are set."""
    required = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "DEEPGRAM_API_KEY",
        "ELEVENLABS_API_KEY",
    ]

    missing = [var for var in required if not os.getenv(var)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return True


def load_prompt(prompt_name: str, variables: dict[str, str]) -> str:
    """
    Load a prompt template and replace variables.

    Args:
        prompt_name: Name of the prompt file (without extension)
        variables: Dictionary of variables to replace in the template

    Returns:
        The rendered prompt string
    """
    prompt_path = Path(__file__).parent / "prompts" / f"{prompt_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

    with open(prompt_path, "r") as f:
        template = f.read()

    # Replace {{variable}} placeholders with values
    def replace_var(match: re.Match) -> str:
        var_name = match.group(1)
        return variables.get(var_name, match.group(0))

    rendered = re.sub(r"\{\{(\w+)\}\}", replace_var, template)

    print(rendered[:15])

    return rendered.strip()


def get_bot_prompt(bot_type: str | None = None) -> str:
    """
    Get the rendered system prompt for a bot type.

    Args:
        bot_type: The bot type. If None, uses BOT_TYPE env var.

    Returns:
        The rendered system prompt
    """
    cfg = get_bot_config(bot_type)

    # Build questions text
    questions = cfg.get("questions", [])
    questions_text = "\n".join(f"{i + 1}. {q['text']}" for i, q in enumerate(questions))

    # Prepare variables for template
    variables = {
        "greeting": cfg.get("greeting", "Hello!").strip(),
        "success_message": cfg.get("success_message", "Thank you!").strip(),
        "failure_message": cfg.get("failure_message", "Thank you for calling.").strip(),
        "clarification_message": cfg.get(
            "clarification_message", "Please answer with yes or no."
        ).strip(),
        "questions": questions_text,
        "company_name": cfg.get("company_name", ""),
    }

    return load_prompt("qualifier", variables)
