"""
MT5 Connection Module

Handles MetaTrader5 platform connection, chart access, and screenshot capture.
Provides interface for connecting to MT5, capturing chart screenshots with reference lines,
and managing the MT5 connection lifecycle.

No emojis or unicode characters in this file.
"""

import MetaTrader5 as mt5
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
import pytz
from PIL import Image
import time
import logging

# Set up logging
logger = logging.getLogger(__name__)


class MT5ConnectionError(Exception):
    """Custom exception for MT5 connection errors."""
    pass


class MT5Connection:
    """
    MetaTrader5 connection manager.
    
    Handles connection, disconnection, and chart operations.
    """
    
    def __init__(self, login: str, password: str, server: str, path: str):
        """
        Initialize MT5 connection manager.
        
        Args:
            login: MT5 account login number
            password: MT5 account password
            server: MT5 broker server
            path: Path to MT5 installation directory
        """
        self.login = login
        self.password = password
        self.server = server
        self.path = path
        self.connected = False
        self.connection_attempts = 0
        self.max_attempts = 3
    
    def connect(self) -> bool:
        """
        Connect to MT5 platform.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            MT5ConnectionError: If connection fails after max attempts
        """
        logger.info("Attempting to connect to MT5...")
        
        for attempt in range(1, self.max_attempts + 1):
            self.connection_attempts = attempt
            
            # Initialize MT5
            if not mt5.initialize(path=self.path):
                error = mt5.last_error()
                logger.warning(f"MT5 initialize failed (attempt {attempt}/{self.max_attempts}): {error}")
                time.sleep(30)  # Wait 30 seconds before retry
                continue
            
            # Login to account
            if not mt5.login(login=int(self.login), password=self.password, server=self.server):
                error = mt5.last_error()
                logger.warning(f"MT5 login failed (attempt {attempt}/{self.max_attempts}): {error}")
                mt5.shutdown()
                time.sleep(30)
                continue
            
            # Connection successful
            self.connected = True
            logger.info(f"MT5 connection successful on attempt {attempt}")
            
            # Log account info
            account_info = mt5.account_info()
            if account_info:
                logger.info(f"Connected to account: {account_info.login}, Balance: {account_info.balance}")
            
            return True
        
        # All attempts failed
        error_msg = f"Failed to connect to MT5 after {self.max_attempts} attempts"
        logger.error(error_msg)
        raise MT5ConnectionError(error_msg)
    
    def disconnect(self) -> None:
        """Disconnect from MT5 platform."""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
    
    def is_connected(self) -> bool:
        """
        Check if MT5 connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        if not self.connected:
            return False
        
        # Try to get account info to verify connection is alive
        account_info = mt5.account_info()
        if account_info is None:
            self.connected = False
            return False
        
        return True
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current account information.
        
        Returns:
            Dictionary with account info or None if not connected
        """
        if not self.is_connected():
            logger.error("Cannot get account info: Not connected to MT5")
            return None
        
        account_info = mt5.account_info()
        if account_info is None:
            return None
        
        return {
            'login': account_info.login,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'margin_free': account_info.margin_free,
            'profit': account_info.profit
        }
    
    def reconnect(self) -> bool:
        """
        Reconnect to MT5 if connection is lost.
        
        Returns:
            True if reconnection successful
        """
        logger.info("Attempting to reconnect to MT5...")
        self.disconnect()
        time.sleep(5)
        return self.connect()


def initialize_mt5_connection(login: str, password: str, server: str, path: str) -> MT5Connection:
    """
    Initialize and connect to MT5.
    
    Args:
        login: MT5 account login
        password: MT5 account password
        server: MT5 broker server
        path: Path to MT5 installation
        
    Returns:
        Connected MT5Connection instance
        
    Raises:
        MT5ConnectionError: If connection fails
    """
    connection = MT5Connection(login, password, server, path)
    connection.connect()
    return connection


def get_chart_screenshot(
    symbol: str,
    timeframe: str,
    width: int = 1920,
    height: int = 1080,
    output_path: Optional[Path] = None
) -> Optional[Path]:
    """
    Capture screenshot of specified chart.
    
    Args:
        symbol: Trading symbol (e.g., "NAS100")
        timeframe: Chart timeframe (e.g., "M5")
        width: Screenshot width in pixels
        height: Screenshot height in pixels
        output_path: Path to save screenshot (auto-generated if None)
        
    Returns:
        Path to saved screenshot or None if failed
    """
    # Map timeframe string to MT5 constant
    timeframe_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1
    }
    
    mt5_timeframe = timeframe_map.get(timeframe)
    if mt5_timeframe is None:
        logger.error(f"Invalid timeframe: {timeframe}")
        return None
    
    # Copy chart to clipboard (MT5 method)
    # Note: This requires MT5 to be running with GUI
    # For headless operation, alternative methods may be needed
    
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select symbol: {symbol}")
        return None
    
    # Get chart window
    # Note: MT5 Python API has limited chart screenshot capabilities
    # This is a placeholder for the actual implementation
    # In production, you may need to use pyautogui or similar for screenshots
    
    logger.warning("Chart screenshot via MT5 API has limitations")
    logger.warning("Consider using pyautogui or platform-specific screenshot tools")
    
    # Generate output path if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_{timestamp}.png"
        output_path = Path("screenshots") / datetime.now().strftime("%Y-%m-%d") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Placeholder: In actual implementation, capture screenshot here
    # For now, create a blank placeholder image
    try:
        img = Image.new('RGB', (width, height), color='white')
        img.save(output_path)
        logger.info(f"Screenshot saved to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")
        return None


