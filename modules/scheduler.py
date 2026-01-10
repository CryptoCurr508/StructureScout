"""
Scheduler Module

Handles task scheduling during trading hours.
Manages market hours detection, trading calendar, and scan scheduling.

No emojis or unicode characters in this file.
"""

import logging
from datetime import datetime, time, timedelta
from typing import Optional, List
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Set up logging
logger = logging.getLogger(__name__)

# US market holidays for 2026
US_MARKET_HOLIDAYS_2026 = [
    "2026-01-01",  # New Year's Day
    "2026-01-19",  # MLK Day
    "2026-02-16",  # Presidents Day
    "2026-04-10",  # Good Friday
    "2026-05-25",  # Memorial Day
    "2026-06-19",  # Juneteenth
    "2026-07-03",  # Independence Day (observed)
    "2026-09-07",  # Labor Day
    "2026-11-26",  # Thanksgiving
    "2026-12-25"   # Christmas
]


def is_market_open(check_time: datetime, timezone_str: str = "America/New_York") -> tuple[bool, str]:
    """
    Check if market is open at given time.
    
    Args:
        check_time: Datetime to check
        timezone_str: Timezone string
        
    Returns:
        Tuple of (is_open, reason_if_closed)
    """
    # Convert to specified timezone
    tz = pytz.timezone(timezone_str)
    if check_time.tzinfo is None:
        check_time = tz.localize(check_time)
    else:
        check_time = check_time.astimezone(tz)
    
    # Check if weekend
    if check_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False, "Weekend (market closed)"
    
    # Check if holiday
    date_str = check_time.strftime("%Y-%m-%d")
    if date_str in US_MARKET_HOLIDAYS_2026:
        return False, f"US market holiday ({date_str})"
    
    # Check if within trading hours (9:30 AM - 4:00 PM EST)
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = check_time.time()
    
    if current_time < market_open:
        return False, f"Before market open (opens at {market_open})"
    if current_time >= market_close:
        return False, f"After market close (closed at {market_close})"
    
    return True, "Market is open"


def is_trading_window(
    check_time: datetime,
    start_time: str = "09:30",
    end_time: str = "11:30",
    timezone_str: str = "America/New_York"
) -> bool:
    """
    Check if current time is within specified trading window.
    
    Args:
        check_time: Datetime to check
        start_time: Start time (HH:MM format)
        end_time: End time (HH:MM format)
        timezone_str: Timezone string
        
    Returns:
        True if within trading window
    """
    # First check if market is open
    is_open, _ = is_market_open(check_time, timezone_str)
    if not is_open:
        return False
    
    # Convert to specified timezone
    tz = pytz.timezone(timezone_str)
    if check_time.tzinfo is None:
        check_time = tz.localize(check_time)
    else:
        check_time = check_time.astimezone(tz)
    
    # Parse start and end times
    start_hour, start_min = map(int, start_time.split(':'))
    end_hour, end_min = map(int, end_time.split(':'))
    
    window_start = time(start_hour, start_min)
    window_end = time(end_hour, end_min)
    current_time = check_time.time()
    
    return window_start <= current_time <= window_end


def calculate_next_trading_session(
    current_time: datetime,
    timezone_str: str = "America/New_York"
) -> datetime:
    """
    Calculate next trading session start time.
    
    Args:
        current_time: Current datetime
        timezone_str: Timezone string
        
    Returns:
        Datetime of next trading session start
    """
    tz = pytz.timezone(timezone_str)
    if current_time.tzinfo is None:
        current_time = tz.localize(current_time)
    
    # Start with next day at 9:30 AM
    next_day = current_time + timedelta(days=1)
    next_session = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
    
    # Keep advancing until we find a trading day
    max_days = 10  # Prevent infinite loop
    for _ in range(max_days):
        is_open, _ = is_market_open(next_session, timezone_str)
        if is_open:
            return next_session
        next_session += timedelta(days=1)
    
    # Fallback to original + 1 day if loop exhausted
    return current_time + timedelta(days=1)


def get_scan_times(timezone_str: str = "America/New_York") -> List[str]:
    """
    Get list of scan times for trading day.
    
    Args:
        timezone_str: Timezone string
        
    Returns:
        List of time strings (HH:MM format)
    """
    # Default scan schedule
    return [
        "09:30",
        "09:45",
        "10:00",
        "10:15",
        "10:30",
        "11:00",
        "11:30"
    ]


