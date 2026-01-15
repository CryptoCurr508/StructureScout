#!/usr/bin/env python3
"""
Test StructureScout Compliance Updates

Tests all the refined strategy compliance updates:
1. MT5 connection improvements
2. GPT prompt updates with detailed pattern rules
3. Live trading switch functionality
4. Position management rules
5. Regime detection enhancements
6. Hold time enforcement

No emojis or unicode characters in this file.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pytz

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from modules.gpt_analysis import build_system_prompt, build_user_prompt
from modules.position_manager import PositionManager
from modules.scheduler import monitor_position_hold_times, should_close_all_positions


def test_config_live_trading_switch():
    """Test live trading switch configuration."""
    print("Testing live trading switch configuration...")
    
    config = get_config()
    
    # Test default values
    assert config.enable_live_trading == False, "Live trading should be disabled by default"
    assert config.require_manual_confirmation == True, "Manual confirmation should be required by default"
    assert config.trading_enabled == False, "Trading should be disabled by default"
    assert config.is_live_trading_allowed == False, "Live trading should not be allowed by default"
    
    print("  [OK] Live trading switches work correctly")
    return True


def test_gpt_prompt_updates():
    """Test GPT prompt updates with refined strategy."""
    print("Testing GPT prompt updates...")
    
    system_prompt = build_system_prompt()
    
    # Check for key pattern rules
    assert "OPENING RANGE BREAKOUT" in system_prompt, "Should contain opening range breakout rules"
    assert "STRUCTURE BREAK" in system_prompt, "Should contain structure break rules"
    assert "MEAN REVERSION AT EXTREMES" in system_prompt, "Should contain mean reversion rules"
    assert "higher highs AND higher lows" in system_prompt, "Should contain trending definition"
    assert "1.5x+ larger than recent 20-bar average" in system_prompt, "Should contain volatility detection"
    assert "3 hours per position" in system_prompt, "Should contain hold time limit"
    
    # Test user prompt
    user_prompt = build_user_prompt(
        timestamp="2026-01-14 10:30",
        account_balance=5000.0,
        risk_amount=50.0,
        prev_day_high=21300.0,
        prev_day_low=21200.0,
        vwap=21250.0
    )
    
    assert "volatility_detected" in user_prompt, "Should ask for volatility detection"
    assert "high_volatility" in user_prompt, "Should include high volatility option"
    
    print("  [OK] GPT prompts contain refined strategy rules")
    return True


def test_position_manager():
    """Test position manager functionality."""
    print("Testing position manager...")
    
    # Create mock position manager
    class MockMT5:
        pass
    
    pm = PositionManager(MockMT5())
    
    # Test position opening
    setup_data = {
        'setup_type': 'opening_range_breakout',
        'setup_direction': 'long',
        'entry_price': 21250.0,
        'stop_loss_price': 21240.0,
        'take_profit_1': 21285.0,
        'take_profit_2': 21320.0
    }
    
    position = pm.open_position(setup_data, ticket=12345)
    
    assert position['ticket'] == 12345, "Should store ticket correctly"
    assert position['setup_type'] == 'opening_range_breakout', "Should store setup type"
    assert position['partial_exit_done'] == False, "Partial exit should not be done initially"
    assert position['max_hold_hours'] == 3, "Should have 3-hour max hold time"
    
    print("  [OK] Position manager works correctly")
    return True


def test_scheduler_hold_time():
    """Test scheduler hold time monitoring."""
    print("Testing scheduler hold time monitoring...")
    
    # Create mock position manager with old position
    class MockPositionManager:
        def __init__(self):
            self.open_positions = {
                12345: {
                    'entry_time': datetime.now(pytz.timezone("America/New_York")) - 
                                pytz.timezone("America/New_York").localize(datetime(2026, 1, 14, 7, 0)),
                    'setup_type': 'structure_break',
                    'direction': 'long'
                }
            }
    
    pm = MockPositionManager()
    violations = monitor_position_hold_times(pm, max_hold_hours=3)
    
    # Should detect violation since position is >3 hours old
    assert len(violations) > 0, "Should detect hold time violation"
    assert violations[0]['urgency'] == 'critical', "Should be critical violation"
    
    # Test time-based position closing
    current_time = datetime.now(pytz.timezone("America/New_York"))
    
    # Test at 10:00 AM (should not close)
    test_time_10am = current_time.replace(hour=10, minute=0)
    should_close, reason = should_close_all_positions(test_time_10am)
    assert should_close == False, "Should not close at 10:00 AM"
    
    # Test at 11:30 AM (should close for lunch)
    test_time_1130am = current_time.replace(hour=11, minute=30)
    should_close, reason = should_close_all_positions(test_time_1130am)
    assert should_close == True, "Should close at 11:30 AM for lunch"
    assert "lunch" in reason.lower(), "Reason should mention lunch"
    
    print("  [OK] Hold time monitoring works correctly")
    return True


def test_mt5_connection_path():
    """Test MT5 connection path handling."""
    print("Testing MT5 connection path handling...")
    
    from modules.mt5_connection import MT5Connection
    
    # Test with path that has spaces
    mt5_conn = MT5Connection(
        login="12345",
        password="test",
        server="TestServer",
        path="C:\\Program Files\\Test MetaTrader 5\\terminal64.exe"
    )
    
    # Check that path is stored correctly
    assert mt5_conn.path == "C:\\Program Files\\Test MetaTrader 5\\terminal64.exe"
    assert "Test MetaTrader 5" in mt5_conn.path, "Should handle spaces in path"
    
    print("  [OK] MT5 path handling works correctly")
    return True


def main():
    """Run all compliance tests."""
    print("=" * 60)
    print("StructureScout Compliance Update Tests")
    print("=" * 60)
    
    tests = [
        test_config_live_trading_switch,
        test_gpt_prompt_updates,
        test_position_manager,
        test_scheduler_hold_time,
        test_mt5_connection_path
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"  [FAILED] {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"  [ERROR] {test.__name__}: {e}")
    
    print("-" * 60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    
    if failed == 0:
        print("[SUCCESS] All compliance updates verified!")
        return 0
    else:
        print("[FAILED] Some tests failed - check implementation")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        exit(main())
    else:
        print("Usage: python3 test_compliance_updates.py --test")
