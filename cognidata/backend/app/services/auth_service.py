import secrets
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.models.user import User

def get_user(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str) -> User:
    role = "admin" if db.query(User).count() == 0 else "user"
    user = User(email=email, hashed_password=hash_password(password), role=role)
    db.add(user); db.commit(); db.refresh(user)
    return user

def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_or_create_oauth_user(db: Session, email: str) -> User:
    user = get_user(db, email)
    if not user:
        user = create_user(db, email, secrets.token_hex(32))
    return user
