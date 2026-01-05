import hashlib

def deterministic_weighted_choice(weights: dict, seed: str) -> str:
    """
    Deterministic weighted choice based on hash.
    Same seed => same result.
    """
    total = sum(weights.values())
    if total <= 0:
        return "XP"

    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    print("haaaaaash h:", h)
    point = (h % 1000000) / 1000000 * total

    print("hhhashlib point:",  point)

    upto = 0
    for k, w in weights.items():
        upto += w
        if point <= upto:
            return k

    return "XP"
