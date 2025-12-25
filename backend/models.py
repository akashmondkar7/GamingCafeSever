from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime, timezone
from enum import Enum
import uuid

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CAFE_OWNER = "CAFE_OWNER"
    STAFF = "STAFF"
    CUSTOMER = "CUSTOMER"

class SubscriptionStatus(str, Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    GRACE = "GRACE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class SubscriptionPlan(str, Enum):
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"

class DeviceType(str, Enum):
    PC = "PC"
    PS5 = "PS5"
    VR = "VR"
    SIMULATOR = "SIMULATOR"

class DeviceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXTENDED = "EXTENDED"

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: Optional[str] = None
    phone: str
    name: str
    role: UserRole
    cafe_id: Optional[str] = None
    wallet_balance: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Cafe(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    owner_id: str
    address: str
    city: str
    description: Optional[str] = None
    subscription_id: Optional[str] = None
    slug: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Subscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cafe_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    price: float
    start_date: datetime
    end_date: datetime
    auto_renew: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Device(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cafe_id: str
    name: str
    device_type: DeviceType
    status: DeviceStatus = DeviceStatus.AVAILABLE
    specifications: Optional[str] = None
    hourly_rate: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Session(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    device_id: str
    cafe_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_hours: Optional[float] = None
    total_amount: float = 0.0
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Game(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cafe_id: str
    name: str
    device_types: List[DeviceType]
    description: Optional[str] = None
    guide: Optional[str] = None
    age_restriction: Optional[int] = None
    popularity_score: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIConversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cafe_owner_id: str
    agent_type: str
    message: str
    response: str
    context: Optional[Dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response models
class LoginRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

class RegisterRequest(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER

class AuthResponse(BaseModel):
    token: str
    user: User

class CafeCreate(BaseModel):
    name: str
    address: str
    city: str
    description: Optional[str] = None

class DeviceCreate(BaseModel):
    name: str
    device_type: DeviceType
    specifications: Optional[str] = None
    hourly_rate: float

class SessionCreate(BaseModel):
    device_id: str
    customer_id: str

class AIMessage(BaseModel):
    message: str
    agent_type: str = "OWNER_ASSISTANT"

class DeviceStatusUpdate(BaseModel):
    status: DeviceStatus
