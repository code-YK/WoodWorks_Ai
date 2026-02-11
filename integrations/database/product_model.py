from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from integrations.database.engine import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(50))