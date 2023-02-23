import fastapi
import sqlite3

app = fastapi.FastAPI()


@app.get("/convert")
def convert(value: float, currency: str, target_currency: str, date: str, source: str):
    conn = sqlite3.connect('exchange_rates.db')
    query = f"SELECT rate FROM exchange_rates WHERE date='{date}' AND currency='{currency}' AND source='{source}'"
    result = conn.execute(query).fetchone()
    if result is None:
        return {"error": "Exchange rate not found for the specified date and currency."}
    rate = result[0]
    query = f"SELECT rate FROM exchange_rates WHERE date='{date}' " \
            f"AND currency='{target_currency}' AND source='{source}'"
    result = conn.execute(query).fetchone()
    if result is None:
        return {"error": "Exchange rate not found for the specified date and target currency."}
    target_rate = result[0]
    conn.close()
    converted_value = value / rate * target_rate
    return {"value": value, "currency": currency, "target_currency": target_currency,
            "converted_value": converted_value}
