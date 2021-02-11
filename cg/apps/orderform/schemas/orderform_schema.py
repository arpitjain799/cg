from enum import Enum
from typing import List, Optional

from cg.constants import DataDelivery, Pipeline
from pydantic import BaseModel, constr


class SexEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class PriorityEnum(str, Enum):
    research = "research"
    standard = "standard"
    priority = "priority"
    express = "express"
    clinical_trials = "clinical trials"


class ContainerEnum(str, Enum):
    agilent_sureselect_cre = "Agilent Sureselect CRE"
    agilent_sureselect_v5 = "Agilent Sureselect V5"
    sureselect_focused_exome = "SureSelect Focused Exome"
    twist_target_hg19_bed = "Twist_Target_hg19.bed"
    other = "other"


class StatusEnum(str, Enum):
    affected = "affected"
    unaffected = "unaffected"
    unknown = "unknown"


STATUS_OPTIONS = ()

NAME_PATTERN = r"^[A-Za-z0-9-]*$"


# Validating orderform
class OrderSample(BaseModel):
    age_at_sampling: Optional[str]
    application: str
    capture_kit: Optional[str]
    case_id: str
    cohorts: List[str] = None
    comment: Optional[str]
    concentration: int
    concentration_sample: int
    container: ContainerEnum = ContainerEnum.other
    container_name: Optional[str]
    customer: Optional[str]
    custom_index: Optional[str]
    data_analysis: Pipeline
    data_delivery: DataDelivery
    elution_buffer: Optional[str]
    extraction_method: Optional[str]
    family_name: Optional[str]
    father: Optional[str]
    formalin_fixation_time: Optional[int]
    from_sample: Optional[str]
    index: str
    index_number: Optional[int]
    index_sequence: Optional[str]
    internal_id: Optional[str]
    mother: Optional[str]
    name: constr(regex=NAME_PATTERN)
    organism: Optional[str]
    organism_other: Optional[str]
    panels: List[str] = None
    phenotype_terms: List[str] = None
    pool: str
    post_formalin_fixation_time: Optional[int]
    priority: PriorityEnum = PriorityEnum.standard
    quantity: Optional[int]
    reagent_label: Optional[str]
    reference_genome: Optional[str]
    require_qcok: bool = False
    rml_plate_name: Optional[str]
    sex: SexEnum = SexEnum.other
    source: Optional[str]
    status: StatusEnum = StatusEnum.unknown
    synopsis: Optional[str]
    time_point: Optional[int]
    tissue_block_size: Optional[str]
    tumour: bool = False
    tumour_purity: Optional[int]
    volume: Optional[int]
    well_position: Optional[str]
    well_position_rml: Optional[str]


# Class for holding information about cases in order
class OrderCase(BaseModel):
    name: str
    samples: List[OrderSample]
    require_qcok: bool = False
    priority: str
    panels: List[str] = None


class MipSample(OrderSample):
    family_name: constr(regex=NAME_PATTERN)
    panels: List[str]
    mother: Optional[constr(regex=NAME_PATTERN)]
    father: Optional[constr(regex=NAME_PATTERN)]


class BalsamicSample(OrderSample):
    name: constr(regex=NAME_PATTERN)
    panels: List[str]
    require_qcok: bool
    volume: str
    tumour: bool


class MipRNASample(OrderSample):
    from_sample: Optional[constr(regex=NAME_PATTERN)]
    name: constr(regex=NAME_PATTERN)
    volume = str


class ExternalSample(OrderSample):
    name: constr(regex=NAME_PATTERN)
    mother: Optional[constr(regex=NAME_PATTERN)]
    father: Optional[constr(regex=NAME_PATTERN)]


class ExternalSample(OrderSample):
    require_qcok: bool
    volume: str
    source: str
    elution_buffer: str
    mother: Optional[constr(regex=NAME_PATTERN)]
    father: Optional[constr(regex=NAME_PATTERN)]


class RMLSample(OrderSample):
    pool: str
    volume: str
    concentration: str
    index: str


class MicrosaltSample(OrderSample):
    organism: str
    reference_genome: str
    require_qcok: bool
    elution_buffer: str
    extraction_method: str


class MetagenomeSample(OrderSample):
    require_qcok: bool
    elution_buffer: str
    source: str


# This is for validating indata
class OrderformSchema(BaseModel):
    comment: Optional[str]
    delivery_type: str
    project_type: str
    customer: str
    name: str
    ticket: Optional[int] = None
    samples: List[OrderSample]
    cases: List[OrderCase] = None


class MipOrderform(OrderformSchema):
    samples: List[MipSample]
