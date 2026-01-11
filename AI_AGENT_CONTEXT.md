# AI Agent Context - StructureScout

**Last Updated:** 2026-01-11 12:47:49  
**Agent Version:** v1.0  
**Project:** StructureScout - Automated NAS100 Trading System  
**Status:** Planning Phase → Implementation Starting

---

## 1. PROJECT OVERVIEW

### What This Project Does
StructureScout is an automated trading system that:
- Runs during US market hours (9:30-11:30 AM EST, Mon-Fri)
- Captures NAS100 5-minute chart screenshots at scheduled intervals
- Sends screenshots to OpenAI GPT-4o-mini Vision API for pattern analysis
- Identifies structure-based trading setups (breakouts, structure breaks, mean reversion)
- Logs all analysis results to CSV with full trade parameters
- Sends Telegram notifications for high-quality setups
- Progresses through validation phases before live trading
- Eventually executes trades via MetaTrader5 API (after validation)

### Main Technology Stack
- **Language**: Python 3.9+
- **Trading Platform**: MetaTrader5 (MT5) API
- **AI Analysis**: OpenAI GPT-4o-mini Vision API
- **Notifications**: python-telegram-bot API
- **Scheduling**: APScheduler or schedule library
- **Data**: pandas (CSV logging), pytz (timezone handling)
- **Image Processing**: Pillow (PIL)
- **Configuration**: python-dotenv (.env files), PyYAML (config.yaml)

### Key Features/Capabilities
1. **Automated Chart Analysis**: AI-powered pattern recognition on 5-min charts
2. **Multi-Phase Validation**: Safe progression from observation to live trading
3. **Risk Management**: Position sizing, daily/weekly loss limits, news avoidance
4. **Professional Logging**: Complete audit trail of all setups and trades
5. **Telegram Control**: Remote monitoring and command interface
6. **News Calendar Integration**: Automatic avoidance of high-impact news events
7. **Milestone Progression**: Manual approval gates between phases
8. **Performance Tracking**: Win rate, R-multiples, setup type analysis

---

## 2. CURRENT STATE

### What's Working
- ✅ Complete technical specification documented (see `StructureScout.txt`)
- ✅ AI Agent Handoff System being implemented (context preservation)
- ✅ Project structure planned and designed
- ✅ System architecture fully defined (18 components)

### What's In Progress
- 🔄 Setting up AI Agent Handoff System (current task)
- 🔄 Creating project directory structure
- 🔄 Writing requirements.txt with dependencies
- 🔄 Creating configuration templates

### Known Issues
- ⚠️ None yet - project in initial setup phase
- ⚠️ Will need MT5 credentials from user for testing
- ⚠️ Will need OpenAI API key from user
- ⚠️ Will need Telegram bot token from user

### Implementation Status
**Phase 0: Setup - 0% Complete**
- [ ] Project structure created
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] MT5 connection tested
- [ ] OpenAI API tested
- [ ] Telegram bot tested

**Phase 1-4: Not Started**

---

## 3. USER PREFERENCES

### Workflow Preferences
- **Modular Architecture**: Each component in separate file, clear interfaces
- **Configuration-Driven**: All parameters in config files, not hardcoded
- **Comprehensive Documentation**: Detailed docstrings with purpose, parameters, returns, examples
- **Type Hints**: Full Python type annotations throughout
- **Extensive Logging**: Every decision point logged with reasoning
- **Test-Driven**: Unit tests for core functions
- **Safety First**: Multiple validation gates, no shortcuts to live trading

### Communication Style
- Professional and technical
- Detailed explanations with code examples
- Clear documentation of decisions and rationale
- Step-by-step implementation approach
- Emphasis on safety and risk management
- **CRITICAL: Always wait for user confirmation before implementing new features**
- **Always provide action plan before implementation**
- **Keep repository updated with regular commits**

### Dos and Don'ts

