#!/usr/bin/env python3
"""
GiesClaw Setup - Install and configure the framework.

Usage:
    python setup.py                                    # Interactive setup
    python setup.py --quick --profile finance          # Quick finance agent
    python setup.py --quick --profile strategy --name "StratBot-1"
"""

from agent.setup.setup_wizard import main

if __name__ == "__main__":
    main()
