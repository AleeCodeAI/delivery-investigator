from pydantic import BaseModel, Field


class RecommenderResult(BaseModel):
    """
    Model representing the result of a recommendation based on business policies.
    """
    recommendation: str = Field(
        description="The recommended action or item."
        )
    evidences: list[str] = Field(
        description="List of evidences supporting the recommendation."
        )
    confidence: float = Field(
        description="Confidence score of the recommendation."
        )