PERSONA_MAP = {
    "u1": "NEW",
    "u2": "RETURNING",
    "u3": "POWER"
}

def get_persona(user_id: str) -> str:
    return PERSONA_MAP.get(user_id, "RETURNING")
