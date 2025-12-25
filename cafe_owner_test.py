import requests
import sys
import json
from datetime import datetime

class CafeOwnerAPITester:
    def __init__(self, base_url="https://gamecafe-os.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.cafe_id = None
        self.device_id = None
        self.session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json() if response.content else {}
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_auth_as_cafe_owner(self):
        """Test authentication as cafe owner"""
        print("\n🔐 TESTING AUTHENTICATION AS CAFE OWNER")
        
        # Register as cafe owner
        success, response = self.run_test(
            "Register Cafe Owner",
            "POST",
            "api/auth/register",
            200,
            data={
                "phone": "+919876543211",
                "name": "Test Cafe Owner",
                "email": "owner@test.com",
                "role": "CAFE_OWNER"
            }
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_core_features(self):
        """Test core features that should work"""
        print("\n🏢 TESTING CORE FEATURES")
        
        # Create cafe
        success, response = self.run_test(
            "Create Cafe",
            "POST",
            "api/cafes",
            200,
            data={
                "name": "Test Gaming Cafe",
                "address": "123 Test Street", 
                "city": "Mumbai",
                "description": "A premium gaming destination"
            }
        )
        if success and 'id' in response:
            self.cafe_id = response['id']
            print(f"   Cafe created: {self.cafe_id}")

        # Create device
        success, response = self.run_test(
            "Create Device",
            "POST",
            "api/devices",
            200,
            data={
                "name": "Gaming PC #1",
                "device_type": "PC",
                "specifications": "RTX 4080, 32GB RAM",
                "hourly_rate": 150
            }
        )
        if success and 'id' in response:
            self.device_id = response['id']
            print(f"   Device created: {self.device_id}")

        # Test analytics
        self.run_test("Get Dashboard Analytics", "GET", "api/analytics/dashboard", 200)

        return True

    def test_ai_agents_fixed(self):
        """Test if AI agents are working now"""
        print("\n🤖 TESTING AI AGENTS (CRITICAL FIX CHECK)")
        
        ai_agents = [
            "OWNER_ASSISTANT",
            "SMART_PRICING", 
            "DEVICE_OPTIMIZATION",
            "CUSTOMER_BEHAVIOR",
            "RISK_FRAUD"
        ]
        
        ai_passed = 0
        for agent_type in ai_agents:
            success, response = self.run_test(
                f"AI Agent - {agent_type}",
                "POST",
                "api/ai/chat",
                200,
                data={
                    "message": f"Give me insights about {agent_type.lower().replace('_', ' ')}",
                    "agent_type": agent_type
                }
            )
            if success and 'response' in response:
                ai_passed += 1
                print(f"   AI Response: {response['response'][:100]}...")

        print(f"   AI Agents Working: {ai_passed}/5")
        return ai_passed >= 3  # At least 3 out of 5 should work

    def test_extended_features(self):
        """Test extended features from routes_extended.py"""
        print("\n🎯 TESTING EXTENDED FEATURES")
        
        # Test game library
        success, response = self.run_test(
            "Create Game",
            "POST",
            "api/games",
            200,
            data={
                "name": "Call of Duty: Modern Warfare",
                "device_types": ["PC"],
                "genre": "FPS",
                "description": "Popular first-person shooter",
                "how_to_start": "Launch from desktop",
                "controls_guide": "WASD to move, Mouse to aim",
                "difficulty_level": "MEDIUM",
                "age_rating": "MATURE"
            }
        )

        # Test pricing rules
        self.run_test(
            "Create Pricing Rule",
            "POST",
            "api/pricing-rules",
            200,
            data={
                "rule_type": "PEAK",
                "multiplier": 1.5,
                "start_time": "18:00",
                "end_time": "23:00",
                "days_of_week": [1, 2, 3, 4, 5]
            }
        )

        # Test coupons
        self.run_test(
            "Create Coupon",
            "POST",
            "api/coupons",
            200,
            data={
                "code": "TESTCOUPON50",
                "discount_type": "percentage",
                "discount_value": 50,
                "min_amount": 100,
                "max_uses": 10,
                "valid_days": 30
            }
        )

        return True

    def test_advanced_features(self):
        """Test advanced features from routes_advanced.py"""
        print("\n⚡ TESTING ADVANCED FEATURES")
        
        # Test export reports
        self.run_test("Export Sessions Report", "GET", "api/reports/sessions/export?format=json", 200)
        
        # Test automation
        self.run_test("Check No-Shows", "POST", "api/automation/check-noshows", 200)
        
        # Test franchise overview
        self.run_test("Get Franchise Overview", "GET", "api/franchise/overview", 200)

        return True

def main():
    print("🚀 TESTING GAMING CAFÉ API AS CAFE OWNER")
    print("=" * 60)
    
    tester = CafeOwnerAPITester()
    
    # Test authentication as cafe owner
    if not tester.test_auth_as_cafe_owner():
        print("❌ Authentication as cafe owner failed, stopping tests")
        return 1

    # Run test suites
    test_suites = [
        tester.test_core_features,
        tester.test_ai_agents_fixed,
        tester.test_extended_features,
        tester.test_advanced_features
    ]
    
    for test_suite in test_suites:
        try:
            test_suite()
        except Exception as e:
            print(f"❌ Test suite failed: {str(e)}")

    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())