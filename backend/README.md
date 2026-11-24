# Delivery Investigator — Backend

The backend of **Delivery Investigator** is a FastAPI-based AI backend responsible for investigating delivery complaints, interpreting operational evidence, and recommending appropriate actions based on company policies.

The backend is built around a single **Investigation Pipeline** consisting of two AI components:

1. **Investigation Agent** — investigates a delivery issue using operational records and produces an evidence-backed investigation report.
2. **Recommender** — receives the investigation report and company policies, then recommends an appropriate action based on the findings and applicable policies.

The pipeline returns its results to the frontend, where a human operator reviews the investigation and recommendation and makes the final decision.

> **Note:** This README provides a high-level overview of the backend architecture. Detailed documentation for the Investigation Agent, Recommender, and their evaluation methodologies is maintained separately.

---

# Architecture Overview

The backend follows a modular architecture in which FastAPI handles API communication, the Investigation Pipeline handles AI processing, and PostgreSQL stores application and operational data.

## High-level architecture

```text
                         Frontend
                            |
                            v
                      FastAPI Backend
                            |
                            v
                    Investigation Pipeline
                            |
                  +---------+---------+
                  |                   |
                  v                   |
           Investigation Agent        |
                  |                   |
                  v                   |
          Investigation Report        |
                  |                   |
                  v                   |
              Recommender <-----------+
                  |
                  |  Investigation Report
                  |  Company Policies
                  v
           Recommendation
                  |
                  v
          Pipeline Result
                  |
                  v
            API Response
                  |
                  v
               Frontend
                  |
                  v
             Human Operator
```

The Investigation Agent and Recommender are sequential components of the same pipeline. The Recommender depends on the investigation report produced by the Investigation Agent.

The backend also handles supporting responsibilities such as database operations, authentication, authorization, and administrative functionality.

---

# Why FastAPI?

Delivery Investigator uses **FastAPI** as its backend framework because it is well suited to modern Python-based AI applications.

Some of its main benefits include:

- **Asynchronous support** — useful for applications involving database queries and external model/API calls.
- **Automatic API documentation** — FastAPI generates OpenAPI documentation and provides an interactive Swagger UI.
- **Pydantic validation** — request and response data can be validated using strongly defined schemas.
- **Clean architecture** — API routes, services, AI components, database operations, and schemas can be organized independently.
- **Python AI ecosystem** — integrates naturally with libraries and tools used for LLM applications.

FastAPI provides the application API layer, while the Investigation Pipeline handles the AI-specific processing.

---

# Investigation Pipeline

The Investigation Pipeline is the core AI component of the backend.

Its purpose is to investigate a delivery complaint, establish what the available records support, and recommend an appropriate next step based on company policies.

The pipeline consists of two sequential components.

## 1. Investigation Agent

The Investigation Agent is responsible for investigating a specific delivery issue using the company's operational records.

It receives the operator's investigation request along with the relevant upfront data retrieved by the application.

The agent examines the available information, determines whether additional evidence is required, and produces a structured investigation result.

### Upfront data

The application retrieves the core records before executing the agent.

The following operational tables provide the initial investigation context:

| Table | Information provided |
|---|---|
| `orders` | Order details, saved delivery destination, order status, and fulfilling warehouse |
| `customers` | Customer information and current address |
| `shipments` | Carrier, shipment status, delivery timestamp, and delivery confirmation |
| `shipment_events` | Chronological shipment tracking history |

This allows the agent to investigate common delivery complaints without needing to retrieve every piece of information through tools.

### Conditional evidence tools

The agent also has access to two tools that retrieve additional evidence when necessary.

| Tool | Data accessed | Purpose |
|---|---|---|
| Address History Tool | `customer_address_history` | Investigates whether an order's delivery destination matches a previously recorded customer address |
| Fulfilment Evidence Tool | `inventory_events`, with optional `inventory` context | Investigates internal fulfilment events that may explain a shipment stall before carrier pickup |

Tool usage is conditional. The agent decides whether additional information could materially improve its investigation.

For example:

- A routine tracking delay can often be investigated using upfront data alone.
- An address discrepancy may require customer address history.
- A shipment stalled before carrier pickup may require fulfilment evidence.

The tools are scoped to the order being investigated. The agent does not have unrestricted access to operational records.

