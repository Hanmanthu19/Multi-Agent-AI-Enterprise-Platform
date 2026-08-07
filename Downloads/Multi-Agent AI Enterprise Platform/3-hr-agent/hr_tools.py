import time

HR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_hr_policy_rag",
            "description": "Queries ChromaDB for company HR policies, PTO limits, sick leave rules, and benefits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query regarding HR policies or PTO"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_hris_leave",
            "description": "Logs approved paid leave into the HRIS database (e.g. Workday/BambooHR).",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "number", "description": "Number of leave days requested"},
                    "leave_type": {"type": "string", "description": "Type of leave (Sick, Casual, Vacation)"},
                    "reason": {"type": "string", "description": "Brief description"}
                },
                "required": ["days", "leave_type", "reason"],
            },
        },
    }
]

def execute_hris_leave(days: float, leave_type: str, reason: str):
    """Simulates updating an HRIS record."""
    return {
        "status": "APPROVED_LOGGED",
        "hris_record_id": f"hris_pto_{int(time.time())}",
        "days_deducted": days,
        "leave_type": leave_type,
        "reason": reason
    }