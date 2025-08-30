#!/usr/bin/env python3
"""
EpochCore Trigger System Mathematical Analysis

This script provides a mathematical analysis of the EpochCore trigger system,
with special focus on:

1. The compounding effects of triggers
2. Growth patterns in different batch configurations
3. Sensitivity analysis to different parameters
4. Relationship between trigger models and common growth models
"""

import argparse
import math

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Constants based on the trigger system
TRIGGER_COUNT = 10
BATCH_CONFIGS = {
    "roi-burst": [1, 2, 3, 4, 10],
    "gov-harden": [5, 6, 7, 10],
    "mesh-expand": [8, 9, 10],
    "full-send": list(range(1, 11))
}

# Mathematical model parameters
LEVERAGE_FACTOR = 10.0      # 10X effect of AUTOCOMPOUND
VELOCITY_FACTOR = 5.0       # Secondary acceleration
BASE_COMPOUND_RATE = 0.010072  # Base compound rate (1.0072%)
TRIGGER_MULTIPLIERS = {
    1: 1.0,  # TREASURYFLOW (base impact)
    2: 1.5,  # MARKETCAP (stronger impact)
    3: 1.2,  # PRICINGFORGE (moderate impact)
    4: 1.8,  # BONUSDROP (high variability)
    5: 1.0,  # GOVCOUNCIL (stability-focused)
    6: 1.0,  # PULLREQUESTVOTE (stability-focused)
    7: 0.8,  # ROLLBACKSEAL (safety, slightly reduces growth)
    8: 2.0,  # MESHSPAWN (strong network effect)
    9: 2.5,  # CIVILIZATIONBLOCK (strongest compound effect)
    10: 10.0  # AUTOCOMPOUND (direct 10X multiplier)
}


def model_single_trigger_effect(base_value, trigger_id, num_activations=1):
    """Model the effect of a single trigger applied multiple times"""
    multiplier = TRIGGER_MULTIPLIERS[trigger_id]

    # Special case for AUTOCOMPOUND (trigger 10)
    if trigger_id == 10:
        return base_value * LEVERAGE_FACTOR

    # For other triggers, apply compound growth
    compound_rate = BASE_COMPOUND_RATE * multiplier
    return base_value * math.pow(1 + compound_rate, num_activations)


def model_batch_effect(base_value, trigger_ids, num_activations=1):
    """Model the combined effect of a batch of triggers"""
    current_value = base_value

    # First apply non-AUTOCOMPOUND triggers
    for trigger_id in sorted(trigger_ids):
        if trigger_id != 10:  # Skip AUTOCOMPOUND for now
            current_value = model_single_trigger_effect(
                current_value, trigger_id, num_activations)

    # Then apply AUTOCOMPOUND if present (applied once at the end)
    if 10 in trigger_ids:
        current_value = model_single_trigger_effect(current_value, 10, 1)

    return current_value


def model_three_stage_growth(initial_value, batch_name, num_activations=1):
    """
    Model the three-stage growth pattern (leverage, velocity, escalation)
    using a specific batch configuration
    """
    if batch_name not in BATCH_CONFIGS:
        raise ValueError(f"Unknown batch: {batch_name}")

    trigger_ids = BATCH_CONFIGS[batch_name]

    # Stage 1: Leverage (base multiplication)
    leverage_value = initial_value * LEVERAGE_FACTOR

    # Stage 2: Velocity (secondary acceleration)
    velocity_value = leverage_value * VELOCITY_FACTOR

    # Stage 3: Escalation (compound growth)
    # Calculate effective compound rate from all non-AUTOCOMPOUND triggers
    effective_rate = sum(BASE_COMPOUND_RATE * TRIGGER_MULTIPLIERS[t]
                         for t in trigger_ids if t != 10)

    # Apply compound growth
    final_value = velocity_value * math.pow(1 + effective_rate, num_activations)

    # If AUTOCOMPOUND is in the batch, apply it at the end
    if 10 in trigger_ids:
        final_value *= LEVERAGE_FACTOR

    return {
        "initial": initial_value,
        "leverage": leverage_value,
        "velocity": velocity_value,
        "final": final_value,
        "effective_rate": effective_rate,
        "growth_factor": final_value / initial_value,
        "doubling_time": 72 / (effective_rate * 100)
        if effective_rate > 0 else float('inf')
    }


def analyze_batch_combinations():
    """Analyze all batch combinations and their growth patterns"""
    results = {}
    initial_value = 7.0
    activations = 100

    for batch_name in BATCH_CONFIGS:
        results[batch_name] = model_three_stage_growth(
            initial_value, batch_name, activations)

    return results


def visualize_growth_curves(initial_value=7.0, activations=100, max_activations=200):
    """Visualize growth curves for different batch configurations"""
    try:
        plt.figure(figsize=(12, 8))

        # Generate data for each batch
        x = list(range(0, max_activations + 1, 5))
        batch_data = {}

        for batch_name in BATCH_CONFIGS:
            y = []
            for act in x:
                result = model_three_stage_growth(initial_value, batch_name, act)
                y.append(result["final"])
            batch_data[batch_name] = y

            # Plot on log scale
            plt.semilogy(x, y, label=f"{batch_name} batch", linewidth=2)

        # Add markers for specific points
        for batch_name, data in batch_data.items():
            result = model_three_stage_growth(initial_value, batch_name, activations)
            act_idx = x.index(activations) if activations in x else -1
            if act_idx >= 0:
                plt.scatter([activations], [data[act_idx]], s=100, zorder=5)
                plt.annotate(f"{batch_name}: {data[act_idx]:.2f}",
                             (activations, data[act_idx]),
                             xytext=(10, 10), textcoords='offset points')

        # Reference lines
        plt.axvline(x=activations, color='gray', linestyle='--', alpha=0.7)

        # Add labels and title
        plt.xlabel('Number of Activations')
        plt.ylabel('Value (log scale)')
        plt.title('Growth Curves for Different Batch Configurations')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Save and display
        plt.tight_layout()
        plt.savefig('trigger_growth_curves.png')
        print("\nVisualization saved to 'trigger_growth_curves.png'")

    except Exception as e:
        print(f"Visualization error: {e}")
        print("Continuing with numerical analysis only...")


