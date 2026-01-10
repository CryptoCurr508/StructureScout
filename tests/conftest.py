# StructureScout Testing Configuration

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_config():
    """Fixture for mock configuration."""
    from unittest.mock import Mock
    config = Mock()
    config.mt5_login = "test_login"
    config.mt5_password = "test_password"
    config.mt5_server = "test_server"
    config.openai_api_key = "test_api_key"
    config.current_mode = "observation"
    config.trading_symbol = "NAS100"
    config.risk_per_trade = 0.01
    return config


@pytest.fixture
def sample_chart_path(tmp_path):
    """Fixture for sample chart image path."""
    from PIL import Image
    img = Image.new('RGB', (1920, 1080), color='white')
    chart_path = tmp_path / "test_chart.png"
    img.save(chart_path)
    return chart_path


@pytest.fixture
def mock_gpt_response():
    """Fixture for mock GPT-4o-mini response."""
    return {
        "timestamp": "2026-01-10 10:30 EST",
        "current_price": 21250.0,
        "market_regime": "trending_up",
        "regime_reasoning": "Higher highs and higher lows",
        "valid_setup_exists": True,
        "setup_type": "structure_break",
        "setup_direction": "long",
        "entry_price": 21255.0,
        "stop_loss_price": 21240.0,
        "stop_loss_reasoning": "Below recent swing low",
        "take_profit_1": 21285.0,
        "take_profit_1_reasoning": "Previous day high resistance",
        "take_profit_2": 21310.0,
        "stop_distance_ticks": 15,
        "reward_risk_ratio": 2.0,
        "setup_quality": "high",
        "confidence_score": 78,
        "analysis_notes": "Clean structure break with good R:R",
        "trade_recommendation": "enter_immediately",
        "caution_flags": []
    }
