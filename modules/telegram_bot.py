"""
Telegram Bot Module

Handles Telegram notifications and command interface.
Sends alerts for trading setups, daily summaries, and receives user commands.

Python code contains NO emojis/unicode.
Telegram MESSAGES (output) CAN contain emojis for user-friendly notifications.
"""

import logging
from typing import Optional, Dict, Any
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# Set up logging
logger = logging.getLogger(__name__)


class TelegramBotError(Exception):
    """Custom exception for Telegram bot errors."""
    pass


class TelegramNotifier:
    """
    Telegram notification manager.
    
    Handles sending messages, photos, and formatted alerts to Telegram.
    Also handles interactive commands from users.
    """
    
    def __init__(self, bot_token: str, chat_id: str, bot_instance=None):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token from BotFather
            chat_id: Telegram chat ID to send messages to
            bot_instance: Reference to main bot instance for commands
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.application = None
        self.initialized = False
        self.bot_instance = bot_instance
    
    async def initialize(self, enable_commands: bool = True) -> bool:
        """
        Initialize bot connection and verify credentials.
        
        Args:
            enable_commands: Enable command handlers
        
        Returns:
            True if initialization successful
            
        Raises:
            TelegramBotError: If initialization fails
        """
        try:
            # Test bot connection
            bot_info = await self.bot.get_me()
            logger.info(f"Telegram bot initialized: @{bot_info.username}")
            
            # Set up command handlers if enabled
            if enable_commands:
                self.application = Application.builder().token(self.bot_token).build()
                
                # Register command handlers
                self.application.add_handler(CommandHandler("start", self._cmd_start))
                self.application.add_handler(CommandHandler("status", self._cmd_status))
                self.application.add_handler(CommandHandler("balance", self._cmd_balance))
                self.application.add_handler(CommandHandler("today", self._cmd_today))
                self.application.add_handler(CommandHandler("stop", self._cmd_stop))
                self.application.add_handler(CommandHandler("resume", self._cmd_resume))
                self.application.add_handler(CommandHandler("help", self._cmd_help))
                
                # Start polling in background
                await self.application.initialize()
                await self.application.start()
                await self.application.updater.start_polling()
                
                logger.info("Telegram command handlers registered and polling started")
            
            self.initialized = True
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize Telegram bot: {e}"
            logger.error(error_msg)
            raise TelegramBotError(error_msg)
    
    async def send_message(
        self,
        message: str,
        parse_mode: str = "Markdown",
        disable_notification: bool = False
    ) -> bool:
        """
        Send text message to Telegram.
        
        Args:
            message: Message text (can contain emojis)
            parse_mode: Parse mode (Markdown, HTML, or None)
            disable_notification: Send silently
            
        Returns:
            True if sent successfully
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_notification=disable_notification
            )
            logger.info("Telegram message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_photo(
        self,
        photo_path: str,
        caption: Optional[str] = None,
        parse_mode: str = "Markdown"
    ) -> bool:
        """
        Send photo with optional caption to Telegram.
        
        Args:
            photo_path: Path to photo file
            caption: Photo caption (can contain emojis)
            parse_mode: Parse mode for caption
            
        Returns:
            True if sent successfully
        """
        try:
            with open(photo_path, 'rb') as photo:
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=caption,
                    parse_mode=parse_mode
                )
            logger.info(f"Telegram photo sent: {photo_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram photo: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown Telegram bot and stop polling."""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot shutdown complete")
    
    # Command Handlers
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        message = """
🚀 *StructureScout Trading Bot* 🚀

Welcome! I'm your automated NAS100 trading assistant.

*Available Commands:*
/status - Check bot status
/balance - View account balance
/today - Today's trading summary
/stop - Pause trading
/resume - Resume trading
/help - Show this help message

📊 I'll send you alerts for high-quality trading setups during market hours (9:30-11:30 AM EST).

Good luck trading! 📈
"""
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"User {update.effective_user.id} sent /start command")
    
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command."""
        if not self.bot_instance:
            await update.message.reply_text("❌ Bot instance not available")
            return
        
        try:
            status = self.bot_instance.get_status()
            message = f"""
