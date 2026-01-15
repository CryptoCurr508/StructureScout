"""
Chart Screenshot Module

Handles capturing screenshots from MT5 terminal for analysis.
Uses pyautogui for reliable screenshot capture when MT5 API is limited.

No emojis or unicode characters in this file.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import pyautogui
import cv2
import numpy as np
from PIL import Image

# Set up logging
logger = logging.getLogger(__name__)


class ChartScreenshotCapture:
    """
    Captures screenshots of MT5 charts for AI analysis.
    
    Uses pyautogui to capture the MT5 window directly since
    the MT5 Python API has limited screenshot capabilities.
    """
    
    def __init__(self, mt5_window_title: str = "MetaTrader 5"):
        """
        Initialize screenshot capture.
        
        Args:
            mt5_window_title: Window title to locate MT5
        """
        self.mt5_window_title = mt5_window_title
        self.chart_region = None  # Will be set after calibration
        
        # Disable pyautogui failsafe (optional, use with caution)
        pyautogui.FAILSAFE = False
        
        logger.info("Chart screenshot capture initialized")
    
    def locate_mt5_window(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Locate MT5 window on screen.
        
        Returns:
            Tuple of (x, y, width, height) or None if not found
        """
        try:
            window = pyautogui.getWindowsWithTitle(self.mt5_window_title)
            if not window:
                logger.error(f"MT5 window '{self.mt5_window_title}' not found")
                return None
            
            mt5_window = window[0]
            if not mt5_window.isVisible:
                logger.error("MT5 window is not visible")
                return None
            
            # Get window bounds
            left = mt5_window.left
            top = mt5_window.top
            width = mt5_window.width
            height = mt5_window.height
            
            logger.info(f"MT5 window found at ({left}, {top}) size {width}x{height}")
            return (left, top, width, height)
            
        except Exception as e:
            logger.error(f"Failed to locate MT5 window: {e}")
            return None
    
    def calibrate_chart_region(self) -> bool:
        """
        Calibrate the chart area within MT5 window.
        
        Returns:
            True if calibration successful
        """
        window_bounds = self.locate_mt5_window()
        if not window_bounds:
            return False
        
        left, top, width, height = window_bounds
        
        # Estimate chart area (exclude toolbars, status bar, etc.)
        # Typical MT5 layout:
        # - Top toolbar: ~50px
        # - Side panel: ~200px (can be hidden)
        # - Bottom status bar: ~30px
        
        chart_left = left + 200  # Assuming side panel is visible
        chart_top = top + 50    # Below toolbar
        chart_width = width - 250  # Account for side panel
        chart_height = height - 100  # Account for toolbar and status bar
        
        # Ensure minimum size
        chart_width = max(chart_width, 800)
        chart_height = max(chart_height, 600)
        
        self.chart_region = (chart_left, chart_top, chart_width, chart_height)
        
        logger.info(f"Chart region calibrated: {self.chart_region}")
        return True
    
    def capture_chart_screenshot(
        self,
        symbol: str = "NAS100",
        timeframe: str = "M5",
        width: int = 1920,
        height: int = 1080,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Capture screenshot of the chart.
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            width: Desired width
            height: Desired height
            output_path: Path to save screenshot
            
        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            # Ensure MT5 window is active
            window_bounds = self.locate_mt5_window()
            if not window_bounds:
                return None
            
            # Calibrate if needed
            if self.chart_region is None:
                if not self.calibrate_chart_region():
                    return None
            
            # Generate output path
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{symbol}_{timeframe}_{timestamp}.png"
                output_path = Path("screenshots") / datetime.now().strftime("%Y-%m-%d") / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Capture the chart region
            chart_left, chart_top, chart_width, chart_height = self.chart_region
            
            # Take screenshot of chart area
            screenshot = pyautogui.screenshot(
                region=(chart_left, chart_top, chart_width, chart_height)
            )
            
            # Resize if needed
            if (chart_width != width) or (chart_height != height):
                screenshot = screenshot.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save screenshot
            screenshot.save(output_path, "PNG")
            
            logger.info(f"Chart screenshot captured: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to capture chart screenshot: {e}")
            return None
    
    def capture_full_screen(self, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Capture full screen (for debugging).
        
        Args:
            output_path: Path to save screenshot
            
        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"full_screen_{timestamp}.png"
                output_path = Path("screenshots") / datetime.now().strftime("%Y-%m-%d") / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(output_path, "PNG")
            
            logger.info(f"Full screen captured: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to capture full screen: {e}")
            return None
    
    def ensure_mt5_chart_ready(self, symbol: str, timeframe: str) -> bool:
        """
        Ensure MT5 is showing the correct chart.
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            
        Returns:
            True if chart is ready
        """
        try:
            # This is a placeholder for chart switching logic
            # In practice, you might need to:
            # 1. Activate MT5 window
            # 2. Navigate to symbol
            # 3. Set timeframe
            # 4. Wait for chart to load
            
            logger.info(f"Ensuring MT5 chart is ready for {symbol} {timeframe}")
            time.sleep(2)  # Wait for chart to load
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure MT5 chart ready: {e}")
            return False


# Global instance
chart_capture = ChartScreenshotCapture()


def get_chart_screenshot(
    symbol: str,
    timeframe: str,
    width: int = 1920,
    height: int = 1080,
    output_path: Optional[Path] = None
) -> Optional[Path]:
    """
    Convenience function to capture chart screenshot.
    
    Args:
        symbol: Trading symbol
        timeframe: Chart timeframe
        width: Screenshot width
        height: Screenshot height
        output_path: Output path
        
    Returns:
        Path to screenshot or None if failed
    """
    return chart_capture.capture_chart_screenshot(
        symbol=symbol,
        timeframe=timeframe,
        width=width,
        height=height,
        output_path=output_path
    )
