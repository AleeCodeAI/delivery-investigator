from typing import ClassVar
from pydantic import BaseModel, Field, computed_field


class RecommenderEvalsResult(BaseModel):
    """
    Evaluation results for the Recommender agent.
    """

    RECOMMENDATION_WEIGHT: ClassVar[int] = 80
    EVIDENCE_CONSISTENCY_WEIGHT: ClassVar[int] = 20
    PASS_THRESHOLD: ClassVar[int] = 80

    recommendation_correct: bool = Field(
        description="Determines whether the agent correctly identifies the recommended action."
    )
    evidence_consistency_correct: bool = Field(
        description="Determines whether the agent appropriately uses the identified evidence to support the claims and reasoning in its recommendation."
    )
    judge_reasoning: str = Field(
        description="Explanation of the judge's evaluations."
    )
    confidence: float = Field(
        description="Confidence score of the evaluation, ranging from 0 to 1."
    )

    @computed_field
    @property
    def overall_score(self) -> int:
        """Calculates the weighted evaluation score."""
        return (
            self.recommendation_correct * self.RECOMMENDATION_WEIGHT
            + self.evidence_consistency_correct * self.EVIDENCE_CONSISTENCY_WEIGHT
        )

    @computed_field
    @property
    def overall_passed(self) -> bool:
        """Determines whether the investigation passes the evaluation."""
        return self.overall_score >= self.PASS_THRESHOLD