📊 *StructureScout Status* 📊

🔌 *Connections:*
• MT5: {status.get('mt5_connected', '❌')}
• OpenAI: {status.get('openai_available', '❌')}
• Telegram: ✅ Connected

⚙️ *System:*
• Mode: {status.get('mode', 'Unknown')}
• Trading: {status.get('trading_active', '❌')}
• Symbol: {status.get('symbol', 'N/A')}

📈 *Today:*
• Scans: {status.get('scans_today', 0)}
• Valid Setups: {status.get('setups_today', 0)}
• Trades: {status.get('trades_today', 0)}

⏰ *Next Scan:* {status.get('next_scan', 'N/A')}
"""
            await update.message.reply_text(message, parse_mode="Markdown")
            logger.info(f"User {update.effective_user.id} requested status")
            
        except Exception as e:
            logger.error(f"Error in /status command: {e}")
            await update.message.reply_text(f"❌ Error getting status: {e}")
    
    async def _cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /balance command."""
        if not self.bot_instance:
            await update.message.reply_text("❌ Bot instance not available")
            return
        
        try:
            balance_info = self.bot_instance.get_balance()
            message = f"""
💰 *Account Balance* 💰

💵 *Balance:* ${balance_info.get('balance', 0):.2f}
📊 *Equity:* ${balance_info.get('equity', 0):.2f}
📈 *Profit:* ${balance_info.get('profit', 0):.2f}

💼 *Margin:*
• Used: ${balance_info.get('margin', 0):.2f}
• Free: ${balance_info.get('margin_free', 0):.2f}
• Level: {balance_info.get('margin_level', 0):.2f}%

📊 *Risk Status:*
• Daily P&L: ${balance_info.get('daily_pnl', 0):.2f}
• Daily Limit: ${balance_info.get('daily_limit', 0):.2f}
• Remaining: ${balance_info.get('daily_remaining', 0):.2f}
"""
            await update.message.reply_text(message, parse_mode="Markdown")
            logger.info(f"User {update.effective_user.id} requested balance")
            
        except Exception as e:
            logger.error(f"Error in /balance command: {e}")
            await update.message.reply_text(f"❌ Error getting balance: {e}")
    
    async def _cmd_today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /today command."""
        if not self.bot_instance:
            await update.message.reply_text("❌ Bot instance not available")
            return
        
        try:
            summary = self.bot_instance.get_today_summary()
            message = format_daily_summary(summary)
            await update.message.reply_text(message, parse_mode="Markdown")
            logger.info(f"User {update.effective_user.id} requested today's summary")
            
        except Exception as e:
            logger.error(f"Error in /today command: {e}")
            await update.message.reply_text(f"❌ Error getting today's summary: {e}")
    
    async def _cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stop command."""
        if not self.bot_instance:
            await update.message.reply_text("❌ Bot instance not available")
            return
        
        try:
            self.bot_instance.pause_trading()
            message = """
⏸️ *Trading Paused* ⏸️

The bot will stop taking new trades.
Existing positions will be monitored.

Use /resume to restart trading.
"""
            await update.message.reply_text(message, parse_mode="Markdown")
            logger.info(f"User {update.effective_user.id} paused trading")
            
        except Exception as e:
            logger.error(f"Error in /stop command: {e}")
            await update.message.reply_text(f"❌ Error pausing trading: {e}")
    
    async def _cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /resume command."""
        if not self.bot_instance:
            await update.message.reply_text("❌ Bot instance not available")
            return
        
        try:
            self.bot_instance.resume_trading()
            message = """
▶️ *Trading Resumed* ▶️

The bot is now actively monitoring for setups.
Trades will be executed according to your risk parameters.

