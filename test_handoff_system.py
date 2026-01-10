#!/usr/bin/env python3
"""
AI Agent Handoff System - Validation Test Suite

Tests all components of the handoff system to ensure reliability.
Run this before your first handoff to verify everything works.

Usage:
    python3 test_handoff_system.py
    python3 test_handoff_system.py --verbose
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print formatted header."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_test(name, passed, details=""):
    """Print test result."""
    status = f"{GREEN}[OK] PASS{RESET}" if passed else f"{RED}[FAIL] FAIL{RESET}"
    print(f"{status} {name}")
    if details:
        print(f"     {details}")

def test_file_exists(filepath, min_size=100):
    """Test if file exists and has minimum size."""
    path = Path(filepath)
    if not path.exists():
        return False, f"File not found: {filepath}"
    
    size = path.stat().st_size
    if size < min_size:
        return False, f"File too small: {size} bytes (min: {min_size})"
    
    return True, f"{size:,} bytes"

def test_json_valid(filepath):
    """Test if JSON file is valid."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return True, f"Valid JSON with {len(data)} top-level keys"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading: {e}"

def test_timestamp_recent(filepath, hours=24):
    """Test if file was modified recently."""
    path = Path(filepath)
    if not path.exists():
        return False, "File not found"
    
    mtime = path.stat().st_mtime
    age_hours = (datetime.now().timestamp() - mtime) / 3600
    
    if age_hours > hours:
        return False, f"Last modified {age_hours:.1f}h ago (>{hours}h)"
    
    return True, f"Last modified {age_hours:.1f}h ago"

def test_markdown_structure(filepath, required_headers):
    """Test if markdown file has required headers."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        missing = []
        for header in required_headers:
            if header not in content:
                missing.append(header)
        
        if missing:
            return False, f"Missing headers: {', '.join(missing)}"
        
        return True, f"All {len(required_headers)} required headers found"
    except Exception as e:
        return False, f"Error reading: {e}"

def test_update_script_executable():
    """Test if update script can be executed."""
    script = Path("update_context.py")
    if not script.exists():
        return False, "Script not found"
    
    # Check if it's a Python file
    if not str(script).endswith('.py'):
        return False, "Not a Python file"
    
    # Try to read it
    try:
        with open(script, 'r') as f:
            content = f.read()
            if 'def main()' not in content:
                return False, "Missing main() function"
            if 'update_state_json' not in content:
                return False, "Missing update functions"
        return True, "Script structure valid"
    except Exception as e:
        return False, f"Error reading: {e}"

def run_all_tests():
    """Run all validation tests."""
    print_header("AI AGENT HANDOFF SYSTEM - VALIDATION TEST SUITE")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Core Files Exist
    print_header("TEST 1: Core Files Exist")
    
    core_files = {
        "NEW_AGENT_START_HERE.md": 5000,
        "AI_AGENT_CONTEXT.md": 10000,
        "project_state.json": 3000,
        "CONVERSATION_SUMMARY.md": 5000,
        "update_context.py": 8000
    }
    
    for filename, min_size in core_files.items():
        total_tests += 1
        passed, details = test_file_exists(filename, min_size)
        print_test(f"File exists: {filename}", passed, details)
        if passed:
            passed_tests += 1
    
    # Test 2: Documentation Files
    print_header("TEST 2: Documentation Files")
    
    doc_files = {
        "README.md": 8000,
        "HANDOFF_GUIDE.md": 5000,
        "VISUAL_GUIDE.md": 10000
    }
    
    for filename, min_size in doc_files.items():
        total_tests += 1
        passed, details = test_file_exists(filename, min_size)
        print_test(f"Documentation: {filename}", passed, details)
        if passed:
            passed_tests += 1
    
    # Test 3: JSON Validity
    print_header("TEST 3: JSON File Validity")
    
    total_tests += 1
    passed, details = test_json_valid("project_state.json")
    print_test("project_state.json is valid JSON", passed, details)
    if passed:
        passed_tests += 1
    
    # Test 4: File Freshness
    print_header("TEST 4: File Freshness (Modified within 24h)")
    
    fresh_files = [
        "AI_AGENT_CONTEXT.md",
        "project_state.json",
        "NEW_AGENT_START_HERE.md"
    ]
    
    for filename in fresh_files:
        total_tests += 1
        passed, details = test_timestamp_recent(filename, hours=24)
        print_test(f"Recent update: {filename}", passed, details)
        if passed:
            passed_tests += 1
    
    # Test 5: Markdown Structure
    print_header("TEST 5: Markdown Structure")
    
    markdown_tests = {
        "NEW_AGENT_START_HERE.md": [
            "IMMEDIATE CONTEXT",
            "MAIN GOAL",
            "WHAT TO DO FIRST",
            "IMPORTANT NOTES"
        ],
        "AI_AGENT_CONTEXT.md": [
            "PROJECT OVERVIEW",
            "CURRENT STATE",
            "USER PREFERENCES",
            "DAILY WORKFLOW",
            "IMPORTANT FILES",
            "GOALS & PRIORITIES"
        ],
        "HANDOFF_GUIDE.md": [
            "The 5 Essential Files",
            "How To Use This System",
            "Commands Reference"
        ]
    }
    
    for filename, headers in markdown_tests.items():
        total_tests += 1
        passed, details = test_markdown_structure(filename, headers)
        print_test(f"Structure: {filename}", passed, details)
        if passed:
            passed_tests += 1
    
    # Test 6: Update Script
    print_header("TEST 6: Update Script Functionality")
    
    total_tests += 1
    passed, details = test_update_script_executable()
    print_test("update_context.py structure", passed, details)
    if passed:
        passed_tests += 1
    
    # Test 7: Required JSON Fields
    print_header("TEST 7: JSON Required Fields")
    
    try:
        with open("project_state.json", 'r') as f:
            state = json.load(f)
        
        required_fields = [
            "last_update",
            "agent_version",
            "project_info",
            "current_state",
            "trading_state",
            "metrics"
        ]
        
        for field in required_fields:
            total_tests += 1
            if field in state:
                print_test(f"JSON field: {field}", True, f"Present with {type(state[field]).__name__}")
                passed_tests += 1
            else:
                print_test(f"JSON field: {field}", False, "Missing")
    except Exception as e:
        print_test("Read project_state.json", False, str(e))
    
    # Final Summary
    print_header("TEST SUMMARY")
    
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {GREEN}{passed_tests}{RESET}")
    print(f"Failed:       {RED}{total_tests - passed_tests}{RESET}")
    print(f"Pass Rate:    {GREEN if pass_rate >= 95 else YELLOW}{pass_rate:.1f}%{RESET}")
    
    if pass_rate >= 95:
        print(f"\n{GREEN}[OK] SYSTEM VALIDATION PASSED{RESET}")
        print("The AI Agent Handoff System is ready for use!")
        return 0
    elif pass_rate >= 80:
        print(f"\n{YELLOW}[WARN] SYSTEM VALIDATION: WARNINGS{RESET}")
        print("System mostly functional but some issues detected.")
        return 1
    else:
        print(f"\n{RED}[ERROR] SYSTEM VALIDATION FAILED{RESET}")
        print("Critical issues detected. Please review and fix.")
        return 2

if __name__ == "__main__":
    sys.exit(run_all_tests())
