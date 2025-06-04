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
            "weekday": 1,  # Monday
            "end_time": "15:30:00",
            "created_at": "2025-04-24T21:27:53.693744",
            "start_time": "09:00:00",
            "provider_id": "b42f0f8e-9c40-460e-844a-d280012c4539"
        },
        {
            "id": "cbc24a05-cae9-4c88-bfd9-73ddf48ac962",
            "weekday": 2,  # Tuesday
            "end_time": "16:00:00",
            "created_at": "2025-04-24T21:27:53.693744",
            "start_time": "10:00:00",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329"
        }
    ],
    "appointments": [
        {
            "id": "55aab0ac-9249-48e0-a85c-6f1bdc4910ff",
            "type": "New Patient",
            "notes": "Consultation for GI symptoms",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "provider_id": "b42f0f8e-9c40-460e-844a-d280012c4539",
            "appointment_time": "2025-06-13T09:00:00",
            "duration_minutes": 30
        },
        {
            "id": "56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e",
            "type": "Follow-Up",
            "notes": "Blood pressure check",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "fe13e36f-0e2e-4324-bc31-07b46a9ec054",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-07T10:00:00",
            "duration_minutes": 15
        },
        {
            "id": "59deb8ea-8217-4c91-ae5e-81ee15e2f7ec",
            "type": "Follow-Up",
            "notes": "Routine check",
            "status": "scheduled",
            "created_at": "2025-04-24T21:27:53.693744",
            "patient_id": "fe13e36f-0e2e-4324-bc31-07b46a9ec054",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-30T10:30:29.959186",
            "duration_minutes": 15
        },
        {
            "id": "5e2fc4f9-b25b-443f-96e3-89618cf6e6f4",
            "type": "Follow-Up",
            "notes": "Lab test review",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "fe13e36f-0e2e-4324-bc31-07b46a9ec054",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-07T11:00:00",
            "duration_minutes": 15
        },
        {
            "id": "5f6a0c3c-eaf4-4c60-8b97-5e15ebd709a6",
            "type": "Follow-Up",
            "notes": "Cholesterol follow-up",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "c552f10c-3eb0-4f3d-b294-69735d607728",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-07T10:15:00",
            "duration_minutes": 15
        },
        {
            "id": "8f7eda11-db72-4b4e-a3fe-f4362df552c7",
            "type": "New Patient",
            "notes": "Initial consultation",
            "status": "scheduled",
            "created_at": "2025-04-24T21:27:53.693744",
            "patient_id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "provider_id": "b42f0f8e-9c40-460e-844a-d280012c4539",
            "appointment_time": "2025-06-13T10:00:00",
            "duration_minutes": 30
        },
        {
            "id": "931da58e-e99b-4698-8b1c-b0c2219fd22b",
            "type": "Follow-up",
            "notes": "Booking after last visit",
            "status": "Scheduled",
            "created_at": "2025-05-07T08:38:46.507704",
            "patient_id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-09T10:30:00",
            "duration_minutes": 30
        },
        {
            "id": "b3d84592-2fd2-4ab1-b41f-511ecfc2c999",
            "type": "New Patient",
            "notes": "Annual wellness visit",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-07T14:30:00",
            "duration_minutes": 30
        },
        {
            "id": "bc4e9045-e1b7-4986-a261-9d7e5c7bdc6b",
            "type": "Follow-Up",
            "notes": "Cough & cold symptoms",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-07T10:00:00",
            "duration_minutes": 15
        },
        {
            "id": "f2d3c67c-ea7f-43a6-8d45-f930726a0a33",
            "type": "Follow-Up",
            "notes": "Medication adjustment",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "c552f10c-3eb0-4f3d-b294-69735d607728",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-07T11:15:00",
            "duration_minutes": 15
        },
        {
            "id": "a524d84d-36c3-4ac2-b0a3-6c43b942d37f",
            "type": "Follow-Up",
            "notes": "Post-procedure review",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "fe13e36f-0e2e-4324-bc31-07b46a9ec054",
            "provider_id": "b42f0f8e-9c40-460e-844a-d280012c4539",
            "appointment_time": "2025-06-02T13:00:00",
            "duration_minutes": 15
        },
        {
            "id": "4ff06a91-15d2-4e79-ae6d-f2170121e5e3",
            "type": "Follow-Up",
            "notes": "Acid reflux follow-up",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "c552f10c-3eb0-4f3d-b294-69735d607728",
            "provider_id": "b42f0f8e-9c40-460e-844a-d280012c4539",
            "appointment_time": "2025-06-02T10:00:00",
            "duration_minutes": 15
        },
        {
            "id": "1d40b8c7-cb1d-4c82-8b2b-7b5030b29d2c",
            "type": "Follow-Up",
            "notes": "Review of colonoscopy results",
            "status": "scheduled",
            "created_at": "2025-04-24T21:33:41.87287",
            "patient_id": "548e45c8-c0ea-4314-b94f-00fe822fe8c8",
            "provider_id": "1cb198af-6574-4f0a-a057-c24cdde69329",
            "appointment_time": "2025-06-03T10:00:00",
            "duration_minutes": 15
        }
    ]
}

