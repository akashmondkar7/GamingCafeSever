from fastapi import HTTPException, Depends
from datetime import datetime, timezone
from auth import get_current_user

async def check_subscription_status(db, user_id: str, required_plan: str = None):
    """Check if user has active subscription and required plan"""
    # Get user's cafe
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user_doc or user_doc.get('role') != 'CAFE_OWNER':
        return True  # Non-owners always have access
    
    # Get cafe
    cafe_doc = await db.cafes.find_one({"owner_id": user_id}, {"_id": 0})
    if not cafe_doc:
        return True
    
    # Get subscription
    sub_doc = await db.subscriptions.find_one({"cafe_id": cafe_doc['id']}, {"_id": 0})
    if not sub_doc:
        return False
    
    # Check if active
    if isinstance(sub_doc['end_date'], str):
        end_date = datetime.fromisoformat(sub_doc['end_date'])
    else:
        end_date = sub_doc['end_date']
    
    now = datetime.now(timezone.utc)
    
    # Check expiry
    if now > end_date and sub_doc['status'] not in ['ACTIVE', 'TRIAL']:
        return False
    
    # Check plan requirement
    if required_plan:
        plan_hierarchy = {'BASIC': 1, 'PRO': 2, 'ENTERPRISE': 3}
        user_plan_level = plan_hierarchy.get(sub_doc['plan'], 0)
        required_plan_level = plan_hierarchy.get(required_plan, 0)
        
        if user_plan_level < required_plan_level:
            return False
    
    return True

def require_subscription(required_plan: str = None):
    """Dependency to check subscription"""
    async def check_sub(current_user: dict = Depends(get_current_user)):
        # This will be injected with db in the route
        return current_user
    return check_sub

# Feature access map based on plans
FEATURE_ACCESS = {
    'BASIC': ['devices', 'sessions', 'basic_analytics'],
    'PRO': ['devices', 'sessions', 'analytics', 'ai_assistant', 'pricing', 'membership', 'games'],
    'ENTERPRISE': ['all']  # All features
}

async def check_feature_access(db, user_id: str, feature: str) -> bool:
    """Check if user's plan allows access to feature"""
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user_doc or user_doc.get('role') != 'CAFE_OWNER':
        return True
    
    cafe_doc = await db.cafes.find_one({"owner_id": user_id}, {"_id": 0})
    if not cafe_doc:
        return False
    
    sub_doc = await db.subscriptions.find_one({"cafe_id": cafe_doc['id']}, {"_id": 0})
    if not sub_doc:
        return False
    
    plan = sub_doc['plan']
    allowed_features = FEATURE_ACCESS.get(plan, [])
    
    if 'all' in allowed_features or feature in allowed_features:
        return True
    
    return False
