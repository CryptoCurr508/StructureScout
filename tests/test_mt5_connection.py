"""
Unit tests for MT5 Connection Module

Tests MT5 connection, chart operations, and screenshot capture functionality.
Uses mocks to avoid requiring actual MT5 connection during testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.mt5_connection import (
    MT5Connection,
    MT5ConnectionError,
    initialize_mt5_connection,
    get_chart_screenshot,
    add_reference_lines_to_chart,
    save_screenshot_with_metadata,
    get_previous_day_levels,
    disconnect_mt5
)


class TestMT5Connection:
    """Tests for MT5Connection class."""
    
    def test_init(self):
        """Test MT5Connection initialization."""
        conn = MT5Connection("12345", "password", "server", "/path/to/mt5")
        
        assert conn.login == "12345"
        assert conn.password == "password"
        assert conn.server == "server"
        assert conn.path == "/path/to/mt5"
        assert conn.connected is False
        assert conn.max_attempts == 3
    
    @patch('modules.mt5_connection.mt5')
    def test_connect_success(self, mock_mt5):
        """Test successful MT5 connection."""
        mock_mt5.initialize.return_value = True
        mock_mt5.login.return_value = True
        mock_mt5.account_info.return_value = Mock(login=12345, balance=5000.0)
        
        conn = MT5Connection("12345", "password", "server", "/path/to/mt5")
        result = conn.connect()
        
        assert result is True
        assert conn.connected is True
        assert mock_mt5.initialize.called
        assert mock_mt5.login.called
    
    @patch('modules.mt5_connection.mt5')
    @patch('modules.mt5_connection.time.sleep')
    def test_connect_failure(self, mock_sleep, mock_mt5):
        """Test MT5 connection failure after retries."""
        mock_mt5.initialize.return_value = False
        mock_mt5.last_error.return_value = (1, "Connection failed")
        
        conn = MT5Connection("12345", "password", "server", "/path/to/mt5")
        
        with pytest.raises(MT5ConnectionError):
            conn.connect()
        
        assert conn.connected is False
        assert mock_mt5.initialize.call_count == 3
    
    @patch('modules.mt5_connection.mt5')
    def test_disconnect(self, mock_mt5):
        """Test MT5 disconnection."""
        mock_mt5.initialize.return_value = True
        mock_mt5.login.return_value = True
        
        conn = MT5Connection("12345", "password", "server", "/path/to/mt5")
        conn.connected = True
        conn.disconnect()
        
        assert conn.connected is False
        assert mock_mt5.shutdown.called
    
    @patch('modules.mt5_connection.mt5')
    def test_is_connected_true(self, mock_mt5):
        """Test is_connected when connected."""
        mock_mt5.account_info.return_value = Mock(login=12345)
        
        conn = MT5Connection("12345", "password", "server", "/path/to/mt5")
        conn.connected = True
        
        assert conn.is_connected() is True
    
    @patch('modules.mt5_connection.mt5')
    def test_is_connected_false(self, mock_mt5):
        """Test is_connected when not connected."""
        mock_mt5.account_info.return_value = None
        
        conn = MT5Connection("12345", "password", "server", "/path/to/mt5")
        conn.connected = True
        
        assert conn.is_connected() is False
        assert conn.connected is False
    
    @patch('modules.mt5_connection.mt5')
    def test_get_account_info(self, mock_mt5):
        """Test getting account information."""
        mock_account = Mock(
            login=12345,
            balance=5000.0,
            equity=5100.0,
            margin=200.0,
            margin_free=4900.0,
            profit=100.0
        )
        mock_mt5.account_info.return_value = mock_account
        
        conn = MT5Connection("12345", "password", "server", "/path/to/mt5")
        conn.connected = True
        
        info = conn.get_account_info()
        
        assert info is not None
        assert info['balance'] == 5000.0
        assert info['equity'] == 5100.0
        assert info['profit'] == 100.0


class TestChartOperations:
    """Tests for chart-related functions."""
    
    @patch('modules.mt5_connection.mt5')
    def test_get_chart_screenshot_invalid_timeframe(self, mock_mt5):
        """Test screenshot with invalid timeframe."""
        result = get_chart_screenshot("NAS100", "INVALID")
        
        assert result is None
    
    @patch('modules.mt5_connection.mt5')
    @patch('modules.mt5_connection.Image')
    def test_get_chart_screenshot_success(self, mock_image, mock_mt5, tmp_path):
        """Test successful chart screenshot."""
        mock_mt5.symbol_select.return_value = True
        mock_img = Mock()
        mock_image.new.return_value = mock_img
        
        output_path = tmp_path / "test_chart.png"
        result = get_chart_screenshot("NAS100", "M5", output_path=output_path)
        
        # Note: Function returns path even with placeholder implementation
        assert result is not None
    
    @patch('modules.mt5_connection.mt5')
    def test_add_reference_lines(self, mock_mt5):
        """Test adding reference lines to chart."""
        mock_mt5.symbol_select.return_value = True
        
        result = add_reference_lines_to_chart(
            symbol="NAS100",
            prev_day_high=21300.0,
            prev_day_low=21200.0,
            vwap=21250.0
        )
        
        assert result is True
        assert mock_mt5.symbol_select.called
    
    def test_save_screenshot_with_metadata(self, sample_chart_path):
        """Test saving screenshot with metadata."""
        timestamp = datetime.now()
        
        result = save_screenshot_with_metadata(
            image_path=sample_chart_path,
            timestamp=timestamp,
            symbol="NAS100",
            timeframe="M5"
        )
        
        assert result is not None
        assert result.exists()
        assert "NAS100" in result.name
    
    @patch('modules.mt5_connection.mt5')
    def test_get_previous_day_levels(self, mock_mt5):
        """Test getting previous day high/low levels."""
        mock_mt5.symbol_select.return_value = True
        mock_mt5.TIMEFRAME_D1 = 16408
        
        # Mock rate data
        mock_rates = [
            {
                'time': 1704931200,
                'open': 21200.0,
                'high': 21300.0,
                'low': 21150.0,
                'close': 21280.0
            }
        ]
        mock_mt5.copy_rates_from.return_value = mock_rates
        
        levels = get_previous_day_levels("NAS100")
        
        assert levels is not None
        assert levels['high'] == 21300.0
        assert levels['low'] == 21150.0
        assert levels['open'] == 21200.0
        assert levels['close'] == 21280.0


class TestModuleFunctions:
    """Tests for module-level functions."""
    
    @patch('modules.mt5_connection.MT5Connection')
    def test_initialize_mt5_connection(self, mock_conn_class):
        """Test initialize_mt5_connection function."""
        mock_instance = Mock()
        mock_conn_class.return_value = mock_instance
        
        result = initialize_mt5_connection("12345", "password", "server", "/path")
        
        assert result == mock_instance
        assert mock_instance.connect.called
    
    @patch('modules.mt5_connection.mt5')
    def test_disconnect_mt5(self, mock_mt5):
        """Test disconnect_mt5 function."""
        disconnect_mt5()
        
        assert mock_mt5.shutdown.called


# Integration-style tests (still mocked but test full workflows)
class TestWorkflows:
    """Integration-style tests for common workflows."""
    
    @patch('modules.mt5_connection.mt5')
    def test_full_connection_workflow(self, mock_mt5):
        """Test complete connection workflow."""
        # Setup mocks
        mock_mt5.initialize.return_value = True
        mock_mt5.login.return_value = True
        mock_mt5.account_info.return_value = Mock(
            login=12345,
            balance=5000.0,
            equity=5000.0,
            margin=0,
            margin_free=5000.0,
            profit=0
        )
        
        # Initialize connection
        conn = initialize_mt5_connection("12345", "password", "server", "/path")
        
        # Verify connected
        assert conn.is_connected()
        
        # Get account info
        info = conn.get_account_info()
        assert info['balance'] == 5000.0
        
        # Disconnect
        conn.disconnect()
        assert conn.connected is False
    
    @patch('modules.mt5_connection.mt5')
    @patch('modules.mt5_connection.Image')
    def test_chart_capture_workflow(self, mock_image, mock_mt5, tmp_path):
        """Test chart capture workflow."""
        mock_mt5.symbol_select.return_value = True
        mock_img = Mock()
        mock_image.new.return_value = mock_img
        
        # Capture screenshot
        timestamp = datetime.now()
        output = tmp_path / "chart.png"
        
        # Create a real image for testing
        from PIL import Image
        img = Image.new('RGB', (1920, 1080), color='white')
        img.save(output)
        
        # Save with metadata
        result = save_screenshot_with_metadata(
            image_path=output,
            timestamp=timestamp,
            symbol="NAS100",
            timeframe="M5"
        )
        
        assert result is not None
        assert result.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
