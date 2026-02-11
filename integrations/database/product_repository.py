from sqlalchemy.orm import Session

from integrations.database.product_model import Product


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def list_products(db: Session) -> list[Product]:
    return db.query(Product).all()
