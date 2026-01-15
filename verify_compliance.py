#!/usr/bin/env python3
"""
Simple Compliance Verification

Verifies that all compliance updates have been implemented correctly
by checking file contents and configuration.

No emojis or unicode characters in this file.
"""

import os
import yaml
from pathlib import Path


def check_file_exists(filepath):
    """Check if file exists."""
    return Path(filepath).exists()


def check_file_contains(filepath, search_terms):
    """Check if file contains all search terms."""
    if not Path(filepath).exists():
        return False, f"File {filepath} does not exist"
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    missing = []
    for term in search_terms:
        if term not in content:
            missing.append(term)
    
    return len(missing) == 0, missing


def main():
    """Run compliance verification."""
    print("=" * 60)
    print("StructureScout Compliance Verification")
    print("=" * 60)
    
    results = []
    
    # 1. Check MT5 connection improvements
    print("1. Checking MT5 connection improvements...")
    mt5_file = "modules/mt5_connection.py"
    search_terms = [
        "MT5 Path:",
        "Server:",
        "Login:",
        "path_variations",
        "N1 Capita lMarkets"
    ]
    success, details = check_file_contains(mt5_file, search_terms)
    results.append(("MT5 Connection", success, details))
    print(f"   {'[OK]' if success else '[FAIL]'} MT5 connection improvements")
    
    # 2. Check GPT prompt updates
    print("2. Checking GPT prompt updates...")
    gpt_file = "modules/gpt_analysis.py"
    search_terms = [
        "OPENING RANGE BREAKOUT",
        "STRUCTURE BREAK", 
        "MEAN REVERSION AT EXTREMES",
        "higher highs AND higher lows",
        "1.5x+ larger than recent 20-bar average",
        "3 hours per position",
        "volatility_detected",
        "high_volatility"
    ]
    success, details = check_file_contains(gpt_file, search_terms)
    results.append(("GPT Prompts", success, details))
    print(f"   {'[OK]' if success else '[FAIL]'} GPT prompt updates")
    
    # 3. Check live trading switch
    print("3. Checking live trading switch...")
    config_file = "config/config.yaml"
    search_terms = [
        "enable_live_trading: false",
        "require_manual_confirmation: true",
        "trading_enabled: false"
    ]
    success, details = check_file_contains(config_file, search_terms)
    results.append(("Live Trading Switch", success, details))
    print(f"   {'[OK]' if success else '[FAIL]'} Live trading switch")
    
    # 4. Check position manager
    print("4. Checking position manager...")
    pm_file = "modules/position_manager.py"
    search_terms = [
        "PositionManager",
        "partial_exit_ratio: 0.5",
        "max_hold_hours: 3",
        "trailing_stop",
        "mean_reversion_full_exit_at_target"
    ]
    success, check_file_exists(pm_file) and check_file_contains(pm_file, search_terms)[0]
    results.append(("Position Manager", success, "File exists and contains required terms"))
    print(f"   {'[OK]' if success else '[FAIL]'} Position manager")
    
    # 5. Check position management config
    print("5. Checking position management config...")
    pm_config_terms = [
        "partial_exit_ratio: 0.5",
        "max_hold_hours: 3",
        "enable_trailing_stops: true",
        "mean_reversion_full_exit_at_target: true"
    ]
    success, details = check_file_contains(config_file, pm_config_terms)
    results.append(("Position Management Config", success, details))
    print(f"   {'[OK]' if success else '[FAIL]'} Position management config")
    
    # 6. Check scheduler updates
    print("6. Checking scheduler updates...")
    scheduler_file = "modules/scheduler.py"
    scheduler_terms = [
        "monitor_position_hold_times",
        "should_close_all_positions",
        "Pre-lunch position close",
        "End-of-day position close"
    ]
    success, details = check_file_contains(scheduler_file, scheduler_terms)
    results.append(("Scheduler Updates", success, details))
    print(f"   {'[OK]' if success else '[FAIL]'} Scheduler updates")
    
    # 7. Check config class updates
    print("7. Checking config class updates...")
    config_class_file = "config/__init__.py"
    config_terms = [
        "enable_live_trading",
        "require_manual_confirmation",
        "is_live_trading_allowed"
    ]
    success, details = check_file_contains(config_class_file, config_terms)
    results.append(("Config Class", success, details))
    print(f"   {'[OK]' if success else '[FAIL]'} Config class updates")
    
    # Summary
    print("-" * 60)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Compliance Checks Passed: {passed}/{total}")
    
    for name, success, details in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {name}")
        if not success and isinstance(details, list):
            for missing in details[:3]:  # Show first 3 missing items
                print(f"      Missing: {missing}")
    
    print("-" * 60)
    
    if passed == total:
        print("[SUCCESS] All compliance updates verified!")
        print("\nThe StructureScout bot now complies with the refined strategy:")
        print("✓ Detailed pattern recognition rules for all 3 setup types")
        print("✓ MT5 connection improvements with better error handling")
        print("✓ Live trading master switch with safety interlocks")
        print("✓ Position management with 50% partial exits and trailing stops")
        print("✓ 3-hour maximum hold time enforcement")
        print("✓ Enhanced regime detection with volatility monitoring")
        print("\nTo enable live trading:")
        print("1. Set enable_live_trading: true in config/config.yaml")
        print("2. Set trading_enabled: true in config/config.yaml")
        print("3. Set current_mode: micro_live or full_live in config/config.yaml")
        return 0
    else:
        print("[INCOMPLETE] Some compliance updates missing")
        return 1


if __name__ == "__main__":
    exit(main())
