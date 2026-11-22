/*
 * Collapsible panel with the raw records behind an investigation: customer,
 * order, shipment and tracking events. Collapsed by default.
 * data: undefined = still loading, null = unavailable.
 */
import { useState, type ReactNode } from 'react'
import { ChevronRight, Loader2 } from 'lucide-react'
import { formatAddress, formatDate, formatDateTime, formatMoney } from '../lib/format'
import type { ShipmentEvent, UpfrontData } from '../lib/types'

function Column({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
      <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-wide text-zinc-600">{title}</h3>
      <dl className="flex flex-col gap-2.5">{children}</dl>
    </div>
  )
}

function Row({ label, value, mono }: { label: string; value: ReactNode; mono?: boolean }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-xs text-zinc-600">{label}</dt>
      <dd className={`break-words text-[13px] ${mono ? 'font-mono text-xs' : ''}`}>{value}</dd>
    </div>
  )
}

// Oldest first, by time (never by event_id).
function byTimestamp(a: ShipmentEvent, b: ShipmentEvent): number {
  const ta = Date.parse(a.event_timestamp)
  const tb = Date.parse(b.event_timestamp)
  return Number.isNaN(ta) || Number.isNaN(tb) ? a.event_timestamp.localeCompare(b.event_timestamp) : ta - tb
}

function Records({ data }: { data: UpfrontData }) {
  const { customer, order, shipment, shipment_events } = data
  const events = [...(shipment_events ?? [])].sort(byTimestamp)

  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-4 md:grid-cols-3">
        <Column title="Customer">
          <Row label="Customer ID" value={customer.customer_id} mono />
          <Row label="Name" value={customer.name} />
          <Row label="Current address" value={formatAddress(customer.current_street, customer.current_city, customer.current_state, customer.current_zip)} />
        </Column>

        <Column title="Order">
          <Row label="Order ID" value={order.order_id} mono />
          <Row label="Warehouse" value={order.fulfilled_from_warehouse_id} mono />
          <Row label="Product" value={`${order.product_name} (SKU ${order.sku}, qty ${order.quantity})`} />
          <Row label="Order date" value={formatDate(order.order_date)} />
          <Row label="Order value" value={formatMoney(order.order_value)} />
          <Row label="Delivery address" value={formatAddress(order.delivery_street, order.delivery_city, order.delivery_state, order.delivery_zip)} />
          <Row label="Order status" value={order.order_status} />
        </Column>

        <Column title="Shipment">
          {shipment ? (
            <>
              <Row label="Shipment ID" value={shipment.shipment_id} mono />
              <Row label="Carrier" value={shipment.carrier} />
              <Row label="Tracking number" value={shipment.tracking_number} mono />
              <Row label="Status" value={shipment.shipment_status} />
              <Row label="Delivered at" value={shipment.delivered_at ? formatDateTime(shipment.delivered_at) : 'Not delivered'} />
              <Row label="Delivery confirmation" value={shipment.delivery_confirmation} />
            </>
          ) : (
            <p className="text-[13px] text-zinc-600">No shipment recorded</p>
          )}
        </Column>
      </div>

      <div className="flex flex-col gap-2">
        <h3 className="text-[11px] font-semibold uppercase tracking-wide text-zinc-600">Tracking events</h3>
        {events.length === 0 ? (
          <p className="text-[13px] text-zinc-600">No shipment events recorded.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-zinc-300">
            <table className="w-full min-w-[560px] border-collapse text-left text-[13px]">
              <thead className="bg-zinc-50 text-xs text-zinc-600">
                <tr>
                  <th className="px-3 py-2 font-medium">Timestamp</th>
                  <th className="px-3 py-2 font-medium">Type</th>
                  <th className="px-3 py-2 font-medium">Location</th>
                  <th className="px-3 py-2 font-medium">Description</th>
                </tr>
              </thead>
              <tbody>
                {events.map((ev) => (
                  <tr key={ev.event_id} className="border-t border-zinc-200 align-top">
                    <td className="whitespace-nowrap px-3 py-2 font-mono text-xs">{formatDateTime(ev.event_timestamp)}</td>
                    <td className="px-3 py-2">{ev.event_type}</td>
                    <td className="px-3 py-2">{ev.location}</td>
                    <td className="px-3 py-2">{ev.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export function UpfrontRecords({ data }: { data: UpfrontData | null | undefined }) {
  const [open, setOpen] = useState(false)

  return (
    <section className="card">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center gap-2.5 rounded-[14px] px-6 py-4 text-left"
      >
        <ChevronRight className={`size-4 shrink-0 text-zinc-600 transition-transform ${open ? 'rotate-90' : ''}`} aria-hidden="true" />
        <span className="text-sm font-semibold">Upfront records</span>
        <span className="hidden text-[13px] text-zinc-600 sm:inline">customer, order, shipment and tracking events</span>
      </button>

      {open && (
        <div className="border-t border-zinc-200 p-6">
          {data === undefined && (
            <p role="status" className="flex items-center gap-2 text-[13px] text-zinc-600">
              <Loader2 className="size-4 animate-spin" aria-hidden="true" />
              Loading records
            </p>
          )}
          {data === null && <p className="text-[13px] text-zinc-600">Records unavailable</p>}
          {data && <Records data={data} />}
        </div>
      )}
    </section>
  )
}