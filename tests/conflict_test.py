#!/usr/bin/env python3

import sys
sys.path.append('/workspace')

from test_appointment_availability import main, MOCK_DATA
import json

def test_conflict_scenarios():
    """Test scenarios that should show conflicts and next available slots"""
    print("=== CONFLICT DETECTION TESTING ===\n")
    
    # Test 1: Try to book exactly when Dr. Euler has appointments on June 7th
    print("Test 1: Try to book during Dr. Euler's busy time on June 7th")
    print("Existing appointment: 10:00-10:15 (Blood pressure check)")
    print("Trying to book: 10:00 AM for 15 minutes")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-07T10:00:00")
    print(f"Available: {result['available']}")
    if not result['available']:
        print(f"Conflict: {result['conflict_reason']}")
        if result.get('next_available'):
            print(f"Next available: {result['next_available']['formatted_datetime']}")
    print()
    
    # Test 2: Try to book overlapping with existing appointment
    print("Test 2: Try to book overlapping appointment")
    print("Existing appointment: 10:15-10:30 (Cholesterol follow-up)")
    print("Trying to book: 10:10 AM for 15 minutes (would overlap)")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-07T10:10:00")
    print(f"Available: {result['available']}")
    if not result['available']:
        print(f"Conflict: {result['conflict_reason']}")
        if result.get('next_available'):
            print(f"Next available: {result['next_available']['formatted_datetime']}")
    print()
    
    # Test 3: Try to book a 30-minute appointment in a busy period
    print("Test 3: Try to book 30-minute appointment during busy period")
    print("Trying to book: 10:45 AM for 30 minutes on June 7th")
    print("This would conflict with 11:00 AM appointment")
    result = main("b3d84592-2fd2-4ab1-b41f-511ecfc2c999", "2025-06-07T10:45:00")
    print(f"Available: {result['available']}")
    if not result['available']:
        print(f"Conflict: {result['conflict_reason']}")
        if result.get('next_available'):
            print(f"Next available: {result['next_available']['formatted_datetime']}")
    print()
    
    # Test 4: Find available slot in a busy day
    print("Test 4: Find available slot on Dr. Euler's busy Tuesday")
    print("Trying to book: 12:00 PM (should be available between appointments)")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-07T12:00:00")
    print(f"Available: {result['available']}")
    if result['available']:
        print("✅ Found available slot during lunch time")
    else:
        print(f"Conflict: {result['conflict_reason']}")
        if result.get('next_available'):
            print(f"Next available: {result['next_available']['formatted_datetime']}")
    print()
    
    # Test 5: Test self-exclusion (rescheduling existing appointment)
    print("Test 5: Test self-exclusion when rescheduling")
    print("Rescheduling appointment 56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e")
    print("From: 2025-06-07T10:00:00 To: 2025-06-07T10:00:00 (same time)")
    print("Should be available because we exclude the appointment being rescheduled")
    result = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-07T10:00:00")
    print(f"Available: {result['available']}")
    if result['available']:
        print("✅ Self-exclusion working correctly")
    else:
        print(f"❌ Self-exclusion failed: {result['conflict_reason']}")
    print()

def show_detailed_schedule():
    """Show detailed schedule for analysis"""
    print("=== DETAILED SCHEDULE ANALYSIS ===\n")
    
    print("Dr. Euler's detailed schedule for June 7th, 2025 (Saturday):")
    print("Working hours: Not available on Saturday")
    print("But has appointments scheduled (data inconsistency):")
    
    euler_id = "1cb198af-6574-4f0a-a057-c24cdde69329"
    appointments = []
    
    for apt in MOCK_DATA["appointments"]:
        if apt["provider_id"] == euler_id and "2025-06-07" in apt["appointment_time"]:
            appointments.append(apt)
    
    appointments.sort(key=lambda x: x["appointment_time"])
    
    for apt in appointments:
        print(f"  {apt['appointment_time'][:16]} - {apt['type']} ({apt['duration_minutes']}min)")
        print(f"    Patient: {apt['patient_id'][:8]}... | Notes: {apt['notes']}")
    
    print(f"\nNote: Dr. Euler is scheduled to work Tuesdays 10:00-16:00")
    print("The June 7th appointments appear to be on a Saturday when he doesn't work.")
    print("This explains why the system correctly identifies conflicts.")
    print()

if __name__ == "__main__":
    test_conflict_scenarios()
    show_detailed_schedule()