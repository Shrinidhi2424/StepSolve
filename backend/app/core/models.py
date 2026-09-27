from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict


class Step(BaseModel):
    step_number: int
    title: str
    description: str
    formula: str
    substitution: Optional[str] = None
    value: Optional[Any] = None


class SolveResponse(BaseModel):
    topic_id: str
    inputs_echo: Dict[str, Any] = Field(default_factory=dict)
    steps: List[Step] = Field(default_factory=list)
    result: Dict[str, Any] = Field(default_factory=dict)
    result_summary: str
    iterations_table: Optional[List[Dict[str, Any]]] = None
    plot_data: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)