#### ✅ DO:
- Create modular, well-organized code structure
- Include comprehensive error handling
- Log every decision and action
- Use type hints and docstrings
- Implement safety checks and validation gates
- Test each component independently
- Keep API keys in .env files
- Follow PEP 8 style guidelines
- **WAIT for user confirmation before implementing new features**
- **Provide detailed action plan before coding**
- **Keep repository updated (commit changes regularly)**
- **NO emojis or unicode characters in code files**

#### ❌ DON'T:
- Hardcode API keys or credentials
- Create monolithic code files
- Skip error handling
- Implement auto-trading without safeguards
- Bypass milestone validation requirements
- Trade during news events without checks
- Ignore risk management limits
- Skip documentation or comments
- **Start implementing without user approval**
- **Use emojis or unicode in Python code**
- **Make changes without explaining the plan first**

---

## 4. DAILY WORKFLOW

### Current Phase (Setup)
No daily commands yet - in development phase.

### Once System is Operational

#### Morning (Before Market Open - 9:25 AM EST):
```bash
# System auto-starts via cron or systemd service
# Performs pre-market checks:
# - MT5 connection test
# - API health checks
# - Load previous day high/low
# - Check for news events today
# - Send "System Ready" Telegram notification
```

#### During Market Hours (9:30-11:30 AM EST):
```bash
# System runs automatically on schedule:
# - Screenshot capture at: 9:30, 9:45, 10:00, 10:15, 10:30, 11:00, 11:30 AM
# - GPT-4o-mini analysis for each screenshot
# - Log results to CSV
# - Send Telegram alerts for quality setups
# - Monitor open positions (if in live trading phase)
```

#### End of Day (12:00 PM EST):
```bash
# Automated daily summary:
# - Generate statistics
# - Send Telegram summary
# - Archive screenshots
# - Close any remaining positions
```

#### Manual Commands:
```bash
# Update context files before agent handoff
python update_context.py

# Manual system status check
python -m modules.health_monitor

# View today's log
cat data/trading_log.csv | grep $(date +%Y-%m-%d)

# Test individual components
python -m modules.mt5_connection --test
python -m modules.gpt_analysis --test
python -m modules.telegram_bot --test
```

#### Weekly (Sunday 6 PM EST):
```bash
# Automated weekly report:
# - Performance statistics
# - Milestone progress evaluation
# - Setup type analysis
# - Advancement recommendation if criteria met
```

### Expected Outputs
- **Screenshots**: `screenshots/YYYY-MM-DD/NAS100_YYYYMMDD_HHMM.png`
- **Daily Logs**: New rows in `data/trading_log.csv`
- **Telegram Alerts**: Real-time setup notifications
- **Daily Summary**: Statistics report at 12 PM
- **Weekly Report**: Sunday evening performance analysis

---

## 5. IMPORTANT FILES

### Planning & Documentation
| File | Purpose |
|------|---------|
| `StructureScout.txt` | Complete technical specification (18 components, 1500+ lines) |
| `AI_AGENT_CONTEXT.md` | This file - human-readable project overview |
| `project_state.json` | Machine-readable current state |
| `CONVERSATION_SUMMARY.md` | Historical decisions across agent sessions |
| `NEW_AGENT_START_HERE.md` | Quick-start guide for new AI agents |
| `README.md` | Public project documentation (to be created) |

### Configuration Files (To Be Created)
| File | Purpose |
|------|---------|
| `config.yaml` | System configuration (trading parameters, schedules, thresholds) |
| `.env` | API keys and credentials (gitignored) |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files to exclude from version control |

### Core Application Files (To Be Implemented)
| File | Purpose |
|------|---------|
| `main.py` | Main execution script, scheduler, workflow orchestration |
| `update_context.py` | Auto-update script for AI agent context files |

