import importlib.resources
import json
from typing import List

from pydantic import BaseModel


class InitialState(BaseModel):
    alumni_count: float
    awareness: float
    prestige: float
    prior_fall_marketing_spend: float
    prior_fall_students_remaining: float


# --- Enrollment ---


class DemandConfig(BaseModel):
    price_min: float
    price_max: float
    demand_steepness: float
    enrollment_intercept: float
    w_awareness: float


class EnrollmentConfig(BaseModel):
    max_students: float
    base_awareness: float
    marketing_efficiency: float
    demand: DemandConfig


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
    years: List[List[Semester]]


# --- Alumni ---


class AlumniConfig(BaseModel):
    candidates_advertised_per_year: float
    donation_per_year: float


class MarketingConfig(BaseModel):
    base_awareness: float
    spend_pct: float
    marketing_efficiency: float


# --- Root ---


class SimulationConfig(BaseModel):
    initial_state: InitialState
    enrollment: EnrollmentConfig
    education: EducationConfig
    alumni: AlumniConfig
    marketing: MarketingConfig


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
