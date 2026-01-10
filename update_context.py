#!/usr/bin/env python3
"""
Universal Context Updater for AI Agent Handoff - StructureScout Edition

Automatically updates context files with latest project state.
Run this script before reaching conversation limits to ensure
the next AI agent has up-to-date context.

Usage:
    python update_context.py
    python update_context.py --verbose
    python update_context.py --check-only
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Project paths
PROJECT_ROOT = Path(__file__).parent
CONTEXT_MD = PROJECT_ROOT / "AI_AGENT_CONTEXT.md"
STATE_JSON = PROJECT_ROOT / "project_state.json"
CONVERSATION_MD = PROJECT_ROOT / "CONVERSATION_SUMMARY.md"
NEW_AGENT_MD = PROJECT_ROOT / "NEW_AGENT_START_HERE.md"

# Optional: Import project modules if they exist
try:
    DATA_DIR = PROJECT_ROOT / "data"
    MODULES_DIR = PROJECT_ROOT / "modules"
except ImportError:
    DATA_DIR = None
    MODULES_DIR = None


def log(message: str, verbose: bool = True) -> None:
    """Print message if verbose mode enabled."""
    if verbose:
        # Remove any emoji/unicode characters for clean output
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(clean_message)


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def get_formatted_timestamp() -> str:
    """Get current timestamp in human-readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_state_json() -> Dict[str, Any]:
    """Load existing state JSON or create new structure."""
    if STATE_JSON.exists():
        with open(STATE_JSON, 'r') as f:
            return json.load(f)
    else:
        # Create new state structure
        return {
            "last_update": None,
            "agent_version": "v1.0",
            "project_info": {},
            "current_state": {},
            "metrics": {},
            "trading_state": {}
        }


def count_project_files() -> Dict[str, int]:
    """Count files in project directories."""
    counts = {
        "modules": 0,
        "data_files": 0,
        "config_files": 0,
        "planning_docs": 0
    }
    
    # Count module files
    modules_dir = PROJECT_ROOT / "modules"
    if modules_dir.exists():
        counts["modules"] = len(list(modules_dir.glob("*.py")))
    
    # Count data files
    data_dir = PROJECT_ROOT / "data"
    if data_dir.exists():
        counts["data_files"] = len(list(data_dir.glob("*.csv"))) + \
                               len(list(data_dir.glob("*.log")))
    
    # Count config files
    config_files = ["config.yaml", ".env", "requirements.txt"]
    counts["config_files"] = sum(1 for f in config_files if (PROJECT_ROOT / f).exists())
    
    # Count planning docs
    planning_files = [
        "StructureScout.txt",
        "AI_AGENT_CONTEXT.md",
        "project_state.json",
        "NEW_AGENT_START_HERE.md",
        "CONVERSATION_SUMMARY.md"
    ]
    counts["planning_docs"] = sum(1 for f in planning_files if (PROJECT_ROOT / f).exists())
    
    return counts


def get_implementation_status() -> Dict[str, str]:
    """Check which components are implemented."""
    status = {}
    
    # Check if main.py exists
    status["main_script"] = "implemented" if (PROJECT_ROOT / "main.py").exists() else "not_started"
    
    # Check module files
    module_files = [
        "mt5_connection.py",
        "gpt_analysis.py",
        "telegram_bot.py",
        "data_logger.py",
        "scheduler.py",
        "performance_analyzer.py",
        "error_handler.py",
        "health_monitor.py",
        "risk_manager.py",
        "trade_executor.py",
        "news_calendar.py",
        "state_manager.py"
    ]
    
    modules_dir = PROJECT_ROOT / "modules"
    if modules_dir.exists():
        for module in module_files:
            module_name = module.replace(".py", "")
            module_path = modules_dir / module
            if module_path.exists():
                # Check file size to determine if it's just a stub
                size = module_path.stat().st_size
                status[module_name] = "implemented" if size > 500 else "started"
            else:
                status[module_name] = "not_started"
    else:
        for module in module_files:
            module_name = module.replace(".py", "")
            status[module_name] = "not_started"
    
    return status


def read_trading_metrics() -> Optional[Dict[str, Any]]:
    """Read metrics from trading log if it exists."""
    log_file = DATA_DIR / "trading_log.csv" if DATA_DIR else None
    
    if log_file and log_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(log_file)
            
            return {
                "total_setups": len(df),
                "valid_setups": df['valid_setup'].sum() if 'valid_setup' in df else 0,
                "high_quality_setups": len(df[df['setup_quality'] == 'high']) if 'setup_quality' in df else 0,
                "average_confidence": df['confidence_score'].mean() if 'confidence_score' in df else None,
                "trades_executed": df['actual_trade_taken'].sum() if 'actual_trade_taken' in df else 0
            }
        except Exception as e:
            log(f"Warning: Could not read trading log: {e}", verbose=True)
            return None
    
    return None


def update_state_json(verbose: bool = True) -> None:
    """Update machine-readable state file."""
    log("[*] Updating project_state.json...", verbose)
    
    # Load existing state
    state = load_state_json()
    
    # Update timestamp
    state['last_update'] = get_current_timestamp()
    
    # Update file counts
    file_counts = count_project_files()
    log(f"   [+] Files found: {file_counts}", verbose)
    
    # Update implementation status
    impl_status = get_implementation_status()
    if 'current_state' not in state:
        state['current_state'] = {}
    state['current_state']['implementation_progress'] = impl_status
    
    # Update metrics from data files if available
    metrics = read_trading_metrics()
    if metrics:
        state['metrics'].update(metrics)
        log(f"   [+] Updated metrics from trading log", verbose)
    
    # Save updated state
    with open(STATE_JSON, 'w') as f:
        json.dump(state, f, indent=2)
    
    log(f"   [OK] Updated: {STATE_JSON}", verbose)


