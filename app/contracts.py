"""Typed contracts for preserving human intent before agent execution."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


IntentStatus = Literal["CLEAR_ENOUGH", "CLARIFY_BEFORE_EXECUTION"]


class IntentIR(BaseModel):
    """Minimal structured representation of a human request.

    This contract deliberately separates the original request from the normalized
    goal and from the question needed to resolve material ambiguity.
    """

    original_request: str = Field(min_length=1)
    normalized_goal: str = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    material_ambiguity: bool = False
    clarification_question: str | None = None
    status: IntentStatus = "CLEAR_ENOUGH"

    @model_validator(mode="after")
    def enforce_clarification_consistency(self) -> "IntentIR":
        if self.material_ambiguity:
            if not self.clarification_question:
                raise ValueError(
                    "material ambiguity requires an explicit clarification question"
                )
            if self.status != "CLARIFY_BEFORE_EXECUTION":
                raise ValueError(
                    "material ambiguity must stop at CLARIFY_BEFORE_EXECUTION"
                )
        elif self.status == "CLARIFY_BEFORE_EXECUTION":
            raise ValueError(
                "CLARIFY_BEFORE_EXECUTION requires material_ambiguity=true"
            )
        return self
