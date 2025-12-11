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
    """
    The effects of the program during a set of semesters.
    """

    net_revenue: float
    students_remaining: float


@dataclass
class AlumniEffectResult:
    """
    The effects of all alumni, calculated each year after graduation.
    """

    awareness_boost: float
    donations: float
    preference_boost: float


@dataclass
class MarketingResult:
    """
    The effects of marketing during a full program.
    """

    awareness_boost: float
    preference_boost: float


@dataclass
class EnrollmentResult:
    """
    The effects of awareness, preference, and cost on a program's enrollment.
    """

    students_enrolled: float


@dataclass
class Reputation:
    """
    The cumulative state of the program's reputation.
    """

    alumni_count: float
    awareness: float  # percent of all applicants who are aware of the program
    preference: float  # percent of aware candidates who would choose this program


@dataclass
class YearResult:
    """
    The result of a year's run of the simulation.
    """

    fall_marketing_spend: float  # Used during next year's marketing calc
    fall_students_remaining: float  # Used during next year's education calc
    net_revenue: float  # Our key KPI
    reputation: Reputation  # Built over time, affects enrollment and donations


def education_phase(
    students_start: float,
    semesters: List,
    cost_per_credit: float,
    config: EducationConfig,
):
    """
    Calculates the income, expense, and remaining students after a set of semesters.
    """

    income = 0.0
    expense = 0.0
    students_remaining = students_start

    for semester in semesters:
        # semester income
        semester_income = students_remaining * (
            config.semester_fees.program_per_student
            + config.semester_fees.general_per_student
            + config.semester_fees.technology_per_student
        )
        income += semester_income

        # semester expense
        semester_expense = students_remaining * (
            config.semester_costs.technology_per_student
            + config.semester_costs.general_per_student
        )
        expense += semester_expense

        for term in semester.terms:
            # term income
            term_tuition_income = (
                students_remaining * cost_per_credit * config.credits_per_term
            )
            income += term_tuition_income

            # term expense
            term_costs = config.term_costs

            term_content_expense = 0.0
            if term.has_licensed_content:
                term_content_expense = (
                    students_remaining * term_costs.content_per_credit_hour
                )

            term_instruction_expense = (
                students_remaining * term_costs.instructor_per_student
            )

            term_intensive_lecturer_expense = 0.0
            if term.has_intensive_lecturer:
                term_intensive_lecturer_expense = term_costs.intensive_lecturer

            term_intensive_experience_expense = 0.0
            if term.has_intensive_experience:
                term_intensive_experience_expense = term_costs.intensive_experience

            expense += (
                term_instruction_expense
                + term_content_expense
                + term_intensive_lecturer_expense
                + term_intensive_experience_expense
            )

            # Term dropout
            students_remaining *= 1.0 - config.dropout_rate_per_term

    net_revenue = income - expense

    return EducationResult(
        net_revenue=net_revenue,
        students_remaining=students_remaining,
    )


def alumni_phase(
    alumni_count: float,
    awareness: float,
    preference: float,
    alumni_config: AlumniConfig,
    market_config: MarketConfig,
):
    """
    Calculates the effects of alumni on awareness, preference, and donations.

    Alumni contribute through word-of-mouth (awareness) and career success (preference).
    Both effects have diminishing returns as awareness/preference approach 100%.
    """
    # Awareness: alumni reach unaware people
    people_reached = alumni_count * alumni_config.candidates_reached_per_year
    unaware_fraction = (100 - awareness) / 100
    people_newly_aware = people_reached * unaware_fraction
    awareness_boost = (people_newly_aware / market_config.size) * 100

    # Preference: alumni influence aware people
    aware_population = market_config.size * (awareness / 100)
    if aware_population > 0:
        people_influenced = alumni_count * alumni_config.candidates_influenced_per_year
        unconvinced_fraction = (100 - preference) / 100
        people_newly_convinced = people_influenced * unconvinced_fraction
        preference_boost = (people_newly_convinced / aware_population) * 100
    else:
        preference_boost = 0

    # Donations
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
):
    """
    Calculates the effects of marketing spend on awareness and preference.

    Marketing is more effective at building awareness than preference.
    Both effects have diminishing returns as awareness/preference approach 100%.
    """
    # Awareness: dollars → people reached → awareness points
    people_reached = marketing_spend / marketing_config.cost_to_reach_one_candidate
    unaware_fraction = (100 - awareness) / 100  # headroom
    people_newly_aware = people_reached * unaware_fraction
    awareness_boost = (people_newly_aware / market_config.size) * 100

    # Preference: dollars → people influenced → preference points
    aware_population = market_config.size * (awareness / 100)
    if aware_population > 0:
        people_influenced = (
            marketing_spend / marketing_config.cost_to_influence_one_candidate
        )
        unconvinced_fraction = (100 - preference) / 100  # headroom
        people_newly_convinced = people_influenced * unconvinced_fraction
        preference_boost = (people_newly_convinced / aware_population) * 100
    else:
        preference_boost = 0

    return MarketingResult(
        awareness_boost=awareness_boost,
        preference_boost=preference_boost,
    )


