import { useApi } from '../hooks/useApi'
import { fetchInventory, fetchLowStock } from '../api/data'
import PageHeader from '../components/shared/PageHeader'
import Card from '../components/shared/Card'
import HealthBadge from '../components/shared/HealthBadge'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorCard from '../components/shared/ErrorCard'
import DataTable, { type Column } from '../components/shared/DataTable'
import type { InventoryItem } from '../types/data'

function StockBar({ current, threshold }: { current: number; threshold: number }) {
  const pct = Math.min(100, (current / (threshold * 2)) * 100)
  const color =
    current <= threshold * 0.5
      ? 'bg-accent-rose'
      : current <= threshold
        ? 'bg-accent-amber'
        : 'bg-accent-emerald'
  return (
    <div className="w-24 h-2 bg-navy-900 rounded-full overflow-hidden">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  )
}

export default function InventoryPage() {
  const { data: invData, loading: iLoad, error: iErr, refetch: iRefetch } = useApi(() => fetchInventory(1000))
  const { data: lowData, loading: lLoad } = useApi(() => fetchLowStock(100))

  if (iLoad || lLoad) return <LoadingSpinner message="Loading inventory..." />
  if (iErr) return <ErrorCard message={iErr} onRetry={iRefetch} />

  const items = invData?.items ?? []
  const lowStock = lowData?.items ?? []

  const columns: Column<InventoryItem>[] = [
    { key: 'sku_id', header: 'SKU', sortable: true, render: (r) => <span className="font-mono text-xs">{r.sku_id}</span> },
    { key: 'product_name', header: 'Product', sortable: true },
    { key: 'category', header: 'Category', sortable: true },
    { key: 'current_stock', header: 'Stock', sortable: true, render: (r) => (
      <div className="flex items-center gap-2">
        <span>{r.current_stock}</span>
        <StockBar current={r.current_stock} threshold={r.reorder_threshold} />
      </div>
    )},
    { key: 'reorder_threshold', header: 'Reorder At', sortable: true },
    { key: 'shelf_location', header: 'Location', sortable: true, render: (r) => <span className="font-mono text-xs">{r.shelf_location}</span> },
    { key: 'unit_price', header: 'Price', sortable: true, render: (r) => `$${r.unit_price.toFixed(2)}` },
    { key: 'health_status', header: 'Health', sortable: true, render: (r) => r.health_status ? <HealthBadge status={r.health_status} /> : <span className="text-text-secondary">--</span> },
  ]

  return (
    <div>
      <PageHeader title="Inventory" description={`${invData?.total ?? 0} SKUs tracked`} />

      {/* Low Stock Alerts */}
      {lowStock.length > 0 && (
        <Card className="mb-6">
          <h3 className="text-sm font-semibold text-text-primary mb-4">Low Stock Alerts ({lowStock.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-72 overflow-y-auto">
            {lowStock.map((item) => (
              <div key={item.sku_id} className="bg-navy-900 rounded-lg p-4 border border-navy-700">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{item.product_name}</p>
                    <p className="text-xs text-text-secondary font-mono">{item.sku_id}</p>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-accent-rose/15 text-accent-rose">
                    {item.stock_percentage.toFixed(0)}%
                  </span>
                </div>
                <div className="w-full h-2 bg-navy-700 rounded-full overflow-hidden mb-2">
                  <div
                    className={`h-full rounded-full ${item.stock_percentage < 30 ? 'bg-accent-rose' : 'bg-accent-amber'}`}
                    style={{ width: `${Math.min(100, item.stock_percentage)}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-text-secondary">
                  <span>Stock: {item.current_stock}/{item.reorder_threshold}</span>
                  {item.days_until_stockout != null && (
                    <span className="text-accent-rose">{item.days_until_stockout.toFixed(0)}d until stockout</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Full Inventory Table */}
      <Card className="p-0">
        <DataTable<InventoryItem>
          columns={columns}
          data={items}
          pageSize={25}
          keyField="sku_id"
        />
      </Card>
    </div>
  )
}
