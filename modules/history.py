import json
from datetime import datetime

def save_trade(trade):
    with open("trade_history.json", "r") as file:
        history = json.load(file)

    trade["created_at"] = datetime.now().isoformat(timespec="seconds")
    history.append(trade)

    with open("trade_history.json", "w") as file:
        json.dump(history, file, indent=4)