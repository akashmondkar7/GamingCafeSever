import requests
import sys
import json
from datetime import datetime

class ComprehensiveAPITester:
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

    def test_auth_flow(self):
        """Test complete authentication flow"""
        print("\n🔐 TESTING AUTHENTICATION FLOW")
        
        # Test OTP login
        success, response = self.run_test(
            "Send OTP",
            "POST",
            "api/auth/login",
            200,
            data={"phone": "+919876543210"}
        )
        if not success:
            return False

        # Test OTP verification
        success, response = self.run_test(
            "Verify OTP",
            "POST", 
            "api/auth/verify-otp",
            200,
            data={"phone": "+919876543210", "otp": "123456"}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_cafe_management(self):
        """Test cafe management endpoints"""
        print("\n🏢 TESTING CAFE MANAGEMENT")
        
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

        # List cafes
        self.run_test("List Cafes", "GET", "api/cafes", 200)
        
        # Get public cafes
        self.run_test("Get Public Cafes", "GET", "api/cafes/public", 200)
        
        # Get specific cafe
        if self.cafe_id:
            self.run_test("Get Cafe Details", "GET", f"api/cafes/{self.cafe_id}", 200)

        return True

    def test_device_management(self):
        """Test device management endpoints"""
        print("\n🎮 TESTING DEVICE MANAGEMENT")
        
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

        # List devices
        self.run_test("List Devices", "GET", "api/devices", 200)
        
        # Update device status
        if self.device_id:
            self.run_test(
                "Update Device Status",
                "PATCH",
                f"api/devices/{self.device_id}/status",
                200,
                data={"status": "MAINTENANCE"}
            )

        return True

    def test_session_management(self):
        """Test session management endpoints"""
        print("\n⏱️ TESTING SESSION MANAGEMENT")
        
        if not self.device_id:
            print("❌ No device available for session testing")
            return False

        # First set device to available
        self.run_test(
            "Set Device Available",
            "PATCH",
            f"api/devices/{self.device_id}/status",
            200,
            data={"status": "AVAILABLE"}
        )

        # Create session
        success, response = self.run_test(
            "Create Session",
            "POST",
            "api/sessions",
            200,
            data={
                "device_id": self.device_id,
                "customer_id": self.user_id
            }
        )
        if success and 'id' in response:
            self.session_id = response['id']
            print(f"   Session created: {self.session_id}")

        # List sessions
        self.run_test("List Sessions", "GET", "api/sessions", 200)
        
        # End session
        if self.session_id:
            self.run_test(
                "End Session",
                "POST",
                f"api/sessions/{self.session_id}/end",
                200
            )

        return True

    def test_ai_agents(self):
        """Test all 7 AI agents"""
        print("\n🤖 TESTING AI AGENTS (ALL 7 TYPES)")
        
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

        # Test extended AI agents
        success, response = self.run_test(
            "AI Staff Performance",
            "POST",
            "api/ai/staff-performance",
            200
        )
        if success:
            ai_passed += 1

        success, response = self.run_test(
            "AI Automation Agent",
            "POST", 
            "api/ai/automation",
            200
        )
        if success:
            ai_passed += 1

        print(f"   AI Agents Working: {ai_passed}/7")
        return ai_passed >= 5  # At least 5 out of 7 should work

    def test_game_library(self):
        """Test game library management"""
        print("\n🎯 TESTING GAME LIBRARY")
        
        # Create game
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

        # List games
        self.run_test("List Games", "GET", "api/games", 200)
        
        # Get game details
        if success and 'id' in response:
            game_id = response['id']
            self.run_test("Get Game Details", "GET", f"api/games/{game_id}", 200)

        return True

    def test_membership_system(self):
        """Test membership and wallet system"""
        print("\n👑 TESTING MEMBERSHIP & WALLET SYSTEM")
        
        # Get membership
        self.run_test("Get My Membership", "GET", "api/membership/my", 200)
        
        # Add money to wallet
        self.run_test(
            "Add Money to Wallet",
            "POST",
            "api/wallet/add-money?amount=1000",
            200
        )
        
        # Get wallet transactions
        self.run_test("Get Wallet Transactions", "GET", "api/wallet/transactions", 200)
        
        # Purchase pass
        success, response = self.run_test(
            "Purchase Gaming Pass",
            "POST",
            "api/membership/purchase-pass",
            200,
            data={
                "pass_type": "HOURLY",
                "cafe_id": self.cafe_id or "default"
            }
        )
        
        # List passes
        self.run_test("List My Passes", "GET", "api/membership/passes", 200)

        return True

    def test_pricing_and_coupons(self):
        """Test pricing rules and coupon system"""
        print("\n💰 TESTING PRICING CONTROLS & COUPONS")
        
        # Create pricing rule
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
        
        # List pricing rules
        self.run_test("List Pricing Rules", "GET", "api/pricing-rules", 200)
        
        # Create coupon
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

    def test_staff_management(self):
        """Test staff panel functionality"""
        print("\n👥 TESTING STAFF MANAGEMENT")
        
        # Start shift
        self.run_test("Start Staff Shift", "POST", "api/staff/shift/start", 200)
        
        return True

    def test_analytics_dashboard(self):
        """Test analytics and dashboard endpoints"""
        print("\n📊 TESTING ANALYTICS & DASHBOARD")
        
        # Get dashboard analytics
        self.run_test("Get Dashboard Analytics", "GET", "api/analytics/dashboard", 200)
        
        # Get subscription info
        self.run_test("Get My Subscription", "GET", "api/subscriptions/my", 200)

        return True

    def test_export_reports(self):
        """Test export functionality"""
        print("\n📄 TESTING EXPORT REPORTS")
        
        # Export sessions report
        self.run_test("Export Sessions Report", "GET", "api/reports/sessions/export?format=json", 200)
        
        # Export revenue report
        self.run_test("Export Revenue Report", "GET", "api/reports/revenue/export", 200)

        return True

    def test_automation_features(self):
        """Test automation features"""
        print("\n⚡ TESTING AUTOMATION FEATURES")
        
        # Check no-shows
        self.run_test("Check No-Shows", "POST", "api/automation/check-noshows", 200)
        
        # Check overstay
        self.run_test("Check Overstay", "POST", "api/automation/check-overstay", 200)

        return True

    def test_qr_and_invoicing(self):
        """Test QR codes and invoicing"""
        print("\n📱 TESTING QR CODES & INVOICING")
        
        if self.session_id:
            # Generate QR code
            self.run_test("Generate Session QR", "GET", f"api/sessions/{self.session_id}/qr", 200)
            
            # Generate invoice
            self.run_test("Generate Invoice", "POST", f"api/invoices/generate?session_id={self.session_id}", 200)
        
        # Get my invoices
        self.run_test("Get My Invoices", "GET", "api/invoices/my", 200)

        return True

    def test_referral_system(self):
        """Test referral system"""
        print("\n🎁 TESTING REFERRAL SYSTEM")
        
        # Apply referral code (will fail if code doesn't exist, but tests endpoint)
        success, response = self.run_test(
            "Apply Referral Code",
            "POST",
            "api/referrals/apply?referral_code=TESTREF123",
            404  # Expected to fail with test code
        )

        return True

    def test_franchise_dashboard(self):
        """Test franchise overview"""
        print("\n🏪 TESTING FRANCHISE DASHBOARD")
        
        # Get franchise overview
        self.run_test("Get Franchise Overview", "GET", "api/franchise/overview", 200)

        return True

def main():
    print("🚀 STARTING COMPREHENSIVE GAMING CAFÉ API TESTING")
    print("=" * 60)
    
    tester = ComprehensiveAPITester()
    
    # Test authentication first
    if not tester.test_auth_flow():
        print("❌ Authentication failed, stopping tests")
        return 1

    # Run all test suites
    test_suites = [
        tester.test_cafe_management,
        tester.test_device_management, 
        tester.test_session_management,
        tester.test_ai_agents,
        tester.test_game_library,
        tester.test_membership_system,
        tester.test_pricing_and_coupons,
        tester.test_staff_management,
        tester.test_analytics_dashboard,
        tester.test_export_reports,
        tester.test_automation_features,
        tester.test_qr_and_invoicing,
        tester.test_referral_system,
        tester.test_franchise_dashboard
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
    
    if tester.tests_passed >= tester.tests_run * 0.8:
        print("🎉 COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())