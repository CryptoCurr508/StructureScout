"""
GPT Analysis Module

Sends chart images to OpenAI GPT-4o-mini Vision API for pattern analysis.
Handles prompt engineering, API communication, response parsing, and setup validation.

No emojis or unicode characters in this file.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import openai
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)


class GPTAnalysisError(Exception):
    """Custom exception for GPT analysis errors."""
    pass


def encode_image_to_base64(image_path: Path) -> str:
    """
    Encode image file to base64 string for API transmission.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded string
        
    Raises:
        FileNotFoundError: If image file doesn't exist
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def build_system_prompt() -> str:
    """
    Build system prompt for GPT-4o-mini with trading expert persona.
    
    Returns:
        System prompt string
    """
    return """You are an expert NAS100 daytrader analyzing 5-minute charts for structure-based trading setups.

Analyze the provided chart image and identify:
1. Market regime (trending up, trending down, or ranging)
2. Presence of valid trade setups (opening range breakout, structure break, mean reversion)
3. Exact entry, stop loss, and take profit levels based on price structure
4. Setup quality rating (High/Medium/Low confidence)

Respond ONLY in valid JSON format with no additional text. Use the exact field names provided in the template."""


def build_user_prompt(
    timestamp: str,
    account_balance: float,
    risk_amount: float,
    prev_day_high: float,
    prev_day_low: float,
    vwap: float,
    or_high: Optional[float] = None,
    or_low: Optional[float] = None
) -> str:
    """
    Build user prompt with market context and JSON template.
    
    Args:
        timestamp: Current time in EST
        account_balance: Account balance in dollars
        risk_amount: Dollar risk per trade (1% of balance)
        prev_day_high: Previous day high price
        prev_day_low: Previous day low price
        vwap: Current VWAP level
        or_high: Opening range high (if after 10 AM)
        or_low: Opening range low (if after 10 AM)
        
    Returns:
        User prompt string with JSON template
    """
    or_info = ""
    if or_high and or_low:
        or_info = f"""- Opening Range High: {or_high}
- Opening Range Low: {or_low}"""
    
    prompt = f"""Current Time: {timestamp} EST
Account Balance: ${account_balance:.2f}
Risk Per Trade: 1% = ${risk_amount:.2f}

Analyze this NAS100 5-minute chart and provide:

{{
  "timestamp": "{timestamp}",
  "current_price": <float>,
  "market_regime": "<trending_up|trending_down|ranging|unclear>",
  "regime_reasoning": "<brief explanation>",
  
  "valid_setup_exists": <true|false>,
  "setup_type": "<opening_range_breakout|structure_break|mean_reversion|none>",
  "setup_direction": "<long|short|none>",
  
  "entry_price": <float or null>,
  "stop_loss_price": <float or null>,
  "stop_loss_reasoning": "<why this level invalidates>",
  "take_profit_1": <float or null>,
  "take_profit_1_reasoning": "<next structural level>",
  "take_profit_2": <float or null>,
  
  "stop_distance_ticks": <int or null>,
  "reward_risk_ratio": <float or null>,
  
  "setup_quality": "<high|medium|low|none>",
  "confidence_score": <0-100>,
  "analysis_notes": "<key observations>",
  
  "trade_recommendation": "<enter_immediately|wait_for_confirmation|no_trade>",
  "caution_flags": [<list of any concerns>]
}}

Reference levels visible on chart:
- Previous Day High: {prev_day_high}
- Previous Day Low: {prev_day_low}
- Current VWAP: {vwap}
{or_info}

Identify setups using ONLY observable price structure and these reference levels."""
    
    return prompt


