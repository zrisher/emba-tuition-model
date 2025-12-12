from dataclasses import dataclass
from typing import List

from .config import (
    AlumniConfig,
    EducationConfig,
    EnrollmentConfig,
    MarketConfig,
    MarketingConfig,
    SimulationConfig,
)


@dataclass
class EducationResult:
    net_revenue: float
    students_remaining: float


@dataclass
class AlumniEffectResult:
    awareness_boost: float
    preference_boost: float
    donations: float


@dataclass
class MarketingResult:
    awareness_boost: float
    preference_boost: float


@dataclass
class EnrollmentResult:
    students_enrolled: float


@dataclass
class Reputation:
    alumni_count: float
    awareness: float  # fraction of market aware (0-1)
    preference: float  # fraction of aware who would choose us (0-1)


@dataclass
class YearResult:
    fall_marketing_spend: float
    fall_students_remaining: float
    students_enrolled: int
    net_revenue: float
    reputation: Reputation


def education_phase(
    students_start: float,
    semesters: List,
    cost_per_credit: float,
    config: EducationConfig,
) -> EducationResult:
    """Calculate income, expense, and remaining students for a set of semesters."""
    income = 0.0
    expense = 0.0
    students = students_start

    for semester in semesters:
        income += students * (
            config.semester_fees.program_per_student
            + config.semester_fees.general_per_student
            + config.semester_fees.technology_per_student
        )
        expense += students * (
            config.semester_costs.technology_per_student
            + config.semester_costs.general_per_student
        )

        for term in semester.terms:
            income += students * cost_per_credit * config.credits_per_term

            tc = config.term_costs
            expense += students * tc.instructor_per_student
            if term.has_licensed_content:
                expense += students * tc.content_per_credit_hour
            if term.has_intensive_lecturer:
                expense += tc.intensive_lecturer
            if term.has_intensive_experience:
                expense += tc.intensive_experience

            students *= 1.0 - config.dropout_rate_per_term

    return EducationResult(net_revenue=income - expense, students_remaining=students)


def alumni_phase(
    alumni_count: float,
    awareness: float,
    preference: float,
    alumni_config: AlumniConfig,
    market_config: MarketConfig,
) -> AlumniEffectResult:
    """Alumni boost awareness/preference with diminishing returns as they approach 1."""
    # Awareness
    people_reached = alumni_count * alumni_config.candidates_reached_per_year
    unaware_fraction = 1 - awareness
    awareness_boost = people_reached * unaware_fraction / market_config.size

    # Preference
    aware_population = market_config.size * awareness
    if aware_population > 0:
        people_influenced = alumni_count * alumni_config.candidates_influenced_per_year
        unconvinced_fraction = 1 - preference
        preference_boost = people_influenced * unconvinced_fraction / aware_population
    else:
        preference_boost = 0

    donations = alumni_count * alumni_config.donation_per_year

    return AlumniEffectResult(
        awareness_boost=awareness_boost,
        preference_boost=preference_boost,
        donations=donations,
    )


def marketing_phase(
    marketing_spend: float,
    awareness: float,
    preference: float,
    marketing_config: MarketingConfig,
    market_config: MarketConfig,
) -> MarketingResult:
    """Marketing boosts awareness/preference with diminishing returns."""
    # Awareness
    people_reached = marketing_spend / marketing_config.cost_to_reach_one_candidate
    unaware_fraction = 1 - awareness
    awareness_boost = people_reached * unaware_fraction / market_config.size

    # Preference
    aware_population = market_config.size * awareness
    if aware_population > 0:
        people_influenced = (
            marketing_spend / marketing_config.cost_to_influence_one_candidate
        )
        unconvinced_fraction = 1 - preference
        preference_boost = people_influenced * unconvinced_fraction / aware_population
    else:
        preference_boost = 0

    return MarketingResult(
        awareness_boost=awareness_boost, preference_boost=preference_boost
    )


def enrollment_phase(
    reputation: Reputation,
    total_tuition_cost: float,
    enrollment_config: EnrollmentConfig,
    market_config: MarketConfig,
) -> EnrollmentResult:
    """
    Enrollment funnel: aware -> preference -> price-adjusted -> apply -> enroll.
    High preference protects against price sensitivity.
    """
    aware_population = market_config.size * reputation.awareness
    base_choice_rate = reputation.preference

    # Price position in market (0 = cheapest, 1 = most expensive)
    tuition_range = market_config.tuition_high - market_config.tuition_low
    if tuition_range > 0:
        price_position = (
            total_tuition_cost - market_config.tuition_low
        ) / tuition_range
        price_position = max(0.0, min(1.0, price_position))
    else:
        price_position = 0.0

    # High preference reduces price sensitivity
    effective_sensitivity = enrollment_config.price_sensitivity * (1 - base_choice_rate)
    price_factor = max(0.0, 1 - effective_sensitivity * price_position)

    effective_choice_rate = base_choice_rate * price_factor
    would_choose = aware_population * effective_choice_rate
    applicants = would_choose * enrollment_config.application_rate
    enrolled = min(applicants, enrollment_config.max_students)

    return EnrollmentResult(students_enrolled=enrolled)


