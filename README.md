# StructureScout 🤖📈

**Automated NAS100 Trading System with GPT-4o-mini Vision Analysis**

An intelligent trading bot that analyzes NAS100 5-minute charts using OpenAI's GPT-4o-mini Vision API to identify structure-based trading setups, validate pattern accuracy through multi-phase testing, and execute trades with professional risk management.

---

## 🎯 Project Status

**Current Phase**: Phase 0 - Setup & Planning  
**Status**: AI Agent Handoff System Implemented ✅  
**Next Steps**: Begin module implementation

---

## 📋 Overview

StructureScout operates during US market hours (9:30-11:30 AM EST) to:

1. **Capture** - Take screenshots of NAS100 5-minute charts with reference levels
2. **Analyze** - Send charts to GPT-4o-mini Vision API for pattern recognition
3. **Identify** - Detect structure-based setups (breakouts, structure breaks, mean reversion)
4. **Validate** - Progress through 4-phase validation system before live trading
5. **Execute** - Place trades via MetaTrader5 API (after validation complete)
6. **Track** - Log all analysis, trades, and outcomes for performance evaluation

---

## 🚀 Key Features

### Intelligent Analysis
- **AI-Powered Pattern Recognition** using GPT-4o-mini Vision API
- **Structure-Based Trading** focusing on price action and key levels
- **Regime Detection** identifies trending vs. ranging markets
- **Confidence Scoring** rates setup quality (high/medium/low)

### Safety First
- **4-Phase Validation System** with manual approval gates
- **News Calendar Integration** avoids trading during high-impact events
- **Risk Management** daily/weekly loss limits, position sizing
- **Weekend/Holiday Detection** automatic market hours handling

### Professional Execution
- **MetaTrader5 Integration** for chart access and trade execution
- **Multi-Mode Operation** observation → paper → micro live → full live
- **Telegram Control Interface** remote monitoring and commands
- **Complete Audit Trail** every decision and trade logged

### Performance Tracking
- **Milestone Validation** criteria-based phase advancement
- **Setup Type Analysis** track which patterns perform best
- **Win Rate & R-Multiples** professional performance metrics
- **Strategy Evolution** detect performance changes over time

---

## 🔧 Technology Stack

- **Python 3.9+** - Core application language
- **MetaTrader5** - Trading platform integration
- **OpenAI API** - GPT-4o-mini Vision for chart analysis
- **python-telegram-bot** - Notification and control interface
- **pandas** - Data manipulation and CSV logging
- **APScheduler** - Task scheduling during trading hours
- **Pillow (PIL)** - Image processing and optimization
- **pytz** - Timezone handling (EST/EDT)
- **python-dotenv** - Environment variable management
- **PyYAML** - Configuration file management

---

## 📁 Project Structure

```
StructureScout/
├── main.py                          # Main execution script
├── update_context.py                # Context updater for AI agents
├── config.yaml                      # System configuration
├── .env                            # API keys (gitignored)
├── requirements.txt                 # Python dependencies
│
├── modules/                         # Core modules
│   ├── mt5_connection.py           # MT5 API integration
│   ├── gpt_analysis.py             # GPT-4o-mini analysis
│   ├── telegram_bot.py             # Telegram interface
│   ├── data_logger.py              # CSV logging
│   ├── scheduler.py                # Task scheduling
│   ├── performance_analyzer.py     # Performance tracking
│   ├── error_handler.py            # Error management
│   ├── health_monitor.py           # System health checks
│   ├── risk_manager.py             # Position sizing & limits
│   ├── trade_executor.py           # Trade execution
│   ├── news_calendar.py            # News avoidance
│   └── state_manager.py            # State persistence
│
├── data/                            # Data files (generated)
│   ├── trading_log.csv             # Analysis log
│   ├── trade_execution.csv         # Execution log
│   ├── error.log                   # Error log
│   ├── system.log                  # System events
│   └── daily_summaries/            # Daily reports
│
├── screenshots/                     # Chart screenshots
│   └── YYYY-MM-DD/                 # Daily folders
│
├── docs/                            # Documentation
│   ├── AI_AGENT_CONTEXT.md         # Project context
│   ├── NEW_AGENT_START_HERE.md     # Quick start guide
│   ├── CONVERSATION_SUMMARY.md     # Decision history
│   └── project_state.json          # Current state
│
└── StructureScout.txt              # Technical specification
```

