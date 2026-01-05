import uuid
from time import time
from datetime import date, datetime
from fastapi import HTTPException, status
from app.cache import get, set
from app.persona import get_persona
from app.policy import calculate_xp, POLICY
from app.utils import deterministic_weighted_choice


def decide_reward(req):
    #idem-key check the cache before do anything, it prevents a double reward or payment
    idem_key = f"idem:{req.txn_id}:{req.user_id}:{req.merchant_id}" 
    idem_ttl = POLICY["idempotency"]["ttl_seconds"] #timetolive expire time

    cached = get(idem_key)
    if cached:
        return cached
    
    # same txn always produces the same decision_id
    raw = f"{req.txn_id}:{req.user_id}:{req.merchant_id}"
    decision_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw))

    #allowed transaction types
    allowed_txn_types = POLICY["transactions"]["allowed_types"]

    if req.txn_type not in allowed_txn_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported transaction type")
    
    try:
        txn_time = datetime.fromisoformat(req.ts.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid timestamp format."
        )
    
    # Reject future-dated transactions
    if txn_time.timestamp() > time():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction timestamp cannot be in the future")

    #System checks what type of user this is (new, old, heavy)
    persona_key = f"persona:{req.user_id}"
    persona = get(persona_key)
    if not persona:
        persona = get_persona(req.user_id)
        set(persona_key, persona, idem_ttl) #persona cache vldty

    #XP calculation   
    xp = calculate_xp(req.amount, persona)

    # Cooldown check: block rewards if user received a rwd recently
    last_reward_key = f"last_reward:{req.user_id}"
    last_reward_ts = get(last_reward_key)

    cooldown_seconds = POLICY["cooldown"]["reward_seconds"]
    now = time()

    cooldown_active = False
    if last_reward_ts:
        if now - last_reward_ts < cooldown_seconds:
            cooldown_active = True
    
    #CAC(Cash rwd's)
    cac_key = f"cac:{req.user_id}:{date.today()}" #how much rwd earn today
    spent = get(cac_key) or 0                     #today's total rwd given
    cap = POLICY["daily_cac_cap"][persona]        #max allowed rwd
    rate = POLICY["checkout"]["cashback_percent"]

    #GOLD chance calculation
    weights = POLICY["reward_weights"]
    seed = f"{req.txn_id}:{req.user_id}:{req.merchant_id}"
    selected_reward = deterministic_weighted_choice(weights, seed)

    #make XP only rwd
    prefer_xp = POLICY["feature_flags"].get("prefer_xp", False)

    #Reward Decision
    if cooldown_active:
        # Cooldown active No reward
        reward_type = "XP"
        reward_value = 0

    elif prefer_xp:
        reward_type = "XP"
        reward_value = 0

    elif selected_reward == "GOLD" and persona == "POWER":
        reward_type = "GOLD"
        reward_value = 0

    elif spent < cap:
        reward_type = "CHECKOUT"
        reward_value = min(int(req.amount * rate), cap - spent)
        set(cac_key, spent + reward_value, idem_ttl)

    else:
        reward_type = "XP"
        reward_value = 0
    
    remaining_cap = max(0, cap - (spent + reward_value))

    response = {
        "decision_id": decision_id,
        "policy_version": POLICY["policy_version"],
        "reward_type": reward_type,
        "reward_value": reward_value,
        "xp": xp,
        "reward": {
            "type": reward_type,
            "value": reward_value,
            "daily_cap": cap,
            "remaining_today": remaining_cap,
        },
        "xp_info": {
            "earned": xp,
            "max_per_txn": POLICY["xp"]["max_xp_per_txn"],
            "rate": f'{POLICY["xp"]["xp_per_rupee"]} XP per ₹',
            "was_capped": xp == POLICY["xp"]["max_xp_per_txn"],
        },
        "reason_codes": [],
        "meta": {
            "persona": persona,
            "cooldown_active": cooldown_active,
        }   
    }

    set(idem_key, response, idem_ttl)

    #update last reward only if real reward is given
    if reward_type != "XP":
        set(f"last_reward:{req.user_id}", now, cooldown_seconds)

    return response
