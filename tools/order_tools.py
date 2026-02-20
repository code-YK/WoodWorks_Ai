import logging
from typing import Optional, Dict, Any
from database.session import get_session
from database.models import Order
from tools.db_tools import update_inventory_stock

logger = logging.getLogger(__name__)


def create_order_entry(
    user_id: int,
    product_id: int,
    human_spec: str,
    technical_spec: str,
    final_price: float,
    receipt_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a confirmed order in the database."""
    logger.info(f"TOOL | create_order_entry | user_id={user_id} product_id={product_id} price={final_price}")

    with get_session() as session:
        order = Order(
            user_id=user_id,
            product_id=product_id,
            human_spec=human_spec,
            technical_spec=technical_spec,
            final_price=final_price,
            status="confirmed",
            receipt_path=receipt_path,
        )
        session.add(order)
        session.flush()
        order_id = order.id
        logger.info(f"TOOL | create_order_entry | ORDER CREATED | order_id={order_id}")

    return {
        "order_id": order_id,
        "status": "confirmed",
        "user_id": user_id,
        "product_id": product_id,
        "final_price": final_price,
    }



def update_order_receipt_path(order_id: int, receipt_path: str) -> bool:
    """Update the receipt path for an existing order."""
    logger.info(f"TOOL | update_order_receipt_path | order_id={order_id}")
    with get_session() as session:
        order = session.query(Order).filter_by(id=order_id).first()
        if not order:
            logger.error(f"TOOL | update_order_receipt_path | order_id={order_id} not found")
            return False
        order.receipt_path = receipt_path
        logger.info(f"TOOL | update_order_receipt_path | updated receipt_path={receipt_path}")
        return True
