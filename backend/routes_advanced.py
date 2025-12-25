from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import csv
import io
from fastapi.responses import StreamingResponse
import json

from auth import get_current_user

def create_advanced_routes(db, api_router):
    """Advanced features: exports, notifications, automation"""
    
    # ==================== EXPORT REPORTS ====================
    
    @api_router.get("/reports/sessions/export")
    async def export_sessions_report(format: str = "csv", current_user: dict = Depends(get_current_user)):
        """Export sessions report as CSV or JSON"""
        # Get user's cafes
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(100).to_list(100)
        if not cafes:
            raise HTTPException(status_code=404, detail="No cafes found")
        
        cafe_ids = [c['id'] for c in cafes]
        
        # Get sessions
        sessions = await db.sessions.find(
            {"cafe_id": {"$in": cafe_ids}},
            {"_id": 0}
        ).sort("created_at", -1).limit(1000).to_list(1000)
        
        if format == "csv":
            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'session_id', 'customer_id', 'device_id', 'start_time', 
                'end_time', 'duration_hours', 'total_amount', 'status'
            ])
            writer.writeheader()
            
            for session in sessions:
                writer.writerow({
                    'session_id': session['id'],
                    'customer_id': session['customer_id'],
                    'device_id': session['device_id'],
                    'start_time': session['start_time'],
                    'end_time': session.get('end_time', ''),
                    'duration_hours': session.get('duration_hours', 0),
                    'total_amount': session.get('total_amount', 0),
                    'status': session['status']
                })
            
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=sessions_report.csv"}
            )
        else:
            # Return JSON
            return {"sessions": sessions, "total": len(sessions)}
    
    @api_router.get("/reports/revenue/export")
    async def export_revenue_report(current_user: dict = Depends(get_current_user)):
        """Export revenue report"""
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(100).to_list(100)
        if not cafes:
            raise HTTPException(status_code=404, detail="No cafes found")
        
        cafe_ids = [c['id'] for c in cafes]
        
        # Aggregate revenue by date
        pipeline = [
            {"$match": {
                "cafe_id": {"$in": cafe_ids},
                "status": "COMPLETED"
            }},
            {"$group": {
                "_id": {"$substr": ["$created_at", 0, 10]},
                "total_revenue": {"$sum": "$total_amount"},
                "session_count": {"$sum": 1}
            }},
            {"$sort": {"_id": -1}},
            {"$limit": 90}
        ]
        
        results = await db.sessions.aggregate(pipeline).to_list(90)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['date', 'revenue', 'sessions'])
        writer.writeheader()
        
        for item in results:
            writer.writerow({
                'date': item['_id'],
                'revenue': item['total_revenue'],
                'sessions': item['session_count']
            })
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=revenue_report.csv"}
        )
    
    # ==================== INVOICE GENERATION ====================
    
    @api_router.post("/invoices/generate")
    async def generate_invoice(session_id: str, current_user: dict = Depends(get_current_user)):
        """Generate invoice for a session"""
        session_doc = await db.sessions.find_one({"id": session_id}, {"_id": 0})
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if invoice already exists
        existing = await db.invoices.find_one({"reference_id": session_id}, {"_id": 0})
        if existing:
            if isinstance(existing['created_at'], str):
                existing['created_at'] = datetime.fromisoformat(existing['created_at'])
            if isinstance(existing['due_date'], str):
                existing['due_date'] = datetime.fromisoformat(existing['due_date'])
            return existing
        
        # Create invoice
        invoice_number = f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{session_id[:8].upper()}"
        
        amount = session_doc.get('total_amount', 0)
        tax_amount = amount * 0.18  # 18% GST
        total_amount = amount + tax_amount
        
        invoice = {
            "id": str(uuid.uuid4()),
            "invoice_number": invoice_number,
            "cafe_id": session_doc['cafe_id'],
            "customer_id": session_doc['customer_id'],
            "reference_id": session_id,
            "amount": amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "status": "PAID" if session_doc.get('status') == 'COMPLETED' else "DRAFT",
            "line_items": [{
                "description": f"Gaming Session - Device {session_doc['device_id'][:8]}",
                "quantity": session_doc.get('duration_hours', 0),
                "rate": amount / session_doc.get('duration_hours', 1) if session_doc.get('duration_hours') else amount,
                "amount": amount
            }],
            "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.invoices.insert_one(invoice)
        
        invoice['created_at'] = datetime.fromisoformat(invoice['created_at'])
        invoice['due_date'] = datetime.fromisoformat(invoice['due_date'])
        return invoice
    
    @api_router.get("/invoices/my")
    async def get_my_invoices(current_user: dict = Depends(get_current_user)):
        """Get invoices for customer"""
        invoices = await db.invoices.find(
            {"customer_id": current_user['user_id']},
            {"_id": 0}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        for inv in invoices:
            if isinstance(inv['created_at'], str):
                inv['created_at'] = datetime.fromisoformat(inv['created_at'])
            if isinstance(inv['due_date'], str):
                inv['due_date'] = datetime.fromisoformat(inv['due_date'])
        
        return invoices
    
    # ==================== NO-SHOW & OVERSTAY AUTOMATION ====================
    
    @api_router.post("/automation/check-noshows")
    async def check_no_shows(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
        """Check and process no-shows"""
        if current_user['role'] != 'CAFE_OWNER':
            raise HTTPException(status_code=403, detail="Only cafe owners can run automation")
        
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(100).to_list(100)
        if not cafes:
            return {"message": "No cafes found"}
        
        cafe_ids = [c['id'] for c in cafes]
        
        # Find sessions that are active but haven't been started in 15 mins
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=15)
        
        no_show_sessions = await db.sessions.find({
            "cafe_id": {"$in": cafe_ids},
            "status": "ACTIVE",
            "start_time": {"$lt": cutoff_time.isoformat()}
        }, {"_id": 0}).limit(50).to_list(50)
        
        processed = 0
        for session in no_show_sessions:
            # Mark as no-show and release device
            await db.sessions.update_one(
                {"id": session['id']},
                {"$set": {"status": "NO_SHOW", "end_time": datetime.now(timezone.utc).isoformat()}}
            )
            
            # Release device
            await db.devices.update_one(
                {"id": session['device_id']},
                {"$set": {"status": "AVAILABLE"}}
            )
            
            # Apply penalty to customer (reduce wallet balance)
            await db.users.update_one(
                {"id": session['customer_id']},
                {"$inc": {"wallet_balance": -50}}  # ₹50 penalty
            )
            
            processed += 1
        
        return {"message": f"Processed {processed} no-shows", "sessions_processed": processed}
    
    @api_router.post("/automation/check-overstay")
    async def check_overstay(current_user: dict = Depends(get_current_user)):
        """Check and bill overstaying sessions"""
        if current_user['role'] != 'CAFE_OWNER':
            raise HTTPException(status_code=403, detail="Only cafe owners can run automation")
        
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0, "id": 1}).limit(100).to_list(100)
        if not cafes:
            return {"message": "No cafes found"}
        
        cafe_ids = [c['id'] for c in cafes]
        
        # Find active sessions older than 4 hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=4)
        
        overstay_sessions = await db.sessions.find({
            "cafe_id": {"$in": cafe_ids},
            "status": "ACTIVE",
            "start_time": {"$lt": cutoff_time.isoformat()}
        }, {"_id": 0}).limit(50).to_list(50)
        
        processed = 0
        for session in overstay_sessions:
            # Calculate actual duration
            start_time = datetime.fromisoformat(session['start_time'])
            duration_hours = (datetime.now(timezone.utc) - start_time).total_seconds() / 3600
            
            # Get device rate
            device_doc = await db.devices.find_one({"id": session['device_id']}, {"_id": 0})
            if device_doc:
                total_amount = duration_hours * device_doc['hourly_rate'] * 1.5  # 50% overstay penalty
                
                # Update session with charges
                await db.sessions.update_one(
                    {"id": session['id']},
                    {"$set": {
                        "total_amount": total_amount,
                        "duration_hours": duration_hours,
                        "overstay_penalty": True
                    }}
                )
                
                processed += 1
        
        return {"message": f"Processed {processed} overstay sessions", "sessions_processed": processed}
    
    # ==================== REFERRAL REWARDS AUTOMATION ====================
    
    @api_router.post("/referrals/apply")
    async def apply_referral_code(referral_code: str, current_user: dict = Depends(get_current_user)):
        """Apply referral code to get rewards"""
        # Find referrer membership
        referrer_membership = await db.memberships.find_one({"referral_code": referral_code.upper()}, {"_id": 0})
        if not referrer_membership:
            raise HTTPException(status_code=404, detail="Invalid referral code")
        
        # Check if already used
        my_membership = await db.memberships.find_one({"customer_id": current_user['user_id']}, {"_id": 0})
        if my_membership and my_membership.get('referred_by'):
            raise HTTPException(status_code=400, detail="You have already used a referral code")
        
        # Apply referral
        await db.memberships.update_one(
            {"customer_id": current_user['user_id']},
            {"$set": {"referred_by": referrer_membership['customer_id']}}
        )
        
        # Reward both users
        reward_amount = 100  # ₹100 for each
        
        # Reward referrer
        await db.users.update_one(
            {"id": referrer_membership['customer_id']},
            {"$inc": {"wallet_balance": reward_amount}}
        )
        
        # Create transaction for referrer
        await db.wallet_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "customer_id": referrer_membership['customer_id'],
            "amount": reward_amount,
            "transaction_type": "credit",
            "description": "Referral reward",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Reward new user
        await db.users.update_one(
            {"id": current_user['user_id']},
            {"$inc": {"wallet_balance": reward_amount}}
        )
        
        # Create transaction for new user
        await db.wallet_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "customer_id": current_user['user_id'],
            "amount": reward_amount,
            "transaction_type": "credit",
            "description": "Referral signup bonus",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {"message": "Referral applied successfully", "reward": reward_amount}
    
    # ==================== DEVICE HEALTH MONITORING ====================
    
    @api_router.post("/devices/{device_id}/health-log")
    async def log_device_health(device_id: str, metric: str, value: str, current_user: dict = Depends(get_current_user)):
        """Log device health metric"""
        health_log = {
            "id": str(uuid.uuid4()),
            "device_id": device_id,
            "metric": metric,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.device_health_logs.insert_one(health_log)
        return {"message": "Health metric logged"}
    
    @api_router.get("/devices/{device_id}/health")
    async def get_device_health(device_id: str, current_user: dict = Depends(get_current_user)):
        """Get device health history"""
        logs = await db.device_health_logs.find(
            {"device_id": device_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(100).to_list(100)
        
        for log in logs:
            if isinstance(log['timestamp'], str):
                log['timestamp'] = datetime.fromisoformat(log['timestamp'])
        
        return logs
    
    # ==================== FRANCHISE DASHBOARD ====================
    
    @api_router.get("/franchise/overview")
    async def get_franchise_overview(current_user: dict = Depends(get_current_user)):
        """Get overview of all cafes in franchise"""
        cafes = await db.cafes.find({"owner_id": current_user['user_id']}, {"_id": 0}).limit(100).to_list(100)
        
        franchise_data = []
        for cafe in cafes:
            # Get metrics for each cafe
            devices_count = await db.devices.count_documents({"cafe_id": cafe['id']})
            active_sessions = await db.sessions.count_documents({"cafe_id": cafe['id'], "status": "ACTIVE"})
            
            # Revenue today
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            revenue_pipeline = [
                {"$match": {
                    "cafe_id": cafe['id'],
                    "status": "COMPLETED",
                    "created_at": {"$gte": today.isoformat()}
                }},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            
            revenue_result = await db.sessions.aggregate(revenue_pipeline).to_list(1)
            today_revenue = revenue_result[0]['total'] if revenue_result else 0
            
            franchise_data.append({
                "cafe_id": cafe['id'],
                "cafe_name": cafe['name'],
                "city": cafe['city'],
                "devices": devices_count,
                "active_sessions": active_sessions,
                "today_revenue": round(today_revenue, 2),
                "utilization": round((active_sessions / devices_count * 100) if devices_count else 0, 2)
            })
        
        return {"cafes": franchise_data, "total_cafes": len(cafes)}
    
    return api_router

import uuid
