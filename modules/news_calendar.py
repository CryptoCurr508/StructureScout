"""
News Calendar Module

Fetches economic calendar data and identifies news blackout periods.
Prevents trading during high-impact news events that cause erratic price behavior.

No emojis or unicode characters in this file.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import pytz

# Set up logging
logger = logging.getLogger(__name__)


class NewsCalendarError(Exception):
    """Custom exception for news calendar errors."""
    pass


# High-impact news events that affect NAS100
HIGH_IMPACT_EVENTS = [
    'FOMC',
    'Federal Reserve',
    'Non-Farm Payrolls',
    'NFP',
    'CPI',
    'Inflation',
    'GDP',
    'Fed Chair',
    'Interest Rate',
    'Unemployment',
    'Retail Sales',
    'ISM Manufacturing',
    'ISM Services'
]


def fetch_daily_economic_calendar(date: datetime, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch economic calendar for specified date.
    
    Args:
        date: Date to fetch calendar for
        api_key: API key for paid service (optional)
        
    Returns:
        List of economic events
        
    Note:
        This is a placeholder implementation. In production, integrate with:
        - ForexFactory scraper
        - TradingEconomics API
        - Investing.com API
        - Or other calendar service
    """
    logger.info(f"Fetching economic calendar for {date.strftime('%Y-%m-%d')}")
    
    # Placeholder: Return empty list
    # In production, implement actual API call or web scraping
    events = []
    
    # Example hardcoded events for testing
    # In production, replace with real data source
    if date.weekday() == 4:  # Friday - NFP day (first Friday of month)
        if date.day <= 7:  # First week of month
            events.append({
                'time': '08:30',
                'title': 'Non-Farm Payrolls',
                'impact': 'high',
                'currency': 'USD'
            })
    
    logger.info(f"Found {len(events)} economic events")
    return events


def classify_event_impact(event: Dict[str, Any]) -> str:
    """
    Classify event impact level.
    
    Args:
        event: Event dictionary with title and details
        
    Returns:
        Impact level: high, medium, or low
    """
    title = event.get('title', '').lower()
    
    # Check if title contains high-impact keywords
    for keyword in HIGH_IMPACT_EVENTS:
        if keyword.lower() in title:
            return 'high'
    
    # Use provided impact if available
    provided_impact = event.get('impact', '').lower()
    if provided_impact in ['high', 'medium', 'low']:
        return provided_impact
    
    return 'low'


def identify_news_blackout_periods(
    events: List[Dict[str, Any]],
    before_minutes: int = 15,
    after_minutes: int = 30,
    timezone_str: str = "America/New_York"
) -> List[Tuple[datetime, datetime]]:
    """
    Identify time periods to avoid trading around news events.
    
    Args:
        events: List of economic events
        before_minutes: Minutes before event to start blackout
        after_minutes: Minutes after event to end blackout
        timezone_str: Timezone string
        
    Returns:
        List of (start, end) datetime tuples for blackout periods
    """
    blackout_periods = []
    tz = pytz.timezone(timezone_str)
    
    for event in events:
        # Only create blackouts for high-impact events
        impact = classify_event_impact(event)
        if impact != 'high':
            continue
        
        # Parse event time
        event_time_str = event.get('time', '')
        try:
            # Assume time is in HH:MM format
            hour, minute = map(int, event_time_str.split(':'))
            
            # Create datetime for today at event time
            event_dt = datetime.now(tz).replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )
            
            # Calculate blackout window
            blackout_start = event_dt - timedelta(minutes=before_minutes)
            blackout_end = event_dt + timedelta(minutes=after_minutes)
            
            blackout_periods.append((blackout_start, blackout_end))
            
            logger.info(f"Blackout period: {blackout_start.strftime('%H:%M')} - "
                       f"{blackout_end.strftime('%H:%M')} for {event.get('title')}")
            
        except Exception as e:
            logger.warning(f"Failed to parse event time '{event_time_str}': {e}")
            continue
    
    return blackout_periods


def is_trading_allowed_now(
    current_time: datetime,
    blackout_periods: List[Tuple[datetime, datetime]]
) -> Tuple[bool, str]:
    """
    Check if trading is allowed at current time.
    
    Args:
        current_time: Current datetime
        blackout_periods: List of blackout period tuples
        
    Returns:
        Tuple of (is_allowed, reason_if_not)
    """
    for start, end in blackout_periods:
        if start <= current_time <= end:
            event_name = "high-impact news event"
            return False, f"Trading paused: {event_name} at {start.strftime('%H:%M')}"
    
    return True, "No news conflicts"


def get_weekly_news_calendar(
    start_date: datetime,
    timezone_str: str = "America/New_York"
) -> Dict[str, Any]:
    """
    Get economic calendar for entire week.
    
    Args:
        start_date: Start of week
        timezone_str: Timezone string
        
    Returns:
        Dictionary with weekly calendar summary
    """
    tz = pytz.timezone(timezone_str)
    
    # Ensure start_date is timezone-aware
    if start_date.tzinfo is None:
        start_date = tz.localize(start_date)
    
    weekly_events = {}
    blackout_count = 0
    
    # Fetch events for each day of the week
    for day_offset in range(7):
        date = start_date + timedelta(days=day_offset)
        day_name = date.strftime('%A')
        
        events = fetch_daily_economic_calendar(date)
        high_impact = [e for e in events if classify_event_impact(e) == 'high']
        
        if high_impact:
            weekly_events[day_name] = high_impact
            blackout_count += len(high_impact)
        else:
            weekly_events[day_name] = []
    
    return {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'events_by_day': weekly_events,
        'total_blackout_periods': blackout_count,
        'timezone': timezone_str
    }


