from datetime import date
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    name: str = 'Demo Citizen'; current_city: str; destination_city: str; state: str = 'Uttar Pradesh'; move_date: date | None = None; move_type: str; reason: str
    vehicle: bool = False; voter: bool = False; benefits: bool = False; student: bool = False; property: bool = False
class UserOut(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
class RelocationCreate(BaseModel):
    current_city: str; destination_city: str; state: str; move_date: date | None = None; move_type: str; reason: str
class ProfileCreate(BaseModel):
    vehicle: bool=False; voter: bool=False; benefits: bool=False; student: bool=False; property: bool=False
class ApplicationCreate(BaseModel):
    user_id: int; service_id: str
class ApplicationPatch(BaseModel):
    status: str
class ChatRequest(BaseModel):
    user_id: int; message: str