# Mock Supabase client
class MockSupabaseTable:
    def __init__(self, table_name, data):
        self.table_name = table_name
        self.data = data
        self.filters = {}
        self.selected_fields = "*"
        
    def select(self, fields):
        self.selected_fields = fields
        return self
        
    def eq(self, field, value):
        if 'eq' not in self.filters:
            self.filters['eq'] = {}
        self.filters['eq'][field] = value
        return self
        
    def neq(self, field, value):
        if 'neq' not in self.filters:
            self.filters['neq'] = {}
        self.filters['neq'][field] = value
        return self
        
    def execute(self):
        filtered_data = self.data[:]
        
        # Apply eq filters
        if 'eq' in self.filters:
            for field, value in self.filters['eq'].items():
                filtered_data = [item for item in filtered_data if item.get(field) == value]
        
        # Apply neq filters
        if 'neq' in self.filters:
            for field, value in self.filters['neq'].items():
                filtered_data = [item for item in filtered_data if item.get(field) != value]
        
        # Reset filters for next query
        self.filters = {}
        
        return MockResponse(filtered_data)

class MockResponse:
    def __init__(self, data):
        self.data = data

class MockSupabaseClient:
    def __init__(self, mock_data):
        self.mock_data = mock_data
        
    def table(self, table_name):
        return MockSupabaseTable(table_name, self.mock_data.get(table_name, []))

# Mock wmill module
class MockWmill:
    @staticmethod
    def get_resource(resource_name):
        return {"url": "mock_url", "key": "mock_key"}

# Import and modify the original functions
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

