# Velora Market – Delivery Investigator synthetic dataset

70 orders, **every one** a deliberately constructed delivery/fulfilment problem. Evaluation (investigation) date: **2026-10-15**. Generated deterministically (seed 189) by a script; all checks listed below were run programmatically before delivery.

## Files
| File | Purpose |
|---|---|
| `customers.csv`, `customer_address_history.csv`, `orders.csv`, `shipments.csv`, `shipment_events.csv`, `inventory_events.csv`, `inventory.csv`, `warehouses.csv` | The eight operational tables. Table/column names and order follow the design reference; schema unchanged. |
| `input_data.csv` | 70 rows (`input_id, order_id, problem_description, input_payload`). `input_payload` is JSON: `investigation_date`, `order_id`, `customer`, `order`, `shipment`, `shipment_events` (events in stored `event_id` order, NOT re-sorted). No tool-returned evidence, no labels. |
| `ground_truth.csv` | 70 rows, one per order: required columns plus `scenario_subtype`. Evaluation-only; never expose to the agent. |
| `seed.sql` | PostgreSQL DDL + INSERTs for all ten tables (single transaction, FK constraints). Operational tables use the unmodified column set; `input_data`/`ground_truth` are separate evaluation tables. |

## Distribution and expected tool use
| Case | Problem type | Orders | Order IDs | Tool |
|---|---|---:|---|---|
| 1 | Delayed shipment | 8 | ORD-189001–008 | none |
| 2 | Failed delivery attempt | 8 | ORD-189009–016 | none |
| 3 | Marked delivered, item not received | 8 | ORD-189017–024 | none |
| 4 | No recent tracking progress | 8 | ORD-189025–032 | none |
| 5 | Apparently conflicting chronology | 8 | ORD-189033–040 | none |
| 6 | Destination differs from current address (A/B/C = 5/5/5, interleaved) | 15 | ORD-189041–055 | address-history |
| 7 | Fulfilment stall before pickup | 15 | ORD-189056–070 | fulfilment-evidence |

Case 7 conditions: quality_hold ×4 (ORD-189056 is the mandatory pattern: SKU-HOME-2002, WH-6, reserved +1 10:05 then quality_hold 0 10:30, label 11:00 on 2026-08-18), count_discrepancy ×3, reservation_released ×3, allocation_shortfall ×3, allocation_failed + backorder_flagged ×2.

## Identifiers
All new IDs use the `189xxx` range with table prefixes: `CUST-`, `ADDR-`, `ORD-`, `SHIP-`, `SE-`, `IE-`, `INV-`, `INPUT-`, `GT-`. Warehouse IDs are fixed `WH-5`…`WH-8` (Ontario Logistics Hub, Sacramento Fulfillment Center, Fresno Distribution Center, Oakland Bay Gateway). No `526xxx` IDs are used. Note: the PDF's sample warehouse IDs (WH-01…04) were replaced by WH-5…8 as instructed in the task.

## Relationships
customers→customer_address_history, customers→orders, orders→shipments (1:1), shipments→shipment_events, orders.fulfilled_from_warehouse_id→warehouses, inventory/inventory_events joined by (sku, warehouse_id), inventory_events.related_order_id→orders. `input_data` and `ground_truth` reference orders.

## Assumptions / interpretation notes
- Timestamps are naive local time, `YYYY-MM-DD HH:MM:SS`; blank = NULL. `effective_to` is inclusive; adjacent address periods have no gaps or overlaps (next `effective_from` = previous `effective_to` + 1 day).
- Orders in cases 1–6 have `reserved` and `shipped_out` inventory events (normal operations). Only case 7 orders have fulfilment-problem events. A few `restock_received` events (no related order) are context noise.
- **`inventory_events` has no description column**, so the schema was not changed. Event meanings come from this controlled catalogue: `reserved` (stock reserved for order), `shipped_out` (stock left warehouse), `quality_hold` (qty 0; the item reserved for the order was placed on hold pending quality inspection), `count_discrepancy` (physical count differed from system; reserved units adjusted), `reservation_released` (allocation released, not replaced), `allocation_shortfall` (negative qty = units that could not be allocated), `allocation_failed` / `backorder_flagged` (qty 0; no allocation made / order backordered), `restock_received`. These are synthetic internal events, not carrier codes.
- Carrier event types: `label_created, picked_up, arrived_at_facility, departed_facility, in_transit, out_for_delivery, delivery_attempt_failed, delivered, delivery_exception, operational_disruption, transportation_delay`. Shipment statuses: `label_created, in_transit, delayed, out_for_delivery, delivery_attempted, delivered`.
- Case 3: the customer genuinely did not receive the item; that fact lives only in the operator description and ground truth, never as a record label.
- Case 5 conflicts resolve via timestamps; some patterns store late-synced scans with higher `event_id` than later-timestamped events, so chronology must come from `event_timestamp`.
- Case 4 gaps are 12–44 days relative to 2026-10-15; no reason is recorded.
- Case 6 customers each have one order; history completeness is intended (subtype B truly has no match). Subtype is derivable only via `customer_address_history`.
- Fulfilment tool query = order's SKU + warehouse + window around order date (≈±7 days), using `related_order_id`; the result may include other orders' events as context.
- `inventory` is a current snapshot only and is deliberately not evidence of historical stock.

## Validation performed
70 distinct orders; distribution 8/8/8/8/8/15/15; 70 inputs and 70 ground-truth rows, 1:1 with orders; unique PKs; all FKs resolve; ID format/prefix checks; warehouse IDs; one shipment per order; unique tracking numbers; order_value = quantity × unit_price; event chronology (no pre-order or post-investigation events); delivered shipments have matching delivered event/timestamp, undelivered ones have none; case 6 subtype re-derived from the data matches ground truth for all 15; address history has no gaps/overlaps; case 7 has `processing`/`label_created`, only a `label_created` event and ≥2 linked inventory events; payloads contain no history/inventory/label leakage; uniform CSV column counts.
