import os
import json
import requests

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

WATCHLIST = "watchlist.txt"
TRIGGERED = "triggered.json"

API = "https://api.exchangerate.fun/latest?base=USD"


def telegram(msg):
    r = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg},
        timeout=10,
    )
    print(r.status_code, r.text)


def load_watchlist():
    pairs = []

    if not os.path.exists(WATCHLIST):
        return pairs

    with open(WATCHLIST, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            try:
                pair, target = line.split(",")
                pair = pair.strip().upper()
                target = float(target.strip())
                pairs.append((pair, target))
            except:
                pass

    return pairs


def load_triggered():
    if not os.path.exists(TRIGGERED):
        return {}

    with open(TRIGGERED, "r") as f:
        return json.load(f)


def save_triggered(data):
    with open(TRIGGERED, "w") as f:
        json.dump(data, f, indent=2)


def price(pair):
    base, quote = pair.split("/")

    r = requests.get(
        API,
        params={"base": base},
        timeout=10,
    )

    if r.status_code != 200:
        return None

    data = r.json()

    try:
        return float(data["rates"][quote])
    except:
        return None


def main():

    triggered = load_triggered()

    for pair, target in load_watchlist():

        key = f"{pair}_{target}"

        if key in triggered:
            continue

        p = price(pair)

        print(pair, "target:", target, "prezzo:", p)

        if p is None:
            continue

        if p >= target:

            telegram(
                f"🎯 TARGET RAGGIUNTO\n\n"
                f"{pair}\n"
                f"Target: {target}\n"
                f"Prezzo: {p}"
            )

            triggered[key] = True

    save_triggered(triggered)


if __name__ == "__main__":
    main()
