# Telegram Commands Guide

## Available Commands

The StructureScout bot now supports interactive Telegram commands for monitoring and controlling the trading bot.

### Status & Information Commands

#### `/start`
Welcome message and command list.

**Example:**
```
/start
```

**Response:**
```
🚀 StructureScout Trading Bot 🚀

Welcome! I'm your automated NAS100 trading assistant.

Available Commands:
/status - Check bot status
/balance - View account balance
/today - Today's trading summary
/stop - Pause trading
/resume - Resume trading
/help - Show this help message
```

---

#### `/status`
Check current bot status, connections, and statistics.

**Example:**
```
/status
```

**Response:**
```
📊 StructureScout Status 📊

🔌 Connections:
• MT5: ✅ Connected
• OpenAI: ✅ Available
• Telegram: ✅ Connected

⚙️ System:
• Mode: Observation
• Trading: ✅ Active
• Symbol: #NAS100_Mar

📈 Today:
• Scans: 5
• Valid Setups: 2
• Trades: 1

⏰ Next Scan: 10:30 AM EST
```

---

#### `/balance`
View current account balance and risk metrics.

**Example:**
```
/balance
```

**Response:**
```
💰 Account Balance 💰

💵 Balance: $5,000.00
📊 Equity: $5,125.50
📈 Profit: $125.50

💼 Margin:
• Used: $250.00
• Free: $4,875.50
• Level: 2050.20%

📊 Risk Status:
• Daily P&L: $125.50
• Daily Limit: $150.00
• Remaining: $24.50
```

---

#### `/today`
Get today's trading summary and statistics.

**Example:**
```
/today
```

**Response:**
```
📊 NAS100 DAILY ANALYSIS SUMMARY 📊
📅 Date: 2026-01-11

🔍 Total Scans: 7
✅ Valid Setups: 3
⭐ High-Quality: 2
📈 Trending: 2 | 📉 Ranging: 1

📋 Setup Breakdown:
• Opening Range Breakouts: 1
• Structure Breaks: 1
• Mean Reversions: 1

🎯 Avg Confidence: 78.5%
📊 Avg R:R: 1:2.35
```

---

### Control Commands

#### `/stop`
Pause trading. The bot will stop taking new trades but continue monitoring.

**Example:**
```
/stop
```

**Response:**
```
⏸️ Trading Paused ⏸️

The bot will stop taking new trades.
Existing positions will be monitored.

Use /resume to restart trading.
```

---

#### `/resume`
Resume trading after being paused.

**Example:**
```
/resume
```

**Response:**
```
▶️ Trading Resumed ▶️

The bot is now actively monitoring for setups.
Trades will be executed according to your risk parameters.

Use /stop to pause trading.
```

---

#### `/help`
Show help message with all available commands.

**Example:**
```
/help
```

**Response:**
```
📚 StructureScout Commands 📚

Status & Information:
/status - Bot status and connections
/balance - Account balance and risk
/today - Today's trading summary

Control:
/stop - Pause trading
/resume - Resume trading
/help - Show this help

Automatic Notifications:
• 🚨 High-quality setup alerts
• 📊 Daily summaries (12:00 PM EST)
• ⚠️ Error and system alerts

Trading Hours:
9:30 AM - 11:30 AM EST (Mon-Fri)
```

---

## Automatic Notifications

In addition to commands, the bot sends automatic notifications:

### 🚨 High-Quality Setup Alerts
Sent when a valid trading setup is detected during market hours.

### 📊 Daily Summary
Sent at 12:00 PM EST with the day's trading statistics.

### ⚠️ Error Alerts
Sent when critical errors occur (connection loss, API failures, etc.).

### 🚀 Startup Notification
Sent when the bot starts successfully.

---

## Testing Commands

To test the commands:

1. **Start the bot:**
   ```bash
   python main.py --dry-run
   ```

2. **Open Telegram** and find your bot (@StructureScout_bot)

3. **Send commands:**
   - Type `/start` to begin
   - Try `/status` to check bot status
   - Test `/balance` to view account info
   - Use `/stop` to pause trading
   - Use `/resume` to restart trading

---

## Security Notes

- Only the configured `TELEGRAM_CHAT_ID` can send commands to the bot
- Commands are logged for security auditing
- Sensitive information (passwords, API keys) is never sent via Telegram

---

## Troubleshooting

### Commands not responding?
1. Check that the bot is running
2. Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
3. Check logs: `logs/system.log`

### Bot not receiving commands?
1. Ensure polling is started (check logs for "polling started")
2. Restart the bot
3. Check Telegram API status

---

## Future Commands (Coming Soon)

- `/positions` - View open positions
- `/history` - View trade history
- `/settings` - Adjust bot settings
- `/report` - Generate weekly report
- `/screenshot` - Request current chart screenshot

---

**Need help?** Check the logs or contact your administrator.
