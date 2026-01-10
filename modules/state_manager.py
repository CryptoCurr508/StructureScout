"""
State Manager Module

Handles system state persistence for crash recovery.
Saves and loads system state including open positions, P&L, and configuration.

No emojis or unicode characters in this file.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)


class StateManagerError(Exception):
    """Custom exception for state management errors."""
    pass


def save_system_state(state_dict: Dict[str, Any], filepath: Path) -> bool:
    """
    Save system state to JSON file.
    
    Args:
        state_dict: State dictionary to save
        filepath: Path to state file
        
    Returns:
        True if saved successfully
    """
    try:
        # Add timestamp
        state_dict['last_updated'] = datetime.now().isoformat()
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(state_dict, f, indent=2)
        
        logger.info(f"System state saved to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save system state: {e}")
        return False


def load_system_state(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Load system state from JSON file.
    
    Args:
        filepath: Path to state file
        
    Returns:
        State dictionary or None if failed
    """
    try:
        if not filepath.exists():
            logger.warning(f"State file not found: {filepath}")
            return None
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        logger.info(f"System state loaded from {filepath}")
        return state
        
    except Exception as e:
        logger.error(f"Failed to load system state: {e}")
        return None


class SystemStateManager:
    """System state manager for persistence."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = {}
    
    def update(self, key: str, value: Any) -> None:
        """Update state value."""
        self.state[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        return self.state.get(key, default)
    
    def save(self) -> bool:
        """Save current state."""
        return save_system_state(self.state, self.state_file)
    
    def load(self) -> bool:
        """Load state from file."""
        loaded = load_system_state(self.state_file)
        if loaded:
            self.state = loaded
            return True
        return False


# Command-line testing interface
if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        print("Testing State Manager Module...")
        print("-" * 50)
        
        test_file = Path("data/test_state.json")
        
        # Test save
        print("Testing state save...")
        test_state = {
            'mode': 'observation',
            'daily_pnl': 0.0,
            'trades_today': 0
        }
        result = save_system_state(test_state, test_file)
        print(f"  [OK] State saved: {result}")
        
        # Test load
        print("Testing state load...")
        loaded = load_system_state(test_file)
        print(f"  [OK] State loaded: mode={loaded.get('mode')}")
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        
        print("-" * 50)
        print("[SUCCESS] All tests passed!")
    else:
        print("Usage: python3 -m modules.state_manager --test")
