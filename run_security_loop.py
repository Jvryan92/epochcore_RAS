#!/usr/bin/env python3
"""
Start recursive security backtest loop
"""

import asyncio

from security_backtest_loop import SecurityBacktestLoop

if __name__ == "__main__":
    try:
        asyncio.run(SecurityBacktestLoop.create_and_run())
    except KeyboardInterrupt:
        print("\nSecurity loop stopped by user")
