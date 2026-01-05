from pydantic import BaseModel
from typing import List, Dict

class RewardRequest(BaseModel):
    txn_id: str
    user_id: str
    merchant_id: str
    amount: float
    txn_type: str

class RewardResponse(BaseModel):
    decision_id: str
    policy_version: str
    reward_type: str
    reward_value: int
    xp: int
    reason_codes: List[str]
    meta: Dict

    #This two only for debegging 
    reward: Dict
    xp_info: Dict
