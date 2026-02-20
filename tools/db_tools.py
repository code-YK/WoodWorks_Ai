import logging
from typing import Optional, List, Dict, Any
from database.session import get_session
from database.models import ProductCatalog, ProductItem, User, WorkflowMemory

logger = logging.getLogger(__name__)


def get_available_products() -> List[Dict[str, Any]]:
    """Fetch all products from the catalog."""
    logger.info("TOOL | get_available_products | called")
    with get_session() as session:
        products = session.query(ProductCatalog).all()
        result = []
        for p in products:
            item = session.query(ProductItem).filter_by(product_id=p.id).first()
            result.append({
                "product_id": p.id,
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "base_price": p.base_price,
                "material": p.material,
                "finish_options": p.finish_options,
                "dimensions_guide": p.dimensions_guide,
                "customizable": bool(p.customizable),
                "stock_quantity": item.stock_quantity if item else 0,
                "sku": item.sku if item else "N/A",
            })
        logger.info(f"TOOL | get_available_products | returned {len(result)} products")
        return result


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single product by ID."""
    logger.info(f"TOOL | get_product_by_id | product_id={product_id}")
    with get_session() as session:
        p = session.query(ProductCatalog).filter_by(id=product_id).first()
        if not p:
            logger.warning(f"TOOL | get_product_by_id | product_id={product_id} not found")
            return None
        item = session.query(ProductItem).filter_by(product_id=p.id).first()
        return {
            "product_id": p.id,
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "base_price": p.base_price,
            "material": p.material,
            "finish_options": p.finish_options,
            "dimensions_guide": p.dimensions_guide,
            "customizable": bool(p.customizable),
            "stock_quantity": item.stock_quantity if item else 0,
            "sku": item.sku if item else "N/A",
        }


def check_inventory(product_id: int, quantity: int = 1) -> Dict[str, Any]:
    """Check if enough stock is available for a product."""
    logger.info(f"TOOL | check_inventory | product_id={product_id} qty={quantity}")
    with get_session() as session:
        item = session.query(ProductItem).filter_by(product_id=product_id).first()
        if not item:
            logger.warning(f"TOOL | check_inventory | no inventory record for product_id={product_id}")
            return {
                "available": False,
                "quantity_in_stock": 0,
                "requested_quantity": quantity,
                "sku": None,
            }
        available = item.stock_quantity >= quantity
        logger.info(f"TOOL | check_inventory | available={available} stock={item.stock_quantity}")
        return {
            "available": available,
            "quantity_in_stock": item.stock_quantity,
            "requested_quantity": quantity,
            "sku": item.sku,
        }


def update_inventory_stock(product_id: int, quantity_to_deduct: int) -> bool:
    """Deduct stock after order creation."""
    logger.info(f"TOOL | update_inventory_stock | product_id={product_id} deduct={quantity_to_deduct}")
    with get_session() as session:
        item = session.query(ProductItem).filter_by(product_id=product_id).first()
        if not item or item.stock_quantity < quantity_to_deduct:
            logger.error(f"TOOL | update_inventory_stock | insufficient stock")
            return False
        item.stock_quantity -= quantity_to_deduct
        logger.info(f"TOOL | update_inventory_stock | new stock={item.stock_quantity}")
        return True


def store_workflow_memory(
    user_id: Optional[int],
    product_id: Optional[int],
    session_type: str,
    agent_summary: str,
    final_state: Dict[str, Any],
    pricing: Optional[float],
) -> int:
    """Store long-term memory of the workflow session."""
    logger.info(f"TOOL | store_workflow_memory | user_id={user_id} product_id={product_id} type={session_type}")
    with get_session() as session:
        memory = WorkflowMemory(
            user_id=user_id,
            product_id=product_id,
            session_type=session_type,
            agent_summary=agent_summary,
            final_state=final_state,
            pricing=pricing,
        )
        session.add(memory)
        session.flush()
        memory_id = memory.id
        logger.info(f"TOOL | store_workflow_memory | stored with id={memory_id}")
        return memory_id


def create_user(name: str, email: Optional[str], phone: Optional[str]) -> int:
    """Create a new user record and return user_id."""
    logger.info(f"TOOL | create_user | name={name}")
    with get_session() as session:
        user = User(name=name, email=email, phone=phone)
        session.add(user)
        session.flush()
        user_id = user.id
        logger.info(f"TOOL | create_user | created user_id={user_id}")
        return user_id
