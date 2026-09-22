from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, User, Citizen, Officer, AuditLog
from auth import verify_password, hash_password, create_access_token, get_current_user
from datetime import datetime
import random

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    mobile: str
    password: str
    full_name: str
    email: str = ""
    address: str = ""
    district: str = "Pune"
    dob: str = ""
    gender: str = ""


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    token = create_access_token({"sub": user.username, "role": user.role})
    
    # Audit log
    db.add(AuditLog(user_identifier=user.username, system="Sanyukt", action="User Login", status="SUCCESS"))
    db.commit()
    
    # Build response
    resp = {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}
    
    if user.role == "citizen" and user.citizen:
        c = user.citizen
        resp["citizen_name"] = c.full_name
        resp["sanyukt_id"] = c.sanyukt_id
        resp["citizen_id"] = c.id
    elif user.role == "officer" and user.officer:
        o = user.officer
        resp["officer_name"] = o.full_name
        resp["officer_id"] = o.officer_id
        resp["department"] = o.department
    
    return resp


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.mobile).first():
        raise HTTPException(status_code=400, detail="Mobile number already registered.")
    
    user = User(username=req.mobile, hashed_password=hash_password(req.password), role="citizen")
    db.add(user)
    db.flush()
    
    # Generate Sanyukt ID
    seq = db.query(Citizen).count() + 1
    sanyukt_id = f"MH-SYN-2026-{seq:06d}"
    
    citizen = Citizen(
        user_id=user.id,
        sanyukt_id=sanyukt_id,
        full_name=req.full_name,
        mobile=req.mobile,
        email=req.email,
        address=req.address,
        district=req.district,
        dob=req.dob,
        gender=req.gender,
        aadhaar_last4=str(random.randint(1000, 9999))
    )
    db.add(citizen)
    db.add(AuditLog(user_identifier=req.mobile, system="Sanyukt", action="Citizen Registration", status="SUCCESS"))
    db.commit()
    
    token = create_access_token({"sub": user.username, "role": "citizen"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "citizen",
        "username": req.mobile,
        "citizen_name": req.full_name,
        "sanyukt_id": sanyukt_id,
        "citizen_id": citizen.id
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resp = {"username": current_user.username, "role": current_user.role}
    if current_user.role == "citizen" and current_user.citizen:
        c = current_user.citizen
        resp.update({
            "citizen_name": c.full_name,
            "sanyukt_id": c.sanyukt_id,
            "citizen_id": c.id,
            "mobile": c.mobile,
            "email": c.email,
            "address": c.address,
            "district": c.district,
            "dob": c.dob,
            "gender": c.gender,
            "aadhaar_last4": c.aadhaar_last4,
        })
    elif current_user.role == "officer" and current_user.officer:
        o = current_user.officer
        resp.update({
            "officer_name": o.full_name,
            "officer_id": o.officer_id,
            "department": o.department,
            "designation": o.designation,
        })
    return resp
