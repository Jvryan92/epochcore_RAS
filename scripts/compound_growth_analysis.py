#!/usr/bin/env python3
"""
Compound Growth Model Analysis

This script analyzes the growth and scaling effects based on three factors:
1. Leverage: Initial scaling factor (10X)
2. Velocity: Secondary acceleration factor (5X)
3. Escalation: Compounding effect over multiple triggers
"""

import math

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


def apply_leverage(value, factor=10.0):
    """Apply leverage - linear multiplication"""
    return value * factor


def apply_velocity(value, factor=5.0):
    """Apply velocity - second-order acceleration"""
    return value * factor


def apply_escalation(value, compound_rate=0.01, trigger_count=100):
    """
    Apply compounding escalation over multiple triggers
    Formula: final_value = initial_value * (1 + rate)^triggers
    """
    return value * math.pow(1 + compound_rate, trigger_count)


def find_compound_rate(initial, final, triggers):
    """Find the compound rate that produces the desired final value"""
    # Rate = (Final/Initial)^(1/triggers) - 1
    return math.pow(final / initial, 1 / triggers) - 1


def analyze_example():
    """Analyze the example provided in the prompt"""
    initial_value = 7

    # Apply leverage (10X)
    after_leverage = apply_leverage(initial_value)
    print(f"Input: {initial_value}")
    print(f"After 10X Leverage: {after_leverage}")

    # Apply velocity (5X)
    after_velocity = apply_velocity(after_leverage)
    print(f"After 5X Velocity: {after_velocity}")

    # Calculate the compound rate needed to achieve the specified final value
    final_value = 953.48
    trigger_count = 100
    compound_rate = find_compound_rate(after_velocity, final_value, trigger_count)

    # Apply escalation with the calculated rate
    after_escalation = apply_escalation(after_velocity, compound_rate, trigger_count)

    print(f"Calculated compound rate: {compound_rate:.6f} ({compound_rate*100:.4f}%)")
    print(
        f"After Triple Escalator ({trigger_count} compounding triggers): {after_escalation:.2f}")

    # Verify our calculations
    print("\nVerification:")
    print(f"{initial_value} × 10 × 5 × (1 + {compound_rate:.6f})^{trigger_count} = {after_escalation:.2f}")

    # Generate data for visualization
    triggers_range = range(0, trigger_count + 1, 5)
    escalation_values = [after_velocity *
                         math.pow(1 + compound_rate, t) for t in triggers_range]

    return {
        'initial': initial_value,
        'leverage': after_leverage,
        'velocity': after_velocity,
        'escalation': after_escalation,
        'compound_rate': compound_rate,
        'trigger_count': trigger_count,
        'triggers_range': triggers_range,
        'escalation_values': escalation_values
    }


def visualize_growth(data):
    """Create visualization of the growth model"""
    if not VISUALIZATION_AVAILABLE:
        print("\nVisualization not available (matplotlib not installed)")
        return

    plt.figure(figsize=(10, 6))

    # Plot the escalation curve
    plt.plot(list(data['triggers_range']), data['escalation_values'],
             'b-', linewidth=2, label='Escalation Growth')

    # Mark key points
    plt.scatter([0], [data['velocity']], color='green',
                s=100, zorder=5, label='After Velocity')
    plt.scatter([data['trigger_count']], [data['escalation']],
                color='red', s=100, zorder=5, label='Final Value')

    # Add a line showing linear growth for comparison
    linear_growth = [data['velocity'] * (1 + t/data['trigger_count'] * (
        data['escalation']/data['velocity'] - 1)) for t in data['triggers_range']]
    plt.plot(list(data['triggers_range']), linear_growth,
             'g--', alpha=0.7, label='Linear Growth')

    # Add labels and title
    plt.xlabel('Number of Triggers')
    plt.ylabel('Value')
    plt.title('Compound Growth Model: Leverage → Velocity → Escalation')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Save the figure
    plt.savefig('compound_growth_model.png')
    print("\nVisualization saved to 'compound_growth_model.png')")


def calculate_time_to_double(rate):
    """Calculate time to double at given compound rate (Rule of 72 approximation)"""
    return 72 / (rate * 100)


def main():
    """Main entry point"""
    print("=" * 60)
    print("Compound Growth Model Analysis")
    print("=" * 60)

    # Analyze the example
    data = analyze_example()

    # Additional insights
    print("\nAdditional Insights:")
    print("- Leverage multiplier: 10x (increases by factor of 10)")
    print("- Velocity multiplier: 5x (increases by factor of 5)")
    print("- Combined multiplier: 50x (leverage × velocity)")
    doubling_time = calculate_time_to_double(data['compound_rate'])
    print(
        f"- At {data['compound_rate']*100:.4f}% compound rate, value doubles every {doubling_time:.1f} triggers")
    print(
        f"- Growth factor from velocity to final: {data['escalation']/data['velocity']:.2f}x")

    # Try to visualize
    visualize_growth(data)

    # Show mathematical formula
    print("\nMathematical Formula:")
    print("Final = Initial × Leverage × Velocity × (1 + CompoundRate)^Triggers")
    print(
        f"Final = {data['initial']} × {10} × {5} × (1 + {data['compound_rate']:.6f})^{data['trigger_count']}")
    print(
        f"Final = {data['initial']} × {10*5} × {math.pow(1+data['compound_rate'], data['trigger_count']):.6f}")
    print(f"Final = {data['escalation']:.2f}")


if __name__ == "__main__":
    main()
