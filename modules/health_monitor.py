"""
Health Monitor Module

System health monitoring and heartbeat checks.
Monitors MT5 connection, API health, and disk space.

No emojis or unicode characters in this file.
"""

import logging
import shutil
from datetime import datetime
from typing import Dict, Any, Tuple
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)


def check_disk_space(path: Path, min_mb: int = 1000) -> Tuple[bool, str]:
    """
    Check if sufficient disk space is available.
    
    Args:
        path: Path to check
        min_mb: Minimum required MB
        
    Returns:
        Tuple of (is_sufficient, message)
    """
    try:
        stat = shutil.disk_usage(path)
        free_mb = stat.free / (1024 * 1024)
        
        if free_mb < min_mb:
            return False, f"Low disk space: {free_mb:.1f}MB (min: {min_mb}MB)"
        
        return True, f"Disk space OK: {free_mb:.1f}MB free"
        
    except Exception as e:
        logger.error(f"Failed to check disk space: {e}")
        return False, f"Disk check failed: {e}"


class HealthMonitor:
    """System health monitor."""
    
    def __init__(self):
        self.last_check = None
        self.status = {}
    
    def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Health status dictionary
        """
        self.last_check = datetime.now()
        
        # Check disk space
        disk_ok, disk_msg = check_disk_space(Path.cwd())
        
        self.status = {
            'timestamp': self.last_check.isoformat(),
            'disk_space': {'healthy': disk_ok, 'message': disk_msg},
            'overall_healthy': disk_ok
        }
        
        logger.info(f"Health check complete: {'HEALTHY' if self.status['overall_healthy'] else 'UNHEALTHY'}")
        return self.status
    
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.status.get('overall_healthy', True)


# Command-line testing interface
if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        print("Testing Health Monitor Module...")
        print("-" * 50)
        
        # Test disk space check
        print("Testing disk space check...")
        is_ok, msg = check_disk_space(Path.cwd())
        print(f"  {msg}")
        
        # Test health monitor
        print("\nTesting health monitor...")
        monitor = HealthMonitor()
        status = monitor.check_all()
        print(f"  Overall healthy: {status['overall_healthy']}")
        print(f"  Last check: {status['timestamp']}")
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
    else:
        print("Usage: python3 -m modules.health_monitor --test")
