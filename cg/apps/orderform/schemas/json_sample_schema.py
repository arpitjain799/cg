from cg.apps.orderform.schemas.orderform_schema import OrderSample
from pydantic import Field


class JsonSample(OrderSample):
    case_id: str = Field(None, alias="family_name")
