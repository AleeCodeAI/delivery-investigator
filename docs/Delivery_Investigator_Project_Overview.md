# Delivery Investigator

## 1. Project Overview

### Client

**Velora Market** is a fictional mid-sized e-commerce company operating in California. Its operators need to investigate delivery complaints using the company's operational records.

### Problem

Delivery complaints can involve delays, failed attempts, stale tracking, apparent tracking conflicts, non-receipt after a delivery scan, or discrepancies between an order's destination and a customer's current address. The available records may explain some cases directly, while others require additional evidence. A symptom must not be mistaken for a proven root cause.

### Solution

Delivery Investigator is a read-only investigation system that brings relevant records together, uses an LLM agent to interpret the evidence, and prepares a concise, evidence-backed finding for a human operator. It reports what is known and unknown; the operator decides what to do next.

## 2. Architecture

The design uses a **tool-using agent with core evidence supplied up front**. The agent does not need to call tools for every investigation.

### 2.1 Data access summary

The eight operational tables are split into three groups: data supplied **upfront**, data reachable **only through a tool**, and **contextual** data that a tool may include. This split is fixed by the design.

| Table | How the agent gets it | Used for |
|---|---|---|
| `orders` | **Upfront** (supplied with every investigation) | What was ordered; saved delivery destination; order status; fulfilling warehouse |
| `customers` | **Upfront** | Customer identity and current address |
| `shipments` | **Upfront** | Carrier, status, ship date, delivery timestamp, delivery confirmation |
| `shipment_events` | **Upfront** | Chronological tracking trail |
| `customer_address_history` | **Tool 1 only** (Address History Tool) | Whether the destination was a previously recorded, unrecognized, or historically valid address |
| `inventory_events` | **Tool 2 only** (Fulfilment Evidence Tool) — primary evidence | Internal events that may explain a pre-pickup stall |
| `inventory` | **Tool 2, contextual and optional** | Current stock/reservation context (never proof of historical stock) |
| `warehouses` | **Tool 2, contextual and optional** | Warehouse name/location for interpreting fulfilment evidence |

Key rules:

- **Upfront data** is limited to the investigated order and its own customer, shipment, and shipment events. It is retrieved by the application before the agent reasons.
- **Tool data** is not in the initial payload. The agent must decide to call the tool to see it.
- Each tool is scoped to the investigated order: Tool 1 reads only the address history of that order's customer; Tool 2 reads only events for that order's SKU, warehouse, and a sensible time window.
- The agent has **no other data access**: no broad customer search, no other tables, and no write operations.

### 2.2 High-level flow

1. **Operator submits an investigation request.** The request identifies the order or issue but does not disclose the suspected cause.
2. **Application retrieves the upfront records.** It gathers the relevant `orders`, `customers`, `shipments`, and `shipment_events` records from the operational database and supplies them to the agent.
3. **Agent investigates the upfront evidence.** It considers the order destination, current customer address, shipment status, delivery confirmation, and chronological tracking trail.
4. **Agent decides whether more evidence is needed.** If the upfront records support a useful conclusion, it answers without a tool call. If an important question remains unresolved and a tool could help distinguish explanations, it calls the appropriate tool, which retrieves data that was **not** supplied upfront.
5. **Agent produces a structured finding.** The report separates evidence, conclusions, and uncertainty, and suggests a next step for the human operator.

```text
Human Operator
      |
      v
Investigation Request
      |
      v
Application retrieves UPFRONT data
      |
      +---- orders
      +---- customers
      +---- shipments
      +---- shipment_events
      |
      v
LLM Investigation Agent
      |
      +---- Upfront evidence is sufficient
      |          |
      |          v
      |     Finding without tool calls
      |
      +---- Important question remains
                 |
                 +---- Tool 1: Address History Tool
                 |         reads: customer_address_history
                 |
                 +---- Tool 2: Fulfilment Evidence Tool
                 |         reads: inventory_events
                 |         context: inventory
                 |
                 v
          Evidence-based finding
                 |
                 v
          Human Operator decides next step
```

