#!/usr/bin/env python3

import sys
sys.path.append('/workspace')

from test_appointment_availability import main, MOCK_DATA
import json

def test_tuesday_conflicts():
    """Test conflicts on a Tuesday when Dr. Euler actually works"""
    print("=== TUESDAY CONFLICT TESTING ===\n")
    
    print("Dr. Euler works Tuesdays 10:00-16:00")
    print("Let's test conflicts on Tuesday June 10th, 2025\n")
    
    # Test 1: Try to book before working hours
    print("Test 1: Before working hours")
    print("Trying to book: 9:00 AM (before 10:00 AM start)")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-10T09:00:00")
    print(f"Available: {result['available']}")
    if not result['available']:
        print(f"Reason: {result['conflict_reason']}")
        if result.get('next_available'):
            print(f"Next available: {result['next_available']['formatted_datetime']}")
    print()
    
    # Test 2: Try to book after working hours
    print("Test 2: After working hours")
    print("Trying to book: 4:00 PM (ends at 4:15 PM, but work ends at 4:00 PM)")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-10T16:00:00")
    print(f"Available: {result['available']}")
    if not result['available']:
        print(f"Reason: {result['conflict_reason']}")
        if result.get('next_available'):
            print(f"Next available: {result['next_available']['formatted_datetime']}")
    print()
    
    # Test 3: Try to book at exactly closing time
    print("Test 3: Appointment ending exactly at closing time")
    print("Trying to book: 3:45 PM (15-min appointment ending at 4:00 PM)")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-10T15:45:00")
    print(f"Available: {result['available']}")
    if result['available']:
        print("✅ Available - appointment ends exactly at closing time")
    else:
        print(f"Reason: {result['conflict_reason']}")
    print()
    
    # Test 4: Available time slots
    print("Test 4: Available time slots")
    available_times = [
        "10:00:00", "10:15:00", "10:30:00", "11:00:00", 
        "12:00:00", "13:00:00", "14:00:00", "15:00:00"
    ]
    
    for time_str in available_times:
        result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", f"2025-06-10T{time_str}")
        status = "✅ Available" if result['available'] else "❌ Not available"
        print(f"  {time_str}: {status}")
        if not result['available']:
            print(f"    Reason: {result['conflict_reason']}")
    print()

def test_monday_conflicts():
    """Test conflicts on Monday for Dr. von Neeumann"""
    print("=== MONDAY CONFLICT TESTING (Dr. von Neeumann) ===\n")
    
    print("Dr. von Neeumann works Mondays 9:00-15:30")
    print("Existing appointments on June 2nd:")
    print("- 10:00-10:15: Acid reflux follow-up")
    print("- 13:00-13:15: Post-procedure review")
    print()
    
    # Test overlapping appointments
    test_times = [
        ("09:00:00", "Start of day"),
        ("09:45:00", "Before first appointment"),
        ("10:00:00", "Exact conflict with 10:00 appointment"),
        ("10:05:00", "Overlapping with 10:00 appointment"),
        ("10:15:00", "Right after first appointment"),
        ("12:45:00", "Before second appointment"),
        ("13:00:00", "Exact conflict with 13:00 appointment"),
        ("13:15:00", "Right after second appointment"),
        ("15:00:00", "30-min appointment ending at 15:30"),
        ("15:15:00", "Would end after closing time")
    ]
    
    for time_str, description in test_times:
        result = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", f"2025-06-02T{time_str}")
        status = "✅ Available" if result['available'] else "❌ Not available"
        print(f"  {time_str} ({description}): {status}")
        if not result['available']:
            print(f"    Reason: {result['conflict_reason']}")
            if result.get('next_available'):
                next_time = result['next_available']['time']
                print(f"    Next available: {next_time}")
    print()

if __name__ == "__main__":
    test_tuesday_conflicts()
    test_monday_conflicts()