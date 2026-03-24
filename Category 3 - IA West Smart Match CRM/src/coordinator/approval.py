"""ActionProposal state machine for HITL approval gate.

Pure Python — no Streamlit imports. Fully testable in isolation.
"""

from __future__ import annotations

import datetime
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

ProposalStatus = Literal["proposed", "approved", "executing", "completed", "failed", "rejected"]


@dataclass
class ActionProposal:
    """Mutable dataclass owning the lifecycle state of a proposed agent action.

    State machine transitions:
        proposed -> approved   (via approve())
        proposed -> rejected   (via reject())
        approved -> executing -> completed  (via stub_execute())

    Invalid transitions raise ValueError.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent: str = ""
    agent: str = ""
    description: str = ""
    reasoning: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    status: ProposalStatus = "proposed"
    source: Literal["parsed", "proactive"] = "parsed"
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().strftime("%H:%M:%S")
    )
    result: str | None = None

    def approve(self) -> None:
        """Transition from proposed to approved."""
        if self.status != "proposed":
            raise ValueError(
                f"Cannot approve proposal in state '{self.status}'"
            )
        self.status = "approved"

    def reject(self) -> None:
        """Transition from proposed to rejected."""
        if self.status != "proposed":
            raise ValueError(
                f"Cannot reject proposal in state '{self.status}'"
            )
        self.status = "rejected"

    def stub_execute(self) -> None:
        """Transition approved -> executing -> completed with mock result.

        Phase 5 stub — real dispatch wires in Phase 6.
        """
        if self.status != "approved":
            raise ValueError(
                f"Cannot execute proposal in state '{self.status}'"
            )
        self.status = "executing"
        self.result = f"[Stub] {self.agent} completed successfully."
        self.status = "completed"
