from sqlalchemy.orm import Session

from integrations.database.user_model import User
from schemas.db.user import UserCreate
from schemas.user.address import Address


def create_user(db: Session, user: UserCreate) -> User:
    address: Address = user.address

    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        address_line_1=address.line_1,
        address_line_2=address.line_2,
        city=address.city,
        state=address.state,
        pincode=address.pincode,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()
