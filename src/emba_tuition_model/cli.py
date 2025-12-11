from .config import load_config
from .simulation import run_model


def main():
    print("EMBA Tuition Model Simulation")

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Configuration Error: {e}")
        return

    final_year = 20

    # --- Optimization Loop ---
    print("\nStarting Optimization Loop...")
    print(f"{'Tuition':<10} | {'Total Net Rev':<15}")
    print("-" * 35)

    best_tuition = 0.0
    max_net_revenue = -float("inf")

    # Test tuition from $0 to $2000 in $50 increments
    for tuition in range(0, 2001, 50):
        results = run_model(float(tuition), final_year, config)
        total_net = sum(r.net_revenue for r in results)

        if total_net > max_net_revenue:
            max_net_revenue = total_net
            best_tuition = tuition

    print("-" * 35)
    print(f"OPTIMAL TUITION FOUND: ${best_tuition}/credit")
    print(f"Maximum Total Net Revenue: ${max_net_revenue:,.2f}")

    # --- Detailed Run for Optimal ---
    print(f"\nDetailed results for optimal tuition (${best_tuition}/credit):")
    results = run_model(float(best_tuition), final_year, config)

    print("-" * 45)
    print(f"{'Year':<6} | {'Net Rev':<12}")
    print("-" * 45)

    for year_index, state in enumerate(results, start=1):
        print(f"{year_index:<6} | ${state.net_revenue:<11,.0f}")

    print("-" * 45)


if __name__ == "__main__":
    main()
