from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# According to project rules, collection name will be the lowercase class name: "contactmessage"
class ContactMessage(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=5000)
    source: Optional[str] = None
