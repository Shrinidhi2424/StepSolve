import importlib
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status

from app.core.models import SolveResponse
from app.registry import TOPICS, get_all_topics_metadata

router = APIRouter()


@router.get("/health", tags=["System"])
def health_check() -> Dict[str, str]:
    """Basic health and liveness check."""
    return {"status": "ok", "service": "StepSolve Backend"}


@router.get("/topics", tags=["Topics"])
def list_topics() -> List[Dict[str, Any]]:
    """List all 15 supported numerical methods across 5 modules."""
    return get_all_topics_metadata()


@router.get("/topics/{topic_id}", tags=["Topics"])
def get_topic_detail(topic_id: str) -> Dict[str, Any]:
    """Retrieve detailed metadata and input schema for a specific topic."""
    if topic_id not in TOPICS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found in registry.",
        )
    item = TOPICS[topic_id]
    return {
        "id": item["id"],
        "module": item["module"],
        "title": item["title"],
        "short_description": item["short_description"],
        "input_schema": item["input_schema"],
    }


@router.post("/solve/{topic_id}", response_model=SolveResponse, tags=["Solvers"])
def solve_topic(topic_id: str, payload: Dict[str, Any]) -> SolveResponse:
    """Execute numerical computation for the requested topic and return step-by-step results."""
    if topic_id not in TOPICS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found in registry.",
        )

    topic_info = TOPICS[topic_id]
    module_path, fn_name = topic_info["solve_fn"].rsplit(".", 1)

    try:
        module = importlib.import_module(module_path)
        solve_fn = getattr(module, fn_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load solver module for '{topic_id}': {str(e)}",
        )

    try:
        response = solve_fn(payload)
        return response
    except NotImplementedError as nie:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(nie),
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Computation error during solve: {str(e)}",
        )
