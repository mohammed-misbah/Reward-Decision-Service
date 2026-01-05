import time
from types import SimpleNamespace
from app.service import decide_reward
from app.cache import clear_cache

#Helpers

def make_request(
    txn_id="txn1",
    user_id="3",
    merchant_id="m1",
    amount=500,
    txn_type="UPI"
):
    return SimpleNamespace(
        txn_id=txn_id,
        user_id=user_id,
        merchant_id=merchant_id,
        amount=amount,
        txn_type=txn_type,
        ts=time.strftime("%Y-%m-%dT%H:%M:%S")
    )

def setup_function():
    # clear in memory cache before each test
    clear_cache()

# Reward logic test

def test_reward_decision_basic():
    req = make_request()
    response = decide_reward(req)

    assert response["decision_id"] is not None
    assert response["reward_type"] in ["CHECKOUT", "XP", "GOLD"]
    assert response["xp"] >= 0

#Idempotency Test

def test_idempotency_same_request_returns_same_response():
    req = make_request(txn_id="txn-idem")

    res1 = decide_reward(req)
    res2 = decide_reward(req)

    assert res1 == res2


#CAC Cap Test

def test_cac_cap_enforced():
    req = make_request(
        txn_id="txn-cac-1",
        user_id="u3",  # POWER user has very low cap
        amount=1000
    )

    # First reward (may give CHECKOUT)
    decide_reward(req)

    # Second transaction (new txn_id but same user)
    req2 = make_request(
        txn_id="txn-cac-2",
        user_id="u3",
        amount=1000
    )

    response = decide_reward(req2)

    assert response["reward_type"] == "XP"
    assert response["reward_value"] == 0





#Cooldown

def test_cooldown_blocks_second_reward():
    # First transaction → real reward
    req1 = make_request(txn_id="cooldown-1")
    res1 = decide_reward(req1)

    assert res1["reward_type"] in ["CHECKOUT", "GOLD"]

    # Immediate second transaction → should hit cooldown
    req2 = make_request(txn_id="cooldown-2")
    res2 = decide_reward(req2)

    assert res2["reward_type"] == "XP"
    assert res2["reward_value"] == 0
    assert res2["meta"]["cooldown_active"] is True


#Gold Reward

def test_gold_reward_is_deterministic():
    req = make_request(
        txn_id="gold-deterministic",
        user_id="u3"  # POWER user (eligible for GOLD)
    )

    res1 = decide_reward(req)
    clear_cache()
    res2 = decide_reward(req)

    assert res1["reward_type"] == res2["reward_type"]


#Redis vs Memory test

def test_idempotency_works_with_cache_backend():
    req = make_request(txn_id="cache-backend-test")

    res1 = decide_reward(req)
    res2 = decide_reward(req)

    assert res1 == res2