### Module Files (To Be Implemented)
| Module | Purpose |
|--------|---------|
| `modules/mt5_connection.py` | MT5 API integration, chart screenshot capture |
| `modules/gpt_analysis.py` | GPT-4o-mini vision analysis, prompt engineering |
| `modules/telegram_bot.py` | Telegram notifications, command interface |
| `modules/data_logger.py` | CSV logging, data persistence |
| `modules/scheduler.py` | Task scheduling, trading hours logic |
| `modules/performance_analyzer.py` | Performance tracking, milestone validation |
| `modules/error_handler.py` | Error management, recovery logic |
| `modules/health_monitor.py` | System health checks, heartbeat monitoring |
| `modules/risk_manager.py` | Position sizing, risk limits, margin checks |
| `modules/trade_executor.py` | Trade execution via MT5 (Phase 3+) |
| `modules/news_calendar.py` | Economic calendar, news avoidance |
| `modules/state_manager.py` | System state persistence, crash recovery |

### Data Files (Will Be Generated)
| File | Purpose |
|------|---------|
| `data/trading_log.csv` | Main analysis log (all setups, AI predictions) |
| `data/trade_execution.csv` | Actual trade execution log (Phase 3+) |
| `data/error.log` | Error and exception log |
| `data/system.log` | System events and heartbeat log |
| `data/risk_log.csv` | Risk limit breaches and pauses |
| `data/daily_summaries/` | Daily summary reports |
| `data/system_state.json` | Current system state (for recovery) |
| `screenshots/YYYY-MM-DD/` | Daily chart screenshots |
| `exports/cursor_analysis_export.json` | Data export for AI analysis |

---

## 6. GOALS & PRIORITIES

### Current Objectives (Priority Order)
1. **Complete AI Agent Handoff System** ← Current focus
   - Create all 4 context files ✅ In progress
   - Write update_context.py script
   - Test handoff process

2. **Set Up Project Structure**
   - Create directory structure
   - Write requirements.txt
   - Create config.yaml template
   - Create .env template

3. **Implement Phase 0: Core Components**
   - MT5 connection module
   - GPT-4o-mini analysis module
   - Telegram bot module
   - Basic logging system

4. **Test Individual Components**
   - Test MT5 connection with user's credentials
   - Test OpenAI API with sample chart
   - Test Telegram notifications
   - Verify timezone handling (EST/EDT)

5. **Build Scheduler & Main Loop**
   - Implement trading hours detection
   - Add news calendar integration
   - Create main workflow orchestration
   - Test end-to-end in observation mode

### What User Wants Next
After completing AI Agent Handoff System:
1. Create complete project directory structure
2. Write requirements.txt with all dependencies
3. Begin implementing MT5 connection module
4. Set up configuration file templates
5. Start Phase 1: Observation mode implementation

### Long-Term Vision

#### Milestone 1: Observation Phase (Weeks 1-4)
- **Goal**: Validate that 3-8 quality setups appear per week
- **Success Criteria**: Consistent setup identification, avg confidence >60%
- **Outcome**: Decision to proceed or abandon strategy

#### Milestone 2: Paper Trading (Weeks 5-6)
- **Goal**: Validate AI prediction accuracy without real money
- **Success Criteria**: 70% setup accuracy (setups behave as predicted)
- **Outcome**: Decision to proceed to live testing or revise

#### Milestone 3: Micro Live (Weeks 7-10)
- **Goal**: Validate execution quality with minimal risk (2 micro contracts)
- **Success Criteria**: 45% win rate, <10% drawdown, <3 ticks slippage
- **Outcome**: Decision to scale to full live or continue testing

#### Milestone 4: Full Live Trading (Week 11+)
- **Goal**: Profitable automated trading at 1% risk per trade
- **Success Criteria**: 50% win rate, 1.5 avg R-multiple, <15% max drawdown
- **Outcome**: Sustainable trading system or pause for analysis

### Ultimate Goal
A fully automated, validated, profitable trading system that:
- Operates independently during market hours
- Identifies 3-8 high-quality setups per week
- Maintains 50%+ win rate with 1.5+ average R-multiple
- Respects strict risk management limits
- Provides complete audit trail and performance tracking
- Requires minimal user intervention (Telegram monitoring only)

---

## 7. TECHNICAL ARCHITECTURE SUMMARY