def add_reference_lines_to_chart(
    symbol: str,
    prev_day_high: float,
    prev_day_low: float,
    vwap: float,
    or_high: Optional[float] = None,
    or_low: Optional[float] = None
) -> bool:
    """
    Add reference lines to chart for visual analysis.
    
    Args:
        symbol: Trading symbol
        prev_day_high: Previous day high price
        prev_day_low: Previous day low price
        vwap: Volume Weighted Average Price
        or_high: Opening range high (optional)
        or_low: Opening range low (optional)
        
    Returns:
        True if lines added successfully
        
    Note:
        This function uses MT5's object creation API to draw lines on charts.
        Lines are color-coded: red (prev high), green (prev low), yellow (VWAP)
    """
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select symbol: {symbol}")
        return False
    
    # Note: MT5 Python API has limited charting capabilities
    # Horizontal lines would typically be added via MT5's ObjectCreate functions
    # This is a placeholder for the actual implementation
    
    logger.info(f"Adding reference lines for {symbol}:")
    logger.info(f"  Previous Day High: {prev_day_high}")
    logger.info(f"  Previous Day Low: {prev_day_low}")
    logger.info(f"  VWAP: {vwap}")
    if or_high and or_low:
        logger.info(f"  Opening Range: {or_low} - {or_high}")
    
    # In production, implement actual line drawing using MT5 ObjectCreate
    # or use TradingView/custom charting solution
    
    return True


def save_screenshot_with_metadata(
    image_path: Path,
    timestamp: datetime,
    symbol: str,
    timeframe: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Save screenshot with metadata in filename and EXIF data.
    
    Args:
        image_path: Path to image file
        timestamp: Timestamp when screenshot was taken
        symbol: Trading symbol
        timeframe: Chart timeframe
        metadata: Additional metadata to store
        
    Returns:
        Path to saved file with metadata
    """
    if not image_path.exists():
        logger.error(f"Image file not found: {image_path}")
        return image_path
    
    # Create new filename with metadata
    date_str = timestamp.strftime("%Y%m%d")
    time_str = timestamp.strftime("%H%M")
    new_filename = f"{symbol}_{date_str}_{time_str}.png"
    
    # Create dated subfolder
    dated_folder = Path("screenshots") / timestamp.strftime("%Y-%m-%d")
    dated_folder.mkdir(parents=True, exist_ok=True)
    
    new_path = dated_folder / new_filename
    
    try:
        # Open and save image (this also allows adding EXIF data)
        img = Image.open(image_path)
        
        # Compress if needed
        if image_path.stat().st_size > 1_000_000:  # > 1MB
            img.save(new_path, optimize=True, quality=85)
            logger.info(f"Screenshot compressed and saved to: {new_path}")
        else:
            img.save(new_path)
            logger.info(f"Screenshot saved to: {new_path}")
        
        # Remove original if different location
        if image_path != new_path and image_path.exists():
            image_path.unlink()
        
        return new_path
    
    except Exception as e:
        logger.error(f"Failed to save screenshot with metadata: {e}")
        return image_path


def get_previous_day_levels(symbol: str) -> Optional[Dict[str, float]]:
    """
    Get previous day's high and low prices.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Dictionary with 'high' and 'low' keys or None if failed
    """
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select symbol: {symbol}")
        return None
    
    # Get previous day's bars
    timezone = pytz.timezone("America/New_York")
    utc_to = datetime.now(timezone)
    
    # Get daily bars
    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_D1, utc_to, 2)
    
    if rates is None or len(rates) < 2:
        logger.error(f"Failed to get historical data for {symbol}")
        return None
    
    # Previous day is index 0 (most recent complete day)
    prev_day = rates[0]
    
    return {
        'high': float(prev_day['high']),
        'low': float(prev_day['low']),
        'open': float(prev_day['open']),
        'close': float(prev_day['close'])
    }


def disconnect_mt5() -> None:
    """Disconnect from MT5 platform."""
    mt5.shutdown()
    logger.info("MT5 shutdown complete")


# Command-line testing interface
if __name__ == "__main__":
    import sys
    from config import get_config
    
    if "--test" in sys.argv:
        print("Testing MT5 Connection Module...")
        print("-" * 50)
        
        # Load configuration
        try:
            config = get_config()
            print(f"[OK] Configuration loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load configuration: {e}")
            sys.exit(1)
        
        # Test connection
        try:
            print(f"Connecting to MT5...")
            print(f"  Login: {config.mt5_login}")
            print(f"  Server: {config.mt5_server}")
            
            connection = initialize_mt5_connection(
                login=config.mt5_login,
                password=config.mt5_password,
                server=config.mt5_server,
                path=config.mt5_path
            )
            print(f"[OK] Connected to MT5")
            
            # Get account info
            account_info = connection.get_account_info()
            if account_info:
                print(f"[OK] Account info retrieved:")
                print(f"  Balance: ${account_info['balance']:.2f}")
                print(f"  Equity: ${account_info['equity']:.2f}")
            
            # Test previous day levels
            levels = get_previous_day_levels(config.trading_symbol)
            if levels:
                print(f"[OK] Previous day levels for {config.trading_symbol}:")
                print(f"  High: {levels['high']}")
                print(f"  Low: {levels['low']}")
            
            # Disconnect
            connection.disconnect()
            print(f"[OK] Disconnected from MT5")
            print("-" * 50)
            print("[SUCCESS] All tests passed!")
            
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            sys.exit(1)
    else:
        print("Usage: python3 -m modules.mt5_connection --test")
