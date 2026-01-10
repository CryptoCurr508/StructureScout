"""
Unit tests for GPT Analysis Module

Tests GPT-4o-mini integration, prompt building, response parsing, and validation logic.
Uses mocks to avoid actual API calls during testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.gpt_analysis import (
    GPTAnalysisError,
    encode_image_to_base64,
    build_system_prompt,
    build_user_prompt,
    analyze_chart_with_gpt4,
    parse_ai_response,
    validate_setup_rules,
    calculate_position_size
)


class TestImageEncoding:
    """Tests for image encoding functions."""
    
    def test_encode_image_success(self, sample_chart_path):
        """Test successful image encoding."""
        encoded = encode_image_to_base64(sample_chart_path)
        
        assert isinstance(encoded, str)
        assert len(encoded) > 0
    
    def test_encode_image_not_found(self):
        """Test encoding non-existent image."""
        with pytest.raises(FileNotFoundError):
            encode_image_to_base64(Path("nonexistent.png"))


class TestPromptBuilding:
    """Tests for prompt construction."""
    
    def test_build_system_prompt(self):
        """Test system prompt creation."""
        prompt = build_system_prompt()
        
        assert isinstance(prompt, str)
        assert "NAS100" in prompt
        assert "JSON" in prompt
        assert len(prompt) > 100
    
    def test_build_user_prompt_basic(self):
        """Test user prompt with basic parameters."""
        prompt = build_user_prompt(
            timestamp="2026-01-10 10:30",
            account_balance=5000.0,
            risk_amount=50.0,
            prev_day_high=21300.0,
            prev_day_low=21200.0,
            vwap=21250.0
        )
        
        assert isinstance(prompt, str)
        assert "2026-01-10 10:30" in prompt
        assert "5000.00" in prompt
        assert "50.00" in prompt
        assert "21300.0" in prompt
        assert len(prompt) > 500
    
    def test_build_user_prompt_with_opening_range(self):
        """Test user prompt with opening range levels."""
        prompt = build_user_prompt(
            timestamp="2026-01-10 10:30",
            account_balance=5000.0,
            risk_amount=50.0,
            prev_day_high=21300.0,
            prev_day_low=21200.0,
            vwap=21250.0,
            or_high=21270.0,
            or_low=21230.0
        )
        
        assert "Opening Range High" in prompt
        assert "21270.0" in prompt
        assert "21230.0" in prompt


class TestResponseParsing:
    """Tests for AI response parsing."""
    
    def test_parse_valid_json(self, mock_gpt_response):
        """Test parsing valid JSON response."""
        json_str = json.dumps(mock_gpt_response)
        parsed = parse_ai_response(json_str)
        
        assert parsed['current_price'] == 21250.0
        assert parsed['market_regime'] == "trending_up"
        assert parsed['valid_setup_exists'] is True
        assert parsed['confidence_score'] == 78
    
    def test_parse_json_with_markdown(self, mock_gpt_response):
        """Test parsing JSON wrapped in markdown code blocks."""
        json_str = "```json\n" + json.dumps(mock_gpt_response) + "\n```"
        parsed = parse_ai_response(json_str)
        
        assert parsed['current_price'] == 21250.0
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        with pytest.raises(GPTAnalysisError):
            parse_ai_response("This is not JSON")
    
    def test_parse_missing_required_fields(self):
        """Test parsing JSON with missing required fields."""
        incomplete = {"current_price": 21250.0}
        json_str = json.dumps(incomplete)
        
        with pytest.raises(GPTAnalysisError):
            parse_ai_response(json_str)
    
    def test_type_conversion(self):
        """Test automatic type conversion for numeric fields."""
        response = {
            "timestamp": "2026-01-10 10:30 EST",
            "current_price": "21250.0",  # String
            "entry_price": "21255.0",  # String
            "confidence_score": "78",  # String
            "market_regime": "trending_up",
            "valid_setup_exists": True,
            "setup_quality": "high",
            "trade_recommendation": "enter_immediately"
        }
        json_str = json.dumps(response)
        parsed = parse_ai_response(json_str)
        
        assert isinstance(parsed['current_price'], float)
        assert isinstance(parsed['entry_price'], float)
        assert isinstance(parsed['confidence_score'], int)


class TestSetupValidation:
    """Tests for setup validation logic."""
    
    def test_validate_valid_setup(self, mock_gpt_response, mock_config):
        """Test validation of valid setup."""
        is_valid, reason = validate_setup_rules(mock_gpt_response, mock_config)
        
        assert is_valid is True
        assert "meets all criteria" in reason
    
    def test_validate_no_setup(self, mock_config):
        """Test validation when no setup exists."""
        response = {
            'valid_setup_exists': False,
            'confidence_score': 50
        }
        
        is_valid, reason = validate_setup_rules(response, mock_config)
        
        assert is_valid is False
        assert "No valid setup" in reason
    
    def test_validate_low_confidence(self, mock_gpt_response, mock_config):
        """Test validation with low confidence score."""
        mock_gpt_response['confidence_score'] = 30
        mock_config.min_confidence_score = 65
        
        is_valid, reason = validate_setup_rules(mock_gpt_response, mock_config)
        
        assert is_valid is False
        assert "Confidence" in reason
    
    def test_validate_low_reward_risk(self, mock_gpt_response, mock_config):
        """Test validation with insufficient R:R ratio."""
        mock_gpt_response['reward_risk_ratio'] = 1.0
        mock_config.min_reward_risk_ratio = 1.5
        
        is_valid, reason = validate_setup_rules(mock_gpt_response, mock_config)
        
        assert is_valid is False
        assert "R:R ratio" in reason


class TestPositionSizing:
    """Tests for position size calculation."""
    
    def test_calculate_position_size_standard(self):
        """Test standard position size calculation."""
        setup_data = {
            'stop_distance_ticks': 20,
            'reward_risk_ratio': 2.0
        }
        
        result = calculate_position_size(
            setup_data=setup_data,
            account_balance=5000.0,
            risk_percentage=0.01,
            point_value=0.25
        )
        
        assert result['dollar_risk'] == 50.0  # 1% of 5000
        assert result['position_size'] == 10  # 50 / (20 * 0.25)
        assert result['dollar_target_1'] == 100.0  # 50 * 2.0
    
    def test_calculate_position_size_zero_stop(self):
        """Test position sizing with zero stop distance."""
        setup_data = {
            'stop_distance_ticks': 0,
            'reward_risk_ratio': 2.0
        }
        
        result = calculate_position_size(
            setup_data=setup_data,
            account_balance=5000.0
        )
        
        assert result['position_size'] == 0
        assert result['dollar_risk'] == 50.0
    
    def test_calculate_position_size_large_stop(self):
        """Test position sizing with large stop distance."""
        setup_data = {
            'stop_distance_ticks': 50,
            'reward_risk_ratio': 1.5
        }
        
        result = calculate_position_size(
            setup_data=setup_data,
            account_balance=10000.0,
            risk_percentage=0.01
        )
        
        # 1% of 10000 = 100
        # Risk per contract = 50 * 0.25 = 12.5
        # Position = 100 / 12.5 = 8
        assert result['position_size'] == 8
        assert result['dollar_risk'] == 100.0


class TestAPIIntegration:
    """Tests for API integration (mocked)."""
    
    @patch('modules.gpt_analysis.OpenAI')
    def test_analyze_chart_success(self, mock_openai, sample_chart_path, mock_gpt_response):
        """Test successful chart analysis."""
        # Setup mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_gpt_response)
        mock_client.chat.completions.create.return_value = mock_response
        
        # Analyze
        result = analyze_chart_with_gpt4(
            image_path=sample_chart_path,
            api_key="test_key",
            timestamp="2026-01-10 10:30",
            account_balance=5000.0,
            risk_amount=50.0,
            prev_day_high=21300.0,
            prev_day_low=21200.0,
            vwap=21250.0
        )
        
        assert result['current_price'] == 21250.0
        assert mock_client.chat.completions.create.called
    
    @patch('modules.gpt_analysis.OpenAI')
    def test_analyze_chart_api_error(self, mock_openai, sample_chart_path):
        """Test chart analysis with API error."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Simulate API error
        from openai import APIError
        mock_client.chat.completions.create.side_effect = APIError("API Error", response=Mock(), body=None)
        
        with pytest.raises(GPTAnalysisError):
            analyze_chart_with_gpt4(
                image_path=sample_chart_path,
                api_key="test_key",
                timestamp="2026-01-10 10:30",
                account_balance=5000.0,
                risk_amount=50.0,
                prev_day_high=21300.0,
                prev_day_low=21200.0,
                vwap=21250.0
            )


class TestWorkflows:
    """Integration-style workflow tests."""
    
    @patch('modules.gpt_analysis.OpenAI')
    def test_full_analysis_workflow(self, mock_openai, sample_chart_path, mock_gpt_response, mock_config):
        """Test complete analysis workflow."""
        # Setup mock API
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_gpt_response)
        mock_client.chat.completions.create.return_value = mock_response
        
        # Analyze chart
        result = analyze_chart_with_gpt4(
            image_path=sample_chart_path,
            api_key="test_key",
            timestamp="2026-01-10 10:30",
            account_balance=5000.0,
            risk_amount=50.0,
            prev_day_high=21300.0,
            prev_day_low=21200.0,
            vwap=21250.0
        )
        
        # Validate setup
        is_valid, reason = validate_setup_rules(result, mock_config)
        assert is_valid is True
        
        # Calculate position
        position_info = calculate_position_size(
            setup_data=result,
            account_balance=5000.0
        )
        assert position_info['position_size'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