### 2.3 Architectural principles

- **Core evidence first:** Provide the records needed for common delivery investigations before asking the agent to reason.
- **Conditional tool use:** Tools retrieve additional evidence only when it could change or materially strengthen the finding.
- **Read-only access:** The system investigates records but does not change them.
- **Bounded conclusions:** The agent must not claim more than the evidence establishes.
- **Stop when appropriate:** Stop when the evidence supports a conclusion or when further available evidence is unlikely to resolve the uncertainty.
- **No forced root cause:** An inconclusive result is acceptable when the records do not explain the issue.

## 3. The Agent

The agent's responsibility is to interpret operational evidence and determine whether further evidence is needed. It is not an autonomous customer-service or fulfilment agent.

### What the agent should do

- Interpret the operator's investigation request.
- Examine the supplied upfront records together.
- Reconstruct shipment progress from tracking events in chronological order.
- Distinguish recorded facts from inferences and unresolved questions.
- Decide whether either evidence tool is relevant.
- Incorporate tool results into the finding.
- Provide a confidence level calibrated to the evidence and explain important limitations.
- Suggest a next step for a human operator.

### What the agent must not do

- Assume every complaint proves company error or customer dishonesty.
- Treat a tracking gap as proof that a parcel is lost.
- Claim that the intended recipient personally received an item just because carrier records show delivery.
- Assume an address mismatch means an old address was used incorrectly.
- Invent a root cause, delivery ETA, or other fact that the records do not support.
- Issue refunds, replacements, or reshipments; edit records; or contact customers or carriers directly.
- Search unrelated customers' personal records. The current design does not require a broad customer-search tool.

### Example investigation cases

| Case | What the agent should establish | Data used | Tool |
|---|---|---|---|
| Documented shipment delay | Report the recorded delay and current status without inventing an ETA. | Upfront data | None |
| Failed delivery attempt | Report the carrier's recorded reason and current shipment status. | Upfront data | None |
| Marked delivered, not received | State what carrier records show while acknowledging that they do not prove the intended recipient received the parcel. | Upfront data | None |
| No recent tracking progress | Report the last known event and that delivery or the reason for the gap is not established. | Upfront data | None |
| Apparent tracking conflict | Read events chronologically to determine whether later events resolve the apparent conflict. | Upfront data | None |
| Destination differs from current address | Determine whether the destination matches a historical address, an unrecognized address, or an address valid on the order date. | Upfront data + `customer_address_history` | Tool 1 — Address History |
| Shipment stalled before carrier pickup | Investigate whether recorded fulfilment or inventory events explain the stall. | Upfront data + `inventory_events` (+ optional `inventory`, `warehouses` context) | Tool 2 — Fulfilment Evidence |

## 4. Tools

The design includes **two conditional evidence tools**. Their final function schemas and exact return payloads have not yet been settled.

| | Tool 1 — Address History | Tool 2 — Fulfilment Evidence |
|---|---|---|
| **Data it retrieves** | `customer_address_history` | `inventory_events` (primary); `inventory` as supporting context |
| **Scoped to** | The customer on the investigated order | The investigated order's SKU |
| **Trigger** | Destination differs from the current address | Label exists but no carrier pickup, and the reason is not in the shipment trail |
| **Not available upfront** | Address history | `inventory_events` and supporting `inventory` context |

### Tool 1 — Retrieve Customer Address History

**Purpose:** Retrieve relevant rows from `customer_address_history` for the customer associated with the investigated order, including address-validity dates.

**Data accessed:** `customer_address_history` only. The upfront data already contains the order's destination (`orders`) and the customer's current address (`customers`); this tool adds the *historical* addresses and their validity periods, which are not supplied upfront.

