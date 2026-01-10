# StructureScout - Setup Instructions

## Prerequisites

- Python 3.9 or higher
- MetaTrader5 platform installed
- OpenAI API account
- Telegram account

---

## Step 1: Clone/Navigate to Project

```bash
cd /home/mperez508/StructureScout
```

---

## Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- MetaTrader5
- OpenAI SDK
- Telegram bot SDK
- pandas, numpy
- APScheduler
- Pillow, pytz
- python-dotenv, PyYAML
- Testing tools (pytest, pylint, etc.)

---

## Step 4: Configure Credentials

### Create .env file

```bash
# Copy the example file
cp env.example .env

# Edit with your actual credentials
nano .env  # or use your preferred editor
```

### Required Credentials

**MetaTrader5**:
- `MT5_LOGIN`: Your MT5 account number
- `MT5_PASSWORD`: Your MT5 password
- `MT5_SERVER`: Your broker's server (e.g., "MetaQuotes-Demo")
- `MT5_PATH`: Path to MT5 installation (e.g., "/usr/bin/mt5" or "C:/Program Files/MetaTrader 5")

**OpenAI**:
- `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys

**Telegram**:
- `TELEGRAM_BOT_TOKEN`: Create bot via @BotFather on Telegram
- `TELEGRAM_CHAT_ID`: Get your chat ID from @userinfobot

### Creating a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the bot token provided
5. Start a chat with your new bot
6. Get your chat ID from `@userinfobot`

---

## Step 5: Review Configuration

Edit `config/config.yaml` to customize:
- Trading hours and scan schedule
- Risk management settings
- Alert preferences
- Data storage paths

**Default settings are safe for observation mode.**

---

## Step 6: Verify Installation

### Test Configuration Loader

```bash
python3 -c "from config import get_config; c = get_config(); print(c.validate_credentials())"
```

Expected output:
```
{'mt5': True, 'openai': True, 'telegram': True}
```

If any show `False`, check your `.env` file.

---

## Step 7: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=modules --cov-report=html
```

---

## Step 8: Test Individual Components

### Test MT5 Connection

```bash
python3 -m modules.mt5_connection --test
```

### Test OpenAI API

```bash
python3 -m modules.gpt_analysis --test
```

### Test Telegram Bot

```bash
python3 -m modules.telegram_bot --test
```

---

## Step 9: Start in Observation Mode

```bash
# The bot starts in observation mode by default (safe, no trading)
python3 main.py
```

The system will:
- Connect to MT5
- Capture screenshots at scheduled times
- Analyze with GPT-4o-mini
- Log all setups to CSV
- Send Telegram alerts for high-quality setups
- **NOT execute any trades** (observation mode)

---

## Directory Structure

```
StructureScout/
├── config/              # Configuration files
│   ├── __init__.py      # Config loader
│   └── config.yaml      # System settings
├── modules/             # Core modules (to be implemented)
│   └── __init__.py
├── data/                # CSV logs (generated at runtime)
├── screenshots/         # Chart images (generated at runtime)
├── logs/                # System logs (generated at runtime)
├── tests/               # Unit tests
│   ├── __init__.py
│   └── conftest.py      # Test fixtures
├── .env                 # Your credentials (NOT in git)
├── env.example          # Template for .env
├── requirements.txt     # Python dependencies
└── main.py              # Main application (to be implemented)
```

---

## Troubleshooting

### MT5 Connection Issues

1. Verify MT5 is installed and running
2. Check `MT5_PATH` is correct
3. Ensure broker server name is exact
4. Test login manually in MT5 platform

### OpenAI API Issues

1. Verify API key is valid
2. Check account has credits
3. Ensure GPT-4o-mini access enabled
4. Test at https://platform.openai.com/playground

### Telegram Issues

1. Verify bot token is correct
2. Ensure you've started a chat with your bot
3. Check chat ID is correct (numeric)
4. Test bot with @BotFather

### Import Errors

```bash
# Make sure you're in the project root
cd /home/mperez508/StructureScout

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## Security Notes

1. **NEVER commit .env file** - It contains your credentials
2. **Keep .gitignore updated** - Ensure .env is excluded
3. **Use strong passwords** - For MT5 and API keys
4. **Limit API permissions** - Use read-only keys where possible
5. **Monitor API usage** - Set spending limits on OpenAI account

---

## What's Next

After setup is complete:

1. **Phase 0 Complete** - Foundation is ready
2. **Phase 1** - Implement core modules (MT5, GPT, Telegram, Logger, Scheduler)
3. **Phase 2** - Add supporting modules (News, Risk, State, Error, Health)
4. **Phase 3** - Create main application workflow
5. **Phase 4** - Observation mode testing (4 weeks)

---

## Getting Help

- Check `IMPLEMENTATION_PLAN.md` for development roadmap
- Review `AI_AGENT_CONTEXT.md` for project overview
- See `StructureScout.txt` for complete technical spec
- Read `HANDOFF_GUIDE.md` for AI agent context system

---

## Development Workflow

1. **Before implementing**: Get user approval
2. **While coding**: No emojis in Python code
3. **After coding**: Run tests, commit changes
4. **Keep updated**: Regular git commits

---

**Setup Version**: v1.0
**Last Updated**: 2026-01-10
**Status**: Phase 0 Complete - Ready for Phase 1
