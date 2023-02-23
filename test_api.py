import unittest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


class TestConversionEndpoint(unittest.TestCase):
    def test_conversion(self):
        response = client.get(
            "/convert?value=50&currency=EUR&target_currency=USD&date=2022-02-18&source=freecurrencyapi")
        self.assertEqual(response.status_code, 200)
        expected_response = {
            "value": 50.0,
            "currency": "EUR",
            "target_currency": "USD",
            "converted_value": 56.61167785690832
        }
        self.assertEqual(response.json(), expected_response)

    def test_conversion_currency_not_exists(self):
        response = client.get(
            "/convert?value=50&currency=BKKD&target_currency=USD&date=2022-02-18&source=freecurrencyapi")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "error": "Exchange rate not found for the specified date and currency."
        })
