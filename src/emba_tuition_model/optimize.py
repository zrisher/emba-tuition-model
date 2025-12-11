from dataclasses import dataclass
from typing import List

from .config import SimulationConfig
from .simulation import YearResult, run_model


@dataclass
class OptimizationResult:
    """Result of tuition optimization."""

    best_tuition_per_credit: float
    max_total_net_revenue: float
    results: List[YearResult]


def find_optimal_tuition(
    config: SimulationConfig,
    num_years: int,
    min_annual_tuition: float = 0,
    max_annual_tuition: float = 90000,
    step: float = 50,
) -> OptimizationResult:
    """
    Find the tuition per credit that maximizes total net revenue.

    Args:
        config: Simulation configuration
        num_years: Number of years to simulate
        min_annual_tuition: Minimum annual tuition to test ($)
        max_annual_tuition: Maximum annual tuition to test ($)
        step: Step size for tuition per credit search ($)

    Returns:
        OptimizationResult with best tuition and corresponding results
    """
    # Calculate credits per year from education config
    terms_per_year = sum(
        len(semester.terms) for year in config.education.years for semester in year
    )
    credits_per_year = terms_per_year * config.education.credits_per_term

    if credits_per_year == 0:
        raise ValueError("Education config must include at least one term.")

    # Convert annual tuition bounds to per-credit bounds
    min_tuition_per_credit = min_annual_tuition / credits_per_year
    max_tuition_per_credit = max_annual_tuition / credits_per_year

    best_tuition = 0.0
    max_net_revenue = -float("inf")
    best_results = []

    # Search for optimal tuition
    tuition = min_tuition_per_credit
    while tuition <= max_tuition_per_credit:
        results = run_model(tuition, num_years, config)
        total_net = sum(r.net_revenue for r in results)

        if total_net > max_net_revenue:
            max_net_revenue = total_net
            best_tuition = tuition
            best_results = results

        tuition += step

    return OptimizationResult(
        best_tuition_per_credit=best_tuition,
        max_total_net_revenue=max_net_revenue,
        results=best_results,
    )
