import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from environs import Env

env = Env()
env.read_env()

APIKEY = env.str("APIKEY")


def get_exchange_rates(source, date_from, base_currency='EUR'):
    """
    Downloads exchange rate data from a specified source and returns it as a Pandas DataFrame.

    Parameters:
    source (str): The source of the exchange rate data. Can be 'freecurrencyapi' or 'ecb'.

    Returns:
    df (pd.DataFrame): A DataFrame containing the exchange rates.

    Raises:
    ValueError: If an unknown exchange rate source is provided.
    """

    # Define the API URL for the specified source
    if source == 'freecurrencyapi':
        api_url = f'https://api.freecurrencyapi.com/v1/historical?apikey={APIKEY}&' \
                  f'base_currency={base_currency}&date_from={date_from}&date_to={date_from}'
        source_name = 'freecurrencyapi'
    elif source == 'ecb':
        api_url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml?ec753c46f8ac370650a1e9f44584d93b'
        source_name = 'ecb'
    else:
        raise ValueError(f"Unknown exchange rate source: {source}")

    # Send a GET request to the API URL and return the response data as a DataFrame
    response = requests.get(api_url)

    if source == 'freecurrencyapi':
        data = response.json()
        rates = {date: {currency: rate for currency, rate in rates.items()} for date, rates in data['data'].items()}
        dfs = [pd.DataFrame.from_dict(rates, orient='index').reset_index().rename(columns={'index': 'date'}) for rates
               in rates.values()]
        df = pd.concat(dfs)
        df = df.rename(columns={'date': 'currency', 0: 'rate'})

    # If the source is ecb, extract the exchange rate data from the response HTML
    elif source == 'ecb':
        soup = BeautifulSoup(response.content, 'lxml-xml')
        rates = []
        for cube in soup.find_all('Cube'):
            if cube.has_attr('time') and cube['time'] == date_from:
                for c in cube.find_all('Cube'):
                    rates.append({'currency': c['currency'], 'rate': c['rate']})
                break
        if not rates:
            # If no exchange rate data is available for the requested date, subtract 1 day and try again
            new_date_from = (datetime.strptime(date_from, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            return get_exchange_rates(source, new_date_from)
        df = pd.DataFrame(rates)
    else:
        raise ValueError(f"Unknown exchange rate source: {source}")

    df['source'] = source_name
    df['date'] = date_from

    # Connect to SQLite database
    conn = sqlite3.connect('exchange_rates.db')

    # Create table if it doesn't exist
    conn.execute('''CREATE TABLE IF NOT EXISTS exchange_rates
                        (currency text, rate real, source text, date text, UNIQUE(currency, source, rate, date))''')

    # Insert data into the table
    for index, row in df.iterrows():
        conn.execute("""
            INSERT INTO exchange_rates (currency, rate, source, date) 
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM exchange_rates 
                WHERE currency = ? AND rate = ? AND source = ? AND date = ?
            )
        """, (row['currency'], row['rate'], row['source'], row['date'], row['currency'], row['rate'], row['source'],
              row['date']))

    # Commit changes and close connection
    conn.commit()

    # Print the result to test get_exchange_rates func. (Uncomment)
    # show = pd.read_sql_query('SELECT * FROM exchange_rates', conn)
    # print(show)

    conn.close()

    return df


def validate_data():
    """
    Function validate data for seven days, but firstly data need to be inserted into database running
    get_exchange_rates function with correct dates (from last seven days).
    """
    # Connect to SQLite database
    conn = sqlite3.connect('exchange_rates.db')

    # Get the date 7 days ago
    date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Execute a SELECT statement to retrieve data for the last 7 days
    query = f"SELECT * FROM exchange_rates WHERE date >= '{date}'"
    result = conn.execute(query).fetchall()

    # Print the result to test validate_data func output in terminal. (Uncomment)
    # print(result)

    # Close the database connection
    conn.close()


if __name__ == '__main__':
    get_exchange_rates('freecurrencyapi', '2022-10-18', 'USD')
    get_exchange_rates('freecurrencyapi', '2022-10-18', 'EUR')
    validate_data()
