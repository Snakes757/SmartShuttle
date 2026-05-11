from pydantic import BaseModel, Field, ConfigDict, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional, List

class UserRole(str, Enum):
    PASSENGER = "Passenger"
    SHUTTLE_OWNER = "ShuttleOwner"
    ADMIN = "Admin"

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"

class TripStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class PassengerBase(BaseModel):
    full_name: str = Field(..., description="Full Name of the passenger")
    gender: GenderEnum
    id_number: str = Field(..., description="Passenger ID Number")
    age: int = Field(..., description="Age of the passenger")
    email: EmailStr
    phone_number: str
    parent_id: Optional[str] = Field(default=None, description="Required if age < 18")
    is_verified: bool = Field(default=False, description="Verified via SMS/Email")

class PassengerCreate(PassengerBase):
    password: str

class PassengerResponse(PassengerBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class VehicleDetails(BaseModel):
    make_model: str
    capacity: int = Field(..., description="Number of seats")
    has_trailer: bool = Field(default=False, description="Must be true if capacity == 7")
    drivers_license_url: str
    pdp_document_url: str
    dekra_report_url: str
    vehicle_photos_urls: List[str]

class ShuttleOwnerBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    vehicle: VehicleDetails
    is_approved_by_admin: bool = False

class ShuttleOwnerCreate(ShuttleOwnerBase):
    password: str

class ShuttleOwnerResponse(ShuttleOwnerBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class RouteBase(BaseModel):
    name: str
    point_a_start: str
    point_b_end: str
    base_distance_km: float

class RouteCreate(RouteBase):
    pass

class RouteResponse(RouteBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class TripBase(BaseModel):
    route_id: str
    driver_id: str
    departure_time: datetime
    status: TripStatus = TripStatus.PENDING

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    id: str
    passenger_id: str
    model_config = ConfigDict(from_attributes=True)

class PickUpPointBase(BaseModel):
    trip_id: str
    location_name: str
    latitude: float
    longitude: float
    radius: float

class PickUpPointCreate(PickUpPointBase):
    pass

class FareCalculationRequest(BaseModel):
    route_id: str
    trip_time: datetime
    passengers_count: int
    tolls_estimated: float

class FareResponse(BaseModel):
    base_fare: float
    tolls: float
    commission: float
    total_cost: float
    cost_per_passenger: float
    strategy_applied: str