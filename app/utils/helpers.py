from typing import List, Dict, Any

def format_response_message(message: str, data: Any = None) -> Dict:
    """Format a consistent response message"""
    response = {"message": message}
    if data:
        response["data"] = data
    return response