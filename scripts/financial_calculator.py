#!/usr/bin/env python3

import argparse
import logging
import sys
from typing import Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_input(value: Union[int, float]) -> bool:
    """Validate that input is within safe bounds."""
    try:
        num = float(value)
        if num <= 0:
            logger.error("Input must be positive")
            return False
        if num > 1000000:  # Reasonable upper limit
            logger.error("Input exceeds maximum allowed value")
            return False
        return True
    except ValueError:
        logger.error("Input must be a valid number")
        return False


def calculate_with_leverage(value: float, leverage: float = 10.0) -> float:
    """Calculate value with leverage, with risk warnings."""
    logger.warning(f"Using {leverage}x leverage - HIGH RISK!")
    return value * leverage


def apply_velocity(value: float, velocity: float = 5.0) -> float:
    """Apply velocity multiplier to value."""
    return value * velocity


def compound_value(value: float, iterations: int = 100, rate: float = 0.01) -> float:
    """Compound value with safeguards."""
    if iterations > 1000:
        logger.warning("High iteration count may lead to extreme values")

    initial = value
    for _ in range(iterations):
        value *= (1 + rate)
        if value > initial * 1000:
            logger.warning("Value has grown more than 1000x initial!")

    return round(value, 2)


def main():
    parser = argparse.ArgumentParser(
        description='Financial calculation tool with risk management'
    )
    parser.add_argument('value', type=float, help='Initial value to process')
    parser.add_argument(
        '--max-leverage',
        type=float,
        default=10.0,
        help='Maximum leverage multiplier'
    )
    parser.add_argument(
        '--velocity',
        type=float,
        default=5.0,
        help='Velocity multiplier'
    )
    parser.add_argument(
        '--compounds',
        type=int,
        default=100,
        help='Number of compounding iterations'
    )

    args = parser.parse_args()

    if not validate_input(args.value):
        sys.exit(1)

    logger.info("RISK WARNING: This tool simulates high-risk financial calculations.")
    logger.info("Do not use for actual financial decisions without professional advice.")

    try:
        leveraged = calculate_with_leverage(args.value, args.max_leverage)
        logger.info(f"After {args.max_leverage}x leverage: {leveraged}")

        with_velocity = apply_velocity(leveraged, args.velocity)
        logger.info(f"After {args.velocity}x velocity: {with_velocity}")

        final = compound_value(with_velocity, args.compounds)
        logger.info(f"After {args.compounds} compounding iterations: {final}")

    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
