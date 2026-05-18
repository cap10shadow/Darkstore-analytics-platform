import { useState, useMemo } from 'react'
import { Search, Filter } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { fetchOrders } from '../api/data'
import PageHeader from '../components/shared/PageHeader'
import Card from '../components/shared/Card'
import StatusBadge from '../components/shared/StatusBadge'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorCard from '../components/shared/ErrorCard'
import DataTable, { type Column } from '../components/shared/DataTable'
import type { Order } from '../types/data'

export default function OrdersPage() {
  const { data, loading, error, refetch } = useApi(() => fetchOrders(1000))
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [delayedOnly, setDelayedOnly] = useState(false)
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  const orders = data?.orders ?? []

  const statuses = useMemo(() => {
    const s = new Set(orders.map((o) => o.status))
    return ['all', ...Array.from(s)]
  }, [orders])

  const filtered = useMemo(() => {
    return orders.filter((o) => {
      if (search && !o.order_id.toLowerCase().includes(search.toLowerCase())) return false
      if (statusFilter !== 'all' && o.status !== statusFilter) return false
      if (delayedOnly && !o.is_delayed) return false
      return true
    })
  }, [orders, search, statusFilter, delayedOnly])

  const fmtCurrency = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)

  const columns: Column<Order>[] = [
    { key: 'order_id', header: 'Order ID', sortable: true, render: (r) => <span className="font-mono text-xs">{r.order_id}</span> },
    { key: 'status', header: 'Status', sortable: true, render: (r) => <StatusBadge status={r.status} /> },
    { key: 'num_items', header: 'Items', sortable: true },
    { key: 'total_value', header: 'Value', sortable: true, render: (r) => fmtCurrency(r.total_value) },
    { key: 'assigned_staff', header: 'Staff', sortable: true },
    {
      key: 'fulfillment_time_minutes',
      header: 'Fulfillment',
      sortable: true,
      render: (r) => (
        <span className={r.is_delayed ? 'text-accent-rose' : ''}>
          {r.fulfillment_time_minutes.toFixed(1)}m
        </span>
      ),
    },
    {
      key: 'is_delayed',
      header: 'Delayed',
      render: (r) =>
        r.is_delayed ? (
          <span className="inline-block w-2 h-2 rounded-full bg-accent-rose" title="Delayed" />
        ) : null,
    },
  ]

  if (loading) return <LoadingSpinner message="Loading orders..." />
  if (error) return <ErrorCard message={error} onRetry={refetch} />

  return (
    <div>
      <PageHeader title="Orders" description={`${data?.total ?? 0} total orders`} />

      {/* Filters */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
            <input
              type="text"
              placeholder="Search by order ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-navy-900 border border-navy-700 rounded-lg pl-9 pr-3 py-2 text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-accent-cyan"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-text-secondary" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-navy-900 border border-navy-700 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
            >
              {statuses.map((s) => (
                <option key={s} value={s}>{s === 'all' ? 'All Statuses' : s}</option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm text-text-secondary cursor-pointer">
            <input
              type="checkbox"
              checked={delayedOnly}
              onChange={(e) => setDelayedOnly(e.target.checked)}
              className="rounded border-navy-700 bg-navy-900 text-accent-rose focus:ring-accent-rose"
            />
            Delayed only
          </label>
          <span className="text-sm text-text-secondary ml-auto">{filtered.length} results</span>
        </div>
      </Card>

      {/* Orders Table */}
      <Card className="p-0">
        <DataTable<Order>
          columns={columns}
          data={filtered}
          pageSize={25}
          keyField="order_id"
          onRowClick={(r) => setExpandedRow(expandedRow === r.order_id ? null : r.order_id)}
          expandedRow={expandedRow}
          renderExpanded={(r) => (
            <div>
              <p className="text-xs text-text-secondary mb-2">Order Items</p>
              <div className="flex flex-wrap gap-2">
                {r.items.map((item, i) => (
                  <span key={i} className="px-2 py-1 bg-navy-800 rounded text-xs text-text-primary">
                    {item.sku} x{item.qty}
                  </span>
                ))}
              </div>
              <div className="mt-2 text-xs text-text-secondary">
                Target: {r.target_time_minutes}m | Actual: {r.fulfillment_time_minutes.toFixed(1)}m | Staff: {r.assigned_staff}
              </div>
            </div>
          )}
        />
      </Card>
    </div>
  )
}