Use /stop to pause trading.
"""
            await update.message.reply_text(message, parse_mode="Markdown")
            logger.info(f"User {update.effective_user.id} resumed trading")
            
        except Exception as e:
            logger.error(f"Error in /resume command: {e}")
            await update.message.reply_text(f"❌ Error resuming trading: {e}")
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        message = """
📚 *StructureScout Commands* 📚

*Status & Information:*
/status - Bot status and connections
/balance - Account balance and risk
/today - Today's trading summary

*Control:*
/stop - Pause trading
/resume - Resume trading
/help - Show this help

*Automatic Notifications:*
• 🚨 High-quality setup alerts
• 📊 Daily summaries (12:00 PM EST)
• ⚠️ Error and system alerts

*Trading Hours:*
9:30 AM - 11:30 AM EST (Mon-Fri)

*Need help?* Contact your administrator.
"""
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"User {update.effective_user.id} requested help")


def format_setup_alert(setup_data: Dict[str, Any], alert_type: str = "high") -> str:
    """
    Format trading setup as Telegram alert message.
    
    Args:
        setup_data: Parsed setup data from GPT analysis
        alert_type: Alert type (high, medium, low)
        
    Returns:
        Formatted message string with emojis for user readability
    """
    if alert_type == "high":
        # High-quality setup alert with full details
        message = f"""
*NAS100 HIGH-QUALITY SETUP DETECTED*

*Setup:* {setup_data.get('setup_type', 'N/A')} | *Direction:* {setup_data.get('setup_direction', 'N/A').upper()}
*Time:* {setup_data.get('timestamp', 'N/A')} EST
*Current Price:* {setup_data.get('current_price', 0):.2f}

*Entry:* {setup_data.get('entry_price', 0):.2f}
*Stop Loss:* {setup_data.get('stop_loss_price', 0):.2f} ({setup_data.get('stop_distance_ticks', 0)} ticks)
*Target 1:* {setup_data.get('take_profit_1', 0):.2f}
*Target 2:* {setup_data.get('take_profit_2', 0):.2f}

*Risk:Reward:* 1:{setup_data.get('reward_risk_ratio', 0):.2f}
*Position Size:* {setup_data.get('position_size', 0)} micro contracts
*Risk Amount:* ${setup_data.get('dollar_risk', 0):.2f} (1%)
*Potential Profit (TP1):* ${setup_data.get('dollar_target_1', 0):.2f}

*AI Analysis:* {setup_data.get('analysis_notes', 'N/A')}

*Market Regime:* {setup_data.get('market_regime', 'N/A')}
*Confidence:* {setup_data.get('confidence_score', 0)}%
"""
        # Add caution flags if any
        caution = setup_data.get('caution_flags', [])
        if caution:
            message += f"\n*Caution:* {', '.join(caution)}\n"
        
        return message
    
    elif alert_type == "medium":
        # Medium-quality setup alert (shorter)
        message = f"""
*NAS100 POTENTIAL SETUP (Medium Confidence)*

*{setup_data.get('setup_type', 'N/A')}* | *{setup_data.get('setup_direction', 'N/A').upper()}*
*Entry:* {setup_data.get('entry_price', 0):.2f} | *Stop:* {setup_data.get('stop_loss_price', 0):.2f}
*R:R:* 1:{setup_data.get('reward_risk_ratio', 0):.2f}

*Wait for confirmation before entry*
*Confidence:* {setup_data.get('confidence_score', 0)}%
"""
        return message
    
    else:
        # Low quality or no setup
        return f"*No high-quality setup at {setup_data.get('timestamp', 'N/A')} EST*"


def format_daily_summary(summary_data: Dict[str, Any]) -> str:
    """
    Format daily trading summary as Telegram message.
    
    Args:
        summary_data: Daily statistics and summary
        
    Returns:
        Formatted summary message with emojis
    """
    message = f"""
*NAS100 DAILY ANALYSIS SUMMARY*
*Date:* {summary_data.get('date', 'N/A')}

