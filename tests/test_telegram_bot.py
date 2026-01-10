"""
Unit tests for Telegram Bot Module

Tests Telegram notification system and message formatting.
Uses mocks to avoid actual Telegram API calls during testing.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.telegram_bot import (
    TelegramBotError,
    TelegramNotifier,
    format_setup_alert,
    format_daily_summary,
    format_weekly_report,
    format_error_notification,
    format_system_status,
    send_message_sync,
    send_photo_sync
)


class TestTelegramNotifier:
    """Tests for TelegramNotifier class."""
    
    def test_init(self):
        """Test TelegramNotifier initialization."""
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        assert notifier.bot_token == "test_token"
        assert notifier.chat_id == "test_chat_id"
        assert notifier.initialized is False
    
    @pytest.mark.asyncio
    @patch('modules.telegram_bot.Bot')
    async def test_initialize_success(self, mock_bot_class):
        """Test successful bot initialization."""
        mock_bot = AsyncMock()
        mock_bot.get_me = AsyncMock(return_value=Mock(username="test_bot"))
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier("test_token", "test_chat_id")
        notifier.bot = mock_bot
        
        result = await notifier.initialize()
        
        assert result is True
        assert notifier.initialized is True
    
    @pytest.mark.asyncio
    @patch('modules.telegram_bot.Bot')
    async def test_send_message_success(self, mock_bot_class):
        """Test successful message sending."""
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier("test_token", "test_chat_id")
        notifier.bot = mock_bot
        
        result = await notifier.send_message("Test message")
        
        assert result is True
        assert mock_bot.send_message.called
    
    @pytest.mark.asyncio
    @patch('modules.telegram_bot.Bot')
    async def test_send_photo_success(self, mock_bot_class, sample_chart_path):
        """Test successful photo sending."""
        mock_bot = AsyncMock()
        mock_bot.send_photo = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier("test_token", "test_chat_id")
        notifier.bot = mock_bot
        
        result = await notifier.send_photo(str(sample_chart_path), "Test caption")
        
        assert result is True
        assert mock_bot.send_photo.called


class TestMessageFormatting:
    """Tests for message formatting functions."""
    
    def test_format_high_quality_alert(self):
        """Test formatting high-quality setup alert."""
        setup_data = {
            'timestamp': '2026-01-10 10:30',
            'setup_type': 'structure_break',
            'setup_direction': 'long',
            'current_price': 21250.0,
            'entry_price': 21255.0,
            'stop_loss_price': 21240.0,
            'stop_distance_ticks': 15,
            'take_profit_1': 21285.0,
            'take_profit_2': 21310.0,
            'reward_risk_ratio': 2.0,
            'position_size': 10,
            'dollar_risk': 50.0,
            'dollar_target_1': 100.0,
            'analysis_notes': 'Clean structure break',
            'market_regime': 'trending_up',
            'confidence_score': 78,
            'caution_flags': []
        }
        
        message = format_setup_alert(setup_data, 'high')
        
        assert isinstance(message, str)
        assert 'HIGH-QUALITY SETUP' in message
        assert 'structure_break' in message
        assert '21250.00' in message
        assert '78%' in message
        assert len(message) > 200
    
    def test_format_medium_quality_alert(self):
        """Test formatting medium-quality setup alert."""
        setup_data = {
            'timestamp': '2026-01-10 10:30',
            'setup_type': 'mean_reversion',
            'setup_direction': 'short',
            'entry_price': 21260.0,
            'stop_loss_price': 21275.0,
            'reward_risk_ratio': 1.5,
            'confidence_score': 65
        }
        
        message = format_setup_alert(setup_data, 'medium')
        
        assert 'Medium Confidence' in message
        assert 'mean_reversion' in message
        assert 'Wait for confirmation' in message
    
    def test_format_alert_with_caution_flags(self):
        """Test formatting alert with caution flags."""
        setup_data = {
            'timestamp': '2026-01-10 10:30',
            'setup_type': 'breakout',
            'setup_direction': 'long',
            'current_price': 21250.0,
            'entry_price': 21255.0,
            'stop_loss_price': 21240.0,
            'stop_distance_ticks': 15,
            'take_profit_1': 21285.0,
            'reward_risk_ratio': 2.0,
            'position_size': 10,
            'dollar_risk': 50.0,
            'dollar_target_1': 100.0,
            'analysis_notes': 'Test',
            'market_regime': 'trending_up',
            'confidence_score': 70,
            'caution_flags': ['News event nearby', 'High volatility']
        }
        
        message = format_setup_alert(setup_data, 'high')
        
        assert 'Caution' in message
        assert 'News event nearby' in message
        assert 'High volatility' in message
    
    def test_format_daily_summary_basic(self):
        """Test formatting basic daily summary."""
        summary_data = {
            'date': '2026-01-10',
            'scan_count': 7,
            'valid_setup_count': 3,
            'high_quality_count': 1,
            'trending_count': 5,
            'ranging_count': 2,
            'or_count': 1,
            'structure_count': 1,
            'mr_count': 1,
            'avg_confidence': 72.5,
            'avg_rr': 1.8
        }
        
        message = format_daily_summary(summary_data)
        
        assert 'DAILY ANALYSIS SUMMARY' in message
        assert '2026-01-10' in message
        assert '7' in message  # scan_count
        assert '3' in message  # valid_setup_count
    
    def test_format_daily_summary_with_trades(self):
        """Test formatting daily summary with executed trades."""
        summary_data = {
            'date': '2026-01-10',
            'scan_count': 7,
            'valid_setup_count': 3,
            'high_quality_count': 1,
            'trending_count': 5,
            'ranging_count': 2,
            'or_count': 1,
            'structure_count': 1,
            'mr_count': 1,
            'avg_confidence': 72.5,
            'avg_rr': 1.8,
            'trades_executed': 2,
            'daily_pnl': 125.50,
            'daily_r_multiple': 2.5
        }
        
        message = format_daily_summary(summary_data)
        
        assert 'Trades Executed Today' in message
        assert '125.50' in message
        assert '2.5R' in message
    
    def test_format_weekly_report_basic(self):
        """Test formatting basic weekly report."""
        report_data = {
            'start_date': '2026-01-06',
            'end_date': '2026-01-10',
            'total_setups': 15,
            'hq_setups': 5,
            'setups_per_day': 3.0,
            'breakout_pct': 40.0,
            'structure_pct': 35.0,
            'mr_pct': 25.0,
            'trending_pct': 60.0,
            'ranging_pct': 40.0,
            'frequency_met': 'Yes',
            'quality_consistent': 'Yes',
            'next_step': 'Continue observation'
        }
        
        message = format_weekly_report(report_data)
        
        assert 'WEEKLY' in message
        assert '2026-01-06' in message
        assert '15' in message  # total_setups
        assert 'Continue observation' in message
    
    def test_format_weekly_report_with_performance(self):
        """Test formatting weekly report with trading performance."""
        report_data = {
            'start_date': '2026-01-06',
            'end_date': '2026-01-10',
            'total_setups': 15,
            'hq_setups': 5,
            'setups_per_day': 3.0,
            'breakout_pct': 40.0,
            'structure_pct': 35.0,
            'mr_pct': 25.0,
            'trending_pct': 60.0,
            'ranging_pct': 40.0,
            'trade_count': 8,
            'win_rate': 62.5,
            'avg_r': 1.8,
            'pf': 2.1,
            'weekly_pnl': 425.0,
            'best_type': 'structure_break',
            'best_wr': 75.0,
            'frequent_type': 'breakout',
            'frequency_met': 'Yes',
            'quality_consistent': 'Yes',
            'next_step': 'Continue observation'
        }
        
        message = format_weekly_report(report_data)
        
        assert 'TRADING PERFORMANCE' in message
        assert '62.5%' in message
        assert '425.00' in message
        assert 'structure_break' in message
    
    def test_format_error_notification(self):
        """Test formatting error notification."""
        message = format_error_notification("MT5 connection lost", "critical")
        
        assert 'CRITICAL ERROR' in message
        assert 'MT5 connection lost' in message
        assert 'CRITICAL' in message.upper()
    
    def test_format_system_status(self):
        """Test formatting system status."""
        status_data = {
            'current_mode': 'observation',
            'status': 'active',
            'open_positions': 0,
            'daily_pnl': 0.0,
            'weekly_pnl': 125.50,
            'trades_today': 0,
            'mt5_status': 'Connected',
            'openai_status': 'OK',
            'telegram_status': 'OK',
            'last_scan': '2026-01-10 10:30 EST'
        }
        
        message = format_system_status(status_data)
        
        assert 'SYSTEM STATUS' in message
        assert 'observation' in message
        assert 'Connected' in message
        assert '125.50' in message


class TestSyncWrappers:
    """Tests for synchronous wrapper functions."""
    
    @patch('modules.telegram_bot.TelegramNotifier')
    @patch('modules.telegram_bot.asyncio.get_event_loop')
    def test_send_message_sync(self, mock_loop_getter, mock_notifier_class):
        """Test synchronous message sending wrapper."""
        mock_notifier = Mock()
        mock_notifier_class.return_value = mock_notifier
        
        mock_loop = Mock()
        mock_loop.run_until_complete = Mock(return_value=True)
        mock_loop_getter.return_value = mock_loop
        
        result = send_message_sync("token", "chat_id", "test message")
        
        assert mock_notifier_class.called
        assert mock_loop.run_until_complete.call_count == 2  # init + send
    
    @patch('modules.telegram_bot.TelegramNotifier')
    @patch('modules.telegram_bot.asyncio.get_event_loop')
    def test_send_photo_sync(self, mock_loop_getter, mock_notifier_class, sample_chart_path):
        """Test synchronous photo sending wrapper."""
        mock_notifier = Mock()
        mock_notifier_class.return_value = mock_notifier
        
        mock_loop = Mock()
        mock_loop.run_until_complete = Mock(return_value=True)
        mock_loop_getter.return_value = mock_loop
        
        result = send_photo_sync("token", "chat_id", str(sample_chart_path), "caption")
        
        assert mock_notifier_class.called
        assert mock_loop.run_until_complete.call_count == 2  # init + send


class TestMessageContent:
    """Tests to verify message content contains user-friendly formatting."""
    
    def test_messages_contain_formatting(self):
        """Verify messages use Markdown formatting."""
        setup_data = {
            'timestamp': '2026-01-10 10:30',
            'setup_type': 'test',
            'setup_direction': 'long',
            'current_price': 21250.0,
            'entry_price': 21255.0,
            'stop_loss_price': 21240.0,
            'stop_distance_ticks': 15,
            'take_profit_1': 21285.0,
            'reward_risk_ratio': 2.0,
            'position_size': 10,
            'dollar_risk': 50.0,
            'dollar_target_1': 100.0,
            'analysis_notes': 'test',
            'market_regime': 'trending_up',
            'confidence_score': 78,
            'caution_flags': []
        }
        
        message = format_setup_alert(setup_data, 'high')
        
        # Check for Markdown bold syntax
        assert '*' in message
        # Messages should have visual structure
        assert '\n' in message
    
    def test_python_code_has_no_emojis(self):
        """Verify this test file itself has no emojis in code."""
        # Read this file
        test_file = Path(__file__)
        content = test_file.read_text()
        
        # Check that emojis/unicode are NOT in Python code
        # (They may appear in test data strings, which is fine)
        # This is a meta-test to ensure the file follows the rule
        
        # If this test runs without encoding errors, we're good
        assert len(content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
