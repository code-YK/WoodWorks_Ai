import traceback
import logging
from graph.state import WoodWorksState
from tools.db_tools import get_available_products

logger = logging.getLogger(__name__)

def data_retrieval_node(state: WoodWorksState) -> WoodWorksState:
    logger.info("NODE | DataRetrieval | ENTER")
    
    # In a real system, this would do vector search or filtered DB queries based on 'refined_query'
    # For this implementation, we'll fetch the full catalog as context, 
    # but we could filter it if the query mentions specific categories.
    
    try:
        products = get_available_products()
        # Simple optimization: if catalog is huge, we'd filter here.
        # For < 50 items, passing all is fine.
        
        # Create a string representation
        lines = []
        for p in products:
            lines.append(f"- {p['name']} ({p['category']}) — ${p['base_price']:,.2f}")
        
        context_str = "\n".join(lines)
        logger.info(f"NODE | DataRetrieval | Retrieved {len(products)} products")
        
    except Exception as e:
        logger.error(f"NODE | DataRetrieval | Error: {e}\n{traceback.format_exc()}")
        context_str = "Error extracting product catalog."

    logger.info("NODE | DataRetrieval | EXIT")
    return {
        **state,
        "retrieved_context": context_str,
        "current_node": "data_retrieval"
    }
