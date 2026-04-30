import requests
from app.core.config import settings

MELI_API_BASE = "https://api.mercadolibre.com"

class MercadoLivreClient:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_user(self):
        response = requests.get(
            f"{MELI_API_BASE}/users/me",
            headers=self._headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_order(self, order_id: str):
        response = requests.get(
            f"{MELI_API_BASE}/orders/{order_id}",
            headers=self._headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_shipment(self, shipment_id: str):
        response = requests.get(
            f"{MELI_API_BASE}/shipments/{shipment_id}",
            headers=self._headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
