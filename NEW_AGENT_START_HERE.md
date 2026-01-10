# 🤖 New AI Agent - START HERE

## ⚡ IMMEDIATE CONTEXT

**Previous agent stopped at**: Initial project setup - AI Agent Handoff System implementation  
**Conversation limit reached**: 2026-01-10  
**Current priority**: Setting up context preservation system for seamless agent handoffs

## 🎯 USER'S MAIN GOAL

Build an automated NAS100 trading system that uses GPT-4o-mini vision API to analyze 5-minute charts, identify structure-based setups, and progress through validation phases (observation → paper trading → micro live → full live trading).

## 📋 WHAT YOU NEED TO KNOW RIGHT NOW

1. **This is a sophisticated trading bot project** - Not yet implemented, currently in planning phase
2. **User has detailed technical specification** - See `StructureScout.txt` for complete architecture
3. **Four-phase validation approach** - Must validate pattern accuracy before risking real money
4. **Key technologies**: Python, MetaTrader5 API, OpenAI GPT-4o-mini Vision, Telegram Bot API

## 🚀 WHAT TO DO FIRST

1. Read: `AI_AGENT_CONTEXT.md` (full project context - 5 min read)
2. Check: `project_state.json` (current implementation state)
3. Review: `StructureScout.txt` (complete technical specification)
4. Ask user: "I've reviewed the StructureScout project context. Ready to continue implementation from [last checkpoint]?"

## 🔧 DAILY COMMANDS USER WILL RUN (Once Implemented)

```bash
# Start the trading bot (during market hours)
python main.py

# Update context files before agent handoff
python update_context.py

# Check system status
python -m modules.health_monitor

# View today's trading log
cat data/trading_log.csv | grep $(date +%Y-%m-%d)
```

## ⚠️ IMPORTANT NOTES

### Critical Requirements:
- **Never execute real trades without explicit milestone approval**
- **All API keys must be in `.env` file (never hardcoded)**
- **System operates only during US market hours: 9:30-11:30 AM EST, Mon-Fri**
- **Four-phase validation: observation (4 weeks) → paper trading (2 weeks) → micro live (4 weeks) → full live**

### User Preferences:
- **Modular code structure** - Each component in separate file
- **Comprehensive logging** - Every decision point logged
- **Type hints throughout** - Full Python type annotations
- **Detailed docstrings** - Every function fully documented
- **Configuration-driven** - Settings in config.yaml, not hardcoded

### Don't Do This:
- ❌ Don't implement auto-trading without safeguards
- ❌ Don't skip news/holiday detection features
- ❌ Don't hardcode API keys or credentials
- ❌ Don't bypass milestone validation gates
- ❌ Don't create monolithic code (keep it modular)
- ❌ **Don't start implementing without user confirmation**
- ❌ **Don't use emojis or unicode in Python code**
- ❌ **Don't make changes without explaining action plan first**

## 📁 KEY FILES TO MONITOR

### Planning Documents:
- `StructureScout.txt` - Complete system architecture (detailed technical spec)
- `AI_AGENT_CONTEXT.md` - Project overview and current state
- `project_state.json` - Machine-readable project status

### Configuration (When Created):
- `config.yaml` - System configuration and trading parameters
- `.env` - API keys (OpenAI, Telegram, MT5 credentials)
- `requirements.txt` - Python dependencies

### Core Modules (To Be Implemented):
- `main.py` - Main execution loop and scheduler
- `modules/mt5_connection.py` - MetaTrader5 integration
- `modules/gpt_analysis.py` - GPT-4o-mini vision analysis
- `modules/telegram_bot.py` - Telegram notifications
- `modules/data_logger.py` - CSV logging system
- `modules/scheduler.py` - Task scheduling
- `modules/performance_analyzer.py` - Performance tracking
- `modules/error_handler.py` - Error management
- `modules/health_monitor.py` - System health checks

### Data Files (Will Be Created):
- `data/trading_log.csv` - Main trading analysis log
- `data/trade_execution.csv` - Actual trade execution log
- `data/error.log` - System errors
- `data/system.log` - System events
- `screenshots/YYYY-MM-DD/` - Daily chart screenshots

## 🎯 PROJECT PHASES (NOT YET STARTED)

### Current Phase: Phase 0 - Setup ⬅️ YOU ARE HERE
- Set up project structure
- Install dependencies
- Configure MT5 connection
- Test OpenAI API integration
- Set up Telegram bot

### Phase 1: Observation (4 weeks)
- Capture screenshots during trading hours
- Analyze with GPT-4o-mini
- Log all setups (no trading)
- Target: 3-8 quality setups per week
- Milestone: Consistent setup identification

### Phase 2: Paper Trading (2 weeks)
- Track how setups perform without execution
- Validate AI accuracy
- Measure setup quality
- Milestone: 70% setup accuracy

### Phase 3: Micro Live (4 weeks)
- Execute with 2 micro contracts only
- Validate execution quality
- Test slippage and fills
- Milestone: 45% win rate, <10% drawdown

### Phase 4: Full Live
- Scale to full 1% risk per trade
- Daily/weekly risk limits active
- Full production trading

## 📊 KEY METRICS TO TRACK

### During Observation Phase:
- Valid setups per week (target: 3-8)
- Average AI confidence score (target: >60%)
- Setup type distribution
- Market regime distribution

### During Live Trading:
- Win rate (target: ≥50%)
- Average R-multiple (target: ≥1.5)
- Profit factor (target: >1.3)
- Max drawdown (limit: <15%)
- Slippage (target: <3 ticks)

## 🔗 QUICK LINKS

**Project Root**: `/home/mperez508/StructureScout`  
**User**: mperez508  
**OS**: Linux (Ubuntu/Debian based)  
**Python Version**: 3.9+ required  
**Timezone**: EST/EDT (US Eastern)

---

## 💡 AGENT HANDOFF CONTEXT

This file is part of an **AI Agent Handoff System** designed to enable seamless continuation of work when conversation limits are reached. The system includes:

1. **NEW_AGENT_START_HERE.md** ← You are reading this
2. **AI_AGENT_CONTEXT.md** - Human-readable project context
3. **project_state.json** - Machine-readable state data
4. **CONVERSATION_SUMMARY.md** - Historical decisions and changes
5. **update_context.py** - Auto-update script for context files

When you (new agent) take over, these files give you complete project understanding without requiring user to re-explain everything.

---

**Last Updated**: 2026-01-10  
**Context System Version**: v1.0  
**Agent Handoff Count**: 1 (You are the first continuation agent)
