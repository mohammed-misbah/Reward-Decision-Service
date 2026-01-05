from fastapi import APIRouter
from app.schemas import RewardRequest, RewardResponse
from app.service import decide_reward

router = APIRouter()

@router.post("/reward/decide", response_model=RewardResponse)

def decide(req: RewardRequest):
    return decide_reward(req)
