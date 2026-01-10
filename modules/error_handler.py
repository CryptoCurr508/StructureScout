"""
Error Handler Module

Centralized error handling and logging.
Classifies errors by severity and takes appropriate action.

No emojis or unicode characters in this file.
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)


class ErrorSeverity:
    """Error severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


def classify_error_severity(error: Exception) -> str:
    """
    Classify error severity based on type and context.
    
    Args:
        error: Exception to classify
        
    Returns:
        Severity level string
    """
    error_type = type(error).__name__
    
    # Critical errors
    critical_types = ['MT5ConnectionError', 'SystemExit', 'KeyboardInterrupt']
    if error_type in critical_types or 'connection' in str(error).lower():
        return ErrorSeverity.CRITICAL
    
    # High priority errors
    high_types = ['GPTAnalysisError', 'TelegramBotError', 'APIError']
    if error_type in high_types or 'api' in str(error).lower():
        return ErrorSeverity.HIGH
    
    # Medium priority
    medium_types = ['DataLoggerError', 'ValueError', 'TypeError']
    if error_type in medium_types:
        return ErrorSeverity.MEDIUM
    
    # Default to low
    return ErrorSeverity.LOW


def log_error(error: Exception, context: str, severity: Optional[str] = None) -> None:
    """
    Log error with context and severity.
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
        severity: Error severity (auto-classified if None)
    """
    if severity is None:
        severity = classify_error_severity(error)
    
    error_msg = f"[{severity.upper()}] {context}: {str(error)}"
    
    if severity == ErrorSeverity.CRITICAL:
        logger.critical(error_msg)
        logger.critical(traceback.format_exc())
    elif severity == ErrorSeverity.HIGH:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    elif severity == ErrorSeverity.MEDIUM:
        logger.warning(error_msg)
    else:
        logger.info(error_msg)


def handle_error(error: Exception, context: str, notify_user: bool = True) -> Dict[str, Any]:
    """
    Handle error with appropriate action.
    
    Args:
        error: Exception to handle
        context: Context string
        notify_user: Whether to send notification
        
    Returns:
        Dictionary with error details and actions taken
    """
    severity = classify_error_severity(error)
    log_error(error, context, severity)
    
    result = {
        'error_type': type(error).__name__,
        'message': str(error),
        'severity': severity,
        'context': context,
        'timestamp': datetime.now().isoformat(),
        'notification_sent': False,
        'system_halted': False
    }
    
    # Take action based on severity
    if severity == ErrorSeverity.CRITICAL:
        result['system_halted'] = True
        logger.critical("CRITICAL ERROR: System may need to halt")
    
    if notify_user and severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
        result['notification_sent'] = True
        logger.info("User notification required")
    
    return result


# Command-line testing interface
if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        print("Testing Error Handler Module...")
        print("-" * 50)
        
        # Test error classification
        print("Testing error classification...")
        test_error = ConnectionError("Connection lost")
        severity = classify_error_severity(test_error)
        print(f"  ConnectionError classified as: {severity}")
        assert severity == ErrorSeverity.CRITICAL
        
        # Test error logging
        print("\nTesting error logging...")
        test_error = ValueError("Invalid value")
        log_error(test_error, "test_context")
        print(f"  [OK] Error logged")
        
        # Test error handling
        print("\nTesting error handling...")
        result = handle_error(test_error, "test_context")
        print(f"  Severity: {result['severity']}")
        print(f"  Notification sent: {result['notification_sent']}")
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
    else:
        print("Usage: python3 -m modules.error_handler --test")