**When to use it:** The order's saved delivery destination differs from the customer's current address, and historical validity could help explain the discrepancy.

**What it helps distinguish:**

1. **Historical address:** The order destination matches an address whose effective period ended before the order date. This supports that the order used a previously recorded address, but does not establish why it was selected.
2. **Unrecognized destination:** The destination matches neither the current address nor an address in the customer's history. The reason remains unexplained by this tool.
3. **Historically valid address:** The destination matches an address that was effective on the order date, even though the customer has since moved. The mismatch alone does not establish an error.

**Expected behaviour:** Compare the exact destination with the historical addresses and compare `order_date` with `effective_from` and `effective_to`. Return the relevant evidence, not a pre-written diagnosis.

**Do not call it** for routine tracking delays or failed delivery attempts unless a specific clue makes address history relevant.

### Tool 2 — Retrieve Fulfilment Evidence

**Purpose:** Retrieve the relevant `inventory_events` for the investigated order's SKU. The agent already has the order's SKU from the upfront data and uses it to fetch the fulfilment evidence.

**Data accessed:**

- `inventory_events` — **the primary source** for this tool, filtered to the order's SKU. This is the main data source for Tool 2.
- `inventory` — supporting data that may be returned alongside `inventory_events` as extra, beneficial context. It is current-state only and cannot prove historical stock. Returning `None` for `inventory` is acceptable when no supporting snapshot is available.

For Tool 2 to produce valid output for the agent, `inventory_events` must be returned. `inventory` is optional supporting evidence and may be `None` without invalidating the tool result.

**When to use it:** The upfront records show a pre-pickup stall and the shipment trail does not explain the reason.

**What it helps establish:** Whether a recorded internal fulfilment event may explain why the order did not progress to carrier pickup.

**Expected behaviour:** Fetch the relevant `inventory_events` for the SKU, and include `inventory` only as supplemental context when available.

### Tool-use decision rule

Before calling a tool, the agent should ask:

> Could this additional evidence distinguish plausible explanations or materially improve the finding?

If not, it should answer from the records already available. If a tool returns no explanation, the agent should say so rather than inventing a cause.

## 5. Database

The project uses an **existing, fixed schema of eight tables**. The current design does not require adding tables or columns. The operational database is treated as a functioning, reliable system; unusual or missing evidence in a case is intentional scenario design, not a general assumption that the database is defective.

Each table below is labelled with how the agent accesses it: **Upfront**, **Tool 1**, or **Tool 2**.

### 5.1 `customers` — *Upfront*

**Purpose:** Customer identity and current address.

```text
customers(
    customer_id,
    name,
    email,
    current_street,
    current_city,
    current_state,
    current_zip,
    account_created_at
)
```

The current address provides context for comparing a customer's present address with the destination saved on an order. Only the record of the customer on the investigated order is supplied.

### 5.2 `customer_address_history` — *Tool 1 only*

**Purpose:** Historical customer addresses and the periods during which they were effective.

```text
customer_address_history(
    address_history_id,
    customer_id,
    street,
    city,
    state,
    zip,
    effective_from,
    effective_to
)
```

A blank or `NULL` `effective_to` means the address is current. Address history helps establish whether an order destination was previously recorded or valid on the order date; it does not automatically establish why the address was selected. **This table is not supplied upfront.**

### 5.3 `orders` — *Upfront*

**Purpose:** Purchase details and the delivery-address snapshot saved for each order.

```text
orders(
    order_id,
    customer_id,
    order_date,
    sku,
    product_name,
    quantity,
    unit_price,
    order_value,
    delivery_street,
    delivery_city,
    delivery_state,
    delivery_zip,
    order_status,
    fulfilled_from_warehouse_id
)
```

The order's destination is intentionally not assumed to be synchronized with the customer's current address. The saved destination can be compared with current and historical address records. The order's `sku` and `fulfilled_from_warehouse_id` also define the scope of the Fulfilment Evidence Tool.

