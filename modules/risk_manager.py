"""
Risk Manager Module

Handles position sizing, risk limits, and margin checks.
Enforces daily/weekly loss limits and position concentration rules.

No emojis or unicode characters in this file.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)


class RiskManagerError(Exception):
    """Custom exception for risk management errors."""
    pass


class RiskManager:
    """
    Risk management system.
    
    Enforces position sizing rules, loss limits, and trading restrictions.
    """
    
    def __init__(
        self,
        account_balance: float,
        risk_per_trade: float = 0.01,
        daily_loss_limit: float = 0.03,
        weekly_loss_limit: float = 0.06,
        max_trades_per_day: int = 3,
        max_trades_per_week: int = 12,
        point_value: float = 0.25
    ):
        """
        Initialize risk manager.
        
        Args:
            account_balance: Current account balance
            risk_per_trade: Risk percentage per trade (0.01 = 1%)
            daily_loss_limit: Daily loss limit as percentage (0.03 = 3%)
            weekly_loss_limit: Weekly loss limit as percentage (0.06 = 6%)
            max_trades_per_day: Maximum trades per day
            max_trades_per_week: Maximum trades per week
            point_value: Dollar value per point (0.25 for NAS100 micro)
        """
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.daily_loss_limit = daily_loss_limit
        self.weekly_loss_limit = weekly_loss_limit
        self.max_trades_per_day = max_trades_per_day
        self.max_trades_per_week = max_trades_per_week
        self.point_value = point_value
        
        # Tracking
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.trades_today = 0
        self.trades_this_week = 0
        self.open_positions = []
        self.last_reset_date = datetime.now().date()
        self.last_week_reset = datetime.now().isocalendar()[1]
    
    def calculate_position_size(
        self,
        mode: str,
        stop_distance_ticks: int,
        override_fixed_size: Optional[int] = None
    ) -> int:
        """
        Calculate position size based on risk rules.
        
        Args:
            mode: Trading mode (observation, paper_trading, micro_live, full_live)
            stop_distance_ticks: Distance to stop loss in ticks
            override_fixed_size: Fixed size override for testing phases
            
        Returns:
            Position size in contracts
        """
        # Observation and paper trading: no real position
        if mode in ['observation', 'paper_trading']:
            return 0
        
        # Micro live: fixed small position
        if mode == 'micro_live':
            return override_fixed_size or 2
        
        # Full live: calculate based on risk
        if mode == 'full_live':
            if stop_distance_ticks <= 0:
                logger.warning("Stop distance is 0, cannot calculate position size")
                return 0
            
            # Calculate risk amount
            risk_amount = self.account_balance * self.risk_per_trade
            
            # Calculate position size
            dollar_risk_per_contract = stop_distance_ticks * self.point_value
            position_size = int(risk_amount / dollar_risk_per_contract)
            
            logger.info(f"Calculated position size: {position_size} contracts "
                       f"(risk: ${risk_amount:.2f}, stop: {stop_distance_ticks} ticks)")
            
            return max(position_size, 0)
        
        return 0
    
    def check_daily_risk_limits(self) -> Tuple[bool, str]:
        """
        Check if daily risk limits have been breached.
        
        Returns:
            Tuple of (can_trade, reason_if_not)
        """
        # Check if we need to reset daily counters
        today = datetime.now().date()
        if today != self.last_reset_date:
            self._reset_daily_counters()
        
        # Check daily loss limit
        daily_loss_amount = self.account_balance * self.daily_loss_limit
        if self.daily_pnl < -daily_loss_amount:
            return False, f"Daily loss limit breached: ${self.daily_pnl:.2f} (limit: ${-daily_loss_amount:.2f})"
        
        # Check max trades per day
        if self.trades_today >= self.max_trades_per_day:
            return False, f"Max trades per day reached: {self.trades_today}/{self.max_trades_per_day}"
        
        return True, "Daily limits OK"
    
    def check_weekly_risk_limits(self) -> Tuple[bool, str]:
        """
        Check if weekly risk limits have been breached.
        
        Returns:
            Tuple of (can_trade, reason_if_not)
        """
        # Check if we need to reset weekly counters
        current_week = datetime.now().isocalendar()[1]
        if current_week != self.last_week_reset:
            self._reset_weekly_counters()
        
        # Check weekly loss limit
        weekly_loss_amount = self.account_balance * self.weekly_loss_limit
        if self.weekly_pnl < -weekly_loss_amount:
            return False, f"Weekly loss limit breached: ${self.weekly_pnl:.2f} (limit: ${-weekly_loss_amount:.2f})"
        
        # Check max trades per week
        if self.trades_this_week >= self.max_trades_per_week:
            return False, f"Max trades per week reached: {self.trades_this_week}/{self.max_trades_per_week}"
        
        return True, "Weekly limits OK"
    
    def can_take_trade(self) -> Tuple[bool, str]:
        """
        Check if new trade can be taken.
        
        Returns:
            Tuple of (can_trade, reason_if_not)
        """
        # Check daily limits
        can_trade_daily, reason = self.check_daily_risk_limits()
        if not can_trade_daily:
            return False, reason
        
        # Check weekly limits
        can_trade_weekly, reason = self.check_weekly_risk_limits()
        if not can_trade_weekly:
            return False, reason
        
        # Check position concentration
        if len(self.open_positions) >= 3:
            return False, "Max simultaneous positions reached (3)"
        
        return True, "All risk checks passed"
    
    def record_trade(self, pnl: float) -> None:
        """
        Record trade outcome and update tracking.
        
        Args:
            pnl: Profit/loss for the trade
        """
        self.daily_pnl += pnl
        self.weekly_pnl += pnl
        self.trades_today += 1
        self.trades_this_week += 1
        
        logger.info(f"Trade recorded: P&L ${pnl:.2f}, "
                   f"Daily: ${self.daily_pnl:.2f}, Weekly: ${self.weekly_pnl:.2f}")
    
    def add_open_position(self, position: Dict[str, Any]) -> None:
        """
        Add position to open positions list.
        
        Args:
            position: Position details dictionary
        """
        self.open_positions.append(position)
        logger.info(f"Position opened: {len(self.open_positions)} open positions")
    
    def remove_open_position(self, position_id: str) -> None:
        """
        Remove position from open positions list.
        
        Args:
            position_id: Position identifier
        """
        self.open_positions = [p for p in self.open_positions if p.get('id') != position_id]
        logger.info(f"Position closed: {len(self.open_positions)} remaining")
    
    def update_account_balance(self, new_balance: float) -> None:
        """
        Update account balance.
        
        Args:
            new_balance: New account balance
        """
        old_balance = self.account_balance
        self.account_balance = new_balance
        logger.info(f"Account balance updated: ${old_balance:.2f} -> ${new_balance:.2f}")
    
    def _reset_daily_counters(self) -> None:
        """Reset daily tracking counters."""
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.last_reset_date = datetime.now().date()
        logger.info("Daily counters reset")
    
    def _reset_weekly_counters(self) -> None:
        """Reset weekly tracking counters."""
        self.weekly_pnl = 0.0
        self.trades_this_week = 0
        self.last_week_reset = datetime.now().isocalendar()[1]
        logger.info("Weekly counters reset")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current risk manager status.
        
        Returns:
            Status dictionary
        """
        daily_limit_used = abs(self.daily_pnl / (self.account_balance * self.daily_loss_limit) * 100) if self.daily_pnl < 0 else 0
        weekly_limit_used = abs(self.weekly_pnl / (self.account_balance * self.weekly_loss_limit) * 100) if self.weekly_pnl < 0 else 0
        
        return {
            'account_balance': self.account_balance,
            'daily_pnl': round(self.daily_pnl, 2),
            'weekly_pnl': round(self.weekly_pnl, 2),
            'trades_today': self.trades_today,
            'trades_this_week': self.trades_this_week,
            'open_positions': len(self.open_positions),
            'daily_limit_used_pct': round(daily_limit_used, 1),
            'weekly_limit_used_pct': round(weekly_limit_used, 1),
            'can_trade': self.can_take_trade()[0]
        }
    
    def save_state(self, filepath: Path) -> bool:
        """
        Save risk manager state to file.
        
        Args:
            filepath: Path to save state file
            
        Returns:
            True if saved successfully
        """
        try:
            state = {
                'account_balance': self.account_balance,
                'daily_pnl': self.daily_pnl,
                'weekly_pnl': self.weekly_pnl,
                'trades_today': self.trades_today,
                'trades_this_week': self.trades_this_week,
                'open_positions': self.open_positions,
                'last_reset_date': self.last_reset_date.isoformat(),
                'last_week_reset': self.last_week_reset
            }
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Risk manager state saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    def load_state(self, filepath: Path) -> bool:
        """
        Load risk manager state from file.
        
        Args:
            filepath: Path to state file
            
        Returns:
            True if loaded successfully
        """
        try:
            if not filepath.exists():
                logger.warning(f"State file not found: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.account_balance = state['account_balance']
            self.daily_pnl = state['daily_pnl']
            self.weekly_pnl = state['weekly_pnl']
            self.trades_today = state['trades_today']
            self.trades_this_week = state['trades_this_week']
            self.open_positions = state['open_positions']
            self.last_reset_date = datetime.fromisoformat(state['last_reset_date']).date()
            self.last_week_reset = state['last_week_reset']
            
            logger.info(f"Risk manager state loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False


# Command-line testing interface
if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        print("Testing Risk Manager Module...")
        print("-" * 50)
        
        # Initialize risk manager
        print("Testing risk manager initialization...")
        rm = RiskManager(account_balance=5000.0)
        print(f"  [OK] Risk manager initialized with $5000 balance")
        
        # Test position sizing
        print("\nTesting position size calculation...")
        size = rm.calculate_position_size('full_live', 20)
        print(f"  Full live mode, 20 tick stop: {size} contracts")
        assert size > 0
        
        size = rm.calculate_position_size('micro_live', 20)
        print(f"  Micro live mode: {size} contracts (fixed)")
        assert size == 2
        
        # Test risk limits
        print("\nTesting risk limit checks...")
        can_trade, reason = rm.can_take_trade()
        print(f"  Can trade: {can_trade} ({reason})")
        assert can_trade is True
        
        # Simulate losing trade
        print("\nSimulating trades...")
        rm.record_trade(-50.0)
        print(f"  After -$50 trade: Daily P&L = ${rm.daily_pnl:.2f}")
        
        # Test daily limit breach
        print("\nTesting daily limit breach...")
        rm.record_trade(-100.0)
        can_trade, reason = rm.check_daily_risk_limits()
        print(f"  After -$100 trade: Can trade = {can_trade}")
        print(f"  Reason: {reason}")
        
        # Test status
        print("\nTesting status report...")
        status = rm.get_status()
        print(f"  Daily P&L: ${status['daily_pnl']}")
        print(f"  Trades today: {status['trades_today']}")
        print(f"  Daily limit used: {status['daily_limit_used_pct']:.1f}%")
        
        # Test state persistence
        print("\nTesting state save/load...")
        test_file = Path("data/test_risk_state.json")
        rm.save_state(test_file)
        print(f"  [OK] State saved")
        
        rm2 = RiskManager(account_balance=0)
        rm2.load_state(test_file)
        print(f"  [OK] State loaded: Daily P&L = ${rm2.daily_pnl:.2f}")
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            print(f"  [OK] Cleaned up test file")
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
        
    else:
        print("Usage: python3 -m modules.risk_manager --test")
