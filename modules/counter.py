def get_next_trade_number():
    with open("trade_counter.txt", "r") as file:
        current = int(file.read().strip())

    next_number = current + 1

    with open("trade_counter.txt", "w") as file:
        file.write(str(next_number))

    return f"#{next_number:03d}"