---

## 🎓 4-Phase Validation System

### Phase 1: Observation (4 weeks)
- **Goal**: Validate setup frequency and quality
- **Actions**: Screenshot + analyze (no trading)
- **Target**: 3-8 quality setups per week
- **Criteria**: Average confidence >60%

### Phase 2: Paper Trading (2 weeks)
- **Goal**: Validate AI prediction accuracy
- **Actions**: Track how setups perform (simulated)
- **Target**: 70% setup accuracy
- **Criteria**: Setups behave as AI predicted

### Phase 3: Micro Live (4 weeks)
- **Goal**: Validate execution quality
- **Actions**: Trade with 2 micro contracts only
- **Target**: 45% win rate, <10% drawdown
- **Criteria**: Acceptable slippage (<3 ticks)

### Phase 4: Full Live
- **Goal**: Profitable automated trading
- **Actions**: Full 1% risk per trade
- **Target**: 50% win rate, 1.5 avg R-multiple
- **Criteria**: <15% max drawdown

---

## 🤖 AI Agent Handoff System

This project includes a **Universal AI Agent Handoff System** that enables seamless continuation when conversation limits are reached.

### Context Files

1. **NEW_AGENT_START_HERE.md** - Quick-start guide (30-second read)
2. **AI_AGENT_CONTEXT.md** - Full project context (5-minute read)
3. **project_state.json** - Machine-readable state data
4. **CONVERSATION_SUMMARY.md** - Historical decisions log

### Usage

When approaching conversation limits:

```bash
# Update all context files
python update_context.py

# Check context system health
python update_context.py --check-only

# Tell new agent: "Read NEW_AGENT_START_HERE.md to continue"
```

New AI agents can understand the complete project state in < 5 minutes with zero context loss.

---

## ⚙️ Configuration

### Required API Keys (in `.env`)

