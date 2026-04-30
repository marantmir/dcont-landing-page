from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Product

router = APIRouter()

@router.get("/products")
def list_products(company_id: int = 1, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.company_id == company_id).limit(100).all()
    return [{"id": p.id, "sku": p.sku, "title": p.title, "price": float(p.price or 0), "cost": float(p.cost or 0)} for p in products]