*Total Scans:* {summary_data.get('scan_count', 0)}
*Valid Setups:* {summary_data.get('valid_setup_count', 0)}
*High-Quality:* {summary_data.get('high_quality_count', 0)}
*Trending:* {summary_data.get('trending_count', 0)} | *Ranging:* {summary_data.get('ranging_count', 0)}

*Setup Breakdown:*
• Opening Range Breakouts: {summary_data.get('or_count', 0)}
• Structure Breaks: {summary_data.get('structure_count', 0)}
• Mean Reversions: {summary_data.get('mr_count', 0)}

*Avg Confidence:* {summary_data.get('avg_confidence', 0):.1f}%
*Avg R:R:* 1:{summary_data.get('avg_rr', 0):.2f}
"""
    
    # Add trading results if any
    if summary_data.get('trades_executed', 0) > 0:
        message += f"""
*Trades Executed Today:* {summary_data.get('trades_executed', 0)}
*P&L:* ${summary_data.get('daily_pnl', 0):.2f} ({summary_data.get('daily_r_multiple', 0):.2f}R)
"""
    
    return message


def format_weekly_report(report_data: Dict[str, Any]) -> str:
    """
    Format weekly performance report as Telegram message.
    
    Args:
        report_data: Weekly statistics and performance
        
    Returns:
        Formatted report message with emojis
    """
    message = f"""
*WEEKLY NAS100 STRATEGY REPORT*
*Week of {report_data.get('start_date', 'N/A')} to {report_data.get('end_date', 'N/A')}*

*SETUP STATISTICS:*
• Total Valid Setups: {report_data.get('total_setups', 0)}
• High-Quality Setups: {report_data.get('hq_setups', 0)}
• Setups Per Day: {report_data.get('setups_per_day', 0):.1f}

*SETUP TYPE DISTRIBUTION:*
• Breakouts: {report_data.get('breakout_pct', 0):.1f}%
• Structure Breaks: {report_data.get('structure_pct', 0):.1f}%
• Mean Reversions: {report_data.get('mr_pct', 0):.1f}%

*MARKET REGIME:*
• Trending: {report_data.get('trending_pct', 0):.1f}%
• Ranging: {report_data.get('ranging_pct', 0):.1f}%
"""
    
    # Add trading performance if trades were executed
    if report_data.get('trade_count', 0) > 0:
        message += f"""
*TRADING PERFORMANCE:*
• Trades Taken: {report_data.get('trade_count', 0)}
• Win Rate: {report_data.get('win_rate', 0):.1f}%
• Avg R-Multiple: {report_data.get('avg_r', 0):.2f}R
• Profit Factor: {report_data.get('pf', 0):.2f}
• Total P&L: ${report_data.get('weekly_pnl', 0):.2f}

*Best Setup Type:* {report_data.get('best_type', 'N/A')} ({report_data.get('best_wr', 0):.1f}% WR)
*Most Frequent:* {report_data.get('frequent_type', 'N/A')}
"""
    
    # Add milestone progress
    message += f"""
*MILESTONE PROGRESS:*
• Trade Frequency Target Met: {report_data.get('frequency_met', 'N/A')}
• Setup Quality Consistent: {report_data.get('quality_consistent', 'N/A')}
• Next Milestone: {report_data.get('next_step', 'N/A')}
"""
    
    return message


def format_error_notification(error_msg: str, severity: str) -> str:
    """
    Format error notification for Telegram.
    
    Args:
        error_msg: Error message
        severity: Error severity (critical, high, medium, low)
        
    Returns:
        Formatted error message
    """
    severity_icons = {
        'critical': 'CRITICAL ERROR',
        'high': 'HIGH PRIORITY ERROR',
        'medium': 'ERROR',
        'low': 'WARNING'
    }
    
    icon = severity_icons.get(severity, 'ERROR')
    
    return f"""
*{icon}*

*Message:* {error_msg}
*Severity:* {severity.upper()}
*Time:* {asyncio.get_event_loop().time()}

