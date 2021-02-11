from typing import List, Optional

from pydantic import BaseModel


class OrderIn(BaseModel):
    name: str
    customer: str
    comment: Optional[str]
    samples: List[dict]
