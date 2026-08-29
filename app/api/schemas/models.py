from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, model_validator

class RelocationProfile(BaseModel):
    """Non-sensitive facts used to personalize a relocation journey."""
    origin_city: str | None = None; origin_state: str | None = None
    destination_city: str; destination_state: str | None = None
    move_scope: Literal['intra_state', 'interstate'] | None = None
    move_date: date | None = None; move_type: Literal['permanent', 'temporary']; reason: str
    # Input-only aliases retained for existing demo clients.
    current_city: str | None = None; state: str | None = None

    @model_validator(mode='before')
    @classmethod
    def normalize_legacy_and_validate_locations(cls, value):
        if not isinstance(value, dict): return value
        data = dict(value)
        data.setdefault('origin_city', data.get('current_city'))
        data.setdefault('origin_state', data.get('state'))
        data.setdefault('destination_state', data.get('state'))
        if not data.get('origin_state'): raise ValueError('origin_state is required')
        if not data.get('destination_state'): raise ValueError('destination_state is required')
        return data

    @model_validator(mode='after')
    def derive_move_scope(self):
        self.move_scope = 'intra_state' if self.origin_state.strip().casefold() == self.destination_state.strip().casefold() else 'interstate'
        return self

class UserCreate(RelocationProfile):
    name: str = 'Demo Citizen'
    vehicle: bool = False; voter: bool = False; benefits: bool = False; student: bool = False; property: bool = False
class UserOut(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
class RelocationCreate(RelocationProfile):
    pass
class ProfileCreate(BaseModel):
    vehicle: bool=False; voter: bool=False; benefits: bool=False; student: bool=False; property: bool=False
class ApplicationCreate(BaseModel):
    user_id: int; service_id: str
class ApplicationPatch(BaseModel):
    status: str
class ChatRequest(BaseModel):
    user_id: int; message: str
