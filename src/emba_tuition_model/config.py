import importlib.resources
import json
from typing import List

from pydantic import BaseModel

# =============================================================================
# Initial State
# =============================================================================
# Starting conditions for the simulation. Represents the program's state
# before year 1 begins (e.g., after initial marketing and first cohort recruitment).


class InitialState(BaseModel):
    alumni_count: float  # Graduates from prior years
    awareness: float  # % of market who know we exist (0-100)
    preference: float  # % of aware candidates who would choose us (0-100)
    prior_fall_marketing_spend: float  # Marketing budget carried into year 1
    prior_fall_students_remaining: float  # Students entering spring/summer of year 1
    # Skip spring/summer in year 1 (e.g., if covered by donations)
    skip_first_spring_summer: bool = False


# =============================================================================
# Market
# =============================================================================
# External market conditions. Defines the total addressable market and
# competitive pricing landscape.


class MarketConfig(BaseModel):
    size: float  # Total addressable candidates (professionals who could do EMBA)
    growth_rate: float  # Annual market growth rate (e.g., 0.03 = 3%)
    tuition_low: float  # Lowest competitive tuition in market
    tuition_high: float  # Highest competitive tuition in market


# =============================================================================
# Reputation
# =============================================================================
# How reputation decays over time. Without active maintenance (alumni activity,
# marketing), awareness and preference naturally fade.


class ReputationConfig(BaseModel):
    awareness_decay_rate: float  # Fraction lost per year (e.g., 0.1 = 10%)
    preference_decay_rate: float  # Fraction lost per year (e.g., 0.05 = 5%)


# =============================================================================
# Alumni
# =============================================================================
# How alumni contribute to reputation building through word-of-mouth
# and career success.


class AlumniConfig(BaseModel):
    candidates_reached_per_year: float  # People each alumnus makes aware per year
    candidates_influenced_per_year: float  # Aware people each alumnus convinces
    donation_per_year: float  # Average annual donation per alumnus ($)


# =============================================================================
# Marketing
# =============================================================================
# How marketing spend translates to reputation building.


class MarketingConfig(BaseModel):
    spend_pct: float  # Fraction of revenue allocated to marketing (e.g., 0.05 = 5%)
    cost_to_reach_one_candidate: float  # $ to make 1 person aware
    cost_to_influence_one_candidate: float  # $ to convince 1 aware person


# =============================================================================
# Enrollment
# =============================================================================
# How reputation and price translate to enrolled students.
# Funnel: aware → interested (preference) → price-adjusted → apply → enroll


class EnrollmentConfig(BaseModel):
    max_students: float  # Program capacity per cohort
    application_rate: float  # Fraction of interested candidates who apply
    price_sensitivity: float  # At max price with 0% preference, lose this fraction


# =============================================================================
# Education
# =============================================================================
# Program structure, costs, and fees. Defines semesters, terms, and the
# economics of delivering education.


class Term(BaseModel):
    name: str
    has_licensed_content: bool
    has_intensive_lecturer: bool
    has_intensive_experience: bool


class Semester(BaseModel):
    name: str
    terms: List[Term]


class SemesterCosts(BaseModel):
    general_per_student: float
    technology_per_student: float


class SemesterFees(BaseModel):
    general_per_student: float
    program_per_student: float
    technology_per_student: float


class TermCosts(BaseModel):
    content_per_credit_hour: float
    instructor_per_student: float
    intensive_lecturer: float
    intensive_experience: float


class EducationConfig(BaseModel):
    credits_per_term: int
    dropout_rate_per_term: float
    semester_costs: SemesterCosts
    semester_fees: SemesterFees
    term_costs: TermCosts
    years: List[List[Semester]]  # years[0] = fall semesters, years[1] = spring/summer


# =============================================================================
# Root Configuration
# =============================================================================


class SimulationConfig(BaseModel):
    initial_state: InitialState
    market: MarketConfig
    reputation: ReputationConfig
    alumni: AlumniConfig
    marketing: MarketingConfig
    enrollment: EnrollmentConfig
    education: EducationConfig


# =============================================================================
# Config Loading
# =============================================================================


def load_config(config_path: str = None) -> SimulationConfig:
    """
    Load configuration from a file path or default resources.
    """
    if config_path:
        with open(config_path, "r") as f:
            raw_config = json.load(f)
    else:
        # Load from package resources
        try:
            config_file = importlib.resources.files("emba_tuition_model.data").joinpath(
                "default_config.json"
            )
            with config_file.open("r") as f:
                raw_config = json.load(f)
        except (ImportError, AttributeError, FileNotFoundError) as e:
            raise RuntimeError(f"Could not load default_config.json: {e}")

    return SimulationConfig(**raw_config)
