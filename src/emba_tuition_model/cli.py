import argparse

from .config import load_config
from .optimize import find_optimal_tuition


def main():
    parser = argparse.ArgumentParser(description="EMBA Tuition Model Simulation")
    parser.add_argument(
        "years", type=int, nargs="?", default=20, help="Number of years to simulate"
    )
    parser.add_argument(
        "-c", "--config", type=str, help="Path to config file (uses default if omitted)"
    )
    args = parser.parse_args()

    print("\n================= EMBA Tuition Model Simulation =================\n")

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Configuration Error: {e}")
        return

    num_years = args.years
    print(f"Num Years: {num_years}")

    tuition_min = config.market.tuition_low
    tuition_max = config.market.tuition_high
    print(f"Check range: ${tuition_min:.0f} - ${tuition_max:.0f}")

    print("\nRunning...\n")
    opt = find_optimal_tuition(config, num_years, tuition_min, tuition_max)
    print(f"Optimal tuition: ${opt.best_tuition_per_credit:.0f}/credit")
    print(f"Final year net revenue: ${opt.final_net_revenue:,.2f}")

    print("Year-by-year results:")
    print("-" * 70)
    print(
        f"{'Year':>4} | {'Awareness':>9} | {'Preference':>10} | "
        f"{'Alumni':>6} | {'Enrolled':>8} | {'Net Revenue':>12}"
    )
    print("-" * 70)

    for i, r in enumerate(opt.results, start=1):
        print(
            f"{i:>4} | {r.reputation.awareness:>8.2%} | "
            f"{r.reputation.preference:>9.2%} | {r.reputation.alumni_count:>6.0f} | "
            f"{r.students_enrolled:>8} | ${r.net_revenue:>11,.0f}"
        )


if __name__ == "__main__":
    main()
