from dataclasses import dataclass, field
from typing import Dict, List, Any
import uuid

@dataclass
class WorkflowState:
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tasks: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    state: str = "pending"
