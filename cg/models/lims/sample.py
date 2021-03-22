from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator
from typing_extensions import Literal

SEX_MAP = {"male": "M", "female": "F"}


class Udf(BaseModel):
    application: str
    capture_kit: Optional[str]
    comment: Optional[str]
    concentration: Optional[str]
    concentration_sample: Optional[str]
    customer: str
    data_analysis: Optional[str]
    data_delivery: Optional[str]
    elution_buffer: Optional[str]
    extraction_method: Optional[str]
    family_name: str = "NA"
    formalin_fixation_time: Optional[str]
    index: Optional[str]
    index_number: Optional[str]
    lab_code: Optional[str]
    organism: Optional[str]
    organism_other: Optional[str]
    pool: Optional[str]
    post_formalin_fixation_time: Optional[str]
    pre_processing_method: Optional[str]
    priority: str = "standard"
    quantity: Optional[str]
    reference_genome: Optional[str]
    region_code: Optional[str]
    require_qcok: bool = False
    rml_plate_name: Optional[str]
    selection_criteria: Optional[str]
    sex: Literal["M", "F", "unknown"] = "unknown"
    source: str = "NA"
    tissue_block_size: Optional[str]
    tumour: bool = False
    tumour_purity: Optional[str]
    volume: Optional[str]
    well_position_rml: Optional[str]
    verified_organism: Optional[str]

    @validator("sex", pre=True)
    def validate_sex(cls, value: str):
        return SEX_MAP.get(value, "unknown")


class LimsSample(BaseModel):
    name: str
    container: str = "Tube"
    container_name: Optional[str]
    well_position: Optional[str]
    index_sequence: Optional[str]
    udfs: Optional[Udf]
