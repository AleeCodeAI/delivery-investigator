from pathlib import Path 
from app.recommender import Recommender
from schemas import RecommenderResult, AgentResult
from database.repos import insert_starting_execution
from uuid import uuid4
import json 
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(message)s")

inputdata_path = Path(__file__).parents[3] / "data" / "evals_data" / "agent_evals_data.json"
outputdata_path = Path(__file__).parents[3] / "data" / "evals_data" / "recommender_evals_data.json"

def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_data(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)


def run_recommender():
    recommender = Recommender()
    agent_results = load_data(inputdata_path)
    recommender_results = []

    for index, case in enumerate(agent_results, start=1):
        session_id = str(uuid4())

        try:
            insert_starting_execution(
                execution_id=session_id,
                customer_id=case["customer_id"],
                order_id=case["order_id"],
                investigation_prompt=case["investigation_prompt"]
            )

            result: RecommenderResult = recommender.recommend(
                agent_result=AgentResult(**case["agent_result"]),
                session_id=session_id
            )

            recommender_results.append({
                "order_id": case["order_id"],
                "recommendation": result.recommendation,
                "evidences": result.evidences,
                "confidence": result.confidence
            })

            # Save after every successful run
            save_data(recommender_results, outputdata_path)
            time.sleep(3)  

            logging.info(f"[{index}/{len(agent_results)}] SUCCESS")

        except Exception as e:
            logging.error(
                f"[{index}/{len(agent_results)}] FAILED: "
                f"{type(e).__name__}: {e}"
            )
            continue

if __name__ == "__main__":
    run_recommender()