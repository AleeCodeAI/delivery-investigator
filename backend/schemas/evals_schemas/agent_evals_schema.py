from typing import ClassVar
from pydantic import BaseModel, Field, computed_field


class AgentEvalsResult(BaseModel):
    """
    Evaluation results for the Delivery Investigator agent.
    """

    CAUSE_WEIGHT: ClassVar[int] = 60
    EVIDENCE_IDENTIFICATION_WEIGHT: ClassVar[int] = 20
    EVIDENCE_CONSISTENCY_WEIGHT: ClassVar[int] = 20
    PASS_THRESHOLD: ClassVar[int] = 80

    cause_correct: bool = Field(
        description="Determines whether the agent correctly identifies the cause of the delivery issue."
    )

    evidence_identification_correct: bool = Field(
        description="Determines whether the agent identifies the essential supporting evidence."
    )

    evidence_consistency_correct: bool = Field(
        description="Determines whether the agent appropriately uses the identified evidence to support the claims and reasoning in its investigation report."
    )

    judge_reasoning: str = Field(
        description="Explanation of the judge's evaluations."
    )

    @computed_field
    @property
    def overall_score(self) -> int:
        """Calculates the weighted evaluation score."""
        return (
            self.cause_correct * self.CAUSE_WEIGHT
            + self.evidence_identification_correct * self.EVIDENCE_IDENTIFICATION_WEIGHT
            + self.evidence_consistency_correct * self.EVIDENCE_CONSISTENCY_WEIGHT
        )

    @computed_field
    @property
    def overall_passed(self) -> bool:
        """Determines whether the investigation passes the evaluation."""
        return self.overall_score >= self.PASS_THRESHOLD