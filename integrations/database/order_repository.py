from sqlalchemy.orm import Session

from integrations.database.order_model import Order, OrderItem
from schemas.db.order import OrderCreate, OrderItemCreate


def create_order(db: Session, order_data: OrderCreate) -> Order:
    order = Order(
        user_id=order_data.user_id,
        total_price=order_data.total_price,
        currency=order_data.currency,
    )

    for item in order_data.items:
        order_item = OrderItem(
            product_id=item.product_id,
            unit_price=item.unit_price,
            quantity=item.quantity,
            technical_spec=item.technical_spec,
        )
        order.items.append(order_item)

    db.add(order)
    db.commit()
    db.refresh(order)

    return order
