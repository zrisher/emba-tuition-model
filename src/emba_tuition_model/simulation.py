from dataclasses import dataclass
from typing import List

from .config import (
    AlumniConfig,
    EducationConfig,
    EnrollmentConfig,
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
    prestige_boost: float


@dataclass
class MarketingResult:
    """
    The effects of marketing during a full program.
    """

    awareness_boost: float
    prestige_boost: float


@dataclass
class EnrollmentResult:
    """
    The effects of awareness, prestige, and cost on a program's enrollment.
    """

    students_enrolled: float


@dataclass
class Reputation:
    """
    The cumulative state of the program's reputation.
    """

    alumni_count: float
    awareness: float  # percent of all applicants who are aware of the program
    prestige: float  # percent of all applicants who would choose this program


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


def alumni_phase(alumni_count: float, config: AlumniConfig):
    # @TODO
    awareness_boost = alumni_count * 0
    prestige_boost = alumni_count * 0

    donations = alumni_count * config.donation_per_year

    return AlumniEffectResult(
        awareness_boost=awareness_boost,
        prestige_boost=prestige_boost,
        donations=donations,
    )


def marketing_phase(
    marketing_spend_for_awareness: float,
    reputation: Reputation,
    total_tuition_cost: float,
    config: MarketingConfig,
):
    # @TODO
    awareness_boost = 0
    prestige_boost = 0

    return MarketingResult(
        awareness_boost=awareness_boost,
        prestige_boost=prestige_boost,
    )


def enrollment_phase(
    reputation: Reputation,
    total_tuition_cost: float,
    config: EnrollmentConfig,
):
    """
    Calculates enrollment demand using a non-linear (Logistic/Sigmoid) function
    based on total tuition and reputation.
    """

    """ old logic
    
    min_price = config.enrollment.demand.price_min
    max_price = config.enrollment.demand.price_max

    # Config parameters for the curve
    midpoint = (min_price + max_price) / 2  # Approx 52.5k
    steepness = config.enrollment.demand.demand_steepness

    # Base demand potential based on awareness (Market Size)
    base_market_size = config.enrollment.demand.enrollment_intercept + (
        awareness * config.enrollment.demand.w_awareness
    )

    # Logistic Function
    try:
        logit = steepness * (tuition_total - midpoint)
        probability = 1.0 / (1.0 + math.exp(logit))
    except OverflowError:
        probability = 0.0

    estimated_demand = base_market_size * probability
    return estimated_demand
    """

    # @TODO
    # Simple placeholder logic until a richer enrollment model is implemented
    applications_submitted = max(
        0.0, config.max_students * (config.base_awareness / 100)
    )
    applications_approved = min(applications_submitted, config.max_students)

    return EnrollmentResult(
        students_enrolled=applications_approved,
    )


def run_year(
    prior_year_result: YearResult,
    cost_per_credit: float,
    total_tuition_cost: float,
    config: SimulationConfig,
):
    # Initial state
    reputation = Reputation(
        alumni_count=prior_year_result.reputation.alumni_count,
        awareness=prior_year_result.reputation.awareness,
        prestige=prior_year_result.reputation.prestige,
    )
    net_revenue = 0

    # Spring/Summer Education
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
        config.alumni,
    )
    reputation.awareness += alumni_result.awareness_boost
    reputation.prestige += alumni_result.prestige_boost
    net_revenue += alumni_result.donations

    # Marketing
    marketing_spend = (
        prior_year_result.fall_marketing_spend + spring_summer_marketing_spend
    )
    marketing_result = marketing_phase(
        marketing_spend,
        reputation,
        total_tuition_cost,
        config.marketing,
    )
    reputation.awareness += marketing_result.awareness_boost
    reputation.prestige += marketing_result.prestige_boost

    # Enrollment
    enrollment = enrollment_phase(
        reputation,
        total_tuition_cost,
        config.enrollment,
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
            prestige=initial_state.prestige,
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
        prior_year_result = run_year(
            prior_year_result,
            cost_per_credit,
            total_tuition_cost,
            config,
        )

        results.append(prior_year_result)

    return results