def format_news_summary(weekly_calendar: Dict[str, Any]) -> str:
    """
    Format weekly news calendar as readable summary.
    
    Args:
        weekly_calendar: Weekly calendar dictionary
        
    Returns:
        Formatted summary string
    """
    summary = f"HIGH-IMPACT NEWS THIS WEEK (Starting {weekly_calendar['start_date']})\n\n"
    
    events_by_day = weekly_calendar['events_by_day']
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        events = events_by_day.get(day, [])
        
        if events:
            summary += f"{day}:\n"
            for event in events:
                time_str = event.get('time', 'N/A')
                title = event.get('title', 'N/A')
                summary += f"  - {title} ({time_str} EST)\n"
        else:
            summary += f"{day}: No high-impact events\n"
    
    summary += f"\nTotal Blackout Periods: {weekly_calendar['total_blackout_periods']}\n"
    
    return summary


class NewsCalendarManager:
    """
    News calendar manager.
    
    Manages economic calendar data and trading restrictions.
    """
    
    def __init__(self, timezone_str: str = "America/New_York"):
        """
        Initialize news calendar manager.
        
        Args:
            timezone_str: Timezone string
        """
        self.timezone_str = timezone_str
        self.tz = pytz.timezone(timezone_str)
        self.blackout_periods = []
        self.last_update = None
    
    def update_calendar(self, date: datetime) -> bool:
        """
        Update calendar for specified date.
        
        Args:
            date: Date to fetch calendar for
            
        Returns:
            True if updated successfully
        """
        try:
            events = fetch_daily_economic_calendar(date)
            self.blackout_periods = identify_news_blackout_periods(events)
            self.last_update = datetime.now(self.tz)
            logger.info(f"Calendar updated: {len(self.blackout_periods)} blackout periods")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update calendar: {e}")
            return False
    
    def is_safe_to_trade(self, check_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Check if safe to trade at given time.
        
        Args:
            check_time: Time to check (default: now)
            
        Returns:
            Tuple of (is_safe, reason)
        """
        if check_time is None:
            check_time = datetime.now(self.tz)
        
        return is_trading_allowed_now(check_time, self.blackout_periods)
    
    def get_next_safe_time(self, current_time: Optional[datetime] = None) -> Optional[datetime]:
        """
        Get next time when trading is safe.
        
        Args:
            current_time: Current time (default: now)
            
        Returns:
            Next safe datetime or None if already safe
        """
        if current_time is None:
            current_time = datetime.now(self.tz)
        
        is_safe, _ = self.is_safe_to_trade(current_time)
        if is_safe:
            return None
        
        # Find when current blackout ends
        for start, end in self.blackout_periods:
            if start <= current_time <= end:
                return end
        
        return current_time  # Fallback


# Command-line testing interface
if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        print("Testing News Calendar Module...")
        print("-" * 50)
        
        # Test event classification
        print("Testing event classification...")
        test_event = {'title': 'Non-Farm Payrolls', 'impact': 'high'}
        impact = classify_event_impact(test_event)
        print(f"  NFP impact: {impact}")
        assert impact == 'high'
        
        # Test blackout period calculation
        print("\nTesting blackout period calculation...")
        events = [
            {'time': '08:30', 'title': 'Non-Farm Payrolls', 'impact': 'high'},
            {'time': '14:00', 'title': 'FOMC Announcement', 'impact': 'high'}
        ]
        
        blackouts = identify_news_blackout_periods(events)
        print(f"  Found {len(blackouts)} blackout periods")
        assert len(blackouts) == 2
        
        # Test trading allowed check
        print("\nTesting trading allowed check...")
        test_time = datetime.now()
        is_allowed, reason = is_trading_allowed_now(test_time, blackouts)
        print(f"  Trading allowed now: {is_allowed}")
        print(f"  Reason: {reason}")
        
        # Test weekly calendar
        print("\nTesting weekly calendar...")
        start_date = datetime.now()
        weekly = get_weekly_news_calendar(start_date)
        summary = format_news_summary(weekly)
        print(f"  Weekly summary generated ({len(summary)} chars)")
        
        # Test manager
        print("\nTesting news calendar manager...")
        manager = NewsCalendarManager()
        result = manager.update_calendar(datetime.now())
        print(f"  Calendar updated: {result}")
        
        is_safe, reason = manager.is_safe_to_trade()
        print(f"  Safe to trade: {is_safe} ({reason})")
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
        print("\nNote: Using placeholder calendar data.")
        print("In production, integrate with ForexFactory or TradingEconomics API.")
        
    else:
        print("Usage: python3 -m modules.news_calendar --test")
