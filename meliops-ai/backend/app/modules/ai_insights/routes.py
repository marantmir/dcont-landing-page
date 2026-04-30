from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models import Order, OrderItem, AIInsight

router = APIRouter()

@router.post("/generate-basic-insights")
def generate_basic_insights(company_id: int = 1, db: Session = Depends(get_db)):
    total_sales = db.query(func.coalesce(func.sum(Order.paid_amount), 0)).filter(Order.company_id == company_id).scalar() or 0
    total_fees = db.query(func.coalesce(func.sum(OrderItem.sale_fee), 0)).join(Order).filter(Order.company_id == company_id).scalar() or 0
    fee_rate = float(total_fees) / float(total_sales) if float(total_sales) > 0 else 0
    insights = []
    if fee_rate > 0.18:
        insights.append(AIInsight(company_id=company_id, insight_type="margin_alert", title="Taxas elevadas", description="As taxas estimadas estão acima de 18% da receita. Revise preço, frete e comissão por SKU.", severity="warning", payload={"fee_rate": fee_rate}))
    else:
        insights.append(AIInsight(company_id=company_id, insight_type="operation_summary", title="Operação monitorada", description="A operação já possui base para acompanhamento financeiro e comercial.", severity="info", payload={"fee_rate": fee_rate}))
    db.add_all(insights)
    db.commit()
    return {"created": len(insights), "fee_rate": fee_rate}

@router.get("/insights")
def list_insights(company_id: int = 1, db: Session = Depends(get_db)):
    rows = db.query(AIInsight).filter(AIInsight.company_id == company_id).order_by(AIInsight.created_at.desc()).limit(50).all()
    return [{"title": r.title, "description": r.description, "severity": r.severity, "created_at": r.created_at} for r in rows]
