#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Gaming Café Management System
Tests all authentication, CRUD operations, AI integration, and analytics endpoints
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class GameCafeAPITester:
    def __init__(self, base_url="https://gamecafe-os.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
            self.failed_tests.append({"test": name, "error": details, "response": response_data})
        
        self.test_results.append({
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, expected_status: int = 200) -> tuple:
        """Make HTTP request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}", {}

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if not success:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                if response_data.get('detail'):
                    error_msg += f" - {response_data['detail']}"
                return False, error_msg, response_data

            return True, "Success", response_data

        except requests.exceptions.Timeout:
            return False, "Request timeout", {}
        except requests.exceptions.ConnectionError:
            return False, "Connection error", {}
        except Exception as e:
            return False, f"Request error: {str(e)}", {}

    def test_auth_flow(self):
        """Test complete authentication flow"""
        print("\n🔐 Testing Authentication Flow...")
        
        # Test phone number for OTP
        test_phone = "+919876543210"
        
        # 1. Send OTP
        success, error, response = self.make_request('POST', 'auth/login', {'phone': test_phone})
        self.log_test("Send OTP", success, error, response)
        
        if not success:
            return False
        
        mock_otp = response.get('mock_otp', '123456')
        
        # 2. Verify OTP and login
        success, error, response = self.make_request('POST', 'auth/verify-otp', {
            'phone': test_phone,
            'otp': mock_otp
        })
        self.log_test("Verify OTP and Login", success, error, response)
        
        if success and response.get('token'):
            self.token = response['token']
            self.user_data = response.get('user', {})
            return True
        
        return False

    def test_register_cafe_owner(self):
        """Test cafe owner registration"""
        print("\n👤 Testing Cafe Owner Registration...")
        
        owner_phone = "+919876543211"
        
        # Send OTP for owner
        success, error, response = self.make_request('POST', 'auth/login', {'phone': owner_phone})
        self.log_test("Send OTP for Owner", success, error, response)
        
        if not success:
            return False
        
        # Register as cafe owner
        success, error, response = self.make_request('POST', 'auth/register', {
            'phone': owner_phone,
            'name': 'Test Cafe Owner',
            'email': 'owner@test.com',
            'role': 'CAFE_OWNER'
        })
        self.log_test("Register Cafe Owner", success, error, response)
        
        if success and response.get('token'):
            self.token = response['token']
            self.user_data = response.get('user', {})
            return True
        
        return False

    def test_cafe_management(self):
        """Test cafe CRUD operations"""
        print("\n🏢 Testing Cafe Management...")
        
        # Create cafe
        cafe_data = {
            'name': 'Test Gaming Cafe',
            'address': '123 Test Street',
            'city': 'Test City',
            'description': 'A test gaming cafe'
        }
        
        success, error, response = self.make_request('POST', 'cafes', cafe_data, 200)
        self.log_test("Create Cafe", success, error, response)
        
        if not success:
            return False, None
        
        cafe_id = response.get('id')
        
        # List cafes
        success, error, response = self.make_request('GET', 'cafes')
        self.log_test("List Cafes", success, error, response)
        
        # Get public cafes
        success, error, response = self.make_request('GET', 'cafes/public')
        self.log_test("Get Public Cafes", success, error, response)
        
        # Get specific cafe
        if cafe_id:
            success, error, response = self.make_request('GET', f'cafes/{cafe_id}')
            self.log_test("Get Specific Cafe", success, error, response)
        
        return True, cafe_id

    def test_device_management(self, cafe_id: str):
        """Test device CRUD operations"""
        print("\n🎮 Testing Device Management...")
        
        # Create device
        device_data = {
            'name': 'Gaming PC #1',
            'device_type': 'PC',
            'specifications': 'RTX 4080, 32GB RAM, i7-13700K',
            'hourly_rate': 150.0
        }
        
        success, error, response = self.make_request('POST', 'devices', device_data, 200)
        self.log_test("Create Device", success, error, response)
        
        if not success:
            return False, None
        
        device_id = response.get('id')
        
        # List devices
        success, error, response = self.make_request('GET', 'devices')
        self.log_test("List Devices", success, error, response)
        
        # List devices by cafe
        if cafe_id:
            success, error, response = self.make_request('GET', f'devices?cafe_id={cafe_id}')
            self.log_test("List Devices by Cafe", success, error, response)
        
        # Update device status
        if device_id:
            success, error, response = self.make_request('PATCH', f'devices/{device_id}/status', 'MAINTENANCE')
            self.log_test("Update Device Status", success, error, response)
        
        return True, device_id

    def test_session_management(self, device_id: str):
        """Test session/booking operations"""
        print("\n⏱️ Testing Session Management...")
        
        if not device_id or not self.user_data:
            self.log_test("Session Management", False, "Missing device_id or user_data")
            return False, None
        
        # Create session
        session_data = {
            'device_id': device_id,
            'customer_id': self.user_data.get('id')
        }
        
        success, error, response = self.make_request('POST', 'sessions', session_data, 200)
        self.log_test("Create Session", success, error, response)
        
        if not success:
            return False, None
        
        session_id = response.get('id')
        
        # List sessions
        success, error, response = self.make_request('GET', 'sessions')
        self.log_test("List Sessions", success, error, response)
        
        # End session
        if session_id:
            success, error, response = self.make_request('POST', f'sessions/{session_id}/end')
            self.log_test("End Session", success, error, response)
        
        return True, session_id

    def test_ai_integration(self):
        """Test AI agent integration"""
        print("\n🤖 Testing AI Integration...")
        
        if not self.user_data or self.user_data.get('role') != 'CAFE_OWNER':
            self.log_test("AI Integration", False, "User is not a cafe owner")
            return False
        
        # Test AI chat
        ai_message = {
            'message': 'How can I improve my cafe revenue?',
            'agent_type': 'OWNER_ASSISTANT'
        }
        
        success, error, response = self.make_request('POST', 'ai/chat', ai_message)
        self.log_test("AI Chat - Owner Assistant", success, error, response)
        
        # Test different AI agents
        ai_agents = [
            'SMART_PRICING',
            'DEVICE_OPTIMIZATION', 
            'CUSTOMER_BEHAVIOR',
            'RISK_FRAUD'
        ]
        
        for agent_type in ai_agents:
            ai_message['agent_type'] = agent_type
            ai_message['message'] = f'Analyze my cafe data for {agent_type.lower()}'
            success, error, response = self.make_request('POST', 'ai/chat', ai_message)
            self.log_test(f"AI Chat - {agent_type}", success, error, response)
        
        return True

    def test_analytics(self):
        """Test analytics endpoints"""
        print("\n📊 Testing Analytics...")
        
        # Get dashboard analytics
        success, error, response = self.make_request('GET', 'analytics/dashboard')
        self.log_test("Dashboard Analytics", success, error, response)
        
        return success

    def test_subscription(self):
        """Test subscription endpoints"""
        print("\n💳 Testing Subscription...")
        
        if not self.user_data or self.user_data.get('role') != 'CAFE_OWNER':
            self.log_test("Subscription", False, "User is not a cafe owner")
            return False
        
        # Get my subscription
        success, error, response = self.make_request('GET', 'subscriptions/my')
        self.log_test("Get My Subscription", success, error, response)
        
        return success

    def test_user_profile(self):
        """Test user profile endpoints"""
        print("\n👤 Testing User Profile...")
        
        # Get current user
        success, error, response = self.make_request('GET', 'auth/me')
        self.log_test("Get Current User", success, error, response)
        
        return success

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Gaming Café API Test Suite...")
        print(f"Testing against: {self.base_url}")
        
        # Test authentication first
        if not self.test_register_cafe_owner():
            print("❌ Authentication failed, stopping tests")
            return self.generate_report()
        
        # Test user profile
        self.test_user_profile()
        
        # Test cafe management
        cafe_success, cafe_id = self.test_cafe_management()
        
        # Test device management
        device_success, device_id = False, None
        if cafe_success and cafe_id:
            device_success, device_id = self.test_device_management(cafe_id)
        
        # Test session management
        if device_success and device_id:
            self.test_session_management(device_id)
        
        # Test AI integration
        self.test_ai_integration()
        
        # Test analytics
        self.test_analytics()
        
        # Test subscription
        self.test_subscription()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print(f"\n📊 Test Results Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['error']}")
        
        # Return results for further processing
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": len(self.failed_tests),
            "success_rate": (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            "failed_test_details": self.failed_tests,
            "all_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = GameCafeAPITester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if results["success_rate"] > 80 else 1

if __name__ == "__main__":
    sys.exit(main())