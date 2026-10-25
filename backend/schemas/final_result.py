from pydantic import BaseModel, Field 
from .investigation_agent_schema import AgentResult
from .recommender_schema import RecommenderResult


class FinalResult(BaseModel):
    agent_result: AgentResult = Field(
        description="the investigation result by agent"
    )
    recommender_result: RecommenderResult | None = Field(
        description="the recommendation proposed based on company policies"
    )