### Component Overview (18 Components)
1. **Configuration & Environment Setup** - API keys, trading parameters
2. **MT5 Chart Screenshot Capture** - Chart access, reference lines, screenshot saving
3. **GPT-4o-mini Vision Analysis** - Pattern recognition, JSON response parsing
4. **Automated Logging System** - CSV persistence, data tracking
5. **Telegram Notification System** - Alerts, daily/weekly reports
6. **Task Scheduler & Main Loop** - Orchestration, trading hours logic
7. **Data Analysis & Performance Tracking** - Statistics, milestone validation
8. **System Monitoring & Health Checks** - Heartbeat, error detection
9. **Configuration for AI Integration** - Context export for AI assistants
10. **Milestone Progression & Mode Switching** - Phase transitions, validation
11. **Economic News Calendar Integration** - News avoidance, blackout periods
12. **Weekend & Holiday Detection** - Trading calendar, market hours
13. **Mode Transition & Milestone Validator** - Advancement logic, criteria checks
14. **Live Trade Execution Engine** - Order placement, position monitoring
15. **Professional Risk Management** - Position sizing, margin checks, limits
16. **Advanced Logging & Audit Trail** - Execution quality, slippage tracking
17. **System State Manager** - Crash recovery, state persistence
18. **Mode-Specific Behavior Matrix** - Per-phase configuration

### Key Design Patterns
- **Modular Architecture**: Each component independent, testable
- **Configuration-Driven**: Settings in config.yaml, not code
- **State Machine**: Four phases with manual approval gates
- **Error Recovery**: Graceful degradation, automatic reconnection
- **Audit Trail**: Complete logging of all decisions and actions

### Data Flow
```
Market Open → Pre-checks → Screenshot Capture → GPT-4o-mini Analysis →
Parse Response → Validate Setup → Log to CSV →
(If High Quality) → Send Telegram Alert →
(If Live Mode + Confirmed) → Execute Trade → Monitor Position →
(On Close) → Log Outcome → Update Statistics →
End of Day → Generate Summary → Archive Data
```

---

## 8. API USAGE & COSTS

### OpenAI API (GPT-4o-mini Vision)
- **Model**: gpt-4o-mini
- **Usage**: 7 scans/day × 5 days = 35 scans/week
- **Cost per scan**: ~$0.00015
- **Weekly cost**: ~$0.00525
- **Monthly cost**: ~$0.27 (negligible)

### Telegram Bot API
- **Cost**: Free (no limits for personal use)

### MetaTrader5 API
- **Cost**: Free (built into MT5 platform)

**Total Monthly Cost**: < $1.00

---

## 9. RISK MANAGEMENT RULES

### Position Sizing
- **Observation/Paper**: No actual positions (0 contracts)
- **Micro Live**: Fixed 2 micro contracts (ignore % calculation)
- **Full Live**: 1% of account balance per trade

### Daily/Weekly Limits
- **Daily Loss Limit**: 3% of account → halt trading for rest of day
- **Weekly Loss Limit**: 6% of account → halt trading for rest of week
- **Max Trades Per Day**: 3 trades (full live mode)
- **Max Trades Per Week**: 12 trades

### Setup Filters
- **Minimum R:R Ratio**: 1.5:1
- **Minimum Confidence**: 65%
- **News Avoidance**: No trades 15 min before, 30 min after high-impact news
- **Market Hours Only**: 9:30-11:30 AM EST, Mon-Fri (no weekends/holidays)

---

## 10. NEXT STEPS FOR NEW AGENT

When a new AI agent takes over:

1. **Read this file completely** (you're doing it now!)
2. **Check `project_state.json`** for machine-readable current state
3. **Review `CONVERSATION_SUMMARY.md`** for historical decisions
4. **Read `StructureScout.txt`** for complete technical details (if needed)
5. **Confirm with user**: "I've reviewed the StructureScout context. Current status: [X]. Ready to continue from [last checkpoint]?"
6. **Proceed with implementation** based on current phase

---

**Last Updated:** 2026-01-11 12:47:49  
**Next Update Due:** When significant progress is made or before next agent handoff  
**Update Frequency:** Before each agent handoff, or when major milestones reached  
**Auto-Update Script:** Run `python update_context.py` before handoff