### Investigation output

The Investigation Agent produces a structured result containing:

- **Investigation report** — a concise explanation of the findings and the likely cause, limited to what the evidence supports.
- **Evidence** — supporting evidence used during the investigation.
- **Investigation success** — whether the investigation was successful.
- **Confidence** — a confidence score representing the agent's assessment.

The report must distinguish documented facts from assumptions and unresolved questions.

Importantly, the agent must not invent a root cause when the available records do not establish one.

For a detailed explanation of the agent's architecture, data access, tools, and implementation decisions, see the dedicated Investigation Agent documentation.

---

## 2. Recommender

The Recommender is the second component of the Investigation Pipeline.

Its responsibility is to interpret the Investigation Agent's report alongside the company's policies and recommend an appropriate action.

Unlike the Investigation Agent, the Recommender does not independently investigate operational records. It uses the investigation findings as its input.

### Inputs

The Recommender receives:

1. **Investigation report** — the findings produced by the Investigation Agent.
2. **Company policies** — the rules and guidelines that determine which actions are appropriate for a particular situation.

### Recommendation process

The Recommender evaluates the investigation findings against the applicable company policies.

It determines which action is appropriate based on the available evidence and policy requirements.

```text
Investigation Report
         |
         |
         v
     Recommender
         ^
         |
         |
   Company Policies
         |
         v
 Policy-based Reasoning
         |
         v
   Recommendation
```

### Recommendation output

The Recommender produces a recommendation that helps the operator understand what action should be considered according to company policy.

The recommendation is advisory. It does not execute the recommended action.

For example, the system does not autonomously issue refunds, replacements, or reshipments.

The human operator remains responsible for reviewing the recommendation and deciding what to do.

---

# Complete Investigation Pipeline Flow

The following diagram represents the complete AI processing flow:

```text
                    Operator Request
                           |
                           v
                  FastAPI Endpoint
                           |
                           v
                Retrieve Upfront Data
                           |
                           v
                 Investigation Agent
                           |
                  +--------+--------+
                  |                 |
                  v                 v
             Available Data    Conditional Tools
                  |                 |
                  +--------+--------+
                           |
                           v
                 Investigation Report
                           |
                           v
                     Recommender
                           ^
                           |
                    Company Policies
                           |
                           v
                    Recommendation
                           |
                           v
                  Pipeline Result
                           |
                           v
                    JSON Response
                           |
                           v
                       Frontend
                           |
                           v
                    Human Operator
```

The pipeline follows a clear separation of responsibilities:

- The Investigation Agent determines what happened based on operational evidence.
- The Recommender determines what action should be considered based on the investigation and company policies.
- The human operator makes the final decision.

This separation prevents the recommendation stage from replacing the investigation process or making unsupported assumptions about what happened.

---

# API Response

Once the Investigation Pipeline completes execution, the backend returns the structured result through the appropriate FastAPI endpoint.

The response contains the investigation findings and recommendation, which the frontend can display to the operator.

```text
Investigation Pipeline
         |
         v
   Structured Result
         |
         v
     JSON Response
         |
         v
      Frontend
         |
         v
    Human Operator
```

The frontend is responsible for presenting the investigation report, supporting evidence, confidence information, and recommendation.

The backend remains responsible for executing the investigation and producing the structured response.

---

# Backend Responsibilities

The backend can be viewed as having the following major responsibilities:

| Component | Responsibility |
|---|---|
| **FastAPI** | Exposes the application API and handles communication with the frontend |
| **Investigation Pipeline** | Coordinates the Investigation Agent and Recommender |
| **Investigation Agent** | Investigates delivery issues using operational evidence |
| **Recommender** | Recommends appropriate actions based on investigation findings and company policies |
| **PostgreSQL** | Stores application and operational data |
| **Authentication and Authorization** | Manages access to the application and its protected functionality |
| **Administrative Functionality** | Supports administrative operations such as invitation management and analytics |

This separation keeps the backend modular and makes individual responsibilities easier to maintain, test, and evaluate.

---

# Evaluation

Delivery Investigator includes an evaluation process to validate the quality and reliability of both AI components in the Investigation Pipeline.

Although the Investigation Agent and Recommender are part of the same pipeline, they have different responsibilities and are evaluated using separate evaluation methodologies.

