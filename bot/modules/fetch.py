import random

async def fetch_price(pair: str = "EURUSD") -> float:
    # Később ide jön az éles API-hívás (pl. Interactive Brokers vagy AlphaVantage)
    return round(1.05 + random.uniform(-0.01, 0.01), 5)
