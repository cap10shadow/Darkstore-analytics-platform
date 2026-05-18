import { useState, useCallback } from 'react'
import { X, MapPin, Clock, TrendingDown, Navigation } from 'lucide-react'
import { useMutation } from '../hooks/useMutation'
import { optimizeRoute } from '../api/routes'
import PageHeader from '../components/shared/PageHeader'
import Card from '../components/shared/Card'
import KpiCard from '../components/shared/KpiCard'
import ErrorCard from '../components/shared/ErrorCard'
import WarehouseGrid from '../components/charts/WarehouseGrid'
import type { RouteOptimizeRequest } from '../types/routes'

const METHODS = [
  { value: 'nn+2opt', label: 'NN + 2-Opt (Best)' },
  { value: 'nn', label: 'Nearest Neighbor' },
  { value: '2opt', label: '2-Opt' },
]

export default function RoutesPage() {
  const [locations, setLocations] = useState<string[]>([])
  const [inputVal, setInputVal] = useState('')
  const [method, setMethod] = useState('nn+2opt')

  const mutation = useMutation(
    useCallback((req: RouteOptimizeRequest) => optimizeRoute(req), [])
  )

  const addLocation = () => {
    const val = inputVal.trim().toUpperCase()
    if (val && !locations.includes(val)) {
      setLocations([...locations, val])
    }
    setInputVal('')
  }

  const removeLocation = (loc: string) => {
    setLocations(locations.filter((l) => l !== loc))
  }

  const handleOptimize = () => {
    if (locations.length < 2) return
    mutation.execute({ pick_list: locations, method })
  }

  const result = mutation.data

  return (
    <div>
      <PageHeader title="Route Optimization" description="Optimize warehouse picking routes using TSP algorithms" />

      {/* Controls */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-end gap-4 mb-4">
          <div className="flex-1 min-w-[250px]">
            <label className="block text-xs text-text-secondary mb-1">Shelf Locations</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addLocation()}
                placeholder="e.g. A05-3"
                className="flex-1 bg-navy-900 border border-navy-700 rounded-lg px-3 py-2 text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-accent-cyan font-mono"
              />
              <button
                onClick={addLocation}
                className="px-3 py-2 rounded-lg bg-navy-700 text-text-primary text-sm hover:bg-navy-600 transition-colors"
              >
                Add
              </button>
            </div>
          </div>
          <div className="w-48">
            <label className="block text-xs text-text-secondary mb-1">Method</label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="w-full bg-navy-900 border border-navy-700 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
            >
              {METHODS.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleOptimize}
            disabled={locations.length < 2 || mutation.loading}
            className="px-4 py-2 rounded-lg bg-accent-cyan text-navy-900 font-medium text-sm hover:bg-accent-cyan/80 disabled:opacity-40 transition-colors"
          >
            {mutation.loading ? 'Optimizing...' : 'Optimize Route'}
          </button>
        </div>

        {/* Location Tags */}
        {locations.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {locations.map((loc) => (
              <span
                key={loc}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent-cyan/10 text-accent-cyan text-sm font-mono"
              >
                <MapPin className="h-3 w-3" />
                {loc}
                <button onClick={() => removeLocation(loc)} className="hover:text-white">
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </Card>

      {mutation.error && <ErrorCard message={mutation.error} />}

      {result && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <KpiCard
              label="Optimized Distance"
              value={`${result.distance.toFixed(1)}m`}
              icon={<Navigation className="h-5 w-5 text-cyan-400" />}
              color="bg-accent-cyan/10"
            />
            <KpiCard
              label="Naive Distance"
              value={`${result.naive_distance.toFixed(1)}m`}
              icon={<Navigation className="h-5 w-5 text-text-secondary" />}
              color="bg-navy-700"
            />
            <KpiCard
              label="Improvement"
              value={`${result.improvement_percent.toFixed(1)}%`}
              icon={<TrendingDown className="h-5 w-5 text-emerald-400" />}
              color="bg-accent-emerald/10"
            />
            <KpiCard
              label="Estimated Time"
              value={`${result.estimated_time_minutes.toFixed(1)}m`}
              icon={<Clock className="h-5 w-5 text-violet-400" />}
              color="bg-accent-violet/10"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Warehouse Grid */}
            <Card className="col-span-2">
              <h3 className="text-sm font-semibold text-text-primary mb-4">Warehouse Route Visualization</h3>
              <WarehouseGrid route={result} />
            </Card>

            {/* Route Sequence */}
            <Card>
              <h3 className="text-sm font-semibold text-text-primary mb-4">Route Sequence ({result.num_stops} stops)</h3>
              <div className="space-y-2">
                {result.route.map((loc, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${i === 0 ? 'bg-accent-emerald text-navy-900' : 'bg-navy-700 text-text-primary'}`}>
                      {i + 1}
                    </span>
                    <span className="font-mono text-sm text-text-primary">{loc}</span>
                    {i === 0 && <span className="text-xs text-accent-emerald">(start)</span>}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
