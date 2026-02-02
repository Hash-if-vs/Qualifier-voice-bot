# Voice Bot - Lead Qualifier & Loan Screener

Voice bot prototypes built with LiveKit Agents framework, OpenAI GPT-4.1 (LLM), Deepgram (STT), and ElevenLabs (TTS) for automated phone screening.

## Overview

This project implements two voice bot case studies:

### Case Study 1: Home Renovation Lead Qualifier
Filters incoming calls for a home renovation company by asking three yes/no questions:
1. Do you own your home?
2. Is your budget over $10,000?
3. Are you looking to start within 3 months?

- **Hot Lead** (all Yes) → Offer to transfer to human agent
- **Not Qualified** (any No) → Politely thank and end call

### Case Study 2: QuickRupee Loan Eligibility Screener
Screens personal loan applicants by asking three eligibility questions:
1. Are you a salaried employee?
2. Is your monthly in-hand salary above ₹25,000?
3. Do you reside in a metro city (Delhi, Mumbai, or Bangalore)?

- **Eligible** (all Yes) → Agent will call back in 10 minutes
- **Not Eligible** (any No) → Inform they don't meet criteria and end call

## Tech Stack

- **Python 3.10+**
- **LiveKit Agents** - Voice infrastructure and agent framework
- **OpenAI GPT-4o-mini** - LLM for natural conversation and intent understanding
- **Deepgram** - Speech-to-Text (STT) with keyterms for better recognition
- **ElevenLabs** - Text-to-Speech (TTS)
- **Silero VAD** - Voice Activity Detection

## Project Structure

```
voice-bot-task/
├── .env                              # Your configuration (create from .env.example)
├── .env.example                      # Configuration template
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── main.py                           # Entry point with AgentSession setup
└── src/
    ├── config/
    │   ├── loader.py                 # YAML configuration loader
    │   └── bots.yaml                 # Bot definitions (questions, messages, LLM settings)
    ├── bots/
    │   ├── base_bot.py               # QualifierAgent base class with system prompt
    │   ├── home_renovation_bot.py    # Home renovation qualifier
    │   └── loan_qualifier_bot.py     # Loan eligibility screener
    └── utils/
        └── stt_config.py             # Deepgram STT with keyterms
```

## Architecture

Inspired by production voice bot patterns:

- **AgentSession** - Manages STT/TTS/VAD/LLM pipeline
- **QualifierAgent** - Base class that builds system prompts from YAML config
- **LLM-Driven Flow** - OpenAI GPT-4o-mini handles conversation logic and intent understanding
- **YAML Configuration** - All questions, messages, and LLM settings in `bots.yaml`
- **STT Keyterms** - Improved recognition for "yes", "no" variants

## Prerequisites

1. **Python 3.10 or higher**
2. **LiveKit Account** - Get API credentials from [LiveKit Cloud](https://cloud.livekit.io/)
3. **OpenAI API Key** - Sign up at [OpenAI](https://platform.openai.com/)
4. **Deepgram API Key** - Sign up at [Deepgram](https://console.deepgram.com/)
5. **ElevenLabs API Key** - Sign up at [ElevenLabs](https://elevenlabs.io/)

## Installation

### 1. Create Virtual Environment

```bash
cd Qualifier-voice-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
LIVEKIT_URL=wss://your-server.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key
BOT_TYPE=home_renovation
```

## Usage

### Running the Bot

```bash
# Using environment variable
python main.py console

# Or with command line argument
python main.py console --bot-type home_renovation
python main.py console --bot-type loan_qualifier
```

### Development Mode

```bash
python main.py dev
```

## How It Works

### LLM-Driven Conversation

The bot uses OpenAI GPT-4.1 to handle the entire conversation flow. A system prompt is dynamically built from the YAML configuration, instructing the LLM to:

1. Greet the caller
2. Ask qualification questions one at a time
3. Interpret user responses naturally (not just literal "yes/no")
4. Ask for clarification when responses are unclear
5. Make qualification decisions based on all answers
6. Deliver appropriate success/failure messages

### Conversation Flow

```
┌─────────────┐
│  Greeting   │  LLM greets the caller
└──────┬──────┘
       ▼
┌─────────────┐
│  Question 1 │  "Do you own your home?"
└──────┬──────┘
       ▼
┌─────────────┐
│  LLM        │  Understands intent from natural speech
│  Interprets │  Asks follow-up if unclear
└──────┬──────┘
       ▼
┌─────────────┐
│  Question 2 │  "Is your budget over $10,000?"
└──────┬──────┘
       ▼
      ...
       ▼
┌─────────────┐
│  Decision   │  All Yes → Success message
│             │  Any No  → Failure message
└─────────────┘
```

### System Prompt Architecture

The `QualifierAgent` base class builds a system prompt from YAML config that includes:
- Greeting message and conversation tone
- All questions to ask (in order)
- Rules for interpreting yes/no responses
- Clarification behavior for unclear answers
- Success and failure message templates

## Customization

### Modifying Questions and Messages

Edit `src/config/bots.yaml`:

```yaml
bots:
  home_renovation:
    greeting: "Hello! Thank you for calling..."
    questions:
      - text: "Do you own your home?"
        key: "owns_home"
      - text: "Is your budget over $10,000?"
        key: "budget_over_10k"
    success_message: "Great! You're a hot lead..."
    failure_message: "Thank you for your interest..."
```

### Adding a New Bot Type

1. Add configuration to `src/config/bots.yaml` (include `llm` settings)
2. Create new bot class in `src/bots/`
3. Update `main.py` to handle new bot type

### Changing LLM Settings

Update in `bots.yaml`:

```yaml
llm:
  provider: "openai"
  model: "gpt-4.1"
  temperature: 0.2
```

### Changing Voice

Update in `bots.yaml`:

```yaml
tts:
  voice_id: "different_voice_id"
  model: "eleven_turbo_v2_5"
```

### Changing STT Settings

Update in `bots.yaml`:

```yaml
stt:
  model: "nova-2"
  language: "en-US"
  endpointing_ms: 300
```

## Troubleshooting

### Bot Not Responding
- Check all API keys in `.env` (especially `OPENAI_API_KEY`)
- Verify LiveKit credentials
- Check logs for errors

### LLM Response Issues
- Verify `OPENAI_API_KEY` is valid
- Check OpenAI API quota/billing
- Review system prompt in logs
- Adjust `temperature` in `bots.yaml` for more/less variation

### Speech Recognition Issues
- Check Deepgram transcription in logs
- Add more keyterms in `stt_config.py` for domain-specific terms

### Connection Issues
- Verify `LIVEKIT_URL` format: `wss://...`
- Ensure firewall allows WebSocket connections
- Check LiveKit server status

## API Keys & Services

| Service | Console | Docs |
|---------|---------|------|
| LiveKit | [cloud.livekit.io](https://cloud.livekit.io/) | [docs.livekit.io](https://docs.livekit.io/) |
| OpenAI | [platform.openai.com](https://platform.openai.com/) | [platform.openai.com/docs](https://platform.openai.com/docs/) |
| Deepgram | [console.deepgram.com](https://console.deepgram.com/) | [developers.deepgram.com](https://developers.deepgram.com/) |
| ElevenLabs | [elevenlabs.io](https://elevenlabs.io/) | [docs.elevenlabs.io](https://docs.elevenlabs.io/) |

## License

This is a prototype project for demonstration purposes.
