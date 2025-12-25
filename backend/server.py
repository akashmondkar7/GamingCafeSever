from fastapi import FastAPI, APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import razorpay

from models import *
from auth import *
from ai_agents import ai_orchestrator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Razorpay client
razorpay_client = razorpay.Client(auth=(
    os.environ.get('RAZORPAY_KEY_ID', 'test_key'),
    os.environ.get('RAZORPAY_KEY_SECRET', 'test_secret')
))

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/login")
async def login(request: LoginRequest):
    """Send OTP to phone number"""
    otp = generate_otp(request.phone)
    # In production, send OTP via SMS
    return {"message": "OTP sent successfully", "mock_otp": otp, "phone": request.phone}

@api_router.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    # Check if user exists
    existing = await db.users.find_one({"phone": request.phone}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_dict = request.model_dump()
    user = User(**user_dict)
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    
    token = create_token(user.id, user.role.value)
    return AuthResponse(token=token, user=user)

@api_router.post("/auth/verify-otp", response_model=AuthResponse)
async def verify_otp_endpoint(request: VerifyOTPRequest):
    """Verify OTP and login"""
    if not verify_otp(request.phone, request.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Find or create user
    user_doc = await db.users.find_one({"phone": request.phone}, {"_id": 0})
    
    if not user_doc:
        # Create new customer
        user = User(phone=request.phone, name="User", role=UserRole.CUSTOMER)
        doc = user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
    else:
        if isinstance(user_doc['created_at'], str):
            user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
        user = User(**user_doc)
    
    token = create_token(user.id, user.role.value)
    return AuthResponse(token=token, user=user)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    user_doc = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    return User(**user_doc)

# ==================== CAFE ROUTES ====================

@api_router.post("/cafes", response_model=Cafe)
async def create_cafe(cafe_data: CafeCreate, current_user: dict = Depends(get_current_user)):
    """Create new cafe (CAFE_OWNER only)"""
    if current_user['role'] not in ['CAFE_OWNER', 'SUPER_ADMIN']:
        raise HTTPException(status_code=403, detail="Only cafe owners can create cafes")
    
    # Generate slug from name
    slug = cafe_data.name.lower().replace(' ', '-')
    
    cafe = Cafe(
        **cafe_data.model_dump(),
        owner_id=current_user['user_id'],
        slug=slug
    )
    
    doc = cafe.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.cafes.insert_one(doc)
    
    # Create default trial subscription
    subscription = Subscription(
        cafe_id=cafe.id,
        plan=SubscriptionPlan.PRO,
        status=SubscriptionStatus.TRIAL,
        price=0,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=7)
    )
    sub_doc = subscription.model_dump()
    sub_doc['start_date'] = sub_doc['start_date'].isoformat()
    sub_doc['end_date'] = sub_doc['end_date'].isoformat()
    sub_doc['created_at'] = sub_doc['created_at'].isoformat()
    await db.subscriptions.insert_one(sub_doc)
    
    # Update cafe with subscription_id
    await db.cafes.update_one(
        {"id": cafe.id},
        {"$set": {"subscription_id": subscription.id}}
    )
    
    return cafe

@api_router.get("/cafes", response_model=List[Cafe])
async def list_cafes(current_user: dict = Depends(get_current_user)):
    """List all cafes (filtered by role)"""
    query = {}
    
    if current_user['role'] == 'CAFE_OWNER':
        query = {"owner_id": current_user['user_id']}
    elif current_user['role'] == 'STAFF':
        # Staff can only see their assigned cafe
        user_doc = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
        if user_doc and user_doc.get('cafe_id'):
            query = {"id": user_doc['cafe_id']}
    
    cafes = await db.cafes.find(query, {"_id": 0}).limit(100).to_list(100)
    
    for cafe in cafes:
        if isinstance(cafe['created_at'], str):
            cafe['created_at'] = datetime.fromisoformat(cafe['created_at'])
    
    return cafes

@api_router.get("/cafes/public", response_model=List[Cafe])
async def list_public_cafes():
    """List all active cafes (public endpoint)"""
    cafes = await db.cafes.find({"is_active": True}, {"_id": 0}).to_list(100)
    
    for cafe in cafes:
        if isinstance(cafe['created_at'], str):
            cafe['created_at'] = datetime.fromisoformat(cafe['created_at'])
    
    return cafes

@api_router.get("/cafes/{cafe_id}", response_model=Cafe)
async def get_cafe(cafe_id: str):
    """Get cafe details (public)"""
    cafe_doc = await db.cafes.find_one({"id": cafe_id}, {"_id": 0})
    if not cafe_doc:
        raise HTTPException(status_code=404, detail="Cafe not found")
    
    if isinstance(cafe_doc['created_at'], str):
        cafe_doc['created_at'] = datetime.fromisoformat(cafe_doc['created_at'])
    
    return Cafe(**cafe_doc)

# ==================== DEVICE ROUTES ====================

@api_router.post("/devices", response_model=Device)
async def create_device(device_data: DeviceCreate, current_user: dict = Depends(get_current_user)):
    """Create new device"""
    # Get user's cafe
    user_doc = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
    if not user_doc or not user_doc.get('cafe_id'):
        # If cafe owner, get their first cafe
        if current_user['role'] == 'CAFE_OWNER':
            cafe_doc = await db.cafes.find_one({"owner_id": current_user['user_id']}, {"_id": 0})
            if cafe_doc:
                cafe_id = cafe_doc['id']
            else:
                raise HTTPException(status_code=400, detail="No cafe found")
        else:
            raise HTTPException(status_code=400, detail="User not assigned to any cafe")
    else:
        cafe_id = user_doc['cafe_id']
    
    device = Device(**device_data.model_dump(), cafe_id=cafe_id)
    doc = device.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.devices.insert_one(doc)
    
    return device

@api_router.get("/devices", response_model=List[Device])
async def list_devices(cafe_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """List devices"""
    query = {}
    
    if cafe_id:
        query = {"cafe_id": cafe_id}
    elif current_user['role'] == 'CAFE_OWNER':
        # Get owner's cafes
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(100).to_list(100)
        cafe_ids = [c['id'] for c in cafes]
        query = {"cafe_id": {"$in": cafe_ids}}
    elif current_user['role'] == 'STAFF':
        user_doc = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
        if user_doc and user_doc.get('cafe_id'):
            query = {"cafe_id": user_doc['cafe_id']}
    
    devices = await db.devices.find(query, {"_id": 0}).limit(100).to_list(100)
    
    for device in devices:
        if isinstance(device['created_at'], str):
            device['created_at'] = datetime.fromisoformat(device['created_at'])
    
    return devices

@api_router.patch("/devices/{device_id}/status")
async def update_device_status(
    device_id: str,
    status_data: DeviceStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update device status"""
    result = await db.devices.update_one(
        {"id": device_id},
        {"$set": {"status": status_data.status.value}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"message": "Device status updated", "status": status_data.status.value}

# ==================== SESSION/BOOKING ROUTES ====================

@api_router.post("/sessions", response_model=Session)
async def create_session(session_data: SessionCreate, current_user: dict = Depends(get_current_user)):
    """Create new gaming session"""
    # Get device
    device_doc = await db.devices.find_one({"id": session_data.device_id}, {"_id": 0})
    if not device_doc:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if device_doc['status'] != DeviceStatus.AVAILABLE.value:
        raise HTTPException(status_code=400, detail="Device not available")
    
    # Create session
    session = Session(
        customer_id=session_data.customer_id,
        device_id=session_data.device_id,
        cafe_id=device_doc['cafe_id'],
        start_time=datetime.now(timezone.utc)
    )
    
    doc = session.model_dump()
    doc['start_time'] = doc['start_time'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.sessions.insert_one(doc)
    
    # Update device status
    await db.devices.update_one(
        {"id": session_data.device_id},
        {"$set": {"status": DeviceStatus.OCCUPIED.value}}
    )
    
    return session

@api_router.post("/sessions/{session_id}/end")
async def end_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """End a gaming session"""
    session_doc = await db.sessions.find_one({"id": session_id}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate duration and amount
    if isinstance(session_doc['start_time'], str):
        start_time = datetime.fromisoformat(session_doc['start_time'])
    else:
        start_time = session_doc['start_time']
    
    end_time = datetime.now(timezone.utc)
    duration_hours = (end_time - start_time).total_seconds() / 3600
    
    # Get device rate
    device_doc = await db.devices.find_one({"id": session_doc['device_id']}, {"_id": 0})
    hourly_rate = device_doc['hourly_rate'] if device_doc else 100
    
    total_amount = duration_hours * hourly_rate
    
    # Update session
    await db.sessions.update_one(
        {"id": session_id},
        {"$set": {
            "end_time": end_time.isoformat(),
            "duration_hours": duration_hours,
            "total_amount": total_amount,
            "status": SessionStatus.COMPLETED.value
        }}
    )
    
    # Free up device
    await db.devices.update_one(
        {"id": session_doc['device_id']},
        {"$set": {"status": DeviceStatus.AVAILABLE.value}}
    )
    
    return {
        "message": "Session ended",
        "duration_hours": round(duration_hours, 2),
        "total_amount": round(total_amount, 2)
    }

@api_router.get("/sessions", response_model=List[Session])
async def list_sessions(cafe_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """List sessions"""
    query = {}
    
    if cafe_id:
        query = {"cafe_id": cafe_id}
    elif current_user['role'] == 'CUSTOMER':
        query = {"customer_id": current_user['user_id']}
    elif current_user['role'] == 'CAFE_OWNER':
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0}).to_list(100)
        cafe_ids = [c['id'] for c in cafes]
        query = {"cafe_id": {"$in": cafe_ids}}
    
    sessions = await db.sessions.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    for session in sessions:
        if isinstance(session['start_time'], str):
            session['start_time'] = datetime.fromisoformat(session['start_time'])
        if session.get('end_time') and isinstance(session['end_time'], str):
            session['end_time'] = datetime.fromisoformat(session['end_time'])
        if isinstance(session['created_at'], str):
            session['created_at'] = datetime.fromisoformat(session['created_at'])
    
    return sessions

# ==================== AI AGENT ROUTES ====================

@api_router.post("/ai/chat")
async def ai_chat(message_data: AIMessage, current_user: dict = Depends(get_current_user)):
    """Chat with AI assistant"""
    if current_user['role'] != 'CAFE_OWNER':
        raise HTTPException(status_code=403, detail="Only cafe owners can use AI assistant")
    
    # Get cafe context
    cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0}).to_list(100)
    if not cafes:
        raise HTTPException(status_code=404, detail="No cafe found")
    
    cafe_id = cafes[0]['id']
    
    # Gather context data
    devices = await db.devices.find({"cafe_id": cafe_id}, {"_id": 0}).to_list(1000)
    sessions = await db.sessions.find({"cafe_id": cafe_id}, {"_id": 0}).to_list(1000)
    
    active_sessions = [s for s in sessions if s.get('status') == 'ACTIVE']
    today = datetime.now(timezone.utc).date()
    
    today_revenue = sum(
        s.get('total_amount', 0) for s in sessions
        if s.get('status') == 'COMPLETED' and
        datetime.fromisoformat(s['created_at']).date() == today
    )
    
    context = {
        'total_devices': len(devices),
        'active_sessions': len(active_sessions),
        'today_revenue': today_revenue,
        'month_revenue': today_revenue * 10,  # Mock
        'avg_utilization': (len(active_sessions) / len(devices) * 100) if devices else 0
    }
    
    # Route to appropriate AI agent
    session_id = f"{current_user['user_id']}_chat"
    
    try:
        if message_data.agent_type == "OWNER_ASSISTANT":
            response = await ai_orchestrator.owner_assistant(message_data.message, context, session_id)
        elif message_data.agent_type == "SMART_PRICING":
            response = await ai_orchestrator.smart_pricing(context, session_id)
        elif message_data.agent_type == "DEVICE_OPTIMIZATION":
            response = await ai_orchestrator.device_optimization(context, session_id)
        elif message_data.agent_type == "CUSTOMER_BEHAVIOR":
            response = await ai_orchestrator.customer_behavior(context, session_id)
        elif message_data.agent_type == "RISK_FRAUD":
            response = await ai_orchestrator.risk_fraud_detection(context, session_id)
        else:
            response = await ai_orchestrator.owner_assistant(message_data.message, context, session_id)
        
        # Save conversation
        conversation = AIConversation(
            cafe_owner_id=current_user['user_id'],
            agent_type=message_data.agent_type,
            message=message_data.message,
            response=response,
            context=context
        )
        conv_doc = conversation.model_dump()
        conv_doc['created_at'] = conv_doc['created_at'].isoformat()
        await db.ai_conversations.insert_one(conv_doc)
        
        return {"response": response, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

# ==================== ANALYTICS ROUTES ====================

@api_router.get("/analytics/dashboard")
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user)):
    """Get dashboard analytics"""
    if current_user['role'] == 'CAFE_OWNER':
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0}).to_list(100)
        cafe_ids = [c['id'] for c in cafes]
    elif current_user['role'] == 'SUPER_ADMIN':
        cafes = await db.cafes.find({}, {"_id": 0}).to_list(1000)
        cafe_ids = [c['id'] for c in cafes]
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get metrics
    total_devices = await db.devices.count_documents({"cafe_id": {"$in": cafe_ids}})
    active_sessions = await db.sessions.count_documents({
        "cafe_id": {"$in": cafe_ids},
        "status": "ACTIVE"
    })
    
    sessions = await db.sessions.find({"cafe_id": {"$in": cafe_ids}}, {"_id": 0}).to_list(10000)
    
    today = datetime.now(timezone.utc).date()
    today_revenue = sum(
        s.get('total_amount', 0) for s in sessions
        if s.get('status') == 'COMPLETED' and
        datetime.fromisoformat(s['created_at']).date() == today
    )
    
    total_revenue = sum(s.get('total_amount', 0) for s in sessions if s.get('status') == 'COMPLETED')
    
    return {
        "total_cafes": len(cafes),
        "total_devices": total_devices,
        "active_sessions": active_sessions,
        "today_revenue": round(today_revenue, 2),
        "total_revenue": round(total_revenue, 2),
        "avg_utilization": round((active_sessions / total_devices * 100) if total_devices else 0, 2)
    }

# ==================== SUBSCRIPTION ROUTES ====================

@api_router.get("/subscriptions/my")
async def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """Get current user's subscription"""
    if current_user['role'] != 'CAFE_OWNER':
        raise HTTPException(status_code=403, detail="Only cafe owners have subscriptions")
    
    cafe_doc = await db.cafes.find_one({"owner_id": current_user['user_id']}, {"_id": 0})
    if not cafe_doc:
        raise HTTPException(status_code=404, detail="Cafe not found")
    
    sub_doc = await db.subscriptions.find_one({"cafe_id": cafe_doc['id']}, {"_id": 0})
    if not sub_doc:
        return None
    
    if isinstance(sub_doc['start_date'], str):
        sub_doc['start_date'] = datetime.fromisoformat(sub_doc['start_date'])
    if isinstance(sub_doc['end_date'], str):
        sub_doc['end_date'] = datetime.fromisoformat(sub_doc['end_date'])
    if isinstance(sub_doc['created_at'], str):
        sub_doc['created_at'] = datetime.fromisoformat(sub_doc['created_at'])
    
    return Subscription(**sub_doc)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
