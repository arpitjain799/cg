from typing import List, Optional

from cg.apps.lims.orderform import REV_SEX_MAP, SOURCE_TYPES
from pydantic import BaseModel, Field, validator


class ExcelSample(BaseModel):
    application: str = Field(..., alias="UDF/Sequencing Analysis")
    capture_kit: str = Field(None, alias="UDF/Capture Library version")
    case: str = Field(None, alias="UDF/familyID")
    comment: str = Field(None, alias="UDF/Comment")
    container: str = Field(None, alias="Container/Type")
    container_name: str = Field(None, alias="Container/Name")
    custom_index: str = Field(None, alias="UDF/Custom index")
    customer: str = Field(..., alias="UDF/customer")
    data_analysis: str = Field(..., alias="UDF/Data Analysis")
    data_delivery: str = Field(None, alias="UDF/Data Delivery")
    elution_buffer: str = Field(None, alias="UDF/Sample Buffer")
    extraction_method: str = Field(None, alias="UDF/Extraction method")
    formalin_fixation_time: str = Field(None, alias="UDF/Formalin Fixation Time")
    index: str = Field(None, alias="UDF/Index type")
    from_sample: str = Field(None, alias="UDF/is_for_sample")
    name: str = Field(..., alias="Sample/Name")
    organism: str = Field(None, alias="UDF/Strain")
    organism_other: str = Field(None, alias="UDF/Other species")
    panels: List[str] = Field(None, alias="UDF/Gene List")
    pool: str = Field(None, alias="UDF/pool name")
    post_formalin_fixation_time: str = Field(None, alias="UDF/Post Formalin Fixation Time")
    priority: str = Field(None, alias="UDF/priority")
    reagent_label: str = Field(None, alias="Sample/Reagent Label")
    reference_genome: str = Field(None, alias="UDF/Reference Genome Microbial")
    require_qcok: bool = Field(None, alias="UDF/Process only if QC OK")
    rml_plate_name: str = Field(None, alias="UDF/RML plate name")
    sex: str = Field(None, alias="UDF/Gender")
    source: str = Field(None, alias="UDF/Source")
    status: str = Field(None, alias="UDF/Status")
    tissue_block_size: str = Field(None, alias="UDF/Tissue Block Size")
    tumour: bool = Field(None, alias="UDF/tumor")
    tumour_purity: str = Field(None, alias="UDF/tumour purity")
    well_position: str = Field(None, alias="Sample/Well Location")
    well_position_rml: str = Field(None, alias="UDF/RML well position")

    @validator("source")
    def validate_source(cls, value: Optional[str]):
        if value in SOURCE_TYPES:
            return value
        return None

    @validator("sex")
    def convert_sex(cls, value: Optional[str]):
        if not value:
            return None
        value = value.strip()
        return REV_SEX_MAP.get(value)

    @validator("require_qcok", "tumour")
    def check_yes(cls, value):
        return bool(value and value == "yes")

    @validator("panels")
    def parse_panels(cls, value):
        if not value:
            return None
        separator = ";"
        if ":" in value:
            separator = ":"
        return value.split[separator]

    @validator("priority", "status")
    def convert_to_lower(cls, value: Optional[str]):
        if not value:
            return None
        value = value.lower()
        if value == "förtur":
            return "priority"
        return value
