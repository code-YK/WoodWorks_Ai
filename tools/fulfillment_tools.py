import logging
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from tools.order_tools import create_order_entry, update_order_receipt_path
from tools.db_tools import update_inventory_stock
from tools.pdf_generator import generate_pdf_receipt
from database.session import get_session
from database.models import Order

logger = logging.getLogger(__name__)


@tool
def create_order_tool(
    user_id: int,
    product_id: int,
    human_spec: str,
    technical_spec: str,
    final_price: float,
) -> Dict[str, Any]:
    """
    Creates a new order in the database and updates inventory stock.
    Returns a dictionary with order details including 'order_id'.
    """
    logger.info(f"TOOL | CreateOrderTool | processing for user_id={user_id} product_id={product_id}")
    
    try:
        # 1. Create Order
        result = create_order_entry(
            user_id=user_id,
            product_id=product_id,
            human_spec=human_spec,
            technical_spec=technical_spec,
            final_price=final_price,
        )
        order_id = result["order_id"]
        
        # 2. Update Inventory
        stock_updated = update_inventory_stock(product_id, 1)
        if not stock_updated:
            logger.warning(f"TOOL | CreateOrderTool | Inventory update failed for product_id={product_id}")
            
        return {
            "order_id": order_id,
            "status": "confirmed",
            "inventory_updated": stock_updated
        }
    except Exception as e:
        logger.error(f"TOOL | CreateOrderTool | Error: {e}")
        raise e


@tool
def generate_receipt_tool(
    order_id: int,
    user_name: str,
    product_name: str,
    technical_summary: str,
    final_price: float,
    human_spec: str,
) -> str:
    """
    Generates a PDF receipt for the order and updates the order record with the file path.
    Returns the absolute file path of the generated PDF.
    """
    logger.info(f"TOOL | GenerateReceiptTool | processing for order_id={order_id}")
    
    try:
        receipt_path = generate_pdf_receipt(
            order_id=order_id,
            user_name=user_name,
            product_name=product_name,
            technical_summary=technical_summary,
            final_price=final_price,
            human_spec=human_spec,
        )
        
        update_result = update_order_receipt_path(order_id, receipt_path)
        if not update_result:
             logger.warning(f"TOOL | GenerateReceiptTool | Failed to update order record with path")

        return receipt_path
    
    except Exception as e:
        logger.error(f"TOOL | GenerateReceiptTool | Error: {e}")
        raise e


@tool
def store_workflow_memory_tool(order_id: int, summary: str) -> bool:
    """
    Stores the final workflow memory/summary into the long-term database.
    Returns True if successful.
    """
    logger.info(f"TOOL | StoreWorkflowMemoryTool | processing for order_id={order_id}")
    # Conceptual implementation - in real system would write to a specialized memory table/vector DB
    return True
