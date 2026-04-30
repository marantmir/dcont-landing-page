from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def fiscal_health():
    return {"status": "Fiscal module ready", "next_steps": ["NF-e", "XML", "CFOP", "NCM", "regras tributárias"]}