def find_next_available_slot(
    supabase, 
    provider_id: str, 
    start_from: datetime, 
    duration_minutes: int,
    appointment_type: str,
    exclude_appointment_id: str = None,
    max_days_ahead: int = 30
) -> Optional[Dict]:
    """
    Find the next available appointment slot after the given datetime.
    """
    
    # Get provider's availability schedule
    availability_response = supabase.table("availability").select("*").eq("provider_id", provider_id).execute()
    
    if not availability_response.data:
        return None
    
    # Create a schedule map
    schedule = {}
    for avail in availability_response.data:
        weekday = avail["weekday"]
        schedule[weekday] = {
            "start_time": datetime.strptime(avail["start_time"], "%H:%M:%S").time(),
            "end_time": datetime.strptime(avail["end_time"], "%H:%M:%S").time()
        }
    
    # Search for next available slot
    # Ensure we don't search in the past
    now = datetime.now()
    search_start = max(start_from, now)
    current_date = search_start.date()
    end_date = current_date + timedelta(days=max_days_ahead)
    
    while current_date <= end_date:
        weekday = current_date.weekday() + 1  # Convert to 1-7 format
        
        if weekday in schedule:
            # Check slots throughout the day in 15-minute intervals
            day_schedule = schedule[weekday]
            
            # Start from the requested time if it's the same day, otherwise from start of working hours
            # Also ensure we don't start in the past
            if current_date == search_start.date():
                start_time = max(search_start.time(), day_schedule["start_time"])
            else:
                start_time = day_schedule["start_time"]
            
            # Create datetime objects for the current day
            current_slot = datetime.combine(current_date, start_time)
            end_of_day = datetime.combine(current_date, day_schedule["end_time"])
            
            # Round up to next 15-minute interval
            minutes = current_slot.minute
            if minutes % 15 != 0:
                next_quarter = ((minutes // 15) + 1) * 15
                if next_quarter >= 60:
                    current_slot = current_slot.replace(hour=current_slot.hour + 1, minute=0, second=0, microsecond=0)
                else:
                    current_slot = current_slot.replace(minute=next_quarter, second=0, microsecond=0)
            
            while current_slot + timedelta(minutes=duration_minutes) <= end_of_day:
                is_available, _ = check_time_availability(
                    supabase, provider_id, current_slot, duration_minutes, appointment_type, exclude_appointment_id
                )
                
                if is_available:
                    return {
                        "datetime": current_slot.isoformat(),
                        "formatted_datetime": current_slot.strftime("%Y-%m-%d at %I:%M %p"),
                        "date": current_slot.strftime("%Y-%m-%d"),
                        "time": current_slot.strftime("%H:%M"),
                        "weekday": current_slot.strftime("%A")
                    }
                
                # Move to next 15-minute slot
                current_slot += timedelta(minutes=15)
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return None

def main(appointment_id: str, preferred_datetime: str) -> Dict:
    """
    Test version of the main function with mock data
    """
    
    # Setup mock Supabase
    supabase = MockSupabaseClient(MOCK_DATA)
    
    try:
        # Step 2: Get the existing appointment details
        appointment_response = supabase.table("appointments").select("*").eq("id", appointment_id).execute()
        
        if not appointment_response.data:
            return {
                "success": False,
                "error": "Appointment not found",
                "available": False
            }
        
        appointment = appointment_response.data[0]
        provider_id = appointment["provider_id"]
        appointment_type = appointment["type"]
        duration_minutes = appointment["duration_minutes"]
        
        # Step 3: Parse preferred datetime
        try:
            preferred_dt = datetime.fromisoformat(preferred_datetime.replace('Z', '+00:00'))
        except ValueError:
            return {
                "success": False,
                "error": "Invalid datetime format. Use ISO format like '2025-06-10T14:00:00'",
                "available": False
            }
        
        # Step 3.5: Check if preferred datetime is in the past
        current_time = datetime.now()
        if preferred_dt <= current_time:
            return {
                "success": False,
                "error": f"Cannot schedule appointments in the past. Requested time: {preferred_datetime}, Current time: {current_time.isoformat()}",
                "available": False
            }
        
        # Step 4: Check if preferred time is available
        is_available, conflict_reason = check_time_availability(
            supabase, provider_id, preferred_dt, duration_minutes, appointment_type, appointment_id
        )
        
        if is_available:
            return {
                "success": True,
                "available": True,
                "preferred_datetime": preferred_datetime,
                "message": "Preferred time is available"
            }
        
        # Step 5: Find next available slot after preferred time
        next_available = find_next_available_slot(
            supabase, provider_id, preferred_dt, duration_minutes, appointment_type, appointment_id
        )
        
        return {
            "success": True,
            "available": False,
            "preferred_datetime": preferred_datetime,
            "conflict_reason": conflict_reason,
            "next_available": next_available,
            "message": f"Preferred time not available. {conflict_reason}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}",
            "available": False
        }

def run_tests():
    """Run various test scenarios"""
    
    print("=== APPOINTMENT AVAILABILITY TESTING ===\n")
    
    # Test Case 1: Try to reschedule to an available time
    print("Test 1: Reschedule to available time")
    print("Appointment: 55aab0ac-9249-48e0-a85c-6f1bdc4910ff (Dr. von Neeumann, Monday 9:00 AM)")
    print("Preferred: Monday 2025-06-09 at 11:00 AM")
    result1 = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", "2025-06-09T11:00:00")
    print(f"Result: {json.dumps(result1, indent=2)}\n")
    
    # Test Case 2: Try to reschedule to a conflicting time
    print("Test 2: Reschedule to conflicting time")
    print("Appointment: 55aab0ac-9249-48e0-a85c-6f1bdc4910ff (Dr. von Neeumann)")
    print("Preferred: Monday 2025-06-02 at 10:00 AM (conflicts with existing appointment)")
    result2 = main("55aab0ac-9249-48e0-a85c-6f1bdc4910ff", "2025-06-02T10:00:00")
    print(f"Result: {json.dumps(result2, indent=2)}\n")
    
    # Test Case 3: Try to reschedule outside working hours
    print("Test 3: Reschedule outside working hours")
    print("Appointment: 56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e (Dr. Euler, Tuesday)")
    print("Preferred: Tuesday 2025-06-10 at 8:00 AM (before working hours)")
    result3 = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-10T08:00:00")
    print(f"Result: {json.dumps(result3, indent=2)}\n")
    
    # Test Case 4: Try to reschedule on a day provider doesn't work
    print("Test 4: Reschedule on unavailable day")
    print("Appointment: 56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e (Dr. Euler)")
    print("Preferred: Wednesday 2025-06-11 at 10:00 AM (Dr. Euler doesn't work Wednesdays)")
    result4 = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-11T10:00:00")
    print(f"Result: {json.dumps(result4, indent=2)}\n")
    
    # Test Case 5: Invalid appointment ID
    print("Test 5: Invalid appointment ID")
    result5 = main("invalid-id", "2025-06-10T10:00:00")
    print(f"Result: {json.dumps(result5, indent=2)}\n")
    
    # Test Case 6: Available time that requires finding next slot
    print("Test 6: Find next available slot")
    print("Appointment: 56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e (Dr. Euler)")
    print("Preferred: Tuesday 2025-06-10 at 10:00 AM (might conflict)")
    result6 = main("56ce8f7b-0103-44c3-b0aa-8d46c8ebf63e", "2025-06-10T10:00:00")
    print(f"Result: {json.dumps(result6, indent=2)}\n")

if __name__ == "__main__":
    run_tests()