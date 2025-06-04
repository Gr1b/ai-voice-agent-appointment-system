# AI Voice Agent Appointment Scheduling Backend

This repository contains Python backend scripts for Windmill that handle appointment availability checking and rescheduling for an AI voice agent system. The scripts integrate with Supabase and include comprehensive visit type management and patient capacity controls.

## 📁 Project Structure

```
├── scripts/                          # Main Windmill scripts
│   ├── get_patient_appointments.py   # n5: Patient lookup by name/DOB
│   ├── check_appointment_availability.py # n7: Check time availability
│   └── reschedule_appointment.py     # n8: Reschedule appointments
├── tests/                            # Comprehensive test suite
│   ├── test_get_patient_appointments.py
│   ├── test_appointment_availability.py
│   ├── test_reschedule_appointment.py
│   ├── test_complete_functionality.py
│   └── test_full_ai_agent_workflow.py
├── docs/                             # Documentation
│   ├── COMPLETION_SUMMARY.md
│   └── FINAL_VALIDATION_SUMMARY.md
├── requirements.txt                  # Python dependencies
├── LICENSE                          # MIT License
└── README.md                        # This file
```

## Scripts Overview

### 1. `get_patient_appointments.py` (n5)
Retrieves patient appointments by name and date of birth, presenting data in AI-agent readable format.

### 2. `check_appointment_availability.py` (n7)
Checks if a preferred appointment time is available and suggests alternatives if not.

### 3. `reschedule_appointment.py` (n8)
Actually reschedules an appointment to a new datetime after availability has been confirmed.

## Features

### Core Functionality
- ✅ **Patient Identification**: Finds patients by name and date of birth with fuzzy matching
- ✅ **Appointment Retrieval**: Gets upcoming appointments with provider details
- ✅ **Structured Data Format**: Presents data in clean format for AI agent processing
- ✅ **Appointment Validation**: Validates existing appointments before rescheduling
- ✅ **Time Availability Checking**: Checks provider schedules and working hours
- ✅ **Conflict Detection**: Prevents double-booking and overlapping appointments
- ✅ **Next Available Slot Finding**: Suggests alternative times when preferred slot is unavailable
- ✅ **Past Date Validation**: Prevents scheduling appointments in the past

### Visit Type Management
- ✅ **Visit Type Validation**: Validates appointment types against the visit_types table
- ✅ **Maximum Patients Per Slot**: Enforces capacity limits based on visit type
- ✅ **Multiple Patients Same Time**: Allows multiple Follow-Up patients at same time (max 2)
- ✅ **Single Patient Restriction**: Enforces single patient limit for New Patient appointments
- ✅ **Intelligent Conflict Resolution**: Distinguishes between exact time matches and overlapping conflicts

## Database Schema

The system works with the following Supabase tables:

### visit_types
```json
{
  "id": "uuid",
  "name": "string",
  "max_patients_per_slot": "integer",
  "default_duration_minutes": "integer"
}
```

### providers
```json
{
  "id": "uuid",
  "role": "string",
  "full_name": "string",
  "specialty": "string",
  "created_at": "timestamp"
}
```

### patients
```json
{
  "id": "uuid",
  "email": "string",
  "phone": "string",
  "full_name": "string",
  "date_of_birth": "date",
  "created_at": "timestamp"
}
```

### availability
```json
{
  "id": "uuid",
  "provider_id": "uuid",
  "weekday": "integer",
  "start_time": "time",
  "end_time": "time",
  "created_at": "timestamp"
}
```

### appointments
```json
{
  "id": "uuid",
  "patient_id": "uuid",
  "provider_id": "uuid",
  "appointment_time": "timestamp",
  "duration_minutes": "integer",
  "type": "string",
  "status": "string",
  "notes": "string",
  "created_at": "timestamp"
}
```

## Usage

### Script 1: Get Patient Appointments (n5)

#### Function Signature
```python
def main(patient_name: str, date_of_birth: str) -> dict:
```

#### Parameters
- `patient_name`: Full name of the patient (case-insensitive)
- `date_of_birth`: Date of birth in YYYY-MM-DD format

#### Return Format
```python
{
    "success": bool,
    "patient_found": bool,
    "patient_name": str,
    "patient_phone": str,
    "patient_email": str,
    "upcoming_appointments": [
        {
            "appointment_id": str,
            "date": str,  # "Monday, June 10, 2025"
            "time": str,  # "10:00 AM"
            "datetime_iso": str,
            "provider_name": str,
            "provider_specialty": str,
            "appointment_type": str,
            "duration_minutes": int,
            "notes": str
        }
    ],
    "next_appointment": dict,  # Same structure as appointment above
    "total_appointments": int,
    "error": str  # if error occurred
}
```

