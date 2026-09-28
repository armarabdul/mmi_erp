from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse

class AuthService:
    @staticmethod
    def authenticate(db: Session, creds: LoginRequest) -> Optional[LoginResponse]:
        user = db.query(User).filter(User.email == creds.email).first()
        if not user or not verify_password(creds.password, user.password_hash):
            return None
        if not user.is_active:
            return None

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "email": user.email})
        branch_name = user.branch.name if user.branch else None
        
        user_resp = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            branch_id=user.branch_id,
            branch_name=branch_name,
            is_active=user.is_active,
        )
        return LoginResponse(access_token=access_token, token_type="bearer", user=user_resp)

auth_service = AuthService()