def analyze_chart_with_gpt4(
    image_path: Path,
    api_key: str,
    timestamp: str,
    account_balance: float,
    risk_amount: float,
    prev_day_high: float,
    prev_day_low: float,
    vwap: float,
    or_high: Optional[float] = None,
    or_low: Optional[float] = None,
    model: str = "gpt-4o-mini",
    max_tokens: int = 800,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Analyze chart image with GPT-4o-mini Vision API.
    
    Args:
        image_path: Path to chart screenshot
        api_key: OpenAI API key
        timestamp: Current timestamp EST
        account_balance: Account balance
        risk_amount: Risk amount per trade
        prev_day_high: Previous day high
        prev_day_low: Previous day low
        vwap: VWAP level
        or_high: Opening range high (optional)
        or_low: Opening range low (optional)
        model: OpenAI model name
        max_tokens: Maximum response tokens
        temperature: Model temperature
        
    Returns:
        Parsed JSON response as dictionary
        
    Raises:
        GPTAnalysisError: If API call or parsing fails
    """
    logger.info(f"Analyzing chart: {image_path}")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Encode image
        base64_image = encode_image_to_base64(image_path)
        
        # Build prompts
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            timestamp=timestamp,
            account_balance=account_balance,
            risk_amount=risk_amount,
            prev_day_high=prev_day_high,
            prev_day_low=prev_day_low,
            vwap=vwap,
            or_high=or_high,
            or_low=or_low
        )
        
        # Make API call
        logger.info("Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract response content
        content = response.choices[0].message.content
        logger.info("Received response from OpenAI")
        
        # Parse JSON response
        parsed = parse_ai_response(content)
        
        return parsed
        
    except openai.APIError as e:
        error_msg = f"OpenAI API error: {e}"
        logger.error(error_msg)
        raise GPTAnalysisError(error_msg)
    
    except Exception as e:
        error_msg = f"Analysis failed: {e}"
        logger.error(error_msg)
        raise GPTAnalysisError(error_msg)


def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON response from GPT-4o-mini.
    
    Args:
        response_text: Raw response text from API
        
    Returns:
        Parsed dictionary with all fields
        
    Raises:
        GPTAnalysisError: If JSON parsing fails or required fields missing
    """
    try:
        # Try to extract JSON from response
        # Sometimes GPT adds markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            json_str = response_text.strip()
        
        # Parse JSON
        parsed = json.loads(json_str)
        
        # Validate required fields
        required_fields = [
            'current_price', 'market_regime', 'valid_setup_exists',
            'setup_quality', 'confidence_score', 'trade_recommendation'
        ]
        
        missing_fields = [field for field in required_fields if field not in parsed]
        if missing_fields:
            raise GPTAnalysisError(f"Missing required fields: {missing_fields}")
        
        # Ensure numeric fields are correct type
        if parsed.get('current_price'):
            parsed['current_price'] = float(parsed['current_price'])
        if parsed.get('entry_price'):
            parsed['entry_price'] = float(parsed['entry_price'])
        if parsed.get('stop_loss_price'):
            parsed['stop_loss_price'] = float(parsed['stop_loss_price'])
        if parsed.get('confidence_score'):
            parsed['confidence_score'] = int(parsed['confidence_score'])
        
        logger.info(f"Parsed response: regime={parsed['market_regime']}, "
                   f"valid_setup={parsed['valid_setup_exists']}, "
                   f"quality={parsed['setup_quality']}")
        
        return parsed
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON response: {e}\nResponse: {response_text}"
        logger.error(error_msg)
        raise GPTAnalysisError(error_msg)
    
    except Exception as e:
        error_msg = f"Response parsing error: {e}"
        logger.error(error_msg)
        raise GPTAnalysisError(error_msg)


def validate_setup_rules(parsed_response: Dict[str, Any], config: Any) -> tuple[bool, str]:
    """
    Validate setup against strategy rules and filters.
    
    Args:
        parsed_response: Parsed AI response
        config: Configuration object with filter settings
        
    Returns:
        Tuple of (is_valid, rejection_reason)
    """
    # Check if setup exists
    if not parsed_response.get('valid_setup_exists'):
        return False, "No valid setup identified"
    
    # Check confidence score
    min_confidence = config.min_confidence_score
    confidence = parsed_response.get('confidence_score', 0)
    if confidence < min_confidence:
        return False, f"Confidence {confidence}% below minimum {min_confidence}%"
    
    # Check reward:risk ratio
    min_rr = config.min_reward_risk_ratio
    rr_ratio = parsed_response.get('reward_risk_ratio')
    if rr_ratio and rr_ratio < min_rr:
        return False, f"R:R ratio {rr_ratio:.2f} below minimum {min_rr}"
    
    # Check stop distance
    stop_distance = parsed_response.get('stop_distance_ticks')
    if stop_distance:
        min_stop = config.get('setup_filters.min_stop_distance_ticks', 10)
        max_stop = config.get('setup_filters.max_stop_distance_ticks', 50)
        
        if stop_distance < min_stop:
            return False, f"Stop distance {stop_distance} ticks too tight (min: {min_stop})"
        if stop_distance > max_stop:
            return False, f"Stop distance {stop_distance} ticks too wide (max: {max_stop})"
    
    # All filters passed
    return True, "Setup meets all criteria"


def calculate_position_size(
    setup_data: Dict[str, Any],
    account_balance: float,
    risk_percentage: float = 0.01,
    point_value: float = 0.25
) -> Dict[str, float]:
    """
    Calculate position size based on risk management rules.
    
    Args:
        setup_data: Parsed setup data with entry and stop
        account_balance: Current account balance
        risk_percentage: Risk as decimal (0.01 = 1%)
        point_value: Dollar value per point (0.25 for NAS100 micro)
        
    Returns:
        Dictionary with position_size, dollar_risk, dollar_target
    """
    risk_amount = account_balance * risk_percentage
    
    stop_distance = setup_data.get('stop_distance_ticks', 0)
    if stop_distance == 0:
        logger.warning("Stop distance is 0, cannot calculate position size")
        return {
            'position_size': 0,
            'dollar_risk': risk_amount,
            'dollar_target_1': 0
        }
    
    # Calculate position size
    dollar_risk_per_contract = stop_distance * point_value
    position_size = int(risk_amount / dollar_risk_per_contract)
    
    # Calculate potential profit
    rr_ratio = setup_data.get('reward_risk_ratio', 0)
    dollar_target_1 = risk_amount * rr_ratio
    
    return {
        'position_size': position_size,
        'dollar_risk': risk_amount,
        'dollar_target_1': dollar_target_1,
        'risk_per_contract': dollar_risk_per_contract
    }


# Command-line testing interface
if __name__ == "__main__":
    import sys
    from config import get_config
    from PIL import Image
    
    if "--test" in sys.argv:
        print("Testing GPT Analysis Module...")
        print("-" * 50)
        
        # Load configuration
        try:
            config = get_config()
            print(f"[OK] Configuration loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load configuration: {e}")
            sys.exit(1)
        
        # Test prompt building
        print("Testing prompt construction...")
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            timestamp="2026-01-10 10:30",
            account_balance=5000.0,
            risk_amount=50.0,
            prev_day_high=21300.0,
            prev_day_low=21200.0,
            vwap=21250.0
        )
        print(f"[OK] System prompt: {len(system_prompt)} chars")
        print(f"[OK] User prompt: {len(user_prompt)} chars")
        
        # Test JSON parsing
        print("Testing JSON parsing...")
        sample_response = """{
            "timestamp": "2026-01-10 10:30 EST",
            "current_price": 21255.0,
            "market_regime": "trending_up",
            "regime_reasoning": "Higher highs and higher lows",
            "valid_setup_exists": true,
            "setup_type": "structure_break",
            "setup_direction": "long",
            "entry_price": 21260.0,
            "stop_loss_price": 21245.0,
            "stop_loss_reasoning": "Below recent swing low",
            "take_profit_1": 21290.0,
            "take_profit_1_reasoning": "Previous day high",
            "take_profit_2": 21310.0,
            "stop_distance_ticks": 15,
            "reward_risk_ratio": 2.0,
            "setup_quality": "high",
            "confidence_score": 78,
            "analysis_notes": "Clean structure break",
            "trade_recommendation": "enter_immediately",
            "caution_flags": []
        }"""
        
        parsed = parse_ai_response(sample_response)
        print(f"[OK] Parsed {len(parsed)} fields")
        
        # Test position sizing
        print("Testing position size calculation...")
        position_info = calculate_position_size(
            setup_data=parsed,
            account_balance=5000.0,
            risk_percentage=0.01
        )
        print(f"[OK] Position size: {position_info['position_size']} contracts")
        print(f"[OK] Dollar risk: ${position_info['dollar_risk']:.2f}")
        print(f"[OK] Dollar target: ${position_info['dollar_target_1']:.2f}")
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
        print()
        print("Note: To test actual API calls, create a test chart image and run:")
        print("  python3 -m modules.gpt_analysis --api-test <image_path>")
        
    else:
        print("Usage: python3 -m modules.gpt_analysis --test")
