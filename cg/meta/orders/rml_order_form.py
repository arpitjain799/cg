from typing import List, Optional

from pydantic import BaseModel


class RMLSample(BaseModel):
    application: str
    comment: Optional[str] = None
    concentration: int
    concentration_sample: int
    data_analysis: str
    data_delivery: str
    index: str
    index_sequence: str
    name: str
    pool: str
    priority: str
    volume: int


# This is for validating indata
class RMLOrderform(BaseModel):
    comment: str
    customer: str
    name: str
    samples: List[RMLSample]


class StatusSample(BaseModel):
    application: str
    comment: Optional[str] = None
    data_delivery: Optional[str] = None
    name: str
    priority: str
    internal_id: Optional[str] = None


class Pool(BaseModel):
    name: str
    application: str
    data_analysis: str
    data_delivery: str
    samples: List[StatusSample]


# This is for specifying outdata
class StatusData(BaseModel):
    customer: str
    order: str
    comment: str
    pools: List[Pool]
