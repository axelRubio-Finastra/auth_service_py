from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from . import models, schemas, auth, email_utils
from .database import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Auth Service", description="A simple authentication service with email verification")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, 
                           name=user.name, last_name=user.last_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = auth.create_email_verification_token(user.email)
    email_utils.send_verification_email(user.email, token)
    return {"message": "User created successfully. Check your email to verify your account."}

@app.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    email = payload.get("sub")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified"}
    if user.verification_token != token:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    user.is_verified = True
    db.commit()
    return {"message": "Email successfully verified"}

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    
    access_token = auth.create_access_token(db_user.email, db_user.role)
    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role}

@app.get("/admin-only")
def admin_route(token: str = Header(...)):
    payload = auth.decode_token(token)
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"message": "Welcome to the admin route!"}


