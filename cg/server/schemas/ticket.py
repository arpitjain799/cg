from pydantic import BaseModel, EmailStr


class TicketIn(BaseModel):
    """Class to describe a simple ticket"""

    name: str
    email: EmailStr
