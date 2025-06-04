#!/usr/bin/env python3

import sys
sys.path.append('/workspace')

from test_appointment_availability import main, MOCK_DATA
import json
from datetime import datetime, timedelta

def comprehensive_validation_test():
    """Comprehensive test covering all validation scenarios"""
    print("=== COMPREHENSIVE VALIDATION TEST ===\n")
    
    current_time = datetime.now()
    print(f"Current time: {current_time.isoformat()}")
    print()
    
    test_scenarios = [
        {
            "name": "Past Date - Yesterday",
            "appointment_id": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "datetime": (current_time - timedelta(days=1)).strftime("%Y-%m-%dT10:00:00"),
            "expected_success": False,
            "expected_reason": "past date"
        },
        {
            "name": "Past Date - Last Week",
            "appointment_id": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "datetime": (current_time - timedelta(days=7)).strftime("%Y-%m-%dT14:00:00"),
            "expected_success": False,
            "expected_reason": "past date"
        },
        {
            "name": "Current Time (should be rejected)",
            "appointment_id": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "datetime": current_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "expected_success": False,
            "expected_reason": "current time"
        },
        {
            "name": "Future - Available Slot",
            "appointment_id": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "datetime": "2025-07-07T10:00:00",  # Monday in July
            "expected_success": True,
            "expected_available": True,
            "expected_reason": "available"
        },
        {
            "name": "Future - Outside Working Hours",
            "appointment_id": "56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e",
            "datetime": "2025-06-10T08:00:00",  # Tuesday before 10 AM
            "expected_success": True,
            "expected_available": False,
            "expected_reason": "outside working hours"
        },
        {
            "name": "Future - Provider Not Available (Wrong Day)",
            "appointment_id": "56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e",
            "datetime": "2025-06-11T10:00:00",  # Wednesday (Dr. Euler doesn't work)
            "expected_success": True,
            "expected_available": False,
            "expected_reason": "provider not available"
        },
        {
            "name": "Future - Appointment Ending After Hours",
            "appointment_id": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "datetime": "2025-06-09T15:15:00",  # 30-min appointment ending at 15:45, but work ends at 15:30
            "expected_success": True,
            "expected_available": False,
            "expected_reason": "outside working hours"
        },
        {
            "name": "Invalid Appointment ID",
            "appointment_id": "invalid-appointment-id",
            "datetime": "2025-06-10T10:00:00",
            "expected_success": False,
            "expected_reason": "appointment not found"
        },
        {
            "name": "Invalid DateTime Format",
            "appointment_id": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "datetime": "invalid-datetime",
            "expected_success": False,
            "expected_reason": "invalid format"
        },
        {
            "name": "Future - Available at Exact Closing Time",
            "appointment_id": "56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e",
            "datetime": "2025-06-10T15:45:00",  # 15-min appointment ending exactly at 16:00
            "expected_success": True,
            "expected_available": True,
            "expected_reason": "available at closing"
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Test {i}: {scenario['name']}")
        print(f"  Appointment ID: {scenario['appointment_id']}")
        print(f"  DateTime: {scenario['datetime']}")
        
        result = main(scenario['appointment_id'], scenario['datetime'])
        
        # Check if the result matches expectations
        success_match = result['success'] == scenario['expected_success']
        
        if scenario['expected_success']:
            if 'expected_available' in scenario:
                available_match = result.get('available') == scenario['expected_available']
            else:
                available_match = True  # Don't check availability if not specified
        else:
            available_match = True  # Don't check availability for failed requests
        
        if success_match and available_match:
            print(f"  ✅ PASS")
            passed_tests += 1
        else:
            print(f"  ❌ FAIL")
            print(f"    Expected success: {scenario['expected_success']}, Got: {result['success']}")
            if 'expected_available' in scenario:
                print(f"    Expected available: {scenario['expected_available']}, Got: {result.get('available')}")
        
        # Show the actual result
        print(f"  Result: Success={result['success']}, Available={result.get('available', 'N/A')}")
        if not result['success']:
            print(f"  Error: {result.get('error', 'Unknown')}")
        elif not result.get('available', True):
            print(f"  Conflict: {result.get('conflict_reason', 'Unknown')}")
            if result.get('next_available'):
                print(f"  Next Available: {result['next_available']['formatted_datetime']}")
        
        print()
    
    print(f"=== TEST SUMMARY ===")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The appointment validation system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")

def test_realistic_scenarios():
    """Test realistic scenarios that might occur in production"""
    print("\n=== REALISTIC PRODUCTION SCENARIOS ===\n")
    
    scenarios = [
        {
            "description": "Patient calls to reschedule from next week to tomorrow",
            "original_appointment": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "preferred_time": "2025-06-05T10:00:00",  # Tomorrow
            "context": "Dr. von Neeumann, should work if it's a Monday"
        },
        {
            "description": "Patient wants to move appointment to lunch time",
            "original_appointment": "56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e",
            "preferred_time": "2025-06-10T12:30:00",  # Tuesday lunch time
            "context": "Dr. Euler, should be available during lunch"
        },
        {
            "description": "Patient requests very early morning appointment",
            "original_appointment": "56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e",
            "preferred_time": "2025-06-10T07:00:00",  # Too early
            "context": "Before Dr. Euler's working hours"
        },
        {
            "description": "Patient wants weekend appointment",
            "original_appointment": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "preferred_time": "2025-06-07T10:00:00",  # Saturday
            "context": "Dr. von Neeumann doesn't work weekends"
        },
        {
            "description": "Patient tries to book in the past (common mistake)",
            "original_appointment": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "preferred_time": "2025-06-01T10:00:00",  # Past date
            "context": "Should be rejected with clear error message"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['description']}")
        print(f"Context: {scenario['context']}")
        print(f"Preferred time: {scenario['preferred_time']}")
        
        result = main(scenario['original_appointment'], scenario['preferred_time'])
        
        if result['success']:
            if result['available']:
                print("✅ Appointment can be rescheduled to preferred time")
            else:
                print(f"⚠️ Preferred time not available: {result['conflict_reason']}")
                if result.get('next_available'):
                    print(f"💡 Suggested alternative: {result['next_available']['formatted_datetime']}")
        else:
            print(f"❌ Request failed: {result['error']}")
        
        print()

if __name__ == "__main__":
    comprehensive_validation_test()
    test_realistic_scenarios()