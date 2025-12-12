import importlib.resources
import json
from typing import List

from pydantic import BaseModel


class InitialState(BaseModel):
    """Starting conditions before year 1 begins."""

    alumni_count: float
    awareness: float  # fraction of market aware of program (0-1)
    preference: float  # fraction of aware candidates who would choose us (0-1)
    prior_fall_marketing_spend: float
    prior_fall_students_remaining: float
    skip_first_spring_summer: bool  # ignoring this launch year


class MarketConfig(BaseModel):
    size: float  # people who would consider enrolling in an EMBA program
    growth_rate: float
    tuition_low: float
    tuition_high: float


class ReputationConfig(BaseModel):
    awareness_decay_rate: float  # fraction lost per year
    preference_decay_rate: float


class AlumniConfig(BaseModel):
    candidates_reached_per_year: float  # people each alumnus makes aware
    candidates_influenced_per_year: float  # aware people each alumnus makes prefer
    donation_per_year: float


class MarketingConfig(BaseModel):
    spend_pct: float  # fraction of program revenue allocated to marketing
    cost_to_reach_one_candidate: float
    cost_to_influence_one_candidate: float


class EnrollmentConfig(BaseModel):
    max_students: float
    application_rate: float  # % of potentials that actually attend an emba
    price_sensitivity: float  # higher = more enrollment loss at high prices


# --- Education ---


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
    years: List[List[Semester]]  # [0] = fall, [1] = spring/summer


# --- Full ---


class SimulationConfig(BaseModel):
    initial_state: InitialState
    market: MarketConfig
    reputation: ReputationConfig
    alumni: AlumniConfig
    marketing: MarketingConfig
    enrollment: EnrollmentConfig
    education: EducationConfig


def load_config(config_path: str = None) -> SimulationConfig:
    """Load configuration from file path or package defaults."""
    if config_path:
        with open(config_path, "r") as f:
            raw_config = json.load(f)
    else:
        try:
            config_file = importlib.resources.files("emba_tuition_model.data").joinpath(
                "default_config.json"
            )
            with config_file.open("r") as f:
                raw_config = json.load(f)
        except (ImportError, AttributeError, FileNotFoundError) as e:
            raise RuntimeError(f"Could not load default_config.json: {e}")

    return SimulationConfig(**raw_config)