class TradingScheduler:
    """
    Trading task scheduler.
    
    Manages scheduled tasks during trading hours.
    """
    
    def __init__(self, timezone_str: str = "America/New_York"):
        """
        Initialize trading scheduler.
        
        Args:
            timezone_str: Timezone for scheduling
        """
        self.timezone_str = timezone_str
        self.tz = pytz.timezone(timezone_str)
        self.scheduler = BackgroundScheduler(timezone=self.tz)
        self.running = False
    
    def start(self) -> None:
        """Start the scheduler."""
        if not self.running:
            self.scheduler.start()
            self.running = True
            logger.info("Trading scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("Trading scheduler stopped")
    
    def schedule_scan(self, scan_time: str, callback_func, args=None) -> str:
        """
        Schedule a market scan at specific time.
        
        Args:
            scan_time: Time to run scan (HH:MM format)
            callback_func: Function to call
            args: Arguments to pass to function
            
        Returns:
            Job ID
        """
        hour, minute = map(int, scan_time.split(':'))
        
        # Schedule on weekdays only
        job = self.scheduler.add_job(
            callback_func,
            trigger=CronTrigger(
                day_of_week='mon-fri',
                hour=hour,
                minute=minute,
                timezone=self.tz
            ),
            args=args or [],
            id=f"scan_{scan_time.replace(':', '')}"
        )
        
        logger.info(f"Scheduled scan at {scan_time} EST")
        return job.id
    
    def schedule_daily_task(self, run_time: str, callback_func, args=None) -> str:
        """
        Schedule a daily task.
        
        Args:
            run_time: Time to run (HH:MM format)
            callback_func: Function to call
            args: Arguments to pass
            
        Returns:
            Job ID
        """
        hour, minute = map(int, run_time.split(':'))
        
        job = self.scheduler.add_job(
            callback_func,
            trigger=CronTrigger(
                day_of_week='mon-fri',
                hour=hour,
                minute=minute,
                timezone=self.tz
            ),
            args=args or [],
            id=f"daily_{run_time.replace(':', '')}"
        )
        
        logger.info(f"Scheduled daily task at {run_time} EST")
        return job.id
    
    def schedule_weekly_task(self, day: str, run_time: str, callback_func, args=None) -> str:
        """
        Schedule a weekly task.
        
        Args:
            day: Day of week (mon, tue, wed, thu, fri, sat, sun)
            run_time: Time to run (HH:MM format)
            callback_func: Function to call
            args: Arguments to pass
            
        Returns:
            Job ID
        """
        hour, minute = map(int, run_time.split(':'))
        
        job = self.scheduler.add_job(
            callback_func,
            trigger=CronTrigger(
                day_of_week=day,
                hour=hour,
                minute=minute,
                timezone=self.tz
            ),
            args=args or [],
            id=f"weekly_{day}_{run_time.replace(':', '')}"
        )
        
        logger.info(f"Scheduled weekly task on {day} at {run_time} EST")
        return job.id
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.
        
        Args:
            job_id: Job ID to remove
            
        Returns:
            True if removed successfully
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def get_jobs(self) -> List[str]:
        """
        Get list of scheduled job IDs.
        
        Returns:
            List of job IDs
        """
        return [job.id for job in self.scheduler.get_jobs()]


# Command-line testing interface
if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        print("Testing Scheduler Module...")
        print("-" * 50)
        
        # Test market hours detection
        print("Testing market hours detection...")
        
        # Test weekday during market hours
        test_time = datetime(2026, 1, 12, 10, 30)  # Monday 10:30 AM
        is_open, reason = is_market_open(test_time)
        print(f"  Monday 10:30 AM: {is_open} ({reason})")
        assert is_open is True
        
        # Test weekend
        test_time = datetime(2026, 1, 10, 10, 30)  # Saturday
        is_open, reason = is_market_open(test_time)
        print(f"  Saturday 10:30 AM: {is_open} ({reason})")
        assert is_open is False
        
        # Test holiday
        test_time = datetime(2026, 1, 1, 10, 30)  # New Year's Day
        is_open, reason = is_market_open(test_time)
        print(f"  New Year's Day: {is_open} ({reason})")
        assert is_open is False
        
        # Test trading window
        print("\nTesting trading window...")
        test_time = datetime(2026, 1, 12, 10, 0)  # Monday 10:00 AM
        in_window = is_trading_window(test_time, "09:30", "11:30")
        print(f"  Monday 10:00 AM (window 9:30-11:30): {in_window}")
        assert in_window is True
        
        # Test next trading session
        print("\nTesting next trading session calculation...")
        test_time = datetime(2026, 1, 10, 15, 0)  # Saturday afternoon
        next_session = calculate_next_trading_session(test_time)
        print(f"  From Saturday: Next session is {next_session.strftime('%A %Y-%m-%d %H:%M')}")
        assert next_session.weekday() < 5  # Should be a weekday
        
        # Test scheduler
        print("\nTesting scheduler...")
        scheduler = TradingScheduler()
        
        def test_callback():
            print("  Test callback executed")
        
        scheduler.start()
        print(f"  [OK] Scheduler started")
        
        # Get scan times
        scan_times = get_scan_times()
        print(f"  [OK] Scan times: {', '.join(scan_times)}")
        
        jobs = scheduler.get_jobs()
        print(f"  [OK] Current jobs: {len(jobs)}")
        
        scheduler.stop()
        print(f"  [OK] Scheduler stopped")
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
        
    else:
        print("Usage: python3 -m modules.scheduler --test")