### 5.4 `shipments` — *Upfront*

**Purpose:** Shipment-level summary.

```text
shipments(
    shipment_id,
    order_id,
    carrier,
    tracking_number,
    ship_date,
    shipment_status,
    delivered_at,
    delivery_confirmation
)
```

This table provides the carrier, tracking identifier, shipping date, current shipment status, delivery timestamp, and recorded delivery-confirmation method.

Proposed synthetic `delivery_confirmation` values include:

- `left_at_door`
- `handed_to_resident`
- `left_at_mailroom`
- `none` (no meaningful confirmation recorded, including for undelivered shipments)

These values describe what the carrier record indicates; they do not necessarily prove that the intended recipient received or collected the parcel.

### 5.5 `shipment_events` — *Upfront*

**Purpose:** Chronological shipment-tracking history.

```text
shipment_events(
    event_id,
    shipment_id,
    event_type,
    event_timestamp,
    location,
    description
)
```

Events help establish the last known progress, recorded delays or failed attempts, and whether apparently conflicting statuses can be reconciled chronologically. `event_type` and `description` should be semantically consistent. Chronology must be read from `event_timestamp`, not from `event_id` order.

### 5.6 `inventory_events` — *Tool 2 (primary data source)*

**Purpose:** Historical inventory movements that may explain a fulfilment stall.

```text
inventory_events(
    event_id,
    sku,
    event_type,
    quantity_change,
    event_timestamp,
    related_order_id
)
```

These events are especially relevant when an order has not progressed to carrier pickup. A synthetic `quality_hold` event may be used consistently to mean that a reserved item was placed on hold pending quality inspection. It should not be presented as a universal real-world carrier event code. **This table is not supplied upfront.**

### 5.7 `inventory` — *Tool 2 (supplementary context)*

**Purpose:** Current stock and reservation snapshot by SKU.

```text
inventory(
    inventory_id,
    sku,
    stock_quantity,
    reserved_quantity
)
```

This table provides additional context only. It is always supplied alongside `inventory_events` as useful supporting data, but current quantities alone cannot establish historical stock availability. **Not supplied upfront.**

### 5.8 Evaluation tables (outside the agent's data)

For testing, two additional tables are kept **separate from the operational schema**. They are not part of the agent's data access beyond the first item below:

- `input_data` — the application input for each case: the operator's request (`problem_description`) and the upfront data (`input_payload`: `customer`, `order`, `shipment`, `shipment_events`). This is what is handed to the agent.
- `ground_truth` — the correct classification, expected findings, and expected tool use for each case. It is used only to score the agent's output and is **never exposed to the agent**.

## 6. Database Relationships

The supplied schema defines these relationships:

- `customers.customer_id` → `customer_address_history.customer_id`
- `customers.customer_id` → `orders.customer_id`
- `orders.order_id` → `shipments.order_id` (the supplied design examples model one shipment per order)
- `shipments.shipment_id` → `shipment_events.shipment_id`
- `inventory_events.related_order_id` can link an inventory event to an order.
- `inventory` and `inventory_events` are interpreted using `sku` when relevant.

### How the data supports an investigation

| Investigation question | Relevant data | Provided via |
|---|---|---|
| What was ordered, and where was it meant to go? | `orders` | Upfront |
| What is the customer's current address? | `customers` | Upfront |
| What is the recorded shipment status and delivery confirmation? | `shipments` | Upfront |
| What happened during the shipment journey? | `shipment_events` | Upfront |
| Was the destination previously recorded, and when was it valid? | `customer_address_history` | Tool 1 |
| Is there a recorded internal event that explains a pre-pickup stall? | `inventory_events` | Tool 2 |
| What is the current stock/reservation context? | `inventory` | Tool 2 (supplementary context) |

