#!/usr/bin/env python3

import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

# Mock data based on the provided schema
MOCK_DATA = {
    "visit_types": [
        {
            "id": "6b4f1d24-b476-4a49-931f-18a4324980aa",
            "name": "New Patient",
            "max_patients_per_slot": 1,
            "default_duration_minutes": 30
        },
        {
            "id": "9cd7cd4b-2995-4326-b449-4c1448429743",
            "name": "Follow-Up",
            "max_patients_per_slot": 2,
            "default_duration_minutes": 15
        }
    ],
    "providers": [
        {
            "id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "role": "NP",
            "full_name": "Dr. Leonhard Euler",
            "specialty": "Family Medicine",
            "created_at": "2025-04-24T21:27:53.693744"
        },
        {
            "id": "b42f0f8e-9c40-460e-844a-d280012c4539",
            "role": "MD",
            "full_name": "Dr. John von Neeumann",
            "specialty": "Gastroenterology",
            "created_at": "2025-04-24T21:27:53.693744"
        }
    ],
    "patients": [
        {
            "id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "full_name": "John Doe",
            "created_at": "2025-04-24T21:27:53.693744",
            "date_of_birth": "1985-06-15"
        },
        {
            "id": "fe13e36f-0e2e-4324-bc31-07b46a9ec054",
            "email": "jane.smith@example.com",
            "phone": "555-234-5678",
            "full_name": "Jane Smith",
            "created_at": "2025-04-24T21:27:53.693744",
            "date_of_birth": "1990-09-28"
        },
        {
            "id": "c552f10c-3eb0-4f3d-b294-69735d607728",
            "email": "carlos.rivera@example.com",
            "phone": "555-345-6789",
            "full_name": "Carlos Rivera",
            "created_at": "2025-04-24T21:27:53.693744",
            "date_of_birth": "1975-12-03"
        }
    ],
    "availability": [
        {
            "id": "0465685d-1d83-4182-a79e-a1b8f511e29d",
            "weekday": 1,
            "end_time": "15:30:00",
            "created_at": "2025-04-24T21:27:53.693744",
            "start_time": "09:00:00",
            "provider_id": "b42f0f8e-9c40-460e-844a-d280012c4539"
        },
        {
            "id": "cbc24a05-cae9-4c88-bfd9-73ddf48ac962",
            "weekday": 2,
            "end_time": "16:00:00",
            "created_at": "2025-04-24T21:27:53.693744",
            "start_time": "10:00:00",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329"
        }
    ],
    "appointments": [
        # Dr. Euler (Tuesday 10:00-16:00) - Only ONE Follow-Up appointment at 10:00
        {
            "id": "follow-up-1",
            "type": "Follow-Up",
            "notes": "First follow-up at 10:00",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "fe13e36f-0e2e-4324-bc31-07b46a9ec054",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-10T10:00:00",
            "duration_minutes": 15
        },
        # Dr. von Neeumann (Monday 9:00-15:30) - New Patient appointment
        {
            "id": "new-patient-1",
            "type": "New Patient",
            "notes": "New patient consultation",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "provider_id": "b42f0f8e-9c40-460e-844a-d280012c4539",
            "appointment_time": "2025-06-09T09:00:00",
            "duration_minutes": 30
        }
    ]
}

class MockSupabaseResponse:
    def __init__(self, data):
        self.data = data

class MockSupabaseTable:
    def __init__(self, table_name, mock_data):
        self.table_name = table_name
        self.mock_data = mock_data
        self.filters = {}
        self.selected_fields = "*"
    
    def select(self, fields):
        self.selected_fields = fields
        return self
    
    def eq(self, field, value):
        if field not in self.filters:
            self.filters[field] = []
        self.filters[field].append(('eq', value))
        return self
    
    def neq(self, field, value):
        if field not in self.filters:
            self.filters[field] = []
        self.filters[field].append(('neq', value))
        return self
    
    def execute(self):
        data = self.mock_data.get(self.table_name, [])
        
        # Apply filters
        filtered_data = []
        for item in data:
            include_item = True
            for field, conditions in self.filters.items():
                for condition_type, value in conditions:
                    if condition_type == 'eq' and item.get(field) != value:
                        include_item = False
                        break
                    elif condition_type == 'neq' and item.get(field) == value:
                        include_item = False
                        break
                if not include_item:
                    break
            
            if include_item:
                filtered_data.append(item)
        
        return MockSupabaseResponse(filtered_data)

class MockSupabase:
    def __init__(self, mock_data):
        self.mock_data = mock_data
    
    def table(self, table_name):
        return MockSupabaseTable(table_name, self.mock_data)

class MockWmill:
    @staticmethod
    def get_resource(resource_name):
        return {"url": "mock_url", "key": "mock_key"}

