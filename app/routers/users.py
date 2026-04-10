from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import OAuthUserLogin, Token
from app.auth import create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/oauth", response_model=Token, status_code=status.HTTP_200_OK)
def oauth_login_or_register(user_in: OAuthUserLogin, db: db_dependency):
    # 1. FIND: Check if the user already exists using their unique ID
    existing_user = db.query(User).filter(User.provider_id == user_in.provider_id).first()
    
    if existing_user:
        # User exists! Generate and return a JWT token for them.
        access_token = create_access_token(data={"sub": str(existing_user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
        
    # 2. CREATE: If they don't exist, register them and grant the ₹1,00,000 starting balance
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        provider_id=user_in.provider_id,
        wallet_balance=100000.0  # Explicitly grant ₹1,00,000 INR
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token for the newly created user
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}