from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Company, User
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth.schemas import RegisterRequest, LoginRequest

router = APIRouter()

@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    company = Company(name=payload.company_name, document=payload.document)
    db.add(company)
    db.flush()
    user = User(
        company_id=company.id,
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="admin"
    )
    db.add(user)
    db.commit()
    token = create_access_token(str(user.id), company.id)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.active == True).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_access_token(str(user.id), user.company_id)
    return {"access_token": token, "token_type": "bearer"}
