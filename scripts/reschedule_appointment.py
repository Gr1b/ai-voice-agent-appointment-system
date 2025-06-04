import wmill
from supabase import create_client, Client
from datetime import datetime
from typing import Dict, Any

def main(appointment_id: str, new_datetime: str) -> Dict[str, Any]:
    """
    Reschedule an appointment to a new datetime.
    
    This function updates an existing appointment with a new datetime.
    It should be called after check_appointment_availability confirms the slot is available.
    
    Args:
        appointment_id (str): UUID of the appointment to reschedule
        new_datetime (str): New datetime in ISO format (e.g., "2025-06-10T10:00:00")
    
    Returns:
        Dict containing success status, updated appointment details, or error information
    """
    
    try:
        # Step 1: Setup Supabase
        config = wmill.get_resource("u/gregory/supabase")
        supabase: Client = create_client(config["url"], config["key"])
        
        # Step 2: Validate datetime format
        try:
            new_dt = datetime.fromisoformat(new_datetime.replace('Z', '+00:00'))
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid datetime format: {new_datetime}. Expected ISO format like '2025-06-10T10:00:00'",
                "appointment_id": appointment_id
            }
        
        # Step 3: Check if appointment exists and get current details
        appointment_response = supabase.table("appointments").select("*").eq("id", appointment_id).execute()
        
        if not appointment_response.data:
            return {
                "success": False,
                "error": "Appointment not found",
                "appointment_id": appointment_id
            }
        
        current_appointment = appointment_response.data[0]
        
        # Step 4: Validate appointment status (only reschedule scheduled appointments)
        if current_appointment.get("status", "").lower() != "scheduled":
            return {
                "success": False,
                "error": f"Cannot reschedule appointment with status: {current_appointment.get('status')}. Only 'scheduled' appointments can be rescheduled.",
                "appointment_id": appointment_id,
                "current_status": current_appointment.get("status")
            }
        
        # Step 5: Prevent scheduling in the past
        current_time = datetime.now()
        if new_dt <= current_time:
            return {
                "success": False,
                "error": f"Cannot schedule appointments in the past. Requested time: {new_datetime}, Current time: {current_time.isoformat()}",
                "appointment_id": appointment_id
            }
        
        # Step 6: Update the appointment
        update_data = {
            "appointment_time": new_datetime,
            "notes": f"{current_appointment.get('notes', '')} - Rescheduled on {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        update_response = supabase.table("appointments").update(update_data).eq("id", appointment_id).execute()
        
        if not update_response.data:
            return {
                "success": False,
                "error": "Failed to update appointment",
                "appointment_id": appointment_id
            }
        
        updated_appointment = update_response.data[0]
        
        # Step 7: Get additional details for response (patient and provider info)
        patient_response = supabase.table("patients").select("full_name, email, phone").eq("id", updated_appointment["patient_id"]).execute()
        provider_response = supabase.table("providers").select("full_name, specialty").eq("id", updated_appointment["provider_id"]).execute()
        
        patient_info = patient_response.data[0] if patient_response.data else {}
        provider_info = provider_response.data[0] if provider_response.data else {}
        
        # Step 8: Format the response
        old_datetime = datetime.fromisoformat(current_appointment["appointment_time"].replace('Z', '+00:00'))
        new_datetime_obj = datetime.fromisoformat(updated_appointment["appointment_time"].replace('Z', '+00:00'))
        
        return {
            "success": True,
            "message": "Appointment successfully rescheduled",
            "appointment_id": appointment_id,
            "patient": {
                "name": patient_info.get("full_name", "Unknown"),
                "email": patient_info.get("email", ""),
                "phone": patient_info.get("phone", "")
            },
            "provider": {
                "name": provider_info.get("full_name", "Unknown"),
                "specialty": provider_info.get("specialty", "")
            },
            "appointment_details": {
                "type": updated_appointment["type"],
                "duration_minutes": updated_appointment["duration_minutes"],
                "status": updated_appointment["status"],
                "notes": updated_appointment["notes"]
            },
            "schedule_change": {
                "old_datetime": old_datetime.isoformat(),
                "old_formatted": old_datetime.strftime("%Y-%m-%d at %I:%M %p"),
                "new_datetime": new_datetime_obj.isoformat(),
                "new_formatted": new_datetime_obj.strftime("%Y-%m-%d at %I:%M %p"),
                "new_date": new_datetime_obj.strftime("%Y-%m-%d"),
                "new_time": new_datetime_obj.strftime("%H:%M"),
                "new_weekday": new_datetime_obj.strftime("%A")
            },
            "rescheduled_at": current_time.isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred while rescheduling appointment: {str(e)}",
            "appointment_id": appointment_id
        }