from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import uuid
import qrcode
import io
import base64

from models_extended import *
from auth import get_current_user
from ai_agents_extended import extended_ai_agents

def create_extended_routes(db, api_router):
    """Create all extended API routes"""
    
    # ==================== GAME LIBRARY ROUTES ====================
    
    @api_router.post("/games", response_model=Game)
    async def create_game(game_data: GameCreate, current_user: dict = Depends(get_current_user)):
        """Create game in library"""
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(10).to_list(10)
        if not cafes:
            raise HTTPException(status_code=404, detail="No cafe found")
        
        game = Game(**game_data.model_dump(), cafe_id=cafes[0]['id'])
        doc = game.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.games.insert_one(doc)
        return game
    
    @api_router.get("/games", response_model=List[Game])
    async def list_games(cafe_id: Optional[str] = None, device_type: Optional[DeviceType] = None):
        """List games"""
        query = {}
        if cafe_id:
            query["cafe_id"] = cafe_id
        if device_type:
            query["device_types"] = device_type.value
        
        games = await db.games.find(query, {"_id": 0}).limit(100).to_list(100)
        for game in games:
            if isinstance(game['created_at'], str):
                game['created_at'] = datetime.fromisoformat(game['created_at'])
        return games
    
    @api_router.get("/games/{game_id}", response_model=Game)
    async def get_game(game_id: str):
        """Get game details with guides"""
        game_doc = await db.games.find_one({"id": game_id}, {"_id": 0})
        if not game_doc:
            raise HTTPException(status_code=404, detail="Game not found")
        if isinstance(game_doc['created_at'], str):
            game_doc['created_at'] = datetime.fromisoformat(game_doc['created_at'])
        return Game(**game_doc)
    
    # ==================== MEMBERSHIP & LOYALTY ROUTES ====================
    
    @api_router.get("/membership/my")
    async def get_my_membership(current_user: dict = Depends(get_current_user)):
        """Get customer membership"""
        membership_doc = await db.memberships.find_one({"customer_id": current_user['user_id']}, {"_id": 0})
        if not membership_doc:
            # Create new membership
            referral_code = str(uuid.uuid4())[:8].upper()
            membership = Membership(
                customer_id=current_user['user_id'],
                cafe_id="default",
                referral_code=referral_code
            )
            doc = membership.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.memberships.insert_one(doc)
            return membership
        
        if isinstance(membership_doc['created_at'], str):
            membership_doc['created_at'] = datetime.fromisoformat(membership_doc['created_at'])
        return Membership(**membership_doc)
    
    @api_router.post("/membership/purchase-pass")
    async def purchase_pass(request: PurchasePassRequest, current_user: dict = Depends(get_current_user)):
        """Purchase a pass"""
        # Define pass pricing
        pass_prices = {
            PassType.HOURLY: {"price": 100, "hours": 1},
            PassType.DAILY: {"price": 500, "hours": 8},
            PassType.WEEKLY: {"price": 2500, "hours": 50},
            PassType.MONTHLY: {"price": 8000, "hours": 200}
        }
        
        pass_info = pass_prices.get(request.pass_type)
        if not pass_info:
            raise HTTPException(status_code=400, detail="Invalid pass type")
        
        # Check wallet balance
        user_doc = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
        if user_doc['wallet_balance'] < pass_info['price']:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
        # Create pass
        valid_from = datetime.now(timezone.utc)
        valid_until = valid_from + timedelta(days=30 if request.pass_type == PassType.MONTHLY else 7 if request.pass_type == PassType.WEEKLY else 1)
        
        pass_obj = Pass(
            customer_id=current_user['user_id'],
            cafe_id=request.cafe_id,
            pass_type=request.pass_type,
            hours_included=pass_info['hours'],
            price=pass_info['price'],
            valid_from=valid_from,
            valid_until=valid_until
        )
        
        doc = pass_obj.model_dump()
        doc['valid_from'] = doc['valid_from'].isoformat()
        doc['valid_until'] = doc['valid_until'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.passes.insert_one(doc)
        
        # Deduct from wallet
        await db.users.update_one(
            {"id": current_user['user_id']},
            {"$inc": {"wallet_balance": -pass_info['price']}}
        )
        
        # Record transaction
        transaction = WalletTransaction(
            customer_id=current_user['user_id'],
            amount=-pass_info['price'],
            transaction_type="debit",
            description=f"Purchased {request.pass_type.value} pass",
            reference_id=pass_obj.id
        )
        trans_doc = transaction.model_dump()
        trans_doc['created_at'] = trans_doc['created_at'].isoformat()
        await db.wallet_transactions.insert_one(trans_doc)
        
        return pass_obj
    
    @api_router.get("/membership/passes", response_model=List[Pass])
    async def list_my_passes(current_user: dict = Depends(get_current_user)):
        """List customer passes"""
        passes = await db.passes.find({"customer_id": current_user['user_id']}, {"_id": 0}).limit(50).to_list(50)
        for p in passes:
            if isinstance(p['valid_from'], str):
                p['valid_from'] = datetime.fromisoformat(p['valid_from'])
            if isinstance(p['valid_until'], str):
                p['valid_until'] = datetime.fromisoformat(p['valid_until'])
            if isinstance(p['created_at'], str):
                p['created_at'] = datetime.fromisoformat(p['created_at'])
        return passes
    
    @api_router.post("/wallet/add-money")
    async def add_money_to_wallet(amount: float, current_user: dict = Depends(get_current_user)):
        """Add money to wallet"""
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        
        await db.users.update_one(
            {"id": current_user['user_id']},
            {"$inc": {"wallet_balance": amount}}
        )
        
        transaction = WalletTransaction(
            customer_id=current_user['user_id'],
            amount=amount,
            transaction_type="credit",
            description="Wallet recharge"
        )
        trans_doc = transaction.model_dump()
        trans_doc['created_at'] = trans_doc['created_at'].isoformat()
        await db.wallet_transactions.insert_one(trans_doc)
        
        return {"message": "Money added successfully", "new_balance": (await db.users.find_one({"id": current_user['user_id']}, {"_id": 0}))['wallet_balance']}
    
    @api_router.get("/wallet/transactions", response_model=List[WalletTransaction])
    async def get_wallet_transactions(current_user: dict = Depends(get_current_user)):
        """Get wallet transaction history"""
        transactions = await db.wallet_transactions.find({"customer_id": current_user['user_id']}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
        for t in transactions:
            if isinstance(t['created_at'], str):
                t['created_at'] = datetime.fromisoformat(t['created_at'])
        return transactions
    
    # ==================== PRICING RULES & COUPONS ====================
    
    @api_router.post("/pricing-rules", response_model=PricingRule)
    async def create_pricing_rule(rule_data: PricingRuleCreate, current_user: dict = Depends(get_current_user)):
        """Create pricing rule"""
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(10).to_list(10)
        if not cafes:
            raise HTTPException(status_code=404, detail="No cafe found")
        
        rule = PricingRule(**rule_data.model_dump(), cafe_id=cafes[0]['id'])
        doc = rule.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.pricing_rules.insert_one(doc)
        return rule
    
    @api_router.get("/pricing-rules", response_model=List[PricingRule])
    async def list_pricing_rules(current_user: dict = Depends(get_current_user)):
        """List pricing rules"""
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(10).to_list(10)
        if not cafes:
            return []
        
        rules = await db.pricing_rules.find({"cafe_id": cafes[0]['id']}, {"_id": 0}).limit(50).to_list(50)
        for r in rules:
            if isinstance(r['created_at'], str):
                r['created_at'] = datetime.fromisoformat(r['created_at'])
        return rules
    
    @api_router.post("/coupons", response_model=Coupon)
    async def create_coupon(coupon_data: CouponCreate, current_user: dict = Depends(get_current_user)):
        """Create coupon"""
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(10).to_list(10)
        if not cafes:
            raise HTTPException(status_code=404, detail="No cafe found")
        
        valid_from = datetime.now(timezone.utc)
        valid_until = valid_from + timedelta(days=coupon_data.valid_days)
        
        coupon = Coupon(
            cafe_id=cafes[0]['id'],
            code=coupon_data.code.upper(),
            discount_type=coupon_data.discount_type,
            discount_value=coupon_data.discount_value,
            min_amount=coupon_data.min_amount,
            max_uses=coupon_data.max_uses,
            valid_from=valid_from,
            valid_until=valid_until
        )
        
        doc = coupon.model_dump()
        doc['valid_from'] = doc['valid_from'].isoformat()
        doc['valid_until'] = doc['valid_until'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.coupons.insert_one(doc)
        return coupon
    
    @api_router.post("/coupons/apply")
    async def apply_coupon(request: ApplyCouponRequest, current_user: dict = Depends(get_current_user)):
        """Apply coupon to session"""
        # Find coupon
        coupon_doc = await db.coupons.find_one({"code": request.code.upper()}, {"_id": 0})
        if not coupon_doc:
            raise HTTPException(status_code=404, detail="Invalid coupon code")
        
        if isinstance(coupon_doc['valid_from'], str):
            coupon_doc['valid_from'] = datetime.fromisoformat(coupon_doc['valid_from'])
        if isinstance(coupon_doc['valid_until'], str):
            coupon_doc['valid_until'] = datetime.fromisoformat(coupon_doc['valid_until'])
        
        now = datetime.now(timezone.utc)
        if not coupon_doc['is_active'] or now < coupon_doc['valid_from'] or now > coupon_doc['valid_until']:
            raise HTTPException(status_code=400, detail="Coupon expired or inactive")
        
        if coupon_doc['max_uses'] and coupon_doc['used_count'] >= coupon_doc['max_uses']:
            raise HTTPException(status_code=400, detail="Coupon usage limit reached")
        
        # Update session with coupon
        await db.sessions.update_one(
            {"id": request.session_id},
            {"$set": {"coupon_code": request.code.upper(), "coupon_discount": coupon_doc['discount_value']}}
        )
        
        # Increment usage
        await db.coupons.update_one(
            {"code": request.code.upper()},
            {"$inc": {"used_count": 1}}
        )
        
        return {"message": "Coupon applied successfully", "discount": coupon_doc['discount_value']}
    
    # ==================== DEVICE MAINTENANCE ====================
    
    @api_router.post("/devices/maintenance", response_model=DeviceMaintenance)
    async def create_maintenance_record(maintenance_data: DeviceMaintenanceCreate, current_user: dict = Depends(get_current_user)):
        """Create maintenance record"""
        device_doc = await db.devices.find_one({"id": maintenance_data.device_id}, {"_id": 0})
        if not device_doc:
            raise HTTPException(status_code=404, detail="Device not found")
        
        maintenance = DeviceMaintenance(**maintenance_data.model_dump(), cafe_id=device_doc['cafe_id'])
        doc = maintenance.model_dump()
        doc['scheduled_date'] = doc['scheduled_date'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.device_maintenance.insert_one(doc)
        
        # Update device status
        await db.devices.update_one(
            {"id": maintenance_data.device_id},
            {"$set": {"status": "MAINTENANCE"}}
        )
        
        return maintenance
    
    @api_router.get("/devices/maintenance", response_model=List[DeviceMaintenance])
    async def list_maintenance_records(current_user: dict = Depends(get_current_user)):
        """List maintenance records"""
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(10).to_list(10)
        if not cafes:
            return []
        
        records = await db.device_maintenance.find({"cafe_id": cafes[0]['id']}, {"_id": 0}).sort("scheduled_date", -1).limit(50).to_list(50)
        for r in records:
            if isinstance(r['scheduled_date'], str):
                r['scheduled_date'] = datetime.fromisoformat(r['scheduled_date'])
            if r.get('completed_date') and isinstance(r['completed_date'], str):
                r['completed_date'] = datetime.fromisoformat(r['completed_date'])
            if isinstance(r['created_at'], str):
                r['created_at'] = datetime.fromisoformat(r['created_at'])
        return records
    
    # ==================== SESSION EXTENSIONS ====================
    
    @api_router.post("/sessions/{session_id}/extend")
    async def extend_session(session_id: str, request: ExtendSessionRequest, current_user: dict = Depends(get_current_user)):
        """Extend gaming session"""
        session_doc = await db.sessions.find_one({"id": session_id}, {"_id": 0})
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session_doc['status'] != 'ACTIVE':
            raise HTTPException(status_code=400, detail="Can only extend active sessions")
        
        # Get device rate
        device_doc = await db.devices.find_one({"id": session_doc['device_id']}, {"_id": 0})
        additional_cost = request.additional_hours * device_doc['hourly_rate']
        
        await db.sessions.update_one(
            {"id": session_id},
            {"$set": {"status": "EXTENDED"}, "$inc": {"total_amount": additional_cost}}
        )
        
        return {"message": "Session extended", "additional_cost": additional_cost}
    
    # ==================== QR CODE GENERATION ====================
    
    @api_router.get("/sessions/{session_id}/qr")
    async def get_session_qr(session_id: str, current_user: dict = Depends(get_current_user)):
        """Generate QR code for session check-in"""
        session_doc = await db.sessions.find_one({"id": session_id}, {"_id": 0})
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"SESSION:{session_id}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {"qr_code": f"data:image/png;base64,{img_str}", "session_id": session_id}
    
    # ==================== EXTENDED AI AGENTS ====================
    
    @api_router.post("/ai/staff-performance")
    async def ai_staff_performance(current_user: dict = Depends(get_current_user)):
        """Get staff performance insights"""
        if current_user['role'] != 'CAFE_OWNER':
            raise HTTPException(status_code=403, detail="Only cafe owners can access this")
        
        # Mock context for demo
        context = {
            'total_staff': 5,
            'avg_checkin_time': 3,
            'customer_satisfaction': 85,
            'peak_coverage': 90,
            'training_completion': 70
        }
        
        session_id = f"{current_user['user_id']}_staff_perf"
        response = await extended_ai_agents.staff_performance(context, session_id)
        
        return {"response": response, "context": context}
    
    @api_router.post("/ai/automation")
    async def ai_automation(current_user: dict = Depends(get_current_user)):
        """Get automation recommendations"""
        if current_user['role'] != 'CAFE_OWNER':
            raise HTTPException(status_code=403, detail="Only cafe owners can access this")
        
        # Mock context for demo
        context = {
            'manual_tasks': 50,
            'avg_response_time': 5,
            'bottlenecks': ['check-in', 'payment processing'],
            'wait_time': 8
        }
        
        session_id = f"{current_user['user_id']}_automation"
        response = await extended_ai_agents.automation_agent(context, session_id)
        
        return {"response": response, "context": context}
    
    # ==================== STAFF MANAGEMENT ====================
    
    @api_router.post("/staff/shift/start")
    async def start_shift(current_user: dict = Depends(get_current_user)):
        """Start staff shift"""
        if current_user['role'] != 'STAFF':
            raise HTTPException(status_code=403, detail="Only staff can start shifts")
        
        user_doc = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
        if not user_doc.get('cafe_id'):
            raise HTTPException(status_code=400, detail="Staff not assigned to cafe")
        
        shift = StaffShift(
            staff_id=current_user['user_id'],
            cafe_id=user_doc['cafe_id'],
            shift_start=datetime.now(timezone.utc)
        )
        
        doc = shift.model_dump()
        doc['shift_start'] = doc['shift_start'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.staff_shifts.insert_one(doc)
        
        return shift
    
    @api_router.post("/staff/shift/end/{shift_id}")
    async def end_shift(shift_id: str, current_user: dict = Depends(get_current_user)):
        """End staff shift"""
        shift_doc = await db.staff_shifts.find_one({"id": shift_id}, {"_id": 0})
        if not shift_doc:
            raise HTTPException(status_code=404, detail="Shift not found")
        
        shift_start = datetime.fromisoformat(shift_doc['shift_start'])
        shift_end = datetime.now(timezone.utc)
        total_hours = (shift_end - shift_start).total_seconds() / 3600
        
        await db.staff_shifts.update_one(
            {"id": shift_id},
            {"$set": {
                "shift_end": shift_end.isoformat(),
                "total_hours": total_hours
            }}
        )
        
        return {"message": "Shift ended", "total_hours": round(total_hours, 2)}
    
    return api_router