```env
# MetaTrader5
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
MT5_PATH=/path/to/mt5

# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### System Configuration (in `config.yaml`)

- Trading hours: 9:30-11:30 AM EST
- Symbol: NAS100 (5-minute charts)
- Risk per trade: 1% of account
- Daily loss limit: 3%
- Weekly loss limit: 6%
- Max trades per day: 3

---

## 📊 Daily Workflow

### Automated Schedule

```
09:25 AM EST  → Pre-market initialization
09:30 AM      → First chart scan
09:45 AM      → Second scan
10:00 AM      → Third scan
10:15 AM      → Fourth scan
10:30 AM      → Fifth scan
11:00 AM      → Sixth scan
11:30 AM      → Final scan
12:00 PM      → Daily summary
```

### Telegram Commands

```
/status       → Current mode, P&L, positions
/mode         → Milestone progress
/advance      → Advance to next phase (if criteria met)
/pause        → Pause bot
/resume       → Resume operation
/limits       → Daily/weekly P&L vs limits
/calendar     → This week's news blackout periods
/force_close  → Close all positions (emergency)
/performance  → Performance statistics
```

---

## 💰 Cost Estimation

- **OpenAI API**: 35 scans/week × $0.00015 = ~$0.27/month
- **Telegram API**: Free
- **MetaTrader5 API**: Free

**Total**: < $1/month (essentially free)

---

## 🛡️ Risk Management

### Position Sizing
- Observation/Paper: 0 contracts
- Micro Live: 2 contracts (fixed)
- Full Live: 1% account risk per trade

### Safety Limits
- Daily loss limit: 3% → halt trading
- Weekly loss limit: 6% → halt trading
- Max 3 trades per day
- Max 12 trades per week

### News Avoidance
- Avoid trading 15 min before high-impact news
- Avoid trading 30 min after high-impact news
- Automatic economic calendar integration

---

## 📈 Performance Metrics

### Tracked Metrics
- Win rate (target: ≥50%)
- Average R-multiple (target: ≥1.5)
- Profit factor (target: >1.3)
- Max drawdown (limit: <15%)
- Slippage (target: <3 ticks)
- Setup frequency (target: 3-8/week)
- Setup accuracy (target: 70%+)

### Analysis Tools
- Setup type performance comparison
- Regime-based performance analysis
- Weekly/monthly performance reports
- Strategy decay detection
- Milestone validation tracking

---

## 🚧 Implementation Status

### ✅ Completed
- Complete technical specification (18 components)
- AI Agent Handoff System (4 context files + update script)
- Project structure design
- Risk management framework
- Milestone progression system

### 🔄 In Progress
- Project directory structure
- Configuration templates
- Module implementation

### 📅 Planned
- Phase 0: Setup (Weeks 1-2)
- Phase 1: Observation (Weeks 3-6)
- Phase 2: Paper Trading (Weeks 7-8)
- Phase 3: Micro Live (Weeks 9-12)
- Phase 4: Full Live (Week 13+)

---

## 📖 Documentation

### For Users
- `README.md` - This file
- `config.yaml` - Configuration reference
- Daily Telegram summaries
- Weekly performance reports

### For Developers
- `StructureScout.txt` - Complete technical specification
- Module docstrings - Detailed function documentation
- `docs/strategy_reference.md` - Trading strategy details
- `docs/api_documentation.md` - API usage guide

### For AI Agents
- `NEW_AGENT_START_HERE.md` - Quick orientation
- `AI_AGENT_CONTEXT.md` - Full project context
- `project_state.json` - Current state data
- `CONVERSATION_SUMMARY.md` - Decision history

---

## 🔒 Security Notes

- **Never commit `.env`** - API keys must stay private
- **Never commit trading logs** - Contains account data
- **Use `.gitignore`** - Exclude sensitive files
- **Secure Telegram bot** - Only respond to authorized user ID

---

## 🎯 Success Criteria

### Phase 1 Success
- 12+ setups identified over 4 weeks
- Average confidence score >60%
- Consistent appearance (not clustered)

### Phase 2 Success
- 70%+ of setups behave as AI predicted
- Clear pattern performance differentiation

### Phase 3 Success
- 45%+ win rate with real executions
- <10% maximum drawdown
- <3 ticks average slippage

### Phase 4 Success
- 50%+ win rate
- 1.5+ average R-multiple
- 1.3+ profit factor
- <15% maximum drawdown
- Sustainable over 30+ trades

---

## 📞 Support & Contact

- **Issues**: Document in CONVERSATION_SUMMARY.md
- **Improvements**: Track in project_state.json
- **Questions**: Telegram command interface
- **Analysis**: Export via cursor_analysis_export.json

---

## 📜 License

Private project - Not for public distribution

---

## 🙏 Acknowledgments

- Built with Claude Sonnet 4.5 (Cursor IDE)
- OpenAI GPT-4o-mini Vision API for pattern analysis
- MetaTrader5 platform for trading integration
- Python community for excellent libraries

---

**Last Updated**: 2026-01-10  
**Version**: 0.1.0  
**Status**: Planning Phase → Implementation Starting  
**Next Milestone**: Complete Phase 0 Setup

---

## 🚀 Quick Start (Once Implemented)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your credentials

# Test components
python -m modules.mt5_connection --test
python -m modules.gpt_analysis --test
python -m modules.telegram_bot --test

# Update context before agent handoff
python update_context.py

# Start the bot (observation mode)
python main.py
```

---

**For AI Agents Taking Over**: Start by reading `NEW_AGENT_START_HERE.md` 🤖