def update_context_md(verbose: bool = True) -> None:
    """Update human-readable context file."""
    log("[*] Updating AI_AGENT_CONTEXT.md...", verbose)
    
    if not CONTEXT_MD.exists():
        log(f"   [WARN] {CONTEXT_MD} not found - skipping", verbose)
        return
    
    content = CONTEXT_MD.read_text()
    
    # Update timestamp in header
    new_timestamp = get_formatted_timestamp()
    content = re.sub(
        r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        f'**Last Updated:** {new_timestamp}',
        content
    )
    
    # Update timestamp at bottom
    content = re.sub(
        r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        f'**Last Updated:** {new_timestamp}',
        content
    )
    
    # Count implementation progress
    impl_status = get_implementation_status()
    implemented_count = sum(1 for v in impl_status.values() if v == "implemented")
    total_count = len(impl_status)
    
    log(f"   [+] Implementation progress: {implemented_count}/{total_count} components", verbose)
    
    # Save updated content
    CONTEXT_MD.write_text(content)
    log(f"   [OK] Updated: {CONTEXT_MD}", verbose)


def update_new_agent_md(verbose: bool = True) -> None:
    """Update NEW_AGENT_START_HERE.md with latest timestamp."""
    log("[*] Updating NEW_AGENT_START_HERE.md...", verbose)
    
    if not NEW_AGENT_MD.exists():
        log(f"   [WARN] {NEW_AGENT_MD} not found - skipping", verbose)
        return
    
    content = NEW_AGENT_MD.read_text()
    
    # Update timestamp at bottom
    new_timestamp = get_formatted_timestamp()
    content = re.sub(
        r'\*\*Last Updated\*\*: \d{4}-\d{2}-\d{2}',
        f'**Last Updated**: {new_timestamp.split()[0]}',
        content
    )
    
    NEW_AGENT_MD.write_text(content)
    log(f"   [OK] Updated: {NEW_AGENT_MD}", verbose)


def check_context_system_health(verbose: bool = True) -> Dict[str, bool]:
    """Check if all context files exist and are recent."""
    log("\n[*] Checking context system health...", verbose)
    
    required_files = {
        "NEW_AGENT_START_HERE.md": NEW_AGENT_MD,
        "AI_AGENT_CONTEXT.md": CONTEXT_MD,
        "project_state.json": STATE_JSON,
        "CONVERSATION_SUMMARY.md": CONVERSATION_MD
    }
    
    health = {}
    
    for name, path in required_files.items():
        exists = path.exists()
        health[name] = exists
        
        if exists:
            # Check file size
            size = path.stat().st_size
            age_hours = (datetime.now().timestamp() - path.stat().st_mtime) / 3600
            
            status = "[OK]" if size > 100 else "[WARN]"
            log(f"   {status} {name}: {size:,} bytes, {age_hours:.1f}h old", verbose)
        else:
            log(f"   [FAIL] {name}: MISSING", verbose)
    
    all_healthy = all(health.values())
    
    if all_healthy:
        log("\n[OK] Context system healthy - all files present", verbose)
    else:
        log("\n[WARN] Context system incomplete - some files missing", verbose)
    
    return health


def generate_summary_report() -> str:
    """Generate a summary report of current project state."""
    state = load_state_json()
    file_counts = count_project_files()
    impl_status = get_implementation_status()
    
    implemented = sum(1 for v in impl_status.values() if v == "implemented")
    total = len(impl_status)
    
    report = f"""
================================================================
         StructureScout - Context Update Summary              
================================================================

Updated: {get_formatted_timestamp()}

PROJECT STATUS:
   Phase: {state.get('current_state', {}).get('phase', 'unknown')}
   Status: {state.get('current_state', {}).get('status', 'unknown')}

FILES:
   Planning Docs: {file_counts['planning_docs']}/5
   Config Files: {file_counts['config_files']}/3
   Module Files: {file_counts['modules']}/12
   Data Files: {file_counts['data_files']}

IMPLEMENTATION:
   Components: {implemented}/{total} implemented
   Progress: {(implemented/total*100):.0f}%

METRICS:
   Total Setups: {state.get('metrics', {}).get('total_setups_identified', 0)}
   Trades Executed: {state.get('trading_state', {}).get('trades_executed', 0)}
   
CONTEXT SYSTEM:
   Version: {state.get('context_system', {}).get('version', 'v1.0')}
   Handoff Count: {state.get('context_system', {}).get('handoff_count', 0)}

[OK] Context files updated successfully!
     Next agent can seamlessly continue from this state.

"""
    return report


def main():
    """Main execution function."""
    # Parse command line arguments
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    check_only = "--check-only" in sys.argv
    
    print("StructureScout Context Updater")
    print("=" * 64)
    
    if check_only:
        # Just check health, don't update
        health = check_context_system_health(verbose=True)
        if all(health.values()):
            print("\n✅ All context files present and healthy")
            sys.exit(0)
        else:
            print("\n⚠️  Some context files missing - run without --check-only to update")
            sys.exit(1)
    
    try:
        # Update all context files
        update_state_json(verbose=verbose)
        update_context_md(verbose=verbose)
        update_new_agent_md(verbose=verbose)
        
        # Check health
        health = check_context_system_health(verbose=verbose)
        
        # Generate and print summary
        summary = generate_summary_report()
        print(summary)
        
        if all(health.values()):
            print("[OK] Context update completed successfully!")
            sys.exit(0)
        else:
            print("[WARN] Context update completed with warnings")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] Error during context update: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