def print_mathematical_analysis(results):
    """Print a detailed mathematical analysis of the results"""
    print("\n" + "=" * 80)
    print(" EpochCore Trigger System Mathematical Analysis ".center(80, "="))
    print("=" * 80)

    print("\nGrowth Analysis by Batch Configuration:")
    print(f"{'Batch':<15} {'Initial':<10} {'Final':<15} {'Growth Factor':<15} {'Eff. Rate %':<12} {'Doubling Time':<15}")
    print("-" * 80)

    for batch_name, result in results.items():
        print(f"{batch_name:<15} {result['initial']:<10.2f} {result['final']:<15.2f} "
              f"{result['growth_factor']:<15.2f}x {result['effective_rate']*100:<12.4f} "
              f"{result['doubling_time']:<15.1f}")

    print("\nThree-Stage Growth Breakdown:")
    for batch_name, result in results.items():
        print(f"\n{batch_name} Batch:")
        print(
            f"  Initial → Leverage: {result['initial']:.2f} → {result['leverage']:.2f} (×{LEVERAGE_FACTOR:.1f})")
        print(
            f"  Leverage → Velocity: {result['leverage']:.2f} → {result['velocity']:.2f} (×{VELOCITY_FACTOR:.1f})")
        leverage_velocity_factor = result['velocity'] / result['initial']
        print(f"  Combined L×V factor: {leverage_velocity_factor:.2f}x")
        escalation_factor = result['final'] / result['velocity']
        print(
            f"  Velocity → Final (Escalation): {result['velocity']:.2f} → {result['final']:.2f} (×{escalation_factor:.2f})")
        print(f"  Effective compound rate: {result['effective_rate']*100:.4f}%")
        print(f"  Total growth factor: {result['growth_factor']:.2f}x")

    print("\nMathematical Formula:")
    print("Final = Initial × Leverage × Velocity × (1 + EffectiveRate)^Activations")

    # Example for full-send batch
    full_result = results.get('full-send', None)
    if full_result:
        print("\nExample (full-send batch):")
        print(f"Final = {full_result['initial']} × {LEVERAGE_FACTOR} × {VELOCITY_FACTOR} × "
              f"(1 + {full_result['effective_rate']:.6f})^100")
        print(f"Final = {full_result['initial']} × {LEVERAGE_FACTOR * VELOCITY_FACTOR} × "
              f"{math.pow(1 + full_result['effective_rate'], 100):.6f}")
        print(f"Final = {full_result['final']:.2f}")

    print("\nTrigger Sensitivity Analysis:")
    print("Relative impact of individual triggers on final growth:")

    sensitivity = {}
    base_result = model_three_stage_growth(7.0, 'full-send', 100)
    base_value = base_result['final']

    for trigger_id in range(1, TRIGGER_COUNT + 1):
        # Remove this trigger from full-send
        modified_triggers = [t for t in BATCH_CONFIGS['full-send'] if t != trigger_id]
        modified_batch = "custom"
        BATCH_CONFIGS[modified_batch] = modified_triggers

        # Calculate result without this trigger
        modified_result = model_three_stage_growth(7.0, modified_batch, 100)
        modified_value = modified_result['final']

        # Calculate impact
        impact = (base_value - modified_value) / base_value * 100
        sensitivity[trigger_id] = impact

    # Sort triggers by impact
    sorted_triggers = sorted(sensitivity.items(), key=lambda x: x[1], reverse=True)

    for trigger_id, impact in sorted_triggers:
        print(f"  Trigger {trigger_id}: {impact:.2f}% impact on final value")


def main():
    parser = argparse.ArgumentParser(
        description="Mathematical analysis of EpochCore trigger system"
    )
    parser.add_argument(
        "--initial", type=float, default=7.0,
        help="Initial value for calculations"
    )
    parser.add_argument(
        "--activations", type=int, default=100,
        help="Number of activations to model"
    )
    parser.add_argument(
        "--max-activations", type=int, default=200,
        help="Maximum activations for growth curve visualization"
    )
    parser.add_argument(
        "--no-viz", action="store_true",
        help="Skip visualization (if matplotlib not available)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print(" EpochCore Trigger System - Mathematical Analysis ".center(80, "="))
    print("=" * 80)

    # Analyze all batch combinations
    results = analyze_batch_combinations()

    # Print detailed mathematical analysis
    print_mathematical_analysis(results)

    # Try to visualize growth curves
    if not args.no_viz:
        try:
            visualize_growth_curves(
                args.initial, args.activations, args.max_activations)
        except Exception as e:
            print(f"\nVisualization error: {e}")
            print("Consider installing matplotlib or use --no-viz option")


if __name__ == "__main__":
    main()
