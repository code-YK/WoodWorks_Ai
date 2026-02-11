"""
Seed initial products into the database.

Run:
    python -m scripts.seed_products
"""

from sqlalchemy.orm import Session

from integrations.database.engine import SessionLocal
from integrations.database.product_model import Product
from schemas.base.enums import ProductCategory


PRODUCTS = [
    # STORAGE UNITS
    {
        "name": "Sliding Wardrobe – 3 Door",
        "category": ProductCategory.STORAGE_UNIT,
    },
    {
        "name": "Sliding Wardrobe – 4 Door",
        "category": ProductCategory.STORAGE_UNIT,
    },
    {
        "name": "Hinged Wardrobe – 2 Door",
        "category": ProductCategory.STORAGE_UNIT,
    },
    {
        "name": "Hinged Wardrobe – 3 Door",
        "category": ProductCategory.STORAGE_UNIT,
    },
    {
        "name": "Shoe Rack with Seating",
        "category": ProductCategory.STORAGE_UNIT,
    },
    {
        "name": "Crockery Storage Unit",
        "category": ProductCategory.STORAGE_UNIT,
    },
    {
        "name": "Pantry Storage Unit",
        "category": ProductCategory.STORAGE_UNIT,
    },
    {
        "name": "Loft Storage Unit",
        "category": ProductCategory.STORAGE_UNIT,
    },

    # KITCHEN MODULES
    {
        "name": "Straight Modular Kitchen",
        "category": ProductCategory.KITCHEN_MODULE,
    },
    {
        "name": "L-Shaped Modular Kitchen",
        "category": ProductCategory.KITCHEN_MODULE,
    },
    {
        "name": "U-Shaped Modular Kitchen",
        "category": ProductCategory.KITCHEN_MODULE,
    },
    {
        "name": "Parallel Modular Kitchen",
        "category": ProductCategory.KITCHEN_MODULE,
    },
    {
        "name": "Island Kitchen Module",
        "category": ProductCategory.KITCHEN_MODULE,
    },

    # ENTERTAINMENT UNITS
    {
        "name": "Floating TV Unit",
        "category": ProductCategory.ENTERTAINMENT_UNIT,
    },
    {
        "name": "Floor Mounted TV Unit",
        "category": ProductCategory.ENTERTAINMENT_UNIT,
    },
    {
        "name": "TV Unit with Storage Cabinets",
        "category": ProductCategory.ENTERTAINMENT_UNIT,
    },
    {
        "name": "TV Unit with Open Shelves",
        "category": ProductCategory.ENTERTAINMENT_UNIT,
    },

    # SEATING
    {
        "name": "3-Seater Sofa",
        "category": ProductCategory.SEATING,
    },
    {
        "name": "L-Shaped Sofa",
        "category": ProductCategory.SEATING,
    },
    {
        "name": "Recliner Chair",
        "category": ProductCategory.SEATING,
    },
    {
        "name": "Dining Chair Set (4 Seater)",
        "category": ProductCategory.SEATING,
    },

    # BEDDING
    {
        "name": "Queen Size Bed with Storage",
        "category": ProductCategory.BEDDING,
    },
    {
        "name": "King Size Bed with Hydraulic Storage",
        "category": ProductCategory.BEDDING,
    },
    {
        "name": "Single Bed",
        "category": ProductCategory.BEDDING,
    },
    {
        "name": "Bunk Bed",
        "category": ProductCategory.BEDDING,
    },
]


def seed_products(db: Session):
    print("Seeding products...")

    for product in PRODUCTS:
        exists = (
            db.query(Product)
            .filter(Product.name == product["name"])
            .first()
        )

        if exists:
            print(f"Skipping existing product: {product['name']}")
            continue

        db_product = Product(
            name=product["name"],
            category=product["category"].value,
        )
        db.add(db_product)

    db.commit()
    print("Product seeding completed")


def main():
    db = SessionLocal()
    try:
        seed_products(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
