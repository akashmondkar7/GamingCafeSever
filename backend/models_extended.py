from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime, timezone
from enum import Enum
import uuid
from models import DeviceType

# Game Library Models
class AgeRating(str, Enum):
    EVERYONE = "EVERYONE"
    TEEN = "TEEN"
    MATURE = "MATURE"
    ADULTS_ONLY = "ADULTS_ONLY"

class Game(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cafe_id: str
    name: str
    device_types: List[DeviceType]
    genre: str
    description: Optional[str] = None
    how_to_start: Optional[str] = None
    controls_guide: Optional[str] = None
    difficulty_level: Optional[str] = None
    video_tutorial_url: Optional[str] = None
    age_rating: AgeRating = AgeRating.EVERYONE
    popularity_score: int = 0
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Membership & Loyalty Models
class MembershipTier(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class PassType(str, Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class Membership(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    cafe_id: str
    tier: MembershipTier = MembershipTier.BRONZE
    points: int = 0
    total_spent: float = 0.0
    total_hours: float = 0.0
    referral_code: str
    referred_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Pass(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    cafe_id: str
    pass_type: PassType
    hours_included: float
    hours_used: float = 0.0
    price: float
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WalletTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    amount: float
    transaction_type: str  # credit, debit, refund, cashback
    description: str
    reference_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Pricing Models
class PricingRuleType(str, Enum):
    PEAK = "PEAK"
    OFFPEAK = "OFFPEAK"
    WEEKEND = "WEEKEND"
    HAPPY_HOUR = "HAPPY_HOUR"
    FESTIVAL = "FESTIVAL"

class PricingRule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cafe_id: str
    rule_type: PricingRuleType
    multiplier: float  # 1.5 for 50% increase, 0.7 for 30% discount
    start_time: Optional[str] = None  # HH:MM format
    end_time: Optional[str] = None
    days_of_week: Optional[List[int]] = None  # 0-6 (Monday-Sunday)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Coupon(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cafe_id: str
    code: str
    discount_type: str  # percentage, fixed
    discount_value: float
    min_amount: Optional[float] = None
    max_uses: Optional[int] = None
    used_count: int = 0
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Staff Models
class StaffShift(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    staff_id: str
    cafe_id: str
    shift_start: datetime
    shift_end: Optional[datetime] = None
    total_hours: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StaffAction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    staff_id: str
    cafe_id: str
    action_type: str  # check_in, device_assign, payment, etc
    details: Dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Device Health & Maintenance
class MaintenanceStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class DeviceMaintenance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    cafe_id: str
    issue_description: str
    maintenance_type: str  # cleaning, repair, upgrade
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DeviceHealthLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    metric: str  # temperature, uptime, errors, etc
    value: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Invoice Model
class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"

class Invoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    cafe_id: str
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    status: InvoiceStatus = InvoiceStatus.DRAFT
    line_items: List[Dict]
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    due_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models
class GameCreate(BaseModel):
    name: str
    device_types: List[DeviceType]
    genre: str
    description: Optional[str] = None
    how_to_start: Optional[str] = None
    controls_guide: Optional[str] = None
    difficulty_level: Optional[str] = None
    video_tutorial_url: Optional[str] = None
    age_rating: AgeRating = AgeRating.EVERYONE
    image_url: Optional[str] = None

class PurchasePassRequest(BaseModel):
    pass_type: PassType
    cafe_id: str

class ApplyCouponRequest(BaseModel):
    code: str
    session_id: str

class PricingRuleCreate(BaseModel):
    rule_type: PricingRuleType
    multiplier: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    days_of_week: Optional[List[int]] = None

class CouponCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    min_amount: Optional[float] = None
    max_uses: Optional[int] = None
    valid_days: int = 30

class DeviceMaintenanceCreate(BaseModel):
    device_id: str
    issue_description: str
    maintenance_type: str
    scheduled_date: datetime

class ExtendSessionRequest(BaseModel):
    additional_hours: float
