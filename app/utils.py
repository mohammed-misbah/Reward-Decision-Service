import hashlib

def deterministic_weighted_choice(weights: dict, seed: str) -> str:
    """
    Deterministic weighted (chance) choice based on hash.
    same seed => same result.
    """
    total = sum(weights.values())
    if total <= 0:
        return "XP"

    hash = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    point = (hash % 1000000) / 1000000 * total

    upto = 0
    for k, w in weights.items():
        upto += w
        if point <= upto:
            return k

    return "XP"
