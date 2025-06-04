#!/usr/bin/env python3

import sys
sys.path.append('/workspace')

from test_appointment_availability import main, MOCK_DATA
import json
from datetime import datetime, timedelta

def test_past_date_scenarios():
    """Test various past date scenarios that should be rejected"""
    print("=== PAST DATE VALIDATION TESTING ===\n")
    
    current_time = datetime.now()
    print(f"Current time: {current_time.isoformat()}")
    print()
    
    # Test 1: Obvious past date (yesterday)
    print("Test 1: Yesterday's date")
    yesterday = current_time - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%dT10:00:00")
    print(f"Trying to book: {yesterday_str}")
    result = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", yesterday_str)
    print(f"Success: {result['success']}")
    print(f"Available: {result['available']}")
    if not result['success']:
        print(f"Error: {result['error']}")
    print()
    
    # Test 2: Last week
    print("Test 2: Last week")
    last_week = current_time - timedelta(days=7)
    last_week_str = last_week.strftime("%Y-%m-%dT14:00:00")
    print(f"Trying to book: {last_week_str}")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", last_week_str)
    print(f"Success: {result['success']}")
    print(f"Available: {result['available']}")
    if not result['success']:
        print(f"Error: {result['error']}")
    print()
    
    # Test 3: A few minutes ago
    print("Test 3: A few minutes ago")
    few_minutes_ago = current_time - timedelta(minutes=5)
    few_minutes_ago_str = few_minutes_ago.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Trying to book: {few_minutes_ago_str}")
    result = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", few_minutes_ago_str)
    print(f"Success: {result['success']}")
    print(f"Available: {result['available']}")
    if not result['success']:
        print(f"Error: {result['error']}")
    print()
    
    # Test 4: Exactly current time (should also be rejected as it's not future)
    print("Test 4: Exactly current time")
    current_time_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Trying to book: {current_time_str}")
    result = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", current_time_str)
    print(f"Success: {result['success']}")
    print(f"Available: {result['available']}")
    if not result['success']:
        print(f"Error: {result['error']}")
    print()
    
    # Test 5: Future date (should work if available)
    print("Test 5: Future date (should work)")
    future_date = current_time + timedelta(days=30)
    # Make sure it's a Monday for Dr. von Neeumann
    while future_date.weekday() != 0:  # 0 = Monday
        future_date += timedelta(days=1)
    future_date_str = future_date.strftime("%Y-%m-%dT10:00:00")
    print(f"Trying to book: {future_date_str}")
    result = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", future_date_str)
    print(f"Success: {result['success']}")
    print(f"Available: {result['available']}")
    if result['success'] and result['available']:
        print("✅ Future date accepted correctly")
    elif result['success'] and not result['available']:
        print(f"⚠️ Future date accepted but not available: {result['conflict_reason']}")
        if result.get('next_available'):
            print(f"Next available: {result['next_available']['formatted_datetime']}")
    else:
        print(f"❌ Future date rejected: {result.get('error', 'Unknown error')}")
    print()

def test_edge_cases_around_current_time():
    """Test edge cases around the current time"""
    print("=== EDGE CASES AROUND CURRENT TIME ===\n")
    
    current_time = datetime.now()
    
    # Test times around current time
    test_offsets = [
        (-60, "1 hour ago"),
        (-30, "30 minutes ago"),
        (-1, "1 minute ago"),
        (0, "exactly now"),
        (1, "1 minute from now"),
        (30, "30 minutes from now"),
        (60, "1 hour from now")
    ]
    
    for offset_minutes, description in test_offsets:
        test_time = current_time + timedelta(minutes=offset_minutes)
        test_time_str = test_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        print(f"Testing {description}: {test_time_str}")
        result = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", test_time_str)
        
        if offset_minutes <= 0:
            # Should be rejected for past/current times
            if not result['success']:
                print(f"  ✅ Correctly rejected: {result['error']}")
            else:
                print(f"  ❌ Should have been rejected but was accepted")
        else:
            # Should be accepted (if provider is available)
            if result['success']:
                print(f"  ✅ Correctly accepted (available: {result['available']})")
                if not result['available']:
                    print(f"    Reason: {result['conflict_reason']}")
            else:
                print(f"  ❌ Should have been accepted but was rejected: {result['error']}")
        print()

def test_next_available_with_past_request():
    """Test that next available slot suggestions don't include past times"""
    print("=== NEXT AVAILABLE SLOT WITH PAST REQUEST ===\n")
    
    current_time = datetime.now()
    
    # Request a past time and see if next available is in the future
    past_time = current_time - timedelta(days=1)
    past_time_str = past_time.strftime("%Y-%m-%dT10:00:00")
    
    print(f"Current time: {current_time.isoformat()}")
    print(f"Requesting past time: {past_time_str}")
    
    # This should fail due to past date validation, but let's test the logic
    # by temporarily modifying our approach
    
    # Let's test with a future date that has conflicts to see next available
    print("\nTesting next available slot logic with future conflicting time:")
    
    # Use a known conflict time from the data
    conflict_time = "2025-06-07T10:00:00"  # Dr. Euler has appointments this day
    print(f"Requesting conflicting time: {conflict_time}")
    
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", conflict_time)
    print(f"Success: {result['success']}")
    print(f"Available: {result['available']}")
    
    if result['success'] and not result['available']:
        if result.get('next_available'):
            next_available_dt = datetime.fromisoformat(result['next_available']['datetime'])
            print(f"Next available: {result['next_available']['formatted_datetime']}")
            
            if next_available_dt > current_time:
                print("✅ Next available slot is correctly in the future")
            else:
                print("❌ Next available slot is in the past!")
        else:
            print("⚠️ No next available slot provided")
    print()

def test_minimum_advance_booking():
    """Test scenarios for minimum advance booking requirements"""
    print("=== MINIMUM ADVANCE BOOKING SCENARIOS ===\n")
    
    current_time = datetime.now()
    
    # Test booking very soon (might want to add minimum advance time)
    soon_times = [
        (5, "5 minutes from now"),
        (15, "15 minutes from now"),
        (30, "30 minutes from now"),
        (60, "1 hour from now"),
        (120, "2 hours from now")
    ]
    
    for offset_minutes, description in soon_times:
        test_time = current_time + timedelta(minutes=offset_minutes)
        # Make sure it's a Monday for Dr. von Neeumann
        while test_time.weekday() != 0:  # 0 = Monday
            test_time += timedelta(days=1)
        
        test_time_str = test_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        print(f"Testing {description}: {test_time_str}")
        result = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", test_time_str)
        
        print(f"  Success: {result['success']}")
        if result['success']:
            print(f"  Available: {result['available']}")
            if not result['available']:
                print(f"  Reason: {result['conflict_reason']}")
        else:
            print(f"  Error: {result['error']}")
        print()

if __name__ == "__main__":
    test_past_date_scenarios()
    test_edge_cases_around_current_time()
    test_next_available_with_past_request()
    test_minimum_advance_booking()