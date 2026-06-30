def calculate_rr(entry, sl, tp):

    entry = float(entry)

    risk = abs(entry - sl)

    reward = abs(tp - entry)

    if risk == 0:
        return 0

    return round(reward / risk, 2)