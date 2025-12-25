from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
from typing import Dict, Optional
from datetime import datetime, timezone

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

class AIAgentOrchestrator:
    """Orchestrates multiple AI agents for gaming cafe management"""
    
    def __init__(self):
        self.api_key = EMERGENT_LLM_KEY
    
    async def owner_assistant(self, message: str, context: Dict, session_id: str) -> str:
        """AI Agent 1: Owner Assistant - Conversational AI for cafe owners"""
        system_message = """You are an intelligent assistant for gaming café owners. 
        Analyze their questions about revenue, device utilization, customer behavior, and trends.
        Provide clear, actionable insights and suggestions to help them increase revenue.
        Be concise and data-driven in your responses."""
        
        # Build context message
        context_str = f"""
        Current Context:
        - Total Devices: {context.get('total_devices', 0)}
        - Active Sessions: {context.get('active_sessions', 0)}
        - Today's Revenue: ₹{context.get('today_revenue', 0)}
        - This Month's Revenue: ₹{context.get('month_revenue', 0)}
        - Average Utilization: {context.get('avg_utilization', 0)}%
        
        User Question: {message}
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=context_str)
        response = await chat.send_message(user_message)
        return response
    
    async def smart_pricing(self, context: Dict, session_id: str) -> str:
        """AI Agent 2: Smart Pricing - Analyzes demand and suggests optimal pricing"""
        system_message = """You are a pricing optimization expert for gaming cafés.
        Analyze usage patterns, peak hours, and demand to suggest optimal pricing strategies.
        Provide specific recommendations with expected revenue impact."""
        
        context_str = f"""
        Analyze this data and suggest pricing optimizations:
        - Peak Hours Usage: {context.get('peak_usage', 0)}%
        - Off-Peak Usage: {context.get('offpeak_usage', 0)}%
        - Current Hourly Rate: ₹{context.get('current_rate', 0)}
        - Weekend vs Weekday Ratio: {context.get('weekend_ratio', 1.0)}
        - Average Session Duration: {context.get('avg_duration', 0)} hours
        
        Provide 3 specific pricing recommendations to maximize revenue.
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=context_str)
        response = await chat.send_message(user_message)
        return response
    
    async def device_optimization(self, context: Dict, session_id: str) -> str:
        """AI Agent 3: Device Optimization - Improves device utilization"""
        system_message = """You are a resource optimization expert for gaming cafés.
        Analyze device utilization patterns and suggest improvements.
        Focus on reducing idle time and maximizing revenue per device."""
        
        context_str = f"""
        Device Utilization Analysis:
        - Total Devices: {context.get('total_devices', 0)}
        - Idle Devices: {context.get('idle_devices', 0)}
        - High-Demand Devices: {context.get('high_demand_devices', [])}
        - Low-Demand Devices: {context.get('low_demand_devices', [])}
        - Average Utilization: {context.get('avg_utilization', 0)}%
        
        Suggest 3 actionable steps to improve device utilization and reduce idle time.
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=context_str)
        response = await chat.send_message(user_message)
        return response
    
    async def customer_behavior(self, context: Dict, session_id: str) -> str:
        """AI Agent 4: Customer Behavior Analysis"""
        system_message = """You are a customer behavior analyst for gaming cafés.
        Identify patterns, segment customers, and suggest retention strategies.
        Focus on increasing customer lifetime value."""
        
        context_str = f"""
        Customer Analytics:
        - Total Customers: {context.get('total_customers', 0)}
        - Repeat Customers: {context.get('repeat_customers', 0)}%
        - Average Spend: ₹{context.get('avg_spend', 0)}
        - Churn Risk: {context.get('churn_risk', 0)}%
        - Popular Gaming Times: {context.get('popular_times', [])}
        
        Suggest strategies to increase customer retention and lifetime value.
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=context_str)
        response = await chat.send_message(user_message)
        return response
    
    async def risk_fraud_detection(self, context: Dict, session_id: str) -> str:
        """AI Agent 7: Risk & Fraud Detection"""
        system_message = """You are a security analyst for gaming cafés.
        Detect suspicious patterns, potential fraud, and revenue protection issues.
        Provide specific alerts and preventive actions."""
        
        context_str = f"""
        Security Analysis:
        - Unusual Booking Patterns: {context.get('unusual_patterns', [])}
        - No-Show Rate: {context.get('noshow_rate', 0)}%
        - Discount Abuse Cases: {context.get('discount_abuse', 0)}
        - Late Payment Issues: {context.get('late_payments', 0)}
        
        Identify risks and suggest preventive measures.
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=context_str)
        response = await chat.send_message(user_message)
        return response

ai_orchestrator = AIAgentOrchestrator()
