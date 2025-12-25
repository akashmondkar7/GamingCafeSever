from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
from typing import Dict
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

class ExtendedAIAgents:
    """Additional AI agents for gaming cafe management"""
    
    def __init__(self):
        self.api_key = EMERGENT_LLM_KEY
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def staff_performance(self, context: Dict, session_id: str) -> str:
        """AI Agent 5: Staff Performance Analysis"""
        system_message = """You are a staff performance analyst for gaming cafés.
        Analyze staff efficiency, identify training gaps, and suggest optimal shifts.
        Focus on data-driven insights to improve staff productivity."""
        
        context_str = f"""
        Staff Performance Data:
        - Total Staff: {context.get('total_staff', 0)}
        - Average Check-in Time: {context.get('avg_checkin_time', 0)} minutes
        - Customer Satisfaction: {context.get('customer_satisfaction', 0)}%
        - Peak Hour Coverage: {context.get('peak_coverage', 0)}%
        - Training Completion: {context.get('training_completion', 0)}%
        
        Provide 3 specific recommendations to improve staff performance.
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=context_str)
        response = await chat.send_message(user_message)
        return response
    
    async def automation_agent(self, context: Dict, session_id: str) -> str:
        """AI Agent 6: Automation & Action Agent"""
        system_message = """You are an automation specialist for gaming cafés.
        Analyze operations and suggest specific automations that can be implemented.
        Focus on reducing manual work and improving efficiency."""
        
        context_str = f"""
        Automation Opportunities:
        - Manual Tasks per Day: {context.get('manual_tasks', 0)}
        - Average Response Time: {context.get('avg_response_time', 0)} minutes
        - Peak Hour Bottlenecks: {context.get('bottlenecks', [])}
        - Customer Wait Time: {context.get('wait_time', 0)} minutes
        
        Suggest 5 automations that would have the highest impact on operations.
        Include: What to automate, expected time savings, and implementation priority.
        """
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=context_str)
        response = await chat.send_message(user_message)
        return response

extended_ai_agents = ExtendedAIAgents()
