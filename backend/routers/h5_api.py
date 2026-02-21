import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import bcrypt
import jwt

from database import get_db
import models
from services.search_service import search_book_info
from services.llm_service import generate_mindmap_markdown
from services.document_service import generate_mindmap_document

router = APIRouter(prefix="/api/h5", tags=["H5 Mini-Program"])

SECRET_KEY = "h5_super_secret_key"
ALGORITHM = "HS256"

# -- Schemas --
class AuthRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    message: str

class UserInfoResponse(BaseModel):
    username: str
    generate_quota: int
    daily_free_used: int
    daily_free_total: int = 5

class PayRequest(BaseModel):
    amount_rmb: int = 5

class H5GenerateMindmapRequest(BaseModel):
    book_title: str

class H5GenerateMindmapResponse(BaseModel):
    pdf_url: str
    message: str
    quota_used: str

# -- Auth Utilities --
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

# -- Endpoints --
@router.post("/register", response_model=TokenResponse)
def register(req: AuthRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed = get_password_hash(req.password)
    user = models.User(username=req.username, hashed_password=hashed, generate_quota=0)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "message": "Registered successfully"}

@router.post("/login", response_model=TokenResponse)
def login(req: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "message": "Logged in successfully"}

@router.get("/me", response_model=UserInfoResponse)
def get_me(request: Request, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    ip = get_ip(request)
    today = datetime.date.today()
    ip_log = db.query(models.IPLog).filter(models.IPLog.ip_address == ip, models.IPLog.date == today).first()
    used = ip_log.usage_count if ip_log else 0

    return {
        "username": user.username,
        "generate_quota": user.generate_quota,
        "daily_free_used": used,
        "daily_free_total": 5
    }

@router.post("/pay")
def mock_pay(req: PayRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Mock payment logic: 5 RMB = 10 quota
    if req.amount_rmb != 5:
        raise HTTPException(status_code=400, detail="Only 5 RMB package available")
    
    quota_to_add = 10
    
    tx = models.Transaction(user_id=user.id, amount_rmb=req.amount_rmb, quota_added=quota_to_add)
    db.add(tx)
    
    user.generate_quota += quota_to_add
    db.add(user)
    
    db.commit()
    return {"message": f"Payment successful. Added {quota_to_add} to quota.", "new_quota": user.generate_quota}

@router.post("/generate_mindmap", response_model=H5GenerateMindmapResponse)
def h5_generate_mindmap(req: H5GenerateMindmapRequest, request: Request, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    ip = get_ip(request)
    today = datetime.date.today()
    
    ip_log = db.query(models.IPLog).filter(models.IPLog.ip_address == ip, models.IPLog.date == today).first()
    if not ip_log:
        ip_log = models.IPLog(ip_address=ip, date=today, usage_count=0)
        db.add(ip_log)
        db.commit()
        db.refresh(ip_log)
    
    quota_used_msg = ""
    # Check free quota first
    if ip_log.usage_count < 5:
        ip_log.usage_count += 1
        db.commit()
        quota_used_msg = "free_daily_quota"
    # Fallback to paid quota
    elif user.generate_quota > 0:
        user.generate_quota -= 1
        db.commit()
        quota_used_msg = "paid_quota"
    else:
        raise HTTPException(status_code=403, detail="Exhausted daily free quota and paid quota. Please recharge.")
    
    # Actually generate the mindmap
    try:
        context = search_book_info(req.book_title)
        md_content = generate_mindmap_markdown(req.book_title, context)
        pdf_url = generate_mindmap_document(req.book_title, md_content)
    except Exception as e:
        # Rollback quota if generation fails?
        # For simplicity, we can just refund it.
        if quota_used_msg == "free_daily_quota":
            ip_log.usage_count -= 1
        elif quota_used_msg == "paid_quota":
            user.generate_quota += 1
        db.commit()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
        
    return H5GenerateMindmapResponse(pdf_url=pdf_url, message="Success", quota_used=quota_used_msg)
