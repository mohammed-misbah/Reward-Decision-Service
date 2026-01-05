import yaml

with open("config/policy.yaml") as f:
    POLICY = yaml.safe_load(f)

def calculate_xp(amount, persona):
    base = amount * POLICY["xp"]["xp_per_rupee"]
    multiplier = POLICY["persona_multiplier"][persona]
    return min(int(base * multiplier), POLICY["xp"]["max_xp_per_txn"])







# xp = min(amount * xp_per_rupee * persona_multiplier, max_xp_per_txn)
# amount = 500
# xp_per_rupee = 1
# persona_multiplier = new_usr_xp =1.5, old_usr_xp=1, heavy_usr_xp=0.5
# max_xp_per_txn = 700 #limit


# xp_new_usr = 500 * 1 * 1.5 
# xp_new_usr = 750

# #final xp amount is
# xp_new_usr = 700 #because limit is 700 can't cross predefined xp
