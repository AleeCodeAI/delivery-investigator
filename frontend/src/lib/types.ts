/*
 * TypeScript types for backend API data. Keep in sync with the API contract.
 * Analytics is an assumed shape and must be verified against a real response.
 */

export type Role = 'admin' | 'operator'

export interface Profile {
  user_id: string
  name: string | null
  email: string
  role: Role
  created_at: string
}

export interface AgentResult {
  investigation_report: string
  evidences: string[]
  investigation_success: boolean
  confidence: number
}

export interface RecommenderResult {
  recommendation: string
  evidences: string[]
  confidence: number
}

export interface RunResult {
  agent_result: AgentResult
  recommender_result: RecommenderResult | null // can be null
}

export interface Customer {
  customer_id: string
  name: string
  current_street: string
  current_city: string
  current_state: string
  current_zip: string
  account_created_at: string
}

export interface Order {
  order_id: string
  customer_id: string
  order_date: string
  sku: string
  product_name: string
  quantity: number
  unit_price: string | number // Decimal: may arrive as a string
  order_value: string | number
  delivery_street: string
  delivery_city: string
  delivery_state: string
  delivery_zip: string
  order_status: string
  fulfilled_from_warehouse_id: string
}

export interface Shipment {
  shipment_id: string
  order_id: string
  carrier: string
  tracking_number: string
  ship_date: string
  shipment_status: string
  delivered_at: string | null
  delivery_confirmation: string
}

export interface ShipmentEvent {
  event_id: string
  shipment_id: string
  event_type: string
  event_timestamp: string
  location: string
  description: string
}

export interface UpfrontData {
  customer: Customer
  order: Order
  shipment: Shipment | null // null when no shipment exists yet
  shipment_events: ShipmentEvent[] | null
}

export interface Execution {
  execution_id: string
  user_id: string | null
  customer_id: string
  order_id: string
  investigation_prompt: string
  upfront_data: UpfrontData | null
  agent_result: AgentResult | null
  recommender_result: RecommenderResult | null
  execution_success: boolean | null
  execution_date: string
  error_message: string | null
}

export interface Invitation {
  access_key: string
  name: string
  email: string
  status: boolean // true = redeemed, false = pending
  created_at: string
}

export interface Analytics {
  overview: {
    total_executions: number
    successful_executions: number
    failed_executions: number
    success_rate: number
    unique_orders_investigated: number
    unique_customers_investigated: number
    active_operators: number
  }
  failure_analytics: { total_failures: number; common_errors: Record<string, number> }
  execution_trends: {
    daily: Record<string, { total: number; successful: number }>
    weekly: Record<string, { total: number; successful: number }>
    monthly: Record<string, { total: number; successful: number }>
  }
  invitations: { total_invitations: number }
}