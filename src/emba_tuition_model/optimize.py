from dataclasses import dataclass
from typing import List

from .config import SimulationConfig
from .simulation import YearResult, run_model


@dataclass
class OptimizationResult:
    best_tuition_per_credit: float
    final_net_revenue: float
    results: List[YearResult]


def find_optimal_tuition(
    config: SimulationConfig,
    num_years: int,
    min_annual_tuition: float,
    max_annual_tuition: float,
    step: float = 1,
) -> OptimizationResult:
    """Find tuition per credit that maximizes final net revenue after num_years."""
    terms_per_year = sum(
        len(sem.terms) for year in config.education.years for sem in year
    )
    credits_per_year = terms_per_year * config.education.credits_per_term
    if credits_per_year == 0:
        raise ValueError("Education config must include at least one term.")

    min_per_credit = min_annual_tuition / credits_per_year
    max_per_credit = max_annual_tuition / credits_per_year

    best_tuition = 0.0
    best_final_net_rev = -float("inf")
    best_results = []

    tuition = min_per_credit
    while tuition <= max_per_credit:
        results = run_model(tuition, num_years, config)
        final_net_rev = results[-1].net_revenue
        if final_net_rev > best_final_net_rev:
            best_final_net_rev = final_net_rev
            best_tuition = tuition
            best_results = results
        tuition += step

    return OptimizationResult(
        best_tuition_per_credit=best_tuition,
        final_net_revenue=best_final_net_rev,
        results=best_results,
    )