# Import and modify the original functions from the main script
def check_time_availability(
    supabase, 
    provider_id: str, 
    requested_dt: datetime, 
    duration_minutes: int,
    appointment_type: str,
    exclude_appointment_id: str = None
) -> Tuple[bool, str]:
    """
    Check if a specific time slot is available for a provider.
    """
    
    # Check provider availability for the day of week
    weekday = requested_dt.weekday() + 1  # Convert to 1-7 format (Monday=1)
    requested_time = requested_dt.time()
    
    # Get provider's availability for this weekday
    availability_response = supabase.table("availability").select("*").eq("provider_id", provider_id).eq("weekday", weekday).execute()
    
    if not availability_response.data:
        return False, f"Provider not available on {requested_dt.strftime('%A')}"
    
    # Check if requested time falls within provider's working hours
    provider_available = False
    for availability in availability_response.data:
        start_time = datetime.strptime(availability["start_time"], "%H:%M:%S").time()
        end_time = datetime.strptime(availability["end_time"], "%H:%M:%S").time()
        
        # Calculate end time of the appointment
        appointment_end = (requested_dt + timedelta(minutes=duration_minutes)).time()
        
        if start_time <= requested_time and appointment_end <= end_time:
            provider_available = True
            break
    
    if not provider_available:
        return False, "Requested time is outside provider's working hours"
    
    # Get visit type information to check max patients per slot
    visit_types_response = supabase.table("visit_types").select("*").eq("name", appointment_type).execute()
    
    if not visit_types_response.data:
        return False, f"Invalid appointment type: {appointment_type}"
    
    visit_type = visit_types_response.data[0]
    max_patients_per_slot = visit_type["max_patients_per_slot"]
    
    # Check for conflicting appointments and count patients in the same time slot
    appointment_start = requested_dt.isoformat()
    appointment_end = (requested_dt + timedelta(minutes=duration_minutes)).isoformat()
    
    # Build query to find overlapping appointments
    query = supabase.table("appointments").select("*").eq("provider_id", provider_id).eq("status", "scheduled")
    
    if exclude_appointment_id:
        query = query.neq("id", exclude_appointment_id)
    
    existing_appointments = query.execute()
    
    overlapping_appointments = []
    exact_time_appointments = []
    
    for existing in existing_appointments.data:
        existing_start = datetime.fromisoformat(existing["appointment_time"].replace('Z', '+00:00'))
        existing_end = existing_start + timedelta(minutes=existing["duration_minutes"])
        
        # Check for overlap
        if (requested_dt < existing_end and 
            datetime.fromisoformat(appointment_end.replace('Z', '+00:00')) > existing_start):
            overlapping_appointments.append(existing)
            
            # Check if it's the exact same time slot
            if existing_start == requested_dt:
                exact_time_appointments.append(existing)
    
    # For appointments at the exact same time, check if we can accommodate more patients
    if exact_time_appointments:
        # Count patients already scheduled at this exact time
        patients_at_same_time = len(exact_time_appointments)
        
        # Check if we can add one more patient
        if patients_at_same_time >= max_patients_per_slot:
            return False, f"Time slot full: {patients_at_same_time}/{max_patients_per_slot} patients already scheduled at {requested_dt.strftime('%Y-%m-%d %H:%M')}"
        
        # If there's room, it's available (same time slot, different patients)
        return True, ""
    
    # For overlapping but not exact same time, it's a conflict
    if overlapping_appointments:
        conflict_time = datetime.fromisoformat(overlapping_appointments[0]["appointment_time"].replace('Z', '+00:00'))
        return False, f"Conflicts with existing appointment at {conflict_time.strftime('%Y-%m-%d %H:%M')}"
    
    return True, ""

