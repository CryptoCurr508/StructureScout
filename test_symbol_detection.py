"""
Test Script for Broker Symbol Auto-Detection

Tests the automatic detection of broker-specific symbol formats like #NAS100_Mar.
Run this after connecting to MT5 to verify symbol detection works correctly.

Usage:
    python3 test_symbol_detection.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from modules.mt5_connection import MT5Connection, detect_broker_symbol
import MetaTrader5 as mt5


def test_symbol_detection():
    """Test broker symbol auto-detection."""
    print("=" * 60)
    print("StructureScout - Symbol Detection Test")
    print("=" * 60)
    
    # Load configuration
    try:
        config = get_config()
        print("\n[OK] Configuration loaded")
    except Exception as e:
        print(f"\n[ERROR] Failed to load configuration: {e}")
        return False
    
    # Connect to MT5
    print(f"\nConnecting to MT5...")
    print(f"  Server: {config.mt5_server}")
    print(f"  Login: {config.mt5_login}")
    
    try:
        connection = MT5Connection(
            login=config.mt5_login,
            password=config.mt5_password,
            server=config.mt5_server,
            path=config.mt5_path
        )
        connection.connect()
        print("[OK] Connected to MT5")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MT5: {e}")
        return False
    
    # Get server time
    server_time = mt5.symbol_info_tick("EURUSD")
    if server_time:
        print(f"\n[INFO] Server Time: {server_time.time}")
    
    # Test symbol detection
    print(f"\n{'=' * 60}")
    print("Testing Symbol Detection")
    print(f"{'=' * 60}")
    
    base_symbol = config.symbol_base
    print(f"\nBase Symbol: {base_symbol}")
    print(f"Configured Symbol: {config.trading_symbol}")
    print(f"Auto-detect enabled: {config.auto_detect_symbol}")
    
    print(f"\nSearching for matching symbols...")
    detected_symbol = detect_broker_symbol(base_symbol)
    
    if detected_symbol:
        print(f"\n[SUCCESS] Detected broker symbol: {detected_symbol}")
        
        # Test if symbol is valid
        symbol_info = mt5.symbol_info(detected_symbol)
        if symbol_info:
            print(f"\n[OK] Symbol is valid and accessible")
            print(f"  Description: {symbol_info.description}")
            print(f"  Point: {symbol_info.point}")
            print(f"  Digits: {symbol_info.digits}")
            print(f"  Trade Mode: {symbol_info.trade_mode}")
            
            # Get current quote
            tick = mt5.symbol_info_tick(detected_symbol)
            if tick:
                print(f"\n[OK] Current market data:")
                print(f"  Bid: {tick.bid}")
                print(f"  Ask: {tick.ask}")
                print(f"  Last: {tick.last}")
        else:
            print(f"\n[WARNING] Symbol detected but not accessible")
    else:
        print(f"\n[ERROR] Could not detect broker symbol")
        print(f"Available symbols containing '{base_symbol}':")
        
        # List all symbols
        symbols = mt5.symbols_get()
        if symbols:
            matching = [s.name for s in symbols if base_symbol.upper() in s.name.upper()]
            if matching:
                for sym in matching[:10]:  # Show first 10
                    print(f"  - {sym}")
            else:
                print(f"  No matching symbols found")
    
    # Disconnect
    connection.disconnect()
    print(f"\n[OK] Disconnected from MT5")
    
    print(f"\n{'=' * 60}")
    print("Test Complete")
    print(f"{'=' * 60}\n")
    
    return detected_symbol is not None


if __name__ == "__main__":
    success = test_symbol_detection()
    sys.exit(0 if success else 1)
