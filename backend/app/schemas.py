from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime
from uuid import UUID


# ENUMS

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class TripStatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# PASSENGER SCHEMAS

class PassengerBase(BaseModel):
    full_name: str = Field(..., description="Passenger's full legal name")
    gender: GenderEnum
    id_number: str = Field(..., description="National ID or Passport Number")
    age: int = Field(..., gt=0, description="Passenger's age")
    email: EmailStr
    phone_number: str

class PassengerCreate(PassengerBase):
    password: str = Field(..., min_length=8, max_length=15)

class PassengerResponse(PassengerBase):
    id: UUID
    created_at: datetime
    
    # ConfigDict(from_attributes=True) allows Pydantic to read data from ORM models (like SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)



# SHUTTLE OWNER SCHEMAS
# System serves both passengers & owners


class ShuttleOwnerBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    business_name: Optional[str] = None

class ShuttleOwnerCreate(ShuttleOwnerBase):
    password: str = Field(..., min_length=8, max_length=15)

class ShuttleOwnerResponse(ShuttleOwnerBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ROUTE SCHEMAS
# Exists independent of trips. Has Point A & Point B.

class RouteBase(BaseModel):
    name: str = Field(..., description="e.g., Pretoria to Johannesburg")
    point_a_start: str = Field(..., description="Starting location/coordinate")
    point_b_end: str = Field(..., description="Ending location/coordinate")
    distance_km: Optional[float] = None

class RouteCreate(RouteBase):
    pass

class RouteResponse(RouteBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# TRIP SCHEMAS
# A trip uses a single route. 


class TripBase(BaseModel):
    route_id: UUID
    shuttle_id: UUID  # Reference to the specific vehicle/taxi used
    departure_time: datetime
    status: TripStatusEnum = TripStatusEnum.SCHEDULED

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# PICK-UP POINT SCHEMAS
#  Requests to edit a route with a radius limitation.


class PickUpPointBase(BaseModel):
    trip_id: UUID
    passenger_id: UUID
    location_name: str = Field(..., description="e.g., James, Lethabo, Lerutle")
    latitude: float
    longitude: float
    radius_meters: float = Field(..., description="Radius such that the location does not affect the route heavily")
    is_within_radius: bool = Field(default=True, description="Flag indicating if the point lies outside the allowed radius (like 'Tau' in PPTX)")

class PickUpPointCreate(PickUpPointBase):
    pass

class PickUpPointResponse(PickUpPointBase):
    id: UUID
    request_time: datetime
    
    model_config = ConfigDict(from_attributes=True)