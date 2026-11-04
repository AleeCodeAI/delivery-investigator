from pathlib import Path 
from agent.agent import InvestigationAgent
from schemas import AgentResult, UpfrontDataSchema
from app.get_upfront_data import get_upfront_data
from database.repos import insert_starting_execution, insert_upfront_data
from uuid import uuid4
import json
import logging 

logging.basicConfig(level=logging.INFO, format="%(message)s")


inputdata_path = Path(__file__).parents[3] / "data" / "evals_data" / "input_data.json"
outputdata_path = Path(__file__).parents[3] / "data" / "evals_data" / "agent_evals_data.json"

def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_data(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)

async def run_agent():
    agent = InvestigationAgent()
    input_data = load_data(inputdata_path)
    agent_results = []

    for index, case in enumerate(input_data, start=1):
        session_id = str(uuid4())

        try:
            insert_starting_execution(
                execution_id=session_id,
                customer_id=case["customer_id"],
                order_id=case["order_id"],
                investigation_prompt=case["problem_description"]
            )

            upfront_data: UpfrontDataSchema = get_upfront_data(
                customer_id=case["customer_id"],
                order_id=case["order_id"]
            )

            insert_upfront_data(
                execution_id=session_id,
                upfront_data=upfront_data.model_dump(mode="json")
            )

            result: AgentResult = await agent.run(
                upfront_data=upfront_data,
                session_id=session_id,
                investigation_prompt=case["problem_description"]
            )

            agent_results.append({
                "order_id": case["order_id"],
                "customer_id": case["customer_id"],
                "investigation_prompt": case["problem_description"],
                "agent_result": result.model_dump(mode="json")
            })

            # Save after every successful run
            save_data(agent_results, outputdata_path)

            print(f"[{index}/{len(input_data)}] SUCCESS")

        except Exception as e:
            print(
                f"[{index}/{len(input_data)}] FAILED: "
                f"{type(e).__name__}: {e}"
            )
            continue

    print(f"\nCompleted: {len(agent_results)}/{len(input_data)} successful runs.")
    print(agent_results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_agent())