Please review system logs for details.
"""


def format_system_status(status_data: Dict[str, Any]) -> str:
    """
    Format system status message.
    
    Args:
        status_data: System status information
        
    Returns:
        Formatted status message
    """
    return f"""
*SYSTEM STATUS*

*Mode:* {status_data.get('current_mode', 'N/A')}
*Status:* {status_data.get('status', 'N/A')}
*Open Positions:* {status_data.get('open_positions', 0)}

*Daily P&L:* ${status_data.get('daily_pnl', 0):.2f}
*Weekly P&L:* ${status_data.get('weekly_pnl', 0):.2f}
*Trades Today:* {status_data.get('trades_today', 0)}

*Connections:*
• MT5: {status_data.get('mt5_status', 'Unknown')}
• OpenAI: {status_data.get('openai_status', 'Unknown')}
• Telegram: {status_data.get('telegram_status', 'Unknown')}

*Last Scan:* {status_data.get('last_scan', 'N/A')}
"""


# Synchronous wrapper functions for easier use
def send_message_sync(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Send Telegram message (synchronous wrapper).
    
    Args:
        bot_token: Bot token
        chat_id: Chat ID
        message: Message text
        
    Returns:
        True if successful
    """
    notifier = TelegramNotifier(bot_token, chat_id)
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(notifier.initialize())
        result = loop.run_until_complete(notifier.send_message(message))
        return result
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False


def send_photo_sync(bot_token: str, chat_id: str, photo_path: str, caption: str = None) -> bool:
    """
    Send Telegram photo (synchronous wrapper).
    
    Args:
        bot_token: Bot token
        chat_id: Chat ID
        photo_path: Path to photo
        caption: Photo caption
        
    Returns:
        True if successful
    """
    notifier = TelegramNotifier(bot_token, chat_id)
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(notifier.initialize())
        result = loop.run_until_complete(notifier.send_photo(photo_path, caption))
        return result
    except Exception as e:
        logger.error(f"Failed to send photo: {e}")
        return False


# Command-line testing interface
if __name__ == "__main__":
    import sys
    from config import get_config
    
    if "--test" in sys.argv:
        print("Testing Telegram Bot Module...")
        print("-" * 50)
        
        # Load configuration
        try:
            config = get_config()
            print(f"[OK] Configuration loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load configuration: {e}")
            sys.exit(1)
        
        # Test message formatting
        print("Testing message formatting...")
        
        sample_setup = {
            'timestamp': '2026-01-10 10:30',
            'setup_type': 'structure_break',
            'setup_direction': 'long',
            'current_price': 21250.0,
            'entry_price': 21255.0,
            'stop_loss_price': 21240.0,
            'stop_distance_ticks': 15,
            'take_profit_1': 21285.0,
            'take_profit_2': 21310.0,
            'reward_risk_ratio': 2.0,
            'position_size': 10,
            'dollar_risk': 50.0,
            'dollar_target_1': 100.0,
            'analysis_notes': 'Clean structure break',
            'market_regime': 'trending_up',
            'confidence_score': 78,
            'caution_flags': []
        }
        
        message = format_setup_alert(sample_setup, 'high')
        print(f"[OK] High-quality alert formatted ({len(message)} chars)")
        
        # Test Telegram connection (if credentials available)
        print("\nTesting Telegram connection...")
        if config.telegram_bot_token and config.telegram_chat_id:
            try:
                result = send_message_sync(
                    bot_token=config.telegram_bot_token,
                    chat_id=config.telegram_chat_id,
                    message="Test message from StructureScout"
                )
                if result:
                    print("[OK] Test message sent successfully")
                else:
                    print("[WARN] Failed to send test message")
            except Exception as e:
                print(f"[ERROR] Telegram test failed: {e}")
        else:
            print("[SKIP] Telegram credentials not configured")
        
        print("-" * 50)
        print("[SUCCESS] Message formatting tests passed!")
        
    else:
        print("Usage: python3 -m modules.telegram_bot --test")
