"""
Long-term memory is persisted in the workflow_memory table via tools.
This module provides query utilities for reading long-term memory.
"""
import logging
from typing import List, Dict, Any, Optional
from database.session import get_session
from database.models import WorkflowMemory

logger = logging.getLogger(__name__)


def get_recent_sessions(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve recent workflow and chat sessions from long-term memory."""
    logger.info(f"LONG_TERM_MEMORY | Fetching last {limit} sessions")
    with get_session() as session:
        records = (
            session.query(WorkflowMemory)
            .order_by(WorkflowMemory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "product_id": r.product_id,
                "session_type": r.session_type,
                "agent_summary": r.agent_summary,
                "pricing": r.pricing,
                "created_at": str(r.created_at),
            }
            for r in records
        ]


def get_user_history(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all sessions for a specific user."""
    logger.info(f"LONG_TERM_MEMORY | Fetching history for user_id={user_id}")
    with get_session() as session:
        records = (
            session.query(WorkflowMemory)
            .filter_by(user_id=user_id)
            .order_by(WorkflowMemory.created_at.desc())
            .all()
        )
        return [
            {
                "id": r.id,
                "product_id": r.product_id,
                "session_type": r.session_type,
                "agent_summary": r.agent_summary,
                "pricing": r.pricing,
                "created_at": str(r.created_at),
            }
            for r in records
        ]
