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
from typing import Optional
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration
from config import get_config

# Import modules
from modules.mt5_connection import MT5Connection, get_previous_day_levels
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
            
            # Initialize Telegram
            logger.info("Initializing Telegram bot...")
            self.telegram = TelegramNotifier(
                bot_token=self.config.telegram_bot_token,
                chat_id=self.config.telegram_chat_id
            )
            import asyncio
            asyncio.run(self.telegram.initialize())
            
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
        
        # Disconnect MT5
        if self.mt5_connection:
            self.mt5_connection.disconnect()
        
        # Save final state
        if self.state_manager:
            self.state_manager.save()
        
        logger.info("StructureScout Bot stopped")
    
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