### Script 2: Check Appointment Availability (n7)

#### Function Signature
```python
def main(appointment_id: str, preferred_datetime: str) -> dict:
```

#### Parameters
- `appointment_id`: UUID of the existing appointment to reschedule
- `preferred_datetime`: ISO format datetime string (e.g., "2025-06-10T10:00:00")

#### Return Format
```python
{
    "success": bool,
    "available": bool,
    "preferred_datetime": str,
    "message": str,
    "conflict_reason": str,  # if not available
    "next_available": {     # if not available
        "datetime": str,
        "formatted_datetime": str,
        "date": str,
        "time": str,
        "weekday": str
    },
    "error": str  # if error occurred
}
```

### Script 3: Reschedule Appointment (n8)

#### Function Signature
```python
def main(appointment_id: str, new_datetime: str) -> dict:
```

#### Parameters
- `appointment_id`: UUID of the existing appointment to reschedule
- `new_datetime`: ISO format datetime string (e.g., "2025-06-10T10:00:00")

#### Return Format
```python
{
    "success": bool,
    "message": str,
    "appointment_id": str,
    "patient": {
        "name": str,
        "email": str,
        "phone": str
    },
    "provider": {
        "name": str,
        "specialty": str
    },
    "appointment_details": {
        "type": str,
        "duration_minutes": int,
        "status": str,
        "notes": str
    },
    "schedule_change": {
        "old_datetime": str,
        "old_formatted": str,
        "new_datetime": str,
        "new_formatted": str,
        "new_date": str,
        "new_time": str,
        "new_weekday": str
    },
    "rescheduled_at": str,
    "error": str  # if error occurred
}
```

## Examples

### Complete Workflow Example

#### Step 1: Get Patient Appointments (n5)
```python
# Get patient's upcoming appointments
patient_result = get_patient_appointments("John Doe", "1985-06-15")

# Example response:
{
    "success": True,
    "patient_found": True,
    "patient_name": "John Doe",
    "upcoming_appointments": [...],
    "next_appointment": {
        "appointment_id": "appointment-uuid",
        "date": "Tuesday, June 17, 2025",
        "time": "10:00 AM",
        ...
    }
}
```

#### Step 2: Check Availability (n7)
```python
# Check if preferred time is available
availability_result = check_appointment_availability("appointment-uuid", "2025-06-10T10:00:00")

# If available:
{
    "success": True,
    "available": True,
    "preferred_datetime": "2025-06-10T10:00:00",
    "message": "Preferred time is available"
}

# If not available:
{
    "success": True,
    "available": False,
    "preferred_datetime": "2025-06-10T10:00:00",
    "conflict_reason": "Time slot full: 2/2 patients already scheduled at 2025-06-10 10:00",
    "next_available": {
        "datetime": "2025-06-10T10:15:00",
        "formatted_datetime": "2025-06-10 at 10:15 AM",
        "date": "2025-06-10",
        "time": "10:15",
        "weekday": "Tuesday"
    },
    "message": "Preferred time not available. Time slot full: 2/2 patients already scheduled at 2025-06-10 10:00"
}
```

#### Step 3: Reschedule Appointment (n8)
```python
# If availability check passed, reschedule the appointment
reschedule_result = reschedule_appointment("appointment-uuid", "2025-06-10T10:00:00")

# Success response:
{
    "success": True,
    "message": "Appointment successfully rescheduled",
    "appointment_id": "appointment-uuid",
    "patient": {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "555-234-5678"
    },
    "provider": {
        "name": "Dr. Leonhard Euler",
        "specialty": "Family Medicine"
    },
    "appointment_details": {
        "type": "Follow-Up",
        "duration_minutes": 15,
        "status": "scheduled",
        "notes": "Patient wants to reschedule - Rescheduled on 2025-06-04 21:21:24"
    },
    "schedule_change": {
        "old_datetime": "2025-06-17T10:00:00",
        "old_formatted": "2025-06-17 at 10:00 AM",
        "new_datetime": "2025-06-10T10:00:00",
        "new_formatted": "2025-06-10 at 10:00 AM",
        "new_date": "2025-06-10",
        "new_time": "10:00",
        "new_weekday": "Tuesday"
    },
    "rescheduled_at": "2025-06-04T21:21:24.318110"
}
```

## Visit Type Logic

### Follow-Up Appointments
- **Maximum Patients**: 2 per time slot
- **Duration**: 15 minutes (default)
- **Behavior**: Multiple patients can be scheduled at the exact same time

### New Patient Appointments
- **Maximum Patients**: 1 per time slot
- **Duration**: 30 minutes (default)
- **Behavior**: Exclusive time slot, no other appointments allowed

