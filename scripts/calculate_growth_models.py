#!/usr/bin/env python3
"""
StrategyDECK Growth Model Calculator

This script calculates various growth models including leverage, velocity, and
compounding escalation effects based on the input value.
"""

import argparse
import math


def calculate_leverage(value, factor=10):
    """Apply simple leverage factor (linear)"""
    return value * factor


def calculate_velocity(value, factor=5):
    """Apply velocity factor (second-order effect)"""
    return value * factor


def calculate_escalation(value, compound_rate=0.01, trigger_count=100):
    """
    Apply escalation with compounding triggers
    
    The Triple Escalator uses a compounding effect formula:
    final_value = initial_value * (1 + rate)^triggers
    """
    return value * math.pow(1 + compound_rate, trigger_count)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Calculate growth models for StrategyDECK"
    )
    parser.add_argument(
        "input_value", type=float,
        help="The initial input value to calculate growth from"
    )
    parser.add_argument(
        "--leverage", type=float, default=10,
        help="The leverage factor to apply (default: 10)"
    )
    parser.add_argument(
        "--velocity", type=float, default=5,
        help="The velocity factor to apply (default: 5)"
    )
    parser.add_argument(
        "--escalator-rate", type=float, default=0.01,
        help="The compound rate for each escalator trigger (default: 0.01)"
    )
    parser.add_argument(
        "--triggers", type=int, default=100,
        help="The number of compound triggers to apply (default: 100)"
    )

    args = parser.parse_args()

    input_value = args.input_value
    leverage_factor = args.leverage
    velocity_factor = args.velocity
    escalator_rate = args.escalator_rate
    trigger_count = args.triggers

    # Calculate the sequential effects
    after_leverage = calculate_leverage(input_value, leverage_factor)
    after_velocity = calculate_velocity(after_leverage, velocity_factor)
    after_escalation = calculate_escalation(after_velocity, escalator_rate, trigger_count)

    # Print results
    print(f"Input value: {input_value}")
    print(f"After {leverage_factor}X Leverage: {after_leverage}")
    print(f"After {velocity_factor}X Velocity: {after_velocity}")
    print(f"After Triple Escalator ({trigger_count} compounding triggers): {after_escalation:.2f}")

    # Calculate the formula that gives us the approximate final value
    estimated_rate = math.pow(after_escalation / after_velocity, 1 / trigger_count) - 1
    print(f"\nEstimated compounding rate: {estimated_rate:.6f}")
    print(f"Formula: {input_value} × {leverage_factor} × {velocity_factor} × (1 + {estimated_rate:.6f})^{trigger_count}")
    print(f"Verification: {input_value * leverage_factor * velocity_factor * math.pow(1 + estimated_rate, trigger_count):.2f}")


if __name__ == "__main__":
    main()
