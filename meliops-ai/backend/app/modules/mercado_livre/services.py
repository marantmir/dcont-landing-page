from datetime import datetime, timedelta
import requests
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import encrypt_value, decrypt_value
from app.db.models import MarketplaceAccount, Order, OrderItem, FinancialEntry, SyncLog
from app.modules.mercado_livre.client import MercadoLivreClient

def exchange_code_for_token(code: str) -> dict:
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.meli_client_id,
        "client_secret": settings.meli_client_secret,
        "code": code,
        "redirect_uri": settings.meli_redirect_uri,
    }
    r = requests.post("https://api.mercadolibre.com/oauth/token", data=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def save_marketplace_account(db: Session, company_id: int, token_data: dict):
    client = MercadoLivreClient(token_data["access_token"])
    user = client.get_user()
    account = db.query(MarketplaceAccount).filter(
        MarketplaceAccount.company_id == company_id,
        MarketplaceAccount.seller_id == str(token_data["user_id"])
    ).first()
    expires_at = datetime.utcnow() + timedelta(seconds=int(token_data.get("expires_in", 0)))
    if not account:
        account = MarketplaceAccount(
            company_id=company_id,
            seller_id=str(token_data["user_id"]),
            nickname=user.get("nickname"),
            access_token_enc=encrypt_value(token_data["access_token"]),
            refresh_token_enc=encrypt_value(token_data["refresh_token"]),
            expires_at=expires_at,
        )
        db.add(account)
    else:
        account.access_token_enc = encrypt_value(token_data["access_token"])
        account.refresh_token_enc = encrypt_value(token_data["refresh_token"])
        account.expires_at = expires_at
        account.nickname = user.get("nickname")
    db.commit()
    return account

def normalize_order(order: dict) -> dict:
    return {
        "marketplace_order_id": str(order.get("id")),
        "status": order.get("status"),
        "buyer_id": str(order.get("buyer", {}).get("id")) if order.get("buyer") else None,
        "buyer_nickname": order.get("buyer", {}).get("nickname") if order.get("buyer") else None,
        "total_amount": order.get("total_amount") or 0,
        "paid_amount": order.get("paid_amount") or 0,
        "currency_id": order.get("currency_id"),
        "shipping_id": str(order.get("shipping", {}).get("id")) if order.get("shipping") else None,
        "date_created": parse_date(order.get("date_created")),
        "date_closed": parse_date(order.get("date_closed")),
        "raw_payload": order,
    }

def parse_date(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)

def upsert_order(db: Session, company_id: int, order_payload: dict):
    data = normalize_order(order_payload)
    order = db.query(Order).filter(
        Order.company_id == company_id,
        Order.marketplace_order_id == data["marketplace_order_id"]
    ).first()
    if not order:
        order = Order(company_id=company_id, **data)
        db.add(order)
        db.flush()
    else:
        for k, v in data.items():
            setattr(order, k, v)
        db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    for item in order_payload.get("order_items", []):
        item_data = item.get("item", {})
        db.add(OrderItem(
            order_id=order.id,
            marketplace_item_id=item_data.get("id"),
            sku=item_data.get("seller_sku"),
            title=item_data.get("title"),
            quantity=item.get("quantity", 1),
            unit_price=item.get("unit_price") or 0,
            sale_fee=item.get("sale_fee") or 0,
            raw_payload=item,
        ))
    db.add(FinancialEntry(
        company_id=company_id,
        order_id=order.id,
        type="receivable",
        description=f"Venda Mercado Livre pedido {order.marketplace_order_id}",
        amount=data["paid_amount"] or data["total_amount"] or 0,
        status="pending",
        raw_payload=order_payload,
    ))
    db.commit()
    return order

def sync_orders(db: Session, account: MarketplaceAccount, limit: int = 50):
    token = decrypt_value(account.access_token_enc)
    client = MercadoLivreClient(token)
    result = client.get_orders_by_seller(account.seller_id, limit=limit)
    count = 0
    for order_summary in result.get("results", []):
        order = client.get_order(str(order_summary.get("id")))
        upsert_order(db, account.company_id, order)
        count += 1
    db.add(SyncLog(company_id=account.company_id, source="mercado_livre", entity="orders", status="success", message=f"{count} pedidos sincronizados"))
    db.commit()
    return {"synced": count}
