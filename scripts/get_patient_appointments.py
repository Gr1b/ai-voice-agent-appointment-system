import wmill
from supabase import create_client, Client
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

def main(patient_name: str, date_of_birth: str) -> Dict[str, Any]:
    """
    Retrieve upcoming appointments for a patient by name and date of birth.
    Returns data in AI-agent readable format with minimum necessary details.
    
    Args:
        patient_name (str): Full name of the patient (case-insensitive)
        date_of_birth (str): Date of birth in YYYY-MM-DD format
    
    Returns:
        Dict containing patient info and upcoming appointments in AI-readable format
    """
    
    try:
        # Step 1: Setup Supabase
        config = wmill.get_resource("u/gregory/supabase")
        supabase: Client = create_client(config["url"], config["key"])
        
        # Step 2: Validate date of birth format
        try:
            dob_date = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid date of birth format: {date_of_birth}. Expected YYYY-MM-DD format."
            }
        
        # Step 3: Find patient by name and DOB
        patient_response = supabase.table("patients").select("*").execute()
        
        if not patient_response.data:
            return {
                "success": False,
                "error": "No patients found in database"
            }
        
        # Find matching patient (case-insensitive name matching)
        matching_patient = None
        patient_name_lower = patient_name.lower().strip()
        
        for patient in patient_response.data:
            if (patient.get("full_name", "").lower().strip() == patient_name_lower and 
                patient.get("date_of_birth") == date_of_birth):
                matching_patient = patient
                break
        
        if not matching_patient:
            return {
                "success": False,
                "error": f"No patient found with name '{patient_name}' and date of birth '{date_of_birth}'"
            }
        
        # Step 4: Get upcoming appointments (scheduled status, future dates only)
        current_time = datetime.now()
        appointments_response = supabase.table("appointments").select("*").eq("patient_id", matching_patient["id"]).eq("status", "scheduled").execute()
        
        if not appointments_response.data:
            return {
                "success": True,
                "patient_found": True,
                "patient_name": matching_patient["full_name"],
                "upcoming_appointments": []
            }
        
        # Filter for future appointments and get provider details
        upcoming_appointments = []
        for appointment in appointments_response.data:
            appointment_time = datetime.fromisoformat(appointment["appointment_time"].replace('Z', '+00:00'))
            
            if appointment_time > current_time:
                # Get provider information
                provider_response = supabase.table("providers").select("full_name, specialty").eq("id", appointment["provider_id"]).execute()
                provider_info = provider_response.data[0] if provider_response.data else {}
                
                # Format appointment for AI agent
                formatted_appointment = {
                    "appointment_id": appointment["id"],
                    "date": appointment_time.strftime("%A, %B %d, %Y"),
                    "time": appointment_time.strftime("%I:%M %p"),
                    "datetime_iso": appointment["appointment_time"],
                    "provider_name": provider_info.get("full_name", "Unknown Provider"),
                    "provider_specialty": provider_info.get("specialty", ""),
                    "appointment_type": appointment["type"],
                    "duration_minutes": appointment["duration_minutes"],
                    "notes": appointment.get("notes", "")
                }
                upcoming_appointments.append(formatted_appointment)
        
        # Sort appointments by date
        upcoming_appointments.sort(key=lambda x: x["datetime_iso"])
        
        if not upcoming_appointments:
            return {
                "success": True,
                "patient_found": True,
                "patient_name": matching_patient["full_name"],
                "upcoming_appointments": []
            }
        
        # Step 5: Format response
        next_appointment = upcoming_appointments[0]
        
        return {
            "success": True,
            "patient_found": True,
            "patient_name": matching_patient["full_name"],
            "patient_phone": matching_patient.get("phone", ""),
            "patient_email": matching_patient.get("email", ""),
            "upcoming_appointments": upcoming_appointments,
            "next_appointment": next_appointment,
            "total_appointments": len(upcoming_appointments)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred while retrieving patient appointments: {str(e)}"
        }