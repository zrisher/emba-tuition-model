from .config import load_config
from .optimize import find_optimal_tuition


def main():
    print("EMBA Tuition Model Simulation")
    print("=" * 70)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Configuration Error: {e}")
        return

    print(f"Market size: {config.market.size:,.0f}")
    print(
        f"Initial state: awareness={config.initial_state.awareness}%, "
        f"preference={config.initial_state.preference}%, "
        f"skip_first_spring_summer={config.initial_state.skip_first_spring_summer}"
    )

    final_year = 20

    # --- Optimization ---
    print("\nFinding optimal tuition (annual range: $0 - $90,000)...")

    opt = find_optimal_tuition(config, final_year)

    print(f"Optimal tuition: ${opt.best_tuition_per_credit:.0f}/credit")
    print(f"Maximum total net revenue: ${opt.max_total_net_revenue:,.2f}")

    # --- Detailed Results ---
    print(f"\nYear-by-year results at ${opt.best_tuition_per_credit:.0f}/credit:")
    results = opt.results

    print("-" * 70)
    print(
        f"{'Year':>4} | {'Awareness':>9} | {'Preference':>10} | "
        f"{'Alumni':>6} | {'Students':>8} | {'Net Revenue':>12}"
    )
    print("-" * 70)

    for year_index, r in enumerate(results, start=1):
        # Estimate enrolled students (before dropout)
        students = r.fall_students_remaining / 0.9025
        print(
            f"{year_index:>4} | {r.reputation.awareness:>8.2f}% | "
            f"{r.reputation.preference:>9.2f}% | {r.reputation.alumni_count:>6.0f} | "
            f"{students:>8.1f} | ${r.net_revenue:>11,.0f}"
        )

    print("-" * 70)

    total_revenue = sum(r.net_revenue for r in results)
    final_awareness = results[-1].reputation.awareness
    final_preference = results[-1].reputation.preference
    final_alumni = results[-1].reputation.alumni_count

    print(f"\nSummary after {final_year} years:")
    print(f"  Total net revenue: ${total_revenue:,.0f}")
    print(f"  Final awareness: {final_awareness:.2f}%")
    print(f"  Final preference: {final_preference:.2f}%")
    print(f"  Total alumni: {final_alumni:.0f}")


if __name__ == "__main__":
    main()
