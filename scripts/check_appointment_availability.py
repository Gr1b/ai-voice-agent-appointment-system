import wmill
from supabase import create_client, Client
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

def main(appointment_id: str, preferred_datetime: str) -> Dict:
    """
    Check appointment availability for rescheduling.
    
    Args:
        appointment_id: ID of the appointment to reschedule
        preferred_datetime: Preferred new datetime in ISO format (e.g., "2025-06-10T14:00:00")
    
    Returns:
        Dict with availability status and alternative suggestions
    """
    
    # Step 1: Setup Supabase
    config = wmill.get_resource("u/gregory/supabase")
    supabase: Client = create_client(config["url"], config["key"])
    
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

def check_time_availability(
    supabase: Client, 
    provider_id: str, 
    requested_dt: datetime, 
    duration_minutes: int,
    appointment_type: str,
    exclude_appointment_id: str = None
) -> Tuple[bool, str]:
    """
    Check if a specific time slot is available for a provider.
    
    Returns:
        Tuple of (is_available, reason_if_not_available)
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
    supabase: Client, 
    provider_id: str, 
    start_from: datetime, 
    duration_minutes: int,
    appointment_type: str,
    exclude_appointment_id: str = None,
    max_days_ahead: int = 30
) -> Optional[Dict]:
    """
    Find the next available appointment slot after the given datetime.
    
    Returns:
        Dict with next available slot info or None if no slot found
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