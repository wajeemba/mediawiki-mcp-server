#!/usr/bin/env python3
"""
Test runner for Cosmere DM MCP Server
Provides easy test execution with different options
"""
import subprocess
import sys
import os


def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")
    
    return result.returncode == 0


def main():
    """Main test runner"""
    print("🚀 Cosmere DM MCP Server Test Runner")
    
    # Check if we're in a virtual environment or have pytest
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[test]"])
    
    # Available test commands
    test_commands = {
        "all": {
            "cmd": "python -m pytest tests/ -v",
            "desc": "Run all tests"
        },
        "basic": {
            "cmd": "python -m pytest tests/test_mcp_server.py::TestBasicFunctionality -v",
            "desc": "Run basic functionality tests"
        },
        "canon": {
            "cmd": "python -m pytest tests/ -m canon -v",
            "desc": "Run canon validation tests"
        },
        "performance": {
            "cmd": "python -m pytest tests/ -m performance -v",
            "desc": "Run performance tests"
        },
        "integration": {
            "cmd": "python -m pytest tests/ -m integration -v",
            "desc": "Run integration tests"
        },
        "quick": {
            "cmd": "python -m pytest tests/ -m \"not slow\" -v",
            "desc": "Run quick tests (excludes slow tests)"
        },
        "coverage": {
            "cmd": "python -m pytest tests/ --cov=src/mediawiki_mcp_server --cov-report=html --cov-report=term-missing",
            "desc": "Run tests with coverage report"
        }
    }
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type in test_commands:
            success = run_command(test_commands[test_type]["cmd"], test_commands[test_type]["desc"])
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("\nAvailable test types:")
            for key, value in test_commands.items():
                print(f"  {key:12} - {value['desc']}")
            sys.exit(1)
    
    # Interactive mode
    print("\nAvailable test options:")
    for key, value in test_commands.items():
        print(f"  {key:12} - {value['desc']}")
    
    choice = input("\nSelect test type (or 'all'): ").strip().lower()
    
    if choice in test_commands:
        success = run_command(test_commands[choice]["cmd"], test_commands[choice]["desc"])
        
        if choice == "coverage":
            print("\n📊 Coverage report generated in htmlcov/index.html")
        
        sys.exit(0 if success else 1)
    else:
        print("❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main() 