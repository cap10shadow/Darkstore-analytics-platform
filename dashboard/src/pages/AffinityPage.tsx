import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchAffinityPairs, fetchRecommendations } from '../api/affinity'
import PageHeader from '../components/shared/PageHeader'
import Card from '../components/shared/Card'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorCard from '../components/shared/ErrorCard'
import EmptyState from '../components/shared/EmptyState'

const priorityColors: Record<string, string> = {
  high: 'bg-accent-rose/15 text-accent-rose',
  medium: 'bg-accent-amber/15 text-accent-amber',
  low: 'bg-accent-blue/15 text-accent-blue',
}

export default function AffinityPage() {
  const [minLift, setMinLift] = useState(1.0)
  const [topN, setTopN] = useState(20)

  const { data: pairsData, loading: pLoad, error: pErr, refetch: pRefetch } = useApi(
    () => fetchAffinityPairs(topN, minLift),
    [topN, minLift]
  )
  const { data: recsData, loading: rLoad, error: rErr, refetch: rRefetch } = useApi(fetchRecommendations)

  if (pLoad || rLoad) return <LoadingSpinner message="Analyzing product affinity..." />
  if (pErr) return <ErrorCard message={pErr} onRetry={pRefetch} />

  const pairs = pairsData?.pairs ?? []
  const recs = recsData?.recommendations ?? []

  return (
    <div>
      <PageHeader title="Product Affinity" description="Co-purchase analysis and co-location recommendations" />

      {/* Controls */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-end gap-6">
          <div className="w-64">
            <label className="block text-xs text-text-secondary mb-1">Min Lift: {minLift.toFixed(1)}</label>
            <input
              type="range"
              min={0.5}
              max={5.0}
              step={0.1}
              value={minLift}
              onChange={(e) => setMinLift(Number(e.target.value))}
              className="w-full accent-accent-violet"
            />
            <div className="flex justify-between text-xs text-text-secondary mt-1">
              <span>0.5</span>
              <span>5.0</span>
            </div>
          </div>
          <div className="w-32">
            <label className="block text-xs text-text-secondary mb-1">Top N</label>
            <input
              type="number"
              min={5}
              max={100}
              value={topN}
              onChange={(e) => setTopN(Number(e.target.value))}
              className="w-full bg-navy-900 border border-navy-700 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-violet"
            />
          </div>
        </div>
      </Card>

      {/* Affinity Pairs Table */}
      <Card className="mb-6">
        <h3 className="text-sm font-semibold text-text-primary mb-4">Affinity Pairs ({pairs.length})</h3>
        {pairs.length === 0 ? (
          <EmptyState title="No pairs" message="No affinity pairs match the current filters." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700">
                  <th className="text-left text-text-secondary font-medium px-4 py-2">Product A</th>
                  <th className="text-left text-text-secondary font-medium px-4 py-2">Product B</th>
                  <th className="text-left text-text-secondary font-medium px-4 py-2">Co-Occurrences</th>
                  <th className="text-left text-text-secondary font-medium px-4 py-2">Confidence</th>
                  <th className="text-left text-text-secondary font-medium px-4 py-2">Lift</th>
                  <th className="text-left text-text-secondary font-medium px-4 py-2">Affinity</th>
                </tr>
              </thead>
              <tbody>
                {pairs.map((p, i) => (
                  <tr key={i} className="border-b border-navy-700/50 hover:bg-navy-700/30">
                    <td className="px-4 py-2">
                      <p className="text-text-primary">{p.product_a}</p>
                      <p className="text-xs text-text-secondary font-mono">{p.sku_a}</p>
                    </td>
                    <td className="px-4 py-2">
                      <p className="text-text-primary">{p.product_b}</p>
                      <p className="text-xs text-text-secondary font-mono">{p.sku_b}</p>
                    </td>
                    <td className="px-4 py-2 text-text-primary">{p.co_occurrences}</td>
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-navy-900 rounded-full overflow-hidden">
                          <div className="h-full bg-accent-cyan rounded-full" style={{ width: `${Math.min(100, p.confidence_a_to_b * 100)}%` }} />
                        </div>
                        <span className="text-text-primary text-xs">{(p.confidence_a_to_b * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-navy-900 rounded-full overflow-hidden">
                          <div className="h-full bg-accent-violet rounded-full" style={{ width: `${Math.min(100, (p.lift / 5) * 100)}%` }} />
                        </div>
                        <span className="text-text-primary text-xs">{p.lift.toFixed(2)}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2 text-accent-emerald font-medium">{p.affinity_score.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Co-location Recommendations */}
      {rErr && <ErrorCard message={rErr} onRetry={rRefetch} />}
      {recs.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-text-primary mb-4">Co-Location Recommendations ({recs.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recs.map((r, i) => (
              <Card key={i}>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{r.product_a} + {r.product_b}</p>
                    <p className="text-xs text-text-secondary font-mono">{r.sku_a} / {r.sku_b}</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${priorityColors[r.priority.toLowerCase()] || 'bg-navy-700 text-text-secondary'}`}>
                    {r.priority}
                  </span>
                </div>
                <p className="text-sm text-text-secondary mb-3">{r.recommendation}</p>
                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div>
                    <span className="text-text-secondary">Current Distance</span>
                    <p className="text-text-primary font-medium">{r.current_distance.toFixed(0)}m</p>
                  </div>
                  <div>
                    <span className="text-text-secondary">Weekly Co-Buys</span>
                    <p className="text-text-primary font-medium">{r.co_occurrences_weekly}</p>
                  </div>
                  <div>
                    <span className="text-text-secondary">Annual Time Saved</span>
                    <p className="text-accent-emerald font-medium">{r.estimated_annual_time_saved_hours.toFixed(1)}h</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
