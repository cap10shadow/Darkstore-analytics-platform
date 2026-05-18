import { useState, useCallback } from 'react'
import { Search } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { useMutation } from '../hooks/useMutation'
import { detectOrderAnomalies, detectInventoryAnomalies, detectStaffAnomalies } from '../api/anomalies'
import PageHeader from '../components/shared/PageHeader'
import Card from '../components/shared/Card'
import Tabs from '../components/shared/Tabs'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorCard from '../components/shared/ErrorCard'
import EmptyState from '../components/shared/EmptyState'

const tabs = [
  { id: 'orders', label: 'Order Anomalies' },
  { id: 'inventory', label: 'Inventory Anomalies' },
  { id: 'staff', label: 'Staff Anomalies' },
]

export default function AnomaliesPage() {
  const [tab, setTab] = useState('orders')
  const [contamination, setContamination] = useState(0.05)

  const orderMutation = useMutation(
    useCallback((c: number) => detectOrderAnomalies(c), [])
  )
  const { data: invAnomalies, loading: invLoading, error: invErr, refetch: invRefetch } = useApi(detectInventoryAnomalies)
  const { data: staffAnomalies, loading: staffLoading, error: staffErr, refetch: staffRefetch } = useApi(detectStaffAnomalies)

  const handleDetectOrders = () => {
    orderMutation.execute(contamination)
  }

  const anomalyTypeColor = (type: string) => {
    const t = type.toLowerCase()
    if (t.includes('critical') || t.includes('severe') || t.includes('high')) return 'bg-accent-rose/15 text-accent-rose'
    if (t.includes('slow') || t.includes('delay') || t.includes('underperform')) return 'bg-accent-amber/15 text-accent-amber'
    if (t.includes('overstock') || t.includes('excess')) return 'bg-accent-blue/15 text-accent-blue'
    return 'bg-accent-violet/15 text-accent-violet'
  }

  return (
    <div>
      <PageHeader title="Anomaly Detection" description="Detect unusual patterns in orders, inventory, and staff performance" />

      <div className="mb-6">
        <Tabs tabs={tabs} active={tab} onChange={setTab} />
      </div>

      {/* Order Anomalies */}
      {tab === 'orders' && (
        <div>
          <Card className="mb-6">
            <div className="flex items-end gap-4">
              <div className="w-64">
                <label className="block text-xs text-text-secondary mb-1">
                  Contamination: {contamination.toFixed(2)}
                </label>
                <input
                  type="range"
                  min={0.01}
                  max={0.2}
                  step={0.01}
                  value={contamination}
                  onChange={(e) => setContamination(Number(e.target.value))}
                  className="w-full accent-accent-rose"
                />
                <div className="flex justify-between text-xs text-text-secondary mt-1">
                  <span>1%</span>
                  <span>20%</span>
                </div>
              </div>
              <button
                onClick={handleDetectOrders}
                disabled={orderMutation.loading}
                className="px-4 py-2 rounded-lg bg-accent-rose text-white font-medium text-sm hover:bg-accent-rose/80 disabled:opacity-40 transition-colors flex items-center gap-2"
              >
                <Search className="h-4 w-4" />
                {orderMutation.loading ? 'Detecting...' : 'Detect Anomalies'}
              </button>
            </div>
          </Card>

          {orderMutation.error && <ErrorCard message={orderMutation.error} />}

          {orderMutation.data && (
            <div>
              <p className="text-sm text-text-secondary mb-4">
                Found {orderMutation.data.total} anomalies (contamination: {orderMutation.data.contamination})
              </p>
              {orderMutation.data.anomalies.length === 0 ? (
                <EmptyState title="No anomalies" message="No order anomalies detected at this contamination level." />
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {orderMutation.data.anomalies.map((a) => (
                    <Card key={a.order_id}>
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-mono text-xs text-text-secondary">{a.order_id}</p>
                          <p className="text-sm font-medium text-text-primary mt-1">{a.reason}</p>
                        </div>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${anomalyTypeColor(a.anomaly_type)}`}>
                          {a.anomaly_type}
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-3 text-xs">
                        <div>
                          <span className="text-text-secondary">Items</span>
                          <p className="text-text-primary font-medium">{a.num_items}</p>
                        </div>
                        <div>
                          <span className="text-text-secondary">Fulfillment</span>
                          <p className="text-text-primary font-medium">{a.fulfillment_time_minutes.toFixed(1)}m</p>
                        </div>
                        <div>
                          <span className="text-text-secondary">Score</span>
                          <p className="text-accent-rose font-medium">{a.anomaly_score.toFixed(3)}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Inventory Anomalies */}
      {tab === 'inventory' && (
        <div>
          {invLoading ? (
            <LoadingSpinner message="Detecting inventory anomalies..." />
          ) : invErr ? (
            <ErrorCard message={invErr} onRetry={invRefetch} />
          ) : invAnomalies && invAnomalies.anomalies.length === 0 ? (
            <EmptyState title="No anomalies" message="No inventory anomalies detected." />
          ) : (
            <div>
              <p className="text-sm text-text-secondary mb-4">
                Found {invAnomalies?.total ?? 0} inventory anomalies
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {invAnomalies?.anomalies.map((a) => (
                  <Card key={a.sku_id}>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="text-sm font-medium text-text-primary">{a.product_name}</p>
                        <p className="font-mono text-xs text-text-secondary">{a.sku_id}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${anomalyTypeColor(a.anomaly_type)}`}>
                        {a.anomaly_type}
                      </span>
                    </div>
                    <p className="text-sm text-text-secondary mb-3">{a.reason}</p>
                    <div className="grid grid-cols-3 gap-3 text-xs">
                      <div>
                        <span className="text-text-secondary">Stock</span>
                        <p className="text-text-primary font-medium">{a.current_stock}</p>
                      </div>
                      <div>
                        <span className="text-text-secondary">Reorder At</span>
                        <p className="text-text-primary font-medium">{a.reorder_threshold}</p>
                      </div>
                      <div>
                        <span className="text-text-secondary">Z-Score</span>
                        <p className="text-accent-amber font-medium">{a.stock_zscore.toFixed(2)}</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Staff Anomalies */}
      {tab === 'staff' && (
        <div>
          {staffLoading ? (
            <LoadingSpinner message="Detecting staff anomalies..." />
          ) : staffErr ? (
            <ErrorCard message={staffErr} onRetry={staffRefetch} />
          ) : staffAnomalies && staffAnomalies.anomalies.length === 0 ? (
            <EmptyState title="No anomalies" message="No staff performance anomalies detected." />
          ) : (
            <div>
              <p className="text-sm text-text-secondary mb-4">
                Found {staffAnomalies?.total ?? 0} staff anomalies
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {staffAnomalies?.anomalies.map((a) => (
                  <Card key={a.staff_id}>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="text-sm font-medium text-text-primary">Staff: {a.staff_id}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${anomalyTypeColor(a.anomaly_type)}`}>
                        {a.anomaly_type}
                      </span>
                    </div>
                    <p className="text-sm text-text-secondary mb-3">{a.reason}</p>
                    <div className="grid grid-cols-3 gap-3 text-xs">
                      <div>
                        <span className="text-text-secondary">Orders</span>
                        <p className="text-text-primary font-medium">{a.total_orders}</p>
                      </div>
                      <div>
                        <span className="text-text-secondary">Avg Time</span>
                        <p className="text-text-primary font-medium">{a.avg_fulfillment_time.toFixed(1)}m</p>
                      </div>
                      <div>
                        <span className="text-text-secondary">Delay Rate</span>
                        <p className="text-accent-rose font-medium">{(a.delay_rate * 100).toFixed(1)}%</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
