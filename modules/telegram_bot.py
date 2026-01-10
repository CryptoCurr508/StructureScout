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
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token from BotFather
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize bot connection and verify credentials.
        
        Returns:
            True if initialization successful
            
        Raises:
            TelegramBotError: If initialization fails
        """
        try:
            # Test bot connection
            bot_info = await self.bot.get_me()
            logger.info(f"Telegram bot initialized: @{bot_info.username}")
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
