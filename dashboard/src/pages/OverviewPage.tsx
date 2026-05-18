import { useEffect } from 'react'
import {
  ShoppingCart,
  DollarSign,
  Clock,
  AlertTriangle,
  Timer,
  Layers,
  PackageX,
  HeartPulse,
} from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { fetchKPIs, fetchOrders, fetchAlerts } from '../api/data'
import PageHeader from '../components/shared/PageHeader'
import KpiCard from '../components/shared/KpiCard'
import Card from '../components/shared/Card'
import StatusBadge from '../components/shared/StatusBadge'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorCard from '../components/shared/ErrorCard'
import OrderStatusPie from '../components/charts/OrderStatusPie'
import AlertsSummaryChart from '../components/charts/AlertsSummaryChart'

export default function OverviewPage() {
  const { data: kpis, loading: kLoad, error: kErr, refetch: kRefetch } = useApi(fetchKPIs)
  const { data: ordersData, loading: oLoad, refetch: oRefetch } = useApi(() => fetchOrders(1000))
  const { data: alertsData, loading: aLoad, refetch: aRefetch } = useApi(fetchAlerts)

  // Auto-refresh every 30s
  useEffect(() => {
    const interval = setInterval(() => {
      kRefetch()
      oRefetch()
      aRefetch()
    }, 30000)
    return () => clearInterval(interval)
  }, [kRefetch, oRefetch, aRefetch])

  if (kLoad || oLoad || aLoad) return <LoadingSpinner message="Loading dashboard..." />
  if (kErr) return <ErrorCard message={kErr} onRetry={kRefetch} />

  const orders = ordersData?.orders ?? []
  const alerts = alertsData?.alerts ?? []

  const fmt = (n: number) => n.toLocaleString()
  const fmtCurrency = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
  const fmtPct = (n: number) => `${(n * 100).toFixed(1)}%`

  return (
    <div>
      <PageHeader title="Overview" description="Real-time darkstore operations dashboard" />

      {/* KPI Cards */}
      {kpis && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <KpiCard label="Orders Today" value={fmt(kpis.total_orders_today)} icon={<ShoppingCart className="h-5 w-5 text-cyan-400" />} color="bg-accent-cyan/10" />
          <KpiCard label="Revenue" value={fmtCurrency(kpis.revenue_today)} icon={<DollarSign className="h-5 w-5 text-emerald-400" />} color="bg-accent-emerald/10" subtitle={`Total: ${fmtCurrency(kpis.total_revenue)}`} />
          <KpiCard label="On-Time Rate" value={fmtPct(kpis.on_time_rate)} icon={<Clock className="h-5 w-5 text-blue-400" />} color="bg-accent-blue/10" />
          <KpiCard label="Active Alerts" value={fmt(kpis.active_alerts)} icon={<AlertTriangle className="h-5 w-5 text-rose-400" />} color="bg-accent-rose/10" subtitle={`${kpis.critical_alerts} critical`} />
          <KpiCard label="Avg Fulfillment" value={`${kpis.avg_fulfillment_minutes.toFixed(1)}m`} icon={<Timer className="h-5 w-5 text-violet-400" />} color="bg-accent-violet/10" />
          <KpiCard label="Backlog" value={fmt(kpis.backlog)} icon={<Layers className="h-5 w-5 text-amber-400" />} color="bg-accent-amber/10" />
          <KpiCard label="Low Stock Items" value={fmt(kpis.low_stock_count)} icon={<PackageX className="h-5 w-5 text-amber-400" />} color="bg-accent-amber/10" />
          <KpiCard label="Stock Health" value={fmtPct(kpis.stock_health_rate)} icon={<HeartPulse className="h-5 w-5 text-emerald-400" />} color="bg-accent-emerald/10" subtitle={`${kpis.total_skus} SKUs`} />
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <Card>
          <h3 className="text-sm font-semibold text-text-primary mb-4">Order Status Distribution</h3>
          <OrderStatusPie orders={orders} />
        </Card>
        <Card>
          <h3 className="text-sm font-semibold text-text-primary mb-4">Alerts by Severity</h3>
          <AlertsSummaryChart alerts={alerts} />
        </Card>
      </div>

      {/* Recent Orders */}
      <Card>
        <h3 className="text-sm font-semibold text-text-primary mb-4">Recent Orders</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-navy-700">
                <th className="text-left text-text-secondary font-medium px-4 py-2">Order ID</th>
                <th className="text-left text-text-secondary font-medium px-4 py-2">Status</th>
                <th className="text-left text-text-secondary font-medium px-4 py-2">Items</th>
                <th className="text-left text-text-secondary font-medium px-4 py-2">Value</th>
                <th className="text-left text-text-secondary font-medium px-4 py-2">Fulfillment</th>
                <th className="text-left text-text-secondary font-medium px-4 py-2">Delayed</th>
              </tr>
            </thead>
            <tbody>
              {orders.slice(0, 5).map((o) => (
                <tr key={o.order_id} className="border-b border-navy-700/50">
                  <td className="px-4 py-2 text-text-primary font-mono text-xs">{o.order_id}</td>
                  <td className="px-4 py-2"><StatusBadge status={o.status} /></td>
                  <td className="px-4 py-2 text-text-primary">{o.num_items}</td>
                  <td className="px-4 py-2 text-text-primary">{fmtCurrency(o.total_value)}</td>
                  <td className="px-4 py-2 text-text-primary">{o.fulfillment_time_minutes.toFixed(1)}m</td>
                  <td className="px-4 py-2">
                    {o.is_delayed ? (
                      <span className="text-accent-rose text-xs font-medium">Delayed</span>
                    ) : (
                      <span className="text-accent-emerald text-xs">On time</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
