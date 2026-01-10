#!/usr/bin/env python3
"""
Setup script for Integration Examples

Checks dependencies and provides setup instructions.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_dependencies():
    """Check for required dependencies."""
    required = {
        "pydantic": "Pydantic",
        "yaml": "PyYAML",
    }

    optional = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "qdrant_client": "Qdrant",
        "sentence_transformers": "Sentence Transformers",
    }

    missing_required = []
    missing_optional = []

    for module, name in required.items():
        try:
            __import__(module)
        except ImportError:
            missing_required.append(name)

    for module, name in optional.items():
        try:
            __import__(module)
        except ImportError:
            missing_optional.append(name)

    return missing_required, missing_optional


def check_local_packages():
    """Check if local packages are available."""
    base = Path(__file__).parent.parent

    packages = {
        "escalation-engine": base / "escalation-engine",
        "hierarchical-memory": base / "hierarchical-memory",
        "ws-status-indicator": base / "ws-status-indicator",
    }

    available = {}
    for name, path in packages.items():
        exists = path.exists()
        available[name] = exists
        status = "found" if exists else "not found"
        print(f"  {name}: {status}")

    return available


def print_setup_instructions(missing_required, missing_optional, available_packages):
    """Print setup instructions."""
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)

    if missing_required:
        print("\n1. Install required Python dependencies:")
        print("   pip install -r requirements.txt")

    if missing_optional:
        print("\n2. Optional dependencies (for enhanced features):")
        for name in missing_optional:
            print(f"   pip install {name.lower().replace(' ', '-')}")

    print("\n3. Local packages:")

    if not all(available_packages.values()):
        print("\n   Some local packages are not in the expected location.")
        print("   The examples will try to import from parent directories.")

    print("\n4. Running examples:")
    print("\n   Python examples:")
    print("     cd 01-simple-ai-agent && python main.py")
    print("     cd 02-dnd-character && python main.py")
    print("     cd 03-customer-service && python main.py")
    print("     cd 04-multi-agent && python main.py")
    print("     cd 05-learning-loop && python main.py")

    print("\n   React example:")
    print("     cd 06-react-dashboard")
    print("     npm install")
    print("     npm run dev")

    print("\n5. Troubleshooting:")
    print("   If you see import errors, ensure the packages are either:")
    print("   - Installed via pip (pip install escalation-engine, etc.)")
    print("   - Available in parent directories")
    print("   - In your PYTHONPATH")

    print("\n" + "=" * 60)


def main():
    """Main setup function."""
    print("=" * 60)
    print("Integration Examples - Setup Check")
    print("=" * 60)

    # Check Python version
    print("\nChecking Python version...")
    if not check_python_version():
        sys.exit(1)

    # Check dependencies
    print("\nChecking Python dependencies...")
    missing_required, missing_optional = check_dependencies()

    if not missing_required:
        print("  All required dependencies installed!")
    else:
        print(f"  Missing required: {', '.join(missing_required)}")

    if missing_optional:
        print(f"  Missing optional: {', '.join(missing_optional)}")
    else:
        print("  All optional dependencies installed!")

    # Check local packages
    print("\nChecking local packages...")
    available_packages = check_local_packages()

    # Print instructions
    print_setup_instructions(missing_required, missing_optional, available_packages)

    print("\nReady to run examples!")
    print()


if __name__ == "__main__":
    main()