def run_year(
    prior_year_result: YearResult,
    cost_per_credit: float,
    total_tuition_cost: float,
    config: SimulationConfig,
    skip_spring_summer: bool = False,
) -> YearResult:
    reputation = Reputation(
        alumni_count=prior_year_result.reputation.alumni_count,
        awareness=prior_year_result.reputation.awareness,
        preference=prior_year_result.reputation.preference,
    )
    net_revenue = 0.0

    # Reputation decays without maintenance
    reputation.awareness *= 1 - config.reputation.awareness_decay_rate
    reputation.preference *= 1 - config.reputation.preference_decay_rate

    # Spring/Summer education (round students entering education)
    spring_students = round(prior_year_result.fall_students_remaining)
    if skip_spring_summer:
        reputation.alumni_count += spring_students
        spring_summer_marketing_spend = 0.0
    else:
        semesters = config.education.years[1] if len(config.education.years) > 1 else []
        edu = education_phase(
            spring_students, semesters, cost_per_credit, config.education
        )
        reputation.alumni_count += round(edu.students_remaining)
        net_revenue += edu.net_revenue
        spring_summer_marketing_spend = max(
            0.0, edu.net_revenue * config.marketing.spend_pct
        )
        net_revenue -= spring_summer_marketing_spend

    # Alumni effects
    alumni = alumni_phase(
        reputation.alumni_count,
        reputation.awareness,
        reputation.preference,
        config.alumni,
        config.market,
    )
    reputation.awareness += alumni.awareness_boost
    reputation.preference += alumni.preference_boost
    net_revenue += alumni.donations

    # Marketing
    marketing_spend = (
        prior_year_result.fall_marketing_spend + spring_summer_marketing_spend
    )
    marketing = marketing_phase(
        marketing_spend,
        reputation.awareness,
        reputation.preference,
        config.marketing,
        config.market,
    )
    reputation.awareness += marketing.awareness_boost
    reputation.preference += marketing.preference_boost

    # Enrollment (round students entering education)
    reputation.awareness = max(0.0, min(1.0, reputation.awareness))
    reputation.preference = max(0.0, min(1.0, reputation.preference))
    enrollment = enrollment_phase(
        reputation, total_tuition_cost, config.enrollment, config.market
    )
    fall_students = round(enrollment.students_enrolled)

    # Fall education
    fall_semesters = config.education.years[0] if config.education.years else []
    fall_edu = education_phase(
        fall_students, fall_semesters, cost_per_credit, config.education
    )
    net_revenue += fall_edu.net_revenue

    fall_marketing_spend = max(0.0, fall_edu.net_revenue * config.marketing.spend_pct)
    net_revenue -= marketing_spend

    return YearResult(
        fall_marketing_spend=fall_marketing_spend,
        fall_students_remaining=round(fall_edu.students_remaining),
        students_enrolled=fall_students,
        net_revenue=net_revenue,
        reputation=reputation,
    )


def run_model(
    cost_per_credit: float, num_years: int, config: SimulationConfig
) -> List[YearResult]:
    initial = config.initial_state
    prior = YearResult(
        fall_marketing_spend=initial.prior_fall_marketing_spend,
        fall_students_remaining=initial.prior_fall_students_remaining,
        students_enrolled=0,
        net_revenue=0.0,
        reputation=Reputation(
            alumni_count=initial.alumni_count,
            awareness=initial.awareness,
            preference=initial.preference,
        ),
    )

    terms_per_year = sum(
        len(sem.terms) for year in config.education.years for sem in year
    )
    if terms_per_year == 0:
        raise ValueError("Education config must include at least one term.")

    total_tuition = cost_per_credit * config.education.credits_per_term * terms_per_year

    results = []
    for year in range(num_years):
        skip = (year == 0) and initial.skip_first_spring_summer
        prior = run_year(prior, cost_per_credit, total_tuition, config, skip)
        results.append(prior)

    return results