### Conflict Resolution
1. **Exact Time Match**: Checks if adding another patient exceeds the visit type's maximum
2. **Overlapping Time**: Traditional conflict detection for different start times
3. **Rescheduling**: Excludes the appointment being rescheduled from conflict checks

## Testing

The repository includes comprehensive test suites:

### Patient Appointment Retrieval Tests
```bash
python test_get_patient_appointments.py
```

### Availability Checking Tests
```bash
python test_appointment_availability.py
```

### Visit Type Specific Tests
```bash
python test_visit_types.py
```

### Rescheduling Tests
```bash
python test_reschedule_appointment.py
```

### Complete System Tests
```bash
python test_complete_functionality.py
```

### Full Workflow Integration Tests
```bash
python test_complete_workflow.py
```

### Complete AI Voice Agent Simulation
```bash
python test_full_ai_agent_workflow.py
```

## AI Voice Agent Integration

These backend scripts are designed to support the following AI voice agent workflow:

1. **Inbound Call Handling**: Agent answers and asks what the patient needs
2. **Rescheduling Detection**: If it's a rescheduling request, continues; otherwise ends call
3. **Patient Identification**: Asks for name and DOB to find patient in DB
4. **Appointment Retrieval**: Uses `get_patient_appointments.py` (n5) to get upcoming appointment details
5. **Preferred Time Collection**: Asks for preferred new time
6. **Availability Check**: Uses `check_appointment_availability.py` (n7) to check availability and conflicts
7. **Confirmation**: Confirms availability or suggests alternatives
8. **Database Update**: Uses `reschedule_appointment.py` (n8) to update the appointment in the database

### Workflow Integration
```python
# AI Voice Agent Workflow Implementation
def handle_rescheduling_request(patient_name, date_of_birth, preferred_time):
    # Step 1: Get patient appointments
    patient_info = get_patient_appointments(patient_name, date_of_birth)
    
    if not patient_info["success"]:
        return f"I couldn't find your information in our system: {patient_info['error']}"
    
    if not patient_info["upcoming_appointments"]:
        return f"Hi {patient_info['patient_name']}, I don't see any upcoming appointments for you."
    
    # Step 2: Get the appointment to reschedule
    appointment_id = patient_info["next_appointment"]["appointment_id"]
    
    # Step 3: Check if preferred time is available
    availability = check_appointment_availability(appointment_id, preferred_time)
    
    if availability["success"] and availability["available"]:
        # Step 4: Reschedule to preferred time
        result = reschedule_appointment(appointment_id, preferred_time)
        return f"Great! I've rescheduled your appointment to {result['schedule_change']['new_formatted']}"
    
    elif availability["success"] and not availability["available"]:
        # Step 5: Offer alternative
        next_slot = availability["next_available"]
        # AI agent asks: "That time isn't available. How about {next_slot['formatted_datetime']}?"
        # If patient agrees, reschedule to alternative
        result = reschedule_appointment(appointment_id, next_slot["datetime"])
        return f"Perfect! I've scheduled you for {result['schedule_change']['new_formatted']}"
    
    else:
        # Step 6: Handle errors gracefully
        return "I'm having trouble with your request. Let me transfer you to a human agent."
```

## Configuration

All scripts expect a Windmill resource named `u/gregory/supabase` with:
```json
{
    "url": "your-supabase-url",
    "key": "your-supabase-anon-key"
}
```

## Error Handling

The scripts handle various error scenarios:
- Invalid appointment IDs
- Past date scheduling attempts
- Provider unavailability
- Invalid visit types
- Database connection issues
- Malformed datetime inputs
- Appointment status validation (only scheduled appointments can be rescheduled)
- Visit type capacity enforcement

## Dependencies

- `wmill`: Windmill integration
- `supabase`: Supabase Python client
- `datetime`: Date and time handling
- `typing`: Type hints

## Files in Repository

### Core Scripts
- `get_patient_appointments.py` - Patient appointment retrieval (n5)
- `check_appointment_availability.py` - Availability checking (n7)
- `reschedule_appointment.py` - Appointment rescheduling (n8)

### Test Files
- `test_get_patient_appointments.py` - Patient appointment retrieval tests
- `test_appointment_availability.py` - Basic availability tests
- `test_visit_types.py` - Visit type specific tests
- `test_reschedule_appointment.py` - Rescheduling functionality tests
- `test_complete_functionality.py` - Complete system tests
- `test_complete_workflow.py` - Full workflow integration tests
- `test_full_ai_agent_workflow.py` - Complete AI voice agent simulation

### Documentation
- `README.md` - This documentation file

## License

This code is designed for use with Prosper AI voice agent systems and Windmill workflow automation.