Dates and timestamps should use a consistent convention. A blank or `NULL` value means that no value is recorded—for example, `delivered_at` may be empty for a shipment that has not been delivered. Synthetic address-validity periods should be coherent; gaps or overlaps should only be used when a scenario intentionally tests them.

## 7. Input and Output

### Investigation input

A human operator provides a request identifying the target order or issue. The request should describe the question to investigate without giving the agent the presumed answer. The application then attaches the **upfront data** (`orders`, `customers`, `shipments`, `shipment_events` for that order). It does not attach address history or inventory data; those are only available through the tools.

Example:

> Investigate order ORD-3106. The delivery destination differs from the customer's current address. Determine what the records establish about the discrepancy.

The request should not say that the order was sent to an old address, because that is a hypothesis the agent must test against the records.

### Investigation output

A compact report should include:

- **Investigation summary:** The order and shipment being investigated.
- **Finding:** A diagnosis phrased at the level the evidence supports.
- **Evidence:** Relevant record IDs, timestamps, statuses, descriptions, and address comparisons, noting whether each item came from the upfront data or a tool.
- **Uncertainty and limitations:** What cannot be established from the available records.
- **Recommended next step:** A suggestion for the human operator, not an automated action.
- **Confidence:** Calibrated to the quality and sufficiency of the evidence, not the confidence of the wording.

### Examples of appropriately bounded findings

- “Carrier records show the parcel was left at the door. The records do not establish that the intended recipient received it.”
- “No recent tracking event is recorded after the last scan. Delivery is not established, and the records do not explain the gap.”
- “The order destination matches a historical address whose effective period ended before the order date. The records support use of a previously recorded address but do not establish why it was selected.”
- “A `quality_hold` event is recorded for the order's SKU before the expected pickup. This is consistent with the fulfilment stall.”

Possibilities must not be presented as facts. For example, theft may be a possible explanation for non-receipt after a recorded doorstep delivery, but the tracking record alone does not prove theft.

## 8. Scope and Safety Boundaries

### In scope

- Investigating a specific order's delivery journey.
- Explaining documented delays, failed attempts, tracking stalls, apparent event conflicts, and address discrepancies.
- Checking address history (Tool 1) when it may resolve a destination discrepancy.
- Checking fulfilment/inventory-event evidence (Tool 2) when a pre-pickup stall is unexplained.
- Producing an evidence-backed finding, limitations, and a suggested human next step.

### Out of scope

- Issuing refunds, replacements, or reshipments autonomously.
- Editing operational records.
- Contacting customers or carriers directly.
- Assuming customer dishonesty or company fault without evidence.
- Treating all missing tracking updates as proof of loss.
- Broad searches of unrelated customers' personal records.
- Accessing any table or data beyond the upfront set and the two scoped tools.

## 9. Decisions Made and Open Implementation Details

### Decisions made

- Use the existing eight-table database schema.
- Supply `orders`, `customers`, `shipments`, and `shipment_events` for the investigated order up front.
- Make `customer_address_history` available only through Tool 1.
- Make `inventory_events` the primary data source for Tool 2, with `inventory` provided as supplementary supporting context alongside it.
- Use tools only when additional evidence could materially improve the investigation.
- Keep two conditional tools: customer address history and fulfilment evidence.
- Include genuine delivered-but-not-received cases.
- Include multiple address-discrepancy variants rather than treating every mismatch as an old-address case.
- Treat a lack of recent tracking progress as a valid finding without asserting loss.
- Standardize synthetic event types and descriptions consistently.
- Keep the system read-only and the human operator responsible for the next action.

### Not yet settled

- Final tool/function schemas and exact return payloads, including the exact shape of the supplementary `inventory` context returned with `inventory_events`.
- Agent framework, system prompt, and implementation details.
- Company policy rules that a separate recommendation component might apply.
- Exact confidence thresholds and evaluation metrics.

These implementation decisions can be made when the relevant components are built; they do not require expanding the current project scope.