def run_visit_type_tests():
    """Run tests specifically for visit type functionality"""
    
    print("=== VISIT TYPE TESTING ===\n")
    
    # Setup mock supabase
    supabase = MockSupabase(MOCK_DATA)
    
    # Test Case 1: Follow-Up appointment - second patient at 10:00 (should be available)
    print("Test 1: Follow-Up appointment - adding second patient at existing time slot")
    print("Provider: Dr. Euler (Tuesday 10:00-16:00)")
    print("Requested: Tuesday 2025-06-10 at 10:00 AM (Follow-Up)")
    print("Expected: Available (1 Follow-Up patient already at 10:00, max is 2)")
    
    requested_dt = datetime(2025, 6, 10, 10, 0)  # Tuesday 10:00 AM
    is_available, reason = check_time_availability(
        supabase, 
        "1cb198af-6574-4f0a-a057-c24cdde69329",  # Dr. Euler
        requested_dt, 
        15,  # 15 minutes
        "Follow-Up",
        None
    )
    print(f"Result: Available={is_available}, Reason='{reason}'\n")
    
    # Test Case 2: Follow-Up appointment - third patient at 10:00 (should NOT be available)
    print("Test 2: Follow-Up appointment - third patient at same time slot")
    print("Provider: Dr. Euler (Tuesday 10:00-16:00)")
    print("Requested: Tuesday 2025-06-10 at 10:00 AM (Follow-Up)")
    print("Expected: NOT Available (adding second appointment first, then trying third)")
    
    # Add a second appointment to fill the slot
    MOCK_DATA["appointments"].append({
        "id": "follow-up-2",
        "type": "Follow-Up",
        "notes": "Second follow-up at 10:00",
        "status": "scheduled",
        "created_at": "2025-04-24T21:33:41.87287",
        "patient_id": "c552f10c-3eb0-4f3d-b294-69735d607728",
        "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
        "appointment_time": "2025-06-10T10:00:00",
        "duration_minutes": 15
    })
    
    supabase = MockSupabase(MOCK_DATA)  # Refresh with new data
    
    is_available, reason = check_time_availability(
        supabase, 
        "1cb198af-6574-4f0a-a057-c24cdde69329",  # Dr. Euler
        requested_dt, 
        15,  # 15 minutes
        "Follow-Up",
        None
    )
    print(f"Result: Available={is_available}, Reason='{reason}'\n")
    
    # Test Case 3: New Patient appointment at same time (should NOT be available)
    print("Test 3: New Patient appointment at occupied time slot")
    print("Provider: Dr. Euler (Tuesday 10:00-16:00)")
    print("Requested: Tuesday 2025-06-10 at 10:00 AM (New Patient)")
    print("Expected: NOT Available (New Patient max is 1, but Follow-Up patients already there)")
    
    is_available, reason = check_time_availability(
        supabase, 
        "1cb198af-6574-4f0a-a057-c24cdde69329",  # Dr. Euler
        requested_dt, 
        30,  # 30 minutes
        "New Patient",
        None
    )
    print(f"Result: Available={is_available}, Reason='{reason}'\n")
    
    # Test Case 4: New Patient appointment at different time (should be available)
    print("Test 4: New Patient appointment at available time slot")
    print("Provider: Dr. Euler (Tuesday 10:00-16:00)")
    print("Requested: Tuesday 2025-06-10 at 11:00 AM (New Patient)")
    print("Expected: Available (no conflicts)")
    
    requested_dt_new = datetime(2025, 6, 10, 11, 0)  # Tuesday 11:00 AM
    is_available, reason = check_time_availability(
        supabase, 
        "1cb198af-6574-4f0a-a057-c24cdde69329",  # Dr. Euler
        requested_dt_new, 
        30,  # 30 minutes
        "New Patient",
        None
    )
    print(f"Result: Available={is_available}, Reason='{reason}'\n")
    
    # Test Case 5: Invalid appointment type
    print("Test 5: Invalid appointment type")
    print("Provider: Dr. Euler (Tuesday 10:00-16:00)")
    print("Requested: Tuesday 2025-06-10 at 12:00 PM (Invalid Type)")
    print("Expected: NOT Available (invalid appointment type)")
    
    requested_dt_invalid = datetime(2025, 6, 10, 12, 0)  # Tuesday 12:00 PM
    is_available, reason = check_time_availability(
        supabase, 
        "1cb198af-6574-4f0a-a057-c24cdde69329",  # Dr. Euler
        requested_dt_invalid, 
        15,  # 15 minutes
        "Invalid Type",
        None
    )
    print(f"Result: Available={is_available}, Reason='{reason}'\n")
    
    # Test Case 5.5: Follow-Up appointment at time with only 1 patient (should be available)
    print("Test 5.5: Follow-Up appointment at time slot with room")
    print("Provider: Dr. Euler (Tuesday 10:00-16:00)")
    print("Requested: Tuesday 2025-06-10 at 10:15 AM (Follow-Up)")
    print("Expected: Available (no appointments at 10:15)")
    
    requested_dt_available = datetime(2025, 6, 10, 10, 15)  # Tuesday 10:15 AM
    is_available, reason = check_time_availability(
        supabase, 
        "1cb198af-6574-4f0a-a057-c24cdde69329",  # Dr. Euler
        requested_dt_available, 
        15,  # 15 minutes
        "Follow-Up",
        None
    )
    print(f"Result: Available={is_available}, Reason='{reason}'\n")
    
    # Test Case 6: Excluding an appointment (rescheduling)
    print("Test 6: Rescheduling existing appointment")
    print("Provider: Dr. Euler (Tuesday 10:00-16:00)")
    print("Requested: Tuesday 2025-06-10 at 10:00 AM (Follow-Up)")
    print("Excluding: follow-up-1 (one of the existing appointments)")
    print("Expected: Available (excluding one appointment makes room)")
    
    is_available, reason = check_time_availability(
        supabase, 
        "1cb198af-6574-4f0a-a057-c24cdde69329",  # Dr. Euler
        requested_dt, 
        15,  # 15 minutes
        "Follow-Up",
        "follow-up-1"  # Exclude this appointment
    )
    print(f"Result: Available={is_available}, Reason='{reason}'\n")

if __name__ == "__main__":
    run_visit_type_tests()