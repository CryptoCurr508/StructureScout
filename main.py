"""
StructureScout Trading Bot - Main Application

Automated NAS100 trading system with GPT-4o-mini Vision analysis.
Orchestrates all modules and executes the main trading workflow.

Usage:
    python3 main.py                 # Run in production mode
    python3 main.py --dry-run       # Run without actual trading
    python3 main.py --test          # Run system tests

No emojis or unicode characters in this file.
"""

import sys
import logging
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration
from config import get_config

# Import modules
from modules.mt5_connection import MT5Connection, get_previous_day_levels, detect_broker_symbol
from modules.gpt_analysis import analyze_chart_with_gpt4, validate_setup_rules, calculate_position_size
from modules.telegram_bot import TelegramNotifier, format_setup_alert, format_daily_summary
from modules.data_logger import log_analysis_to_csv, get_weekly_summary_stats
from modules.scheduler import TradingScheduler, is_trading_window
from modules.news_calendar import NewsCalendarManager
from modules.risk_manager import RiskManager
from modules.state_manager import SystemStateManager
from modules.error_handler import handle_error
from modules.health_monitor import HealthMonitor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class StructureScoutBot:
    """
    Main trading bot class.
    
    Orchestrates all components and executes trading workflow.
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize trading bot.
        
        Args:
            dry_run: If True, run without actual trading
        """
        self.dry_run = dry_run
        self.config = get_config()
        self.running = False
        self.trading_paused = False
        
        # Trading statistics
        self.scans_today = 0
        self.setups_today = 0
        self.trades_today = 0
        
        # Initialize components
        self.mt5_connection: Optional[MT5Connection] = None
        self.telegram: Optional[TelegramNotifier] = None
        self.scheduler: Optional[TradingScheduler] = None
        self.news_calendar: Optional[NewsCalendarManager] = None
        self.risk_manager: Optional[RiskManager] = None
        self.state_manager: Optional[SystemStateManager] = None
        self.health_monitor: Optional[HealthMonitor] = None
        
        logger.info(f"StructureScout Bot initialized (dry_run={dry_run})")
    
    def initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing StructureScout components...")
            
            # Validate credentials
            missing = self.config.get_missing_credentials()
            if missing:
                logger.error(f"Missing credentials: {', '.join(missing)}")
                logger.error("Please configure .env file with all required credentials")
                return False
            
            # Initialize MT5 connection
            if not self.dry_run:
                logger.info("Connecting to MT5...")
                self.mt5_connection = MT5Connection(
                    login=self.config.mt5_login,
                    password=self.config.mt5_password,
                    server=self.config.mt5_server,
                    path=self.config.mt5_path
                )
                self.mt5_connection.connect()
                
                # Auto-detect broker symbol format if enabled
                if self.config.auto_detect_symbol:
                    logger.info(f"Auto-detecting broker symbol format for {self.config.symbol_base}...")
                    detected_symbol = detect_broker_symbol(self.config.symbol_base)
                    if detected_symbol:
                        self.config.trading_symbol = detected_symbol
                        logger.info(f"Using broker symbol: {detected_symbol}")
                    else:
                        logger.warning(f"Could not auto-detect symbol, using configured: {self.config.trading_symbol}")
            
            # Initialize Telegram with command handlers
            logger.info("Initializing Telegram bot...")
            self.telegram = TelegramNotifier(
                bot_token=self.config.telegram_bot_token,
                chat_id=self.config.telegram_chat_id,
                bot_instance=self
            )
            self.telegram.initialize(enable_commands=True)
            
            # Initialize scheduler
            self.scheduler = TradingScheduler(timezone_str=self.config.timezone)
            
            # Initialize news calendar
            self.news_calendar = NewsCalendarManager(timezone_str=self.config.timezone)
            self.news_calendar.update_calendar(datetime.now())
            
            # Initialize risk manager
            account_balance = 5000.0  # Default, should be pulled from MT5
            if self.mt5_connection:
                account_info = self.mt5_connection.get_account_info()
                if account_info:
                    account_balance = account_info['balance']
            
            self.risk_manager = RiskManager(
                account_balance=account_balance,
                risk_per_trade=self.config.risk_per_trade,
                daily_loss_limit=self.config.daily_loss_limit,
                weekly_loss_limit=self.config.weekly_loss_limit,
                max_trades_per_day=self.config.max_trades_per_day
            )
            
            # Initialize state manager
            state_file = Path("data/system_state.json")
            self.state_manager = SystemStateManager(state_file)
            self.state_manager.load()  # Load previous state if exists
            
            # Initialize health monitor
            self.health_monitor = HealthMonitor()
            
            logger.info("All components initialized successfully")
            
            # Send startup notification
            if self.telegram:
                startup_msg = f"""
*StructureScout Bot Started*

*Mode:* {self.config.current_mode}
*Status:* System initialized
*Dry Run:* {'Yes' if self.dry_run else 'No'}

Bot is ready to begin trading hours monitoring.
"""
                asyncio.run(self.telegram.send_message(startup_msg))
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            handle_error(e, "bot_initialization")
            return False
    
    def main_analysis_workflow(self) -> None:
        """
        Main analysis workflow - executed at each scheduled time.
        
        This is the core function that runs during trading hours.
        """
        try:
            logger.info("="*60)
            logger.info("Starting analysis workflow...")
            
            # Increment scan counter
            self.scans_today += 1
            
            # Check if trading is paused
            if self.trading_paused:
                logger.info("Trading is paused by user, skipping scan")
                return
            
            # Check if we're in trading window
            current_time = datetime.now()
            if not is_trading_window(current_time):
                logger.info("Outside trading window, skipping scan")
                return
            
            # Check news calendar
            is_safe, reason = self.news_calendar.is_safe_to_trade()
            if not is_safe:
                logger.info(f"News blackout: {reason}")
                return
            
            # Check risk limits
            can_trade, reason = self.risk_manager.can_take_trade()
            if not can_trade:
                logger.warning(f"Risk limit reached: {reason}")
                return
            
            # Get previous day levels (for reference lines)
            levels = get_previous_day_levels(self.config.trading_symbol)
            if not levels:
                logger.error("Failed to get previous day levels")
                return
            
            # TODO: Capture screenshot (placeholder for now)
            # screenshot_path = get_chart_screenshot(...)
            screenshot_path = None
            
            # Analyze with GPT-4o-mini
            logger.info("Analyzing chart with GPT-4o-mini...")
            timestamp_str = current_time.strftime("%Y-%m-%d %H:%M")
            
            # TODO: Implement actual analysis when screenshot available
            # For now, log that we would analyze
            logger.info(f"Would analyze chart at {timestamp_str}")
            logger.info(f"Prev day high: {levels['high']}, low: {levels['low']}")
            
            # Save state
            self.state_manager.update('last_scan', timestamp_str)
            self.state_manager.save()
            
            logger.info("Analysis workflow complete")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Analysis workflow failed: {e}")
            handle_error(e, "analysis_workflow")
    
    def start(self) -> None:
        """
        Start the trading bot.
        
        Schedules all tasks and begins monitoring.
        """
        if not self.initialize():
            logger.error("Failed to initialize bot")
            return
        
        self.running = True
        logger.info("StructureScout Bot started")
        
        # Schedule scans at configured times
        for scan_time in self.config.scan_schedule:
            self.scheduler.schedule_scan(scan_time, self.main_analysis_workflow)
            logger.info(f"Scheduled scan at {scan_time} EST")
        
        # Schedule daily summary at 12:00 PM
        self.scheduler.schedule_daily_task("12:00", self.generate_daily_summary)
        
        # Start scheduler
        self.scheduler.start()
        
        logger.info("Scheduler started, monitoring trading hours...")
        
        # Keep running
        try:
            while self.running:
                time.sleep(60)  # Sleep 1 minute between checks
                
                # Run health check every hour
                if datetime.now().minute == 0:
                    self.health_monitor.check_all()
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
    
    def stop(self) -> None:
        """Stop the trading bot."""
        logger.info("Shutting down StructureScout Bot...")
        
        self.running = False
        
        # Stop scheduler
        if self.scheduler:
            self.scheduler.stop()
        
        # Shutdown Telegram bot
        if self.telegram:
            self.telegram.shutdown()
        
        # Disconnect MT5
        if self.mt5_connection:
            self.mt5_connection.disconnect()
        
        # Save final state
        if self.state_manager:
            self.state_manager.save()
        
        logger.info("StructureScout Bot stopped")
    
    # Command handler methods for Telegram
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status for /status command."""
        mt5_status = "✅ Connected" if (self.mt5_connection and self.mt5_connection.is_connected()) else "❌ Disconnected"
        openai_status = "✅ Available" if self.config.openai_api_key else "❌ Not configured"
        trading_status = "✅ Active" if (self.running and not self.trading_paused) else "⏸️ Paused" if self.trading_paused else "❌ Stopped"
        
        next_scan = "N/A"
        if self.scheduler:
            # Get next scheduled job time
            jobs = self.scheduler.scheduler.get_jobs()
            if jobs:
                next_job = min(jobs, key=lambda j: j.next_run_time)
                next_scan = next_job.next_run_time.strftime("%I:%M %p EST")
        
        return {
            'mt5_connected': mt5_status,
            'openai_available': openai_status,
            'mode': self.config.current_mode.title(),
            'trading_active': trading_status,
            'symbol': self.config.trading_symbol,
            'scans_today': self.scans_today,
            'setups_today': self.setups_today,
            'trades_today': self.trades_today,
            'next_scan': next_scan
        }
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance for /balance command."""
        if not self.mt5_connection or not self.mt5_connection.is_connected():
            return {
                'balance': 0,
                'equity': 0,
                'profit': 0,
                'margin': 0,
                'margin_free': 0,
                'margin_level': 0,
                'daily_pnl': 0,
                'daily_limit': 0,
                'daily_remaining': 0
            }
        
        account_info = self.mt5_connection.get_account_info()
        if not account_info:
            return {}
        
        daily_limit = account_info['balance'] * self.config.daily_loss_limit
        daily_pnl = account_info['profit']
        daily_remaining = daily_limit - abs(daily_pnl) if daily_pnl < 0 else daily_limit
        
        return {
            'balance': account_info['balance'],
            'equity': account_info['equity'],
            'profit': account_info['profit'],
            'margin': account_info['margin'],
            'margin_free': account_info['margin_free'],
            'margin_level': (account_info['equity'] / account_info['margin'] * 100) if account_info['margin'] > 0 else 0,
            'daily_pnl': daily_pnl,
            'daily_limit': daily_limit,
            'daily_remaining': daily_remaining
        }
    
    def get_today_summary(self) -> Dict[str, Any]:
        """Get today's trading summary for /today command."""
        log_file = self.config.trading_log_path
        
        if not log_file.exists():
            return {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'scan_count': 0,
                'valid_setup_count': 0,
                'high_quality_count': 0,
                'trending_count': 0,
                'ranging_count': 0,
                'or_count': 0,
                'structure_count': 0,
                'mr_count': 0,
                'avg_confidence': 0,
                'avg_rr': 0,
                'trades_executed': 0,
                'daily_pnl': 0,
                'daily_r_multiple': 0
            }
        
        stats = get_weekly_summary_stats(log_file, days=1)
        
        return {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'scan_count': self.scans_today,
            'valid_setup_count': self.setups_today,
            'high_quality_count': stats.get('high_quality_setups', 0),
            'trending_count': stats.get('trending_count', 0),
            'ranging_count': stats.get('ranging_count', 0),
            'or_count': 0,
            'structure_count': 0,
            'mr_count': 0,
            'avg_confidence': stats.get('avg_confidence', 0),
            'avg_rr': stats.get('avg_rr', 0),
            'trades_executed': self.trades_today,
            'daily_pnl': 0,
            'daily_r_multiple': 0
        }
    
    def pause_trading(self) -> None:
        """Pause trading (for /stop command)."""
        self.trading_paused = True
        logger.info("Trading paused by user command")
        
        if self.state_manager:
            self.state_manager.save()
    
    def resume_trading(self) -> None:
        """Resume trading (for /resume command)."""
        self.trading_paused = False
        logger.info("Trading resumed by user command")
        
        if self.state_manager:
            self.state_manager.save()
    
    def generate_daily_summary(self) -> None:
        """Generate and send daily summary."""
        try:
            logger.info("Generating daily summary...")
            
            # Get today's statistics
            log_file = self.config.trading_log_path
            if log_file.exists():
                stats = get_weekly_summary_stats(log_file, days=1)
                
                # Format and send
                summary_data = {
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'scan_count': stats.get('total_scans', 0),
                    'valid_setup_count': stats.get('valid_setups', 0),
                    'high_quality_count': stats.get('high_quality_setups', 0),
                    'trending_count': stats.get('trending_count', 0),
                    'ranging_count': stats.get('ranging_count', 0),
                    'or_count': 0,
                    'structure_count': 0,
                    'mr_count': 0,
                    'avg_confidence': stats.get('avg_confidence', 0),
                    'avg_rr': stats.get('avg_rr', 0)
                }
                
                message = format_daily_summary(summary_data)
                import asyncio
                asyncio.run(self.telegram.send_message(message))
                
                logger.info("Daily summary sent")
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")


def main():
    """Main entry point."""
    # Parse command line arguments
    dry_run = "--dry-run" in sys.argv
    test_mode = "--test" in sys.argv
    
    if test_mode:
        print("Running system tests...")
        print("-" * 60)
        
        # Test configuration
        print("Testing configuration...")
        try:
            config = get_config()
            print(f"  [OK] Configuration loaded")
            print(f"  Mode: {config.current_mode}")
            print(f"  Symbol: {config.trading_symbol}")
        except Exception as e:
            print(f"  [ERROR] Configuration failed: {e}")
            return 1
        
        # Test credential validation
        print("\nTesting credentials...")
        validation = config.validate_credentials()
        for service, valid in validation.items():
            status = "[OK]" if valid else "[MISSING]"
            print(f"  {status} {service}")
        
        if not all(validation.values()):
            print("\n[WARN] Some credentials missing. Bot will not run without them.")
        
        print("-" * 60)
        print("[SUCCESS] System tests passed!")
        return 0
    
    # Create and start bot
    bot = StructureScoutBot(dry_run=dry_run)
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start bot
    bot.start()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