def enrollment_phase(
    reputation: Reputation,
    total_tuition_cost: float,
    enrollment_config: EnrollmentConfig,
    market_config: MarketConfig,
):
    """
    Calculates enrollment using a funnel model based on reputation and price.

    Funnel:
    1. Aware population = market size × awareness
    2. Base preference = preference (would choose us ignoring price)
    3. Price-adjusted preference = base × price_factor (high preference protects)
    4. Would choose us = aware × price-adjusted preference
    5. Applicants = would_choose × application_rate
    6. Enrolled = min(applicants, max_students)
    """
    # Step 1: Aware population
    aware_population = market_config.size * (reputation.awareness / 100)

    # Step 2: Base preference (would choose us if price wasn't a factor)
    base_choice_rate = reputation.preference / 100

    # Step 3: Price adjustment (high preference reduces price sensitivity)
    tuition_range = market_config.tuition_high - market_config.tuition_low
    if tuition_range > 0:
        price_position = (
            total_tuition_cost - market_config.tuition_low
        ) / tuition_range
        price_position = max(0.0, min(1.0, price_position))  # clamp to 0-1
    else:
        price_position = 0.0

    # High prestige protects against price sensitivity
    effective_sensitivity = enrollment_config.price_sensitivity * (1 - base_choice_rate)
    price_factor = max(0.0, 1 - effective_sensitivity * price_position)

    # Effective choice rate = base preference adjusted by price
    effective_choice_rate = base_choice_rate * price_factor

    # Step 4: Would choose us
    would_choose = aware_population * effective_choice_rate

    # Step 5: Actually apply
    applicants = would_choose * enrollment_config.application_rate

    # Step 6: Enroll (capped by capacity)
    enrolled = min(applicants, enrollment_config.max_students)

    return EnrollmentResult(
        students_enrolled=enrolled,
    )


def run_year(
    prior_year_result: YearResult,
    cost_per_credit: float,
    total_tuition_cost: float,
    config: SimulationConfig,
    skip_spring_summer: bool = False,
):
    # Initial state
    reputation = Reputation(
        alumni_count=prior_year_result.reputation.alumni_count,
        awareness=prior_year_result.reputation.awareness,
        preference=prior_year_result.reputation.preference,
    )
    net_revenue = 0

    # Apply decay at start of year (reputation fades without maintenance)
    reputation.awareness *= 1 - config.reputation.awareness_decay_rate
    reputation.preference *= 1 - config.reputation.preference_decay_rate

    # Spring/Summer Education (skip if flagged, e.g., first year covered by donations)
    if skip_spring_summer:
        # Students who completed fall still graduate, but no revenue/expense
        reputation.alumni_count += prior_year_result.fall_students_remaining
        spring_summer_marketing_spend = 0.0
    else:
        spring_summer_semesters = (
            config.education.years[1] if len(config.education.years) > 1 else []
        )
        spring_summer_education = education_phase(
            prior_year_result.fall_students_remaining,
            spring_summer_semesters,
            cost_per_credit,
            config.education,
        )
        reputation.alumni_count += spring_summer_education.students_remaining
        net_revenue += spring_summer_education.net_revenue

        spring_summer_marketing_spend = max(
            0.0, spring_summer_education.net_revenue * config.marketing.spend_pct
        )
        net_revenue -= spring_summer_marketing_spend

    # Alumni Effects
    alumni_result = alumni_phase(
        reputation.alumni_count,
        reputation.awareness,
        reputation.preference,
        config.alumni,
        config.market,
    )
    reputation.awareness += alumni_result.awareness_boost
    reputation.preference += alumni_result.preference_boost
    net_revenue += alumni_result.donations

    # Marketing
    marketing_spend = (
        prior_year_result.fall_marketing_spend + spring_summer_marketing_spend
    )
    marketing_result = marketing_phase(
        marketing_spend,
        reputation.awareness,
        reputation.preference,
        config.marketing,
        config.market,
    )
    reputation.awareness += marketing_result.awareness_boost
    reputation.preference += marketing_result.preference_boost

    # Clamp awareness and preference to valid range (0-100%)
    reputation.awareness = max(0.0, min(100.0, reputation.awareness))
    reputation.preference = max(0.0, min(100.0, reputation.preference))

    # Enrollment
    enrollment = enrollment_phase(
        reputation,
        total_tuition_cost,
        config.enrollment,
        config.market,
    )

    # Fall Education
    fall_semesters = (
        config.education.years[0] if len(config.education.years) > 0 else []
    )
    fall_education = education_phase(
        enrollment.students_enrolled,
        fall_semesters,
        cost_per_credit,
        config.education,
    )
    net_revenue += fall_education.net_revenue

    fall_marketing_spend = max(
        0.0, fall_education.net_revenue * config.marketing.spend_pct
    )
    net_revenue -= marketing_spend

    # End of year result
    return YearResult(
        fall_marketing_spend=fall_marketing_spend,
        fall_students_remaining=fall_education.students_remaining,
        net_revenue=net_revenue,
        reputation=reputation,
    )


def run_model(
    cost_per_credit: float, num_years: int, config: SimulationConfig
) -> List[YearResult]:
    results = []

    initial_state = config.initial_state
    prior_year_result = YearResult(
        fall_marketing_spend=initial_state.prior_fall_marketing_spend,
        fall_students_remaining=initial_state.prior_fall_students_remaining,
        net_revenue=0.0,
        reputation=Reputation(
            alumni_count=initial_state.alumni_count,
            awareness=initial_state.awareness,
            preference=initial_state.preference,
        ),
    )

    terms_per_year = sum(
        len(semester.terms) for year in config.education.years for semester in year
    )
    if terms_per_year == 0:
        raise ValueError("Education config must include at least one term.")
    total_tuition_cost = (
        cost_per_credit * config.education.credits_per_term * terms_per_year
    )

    for year in range(num_years):
        # Skip spring/summer in first year if configured (e.g., covered by donations)
        skip_spring_summer = (year == 0) and initial_state.skip_first_spring_summer

        prior_year_result = run_year(
            prior_year_result,
            cost_per_credit,
            total_tuition_cost,
            config,
            skip_spring_summer=skip_spring_summer,
        )

        results.append(prior_year_result)

    return results