Both evaluations use an **LLM-as-a-Judge** approach.

## 1. Investigation Agent Evaluation

The Investigation Agent is evaluated using **70 synthetic investigation cases**.

Evaluation is performed in two separate stages:

1. **Agent execution** — the agent processes the investigation cases and saves its results.
2. **Evaluation** — an LLM judge evaluates the saved agent results against the corresponding ground truth.

The evaluator does not execute the agent. It evaluates previously generated results.

### Evaluation criteria

The agent is evaluated using two binary criteria:

| Criterion | Weight | Purpose |
|---|---:|---|
| `cause_correct` | 80% | Determines whether the investigation report correctly identifies the actual scenario |
| `evidence_consistency_correct` | 20% | Determines whether the report's claims are supported by the evidence cited by the agent |

The overall score for each case is calculated as:

```text
Score = (cause_correct × 80) + (evidence_consistency_correct × 20)
```

A case passes when its score is at least 80.

This means that correctly identifying the cause is essential. Evidence consistency alone cannot compensate for an incorrect cause.

### Evaluation threshold

The required overall pass rate is **90%**.

For the 70-case evaluation set, at least 63 cases must pass.

### Judge calibration

Before the final evaluation, the judge was calibrated using 15 independently generated mock cases.

The expected judgments were established manually and compared with the judge's decisions.

The final calibration achieved 100% alignment.

Calibration is repeated when significant changes are made to the judge instructions or evaluation methodology.

The detailed evaluation methodology is documented separately.

## 2. Recommender Evaluation

The Recommender is also evaluated using an LLM-as-a-Judge approach.

Its evaluation focuses on whether the recommendation follows company policies and is supported by the available investigation findings.

### Evaluation criteria

The Recommender is evaluated using two criteria:

| Criterion | Purpose |
|---|---|
| `recommendation_correct` | Determines whether the recommendation is appropriate according to the company's policies |
| `evidence_consistency_correct` | Determines whether the recommendation is supported by the investigation evidence and relevant policy information |

### Evaluation threshold

The required pass rate is **90%**.

A separate judge calibration process was not performed for the Recommender because its evaluation criteria involve a comparatively straightforward policy-based assessment.

The Recommender evaluation successfully passed the required threshold.

The detailed evaluation methodology is documented separately.

## Evaluation philosophy

The purpose of evaluation is to validate whether the AI components produce reliable results, not simply whether the application executes successfully.

The two components are evaluated according to their actual responsibilities:

- The Investigation Agent must identify the correct cause and produce evidence-consistent findings.
- The Recommender must provide recommendations that follow company policies and are supported by the investigation.

This allows each component to be evaluated independently while preserving the fact that both operate within one Investigation Pipeline.

---

# Scope and Decision Boundaries

Delivery Investigator is designed to support human operators, not replace their decision-making.

The backend is responsible for:

- Investigating delivery complaints using available operational records.
- Retrieving additional evidence when required.
- Producing evidence-backed investigation findings.
- Recommending appropriate actions according to company policies.
- Returning structured results to the frontend.

The backend does not:

- Issue refunds autonomously.
- Create replacement or reshipment orders autonomously.
- Modify operational records as part of an investigation.
- Contact customers or carriers directly.
- Treat unsupported assumptions as established facts.
- Make the final operational decision on behalf of the human operator.

The operator remains responsible for reviewing the results and taking any necessary action.

---

# Overall Design Philosophy

The backend follows a simple principle:

> **Investigate using reliable evidence, evaluate the findings against company policies, and leave the final decision to the human operator.**

Rather than treating the LLM as a single component responsible for the entire process, the Investigation Pipeline separates investigation and recommendation into two sequential components.

This makes the system:

- **Modular** — investigation and recommendation have clearly defined responsibilities.
- **Evidence-driven** — investigation findings are grounded in operational records.
- **Policy-aware** — recommendations are based on company policies.
- **Human-controlled** — the system recommends actions but does not execute them autonomously.
- **Evaluable** — each AI component has its own evaluation methodology.
- **Maintainable** — individual components can be improved without redesigning the entire backend.

The result is a backend that combines evidence-based investigation with policy-based recommendations while keeping important business decisions under human control.