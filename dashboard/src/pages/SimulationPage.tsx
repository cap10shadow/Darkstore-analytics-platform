import { useState, useCallback } from 'react'
import { Play, Zap, TruckIcon, Clock, AlertTriangle, ShoppingCart, Activity, ChevronDown, ChevronUp } from 'lucide-react'
import { useMutation } from '../hooks/useMutation'
import { runSimulation } from '../api/simulator'
import PageHeader from '../components/shared/PageHeader'
import Card from '../components/shared/Card'
import KpiCard from '../components/shared/KpiCard'
import ErrorCard from '../components/shared/ErrorCard'
import EventDistributionChart from '../components/charts/EventDistributionChart'
import type { SimulationRequest } from '../types/simulator'

interface ScenarioConfig {
  type: 'normal' | 'flash_sale' | 'supply_delay'
  label: string
  description: string
  icon: React.ReactNode
  activeBg: string
  activeBorder: string
  activeIconBg: string
  activeText: string
}

const scenarios: ScenarioConfig[] = [
  {
    type: 'normal',
    label: 'Normal Operations',
    description: 'Steady-state darkstore operations',
    icon: <Play className="h-5 w-5" />,
    activeBg: 'bg-accent-cyan/10',
    activeBorder: 'border-accent-cyan/50',
    activeIconBg: 'bg-accent-cyan/20',
    activeText: 'text-accent-cyan',
  },
  {
    type: 'flash_sale',
    label: 'Flash Sale',
    description: 'Sudden spike in order volume',
    icon: <Zap className="h-5 w-5" />,
    activeBg: 'bg-accent-amber/10',
    activeBorder: 'border-accent-amber/50',
    activeIconBg: 'bg-accent-amber/20',
    activeText: 'text-accent-amber',
  },
  {
    type: 'supply_delay',
    label: 'Supply Delay',
    description: 'Supplier delivery delays',
    icon: <TruckIcon className="h-5 w-5" />,
    activeBg: 'bg-accent-rose/10',
    activeBorder: 'border-accent-rose/50',
    activeIconBg: 'bg-accent-rose/20',
    activeText: 'text-accent-rose',
  },
]

export default function SimulationPage() {
  const [selectedScenario, setSelectedScenario] = useState<'normal' | 'flash_sale' | 'supply_delay'>('normal')
  const [durationHours, setDurationHours] = useState(8)
  const [ordersPerHour, setOrdersPerHour] = useState(20)
  const [upliftFactor, setUpliftFactor] = useState(5.0)
  const [delayDays, setDelayDays] = useState(3)
  const [showAllEvents, setShowAllEvents] = useState(false)

  const mutation = useMutation(
    useCallback((req: SimulationRequest) => runSimulation(req), [])
  )

  const handleRun = () => {
    const req: SimulationRequest = {
      scenario_type: selectedScenario,
      duration_hours: durationHours,
    }
    if (selectedScenario === 'normal') req.orders_per_hour = ordersPerHour
    if (selectedScenario === 'flash_sale') req.uplift_factor = upliftFactor
    if (selectedScenario === 'supply_delay') req.delay_days = delayDays
    mutation.execute(req)
  }

  const result = mutation.data

  return (
    <div>
      <PageHeader title="Event Simulation" description="Simulate darkstore scenarios and analyze outcomes" />

      {/* Scenario Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {scenarios.map((s) => (
          <button
            key={s.type}
            onClick={() => setSelectedScenario(s.type)}
            className={`text-left p-5 rounded-xl border transition-all ${
              selectedScenario === s.type
                ? `${s.activeBg} ${s.activeBorder}`
                : 'bg-navy-800 border-navy-700 hover:border-navy-600'
            }`}
          >
            <div className={`inline-flex p-2 rounded-lg mb-3 ${selectedScenario === s.type ? s.activeIconBg : 'bg-navy-700'}`}>
              <span className={selectedScenario === s.type ? s.activeText : 'text-text-secondary'}>
                {s.icon}
              </span>
            </div>
            <p className="font-medium text-text-primary">{s.label}</p>
            <p className="text-xs text-text-secondary mt-1">{s.description}</p>
          </button>
        ))}
      </div>

      {/* Parameters */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-end gap-6">
          <div className="w-48">
            <label className="block text-xs text-text-secondary mb-1">Duration: {durationHours}h</label>
            <input
              type="range"
              min={1}
              max={24}
              value={durationHours}
              onChange={(e) => setDurationHours(Number(e.target.value))}
              className="w-full accent-accent-cyan"
            />
          </div>

          {selectedScenario === 'normal' && (
            <div className="w-48">
              <label className="block text-xs text-text-secondary mb-1">Orders/Hour: {ordersPerHour}</label>
              <input
                type="range"
                min={5}
                max={100}
                value={ordersPerHour}
                onChange={(e) => setOrdersPerHour(Number(e.target.value))}
                className="w-full accent-accent-cyan"
              />
            </div>
          )}

          {selectedScenario === 'flash_sale' && (
            <div className="w-48">
              <label className="block text-xs text-text-secondary mb-1">Uplift Factor: {upliftFactor.toFixed(1)}x</label>
              <input
                type="range"
                min={2}
                max={10}
                step={0.5}
                value={upliftFactor}
                onChange={(e) => setUpliftFactor(Number(e.target.value))}
                className="w-full accent-accent-amber"
              />
            </div>
          )}

          {selectedScenario === 'supply_delay' && (
            <div className="w-48">
              <label className="block text-xs text-text-secondary mb-1">Delay Days: {delayDays}</label>
              <input
                type="range"
                min={1}
                max={7}
                value={delayDays}
                onChange={(e) => setDelayDays(Number(e.target.value))}
                className="w-full accent-accent-rose"
              />
            </div>
          )}

          <button
            onClick={handleRun}
            disabled={mutation.loading}
            className="px-5 py-2 rounded-lg bg-accent-cyan text-navy-900 font-medium text-sm hover:bg-accent-cyan/80 disabled:opacity-40 transition-colors flex items-center gap-2"
          >
            <Play className="h-4 w-4" />
            {mutation.loading ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>
      </Card>

      {mutation.error && <ErrorCard message={mutation.error} />}

      {result && (
        <>
          {/* Metrics */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <KpiCard
              label="Total Events"
              value={result.metrics.total_events.toLocaleString()}
              icon={<Activity className="h-5 w-5 text-cyan-400" />}
              color="bg-accent-cyan/10"
            />
            <KpiCard
              label="Total Orders"
              value={result.metrics.total_orders.toLocaleString()}
              icon={<ShoppingCart className="h-5 w-5 text-blue-400" />}
              color="bg-accent-blue/10"
            />
            <KpiCard
              label="Avg Pick Time"
              value={`${result.metrics.avg_pick_time_minutes.toFixed(1)}m`}
              icon={<Clock className="h-5 w-5 text-violet-400" />}
              color="bg-accent-violet/10"
            />
            <KpiCard
              label="Alerts Generated"
              value={result.metrics.total_alerts.toLocaleString()}
              icon={<AlertTriangle className="h-5 w-5 text-rose-400" />}
              color="bg-accent-rose/10"
            />
          </div>

          {/* Event Distribution Chart */}
          <Card className="mb-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">Event Distribution</h3>
            <EventDistributionChart eventCounts={result.metrics.event_counts} />
          </Card>

          {/* Event Timeline */}
          <Card>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-semibold text-text-primary">
                Event Timeline ({showAllEvents ? result.events.length : Math.min(50, result.events.length)} of {result.events.length})
              </h3>
              {result.events.length > 50 && (
                <button
                  onClick={() => setShowAllEvents(!showAllEvents)}
                  className="flex items-center gap-1 text-xs text-accent-cyan hover:text-accent-cyan/80"
                >
                  {showAllEvents ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                  {showAllEvents ? 'Show less' : 'Show all'}
                </button>
              )}
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {(showAllEvents ? result.events : result.events.slice(0, 50)).map((evt) => {
                const typeColor = evt.event_type.includes('alert') || evt.event_type.includes('anomaly')
                  ? 'text-accent-rose'
                  : evt.event_type.includes('order')
                    ? 'text-accent-cyan'
                    : 'text-accent-amber'

                return (
                  <div key={evt.event_id} className="flex items-start gap-3 py-2 border-b border-navy-700/30">
                    <span className="text-xs text-text-secondary font-mono whitespace-nowrap min-w-[140px]">
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`text-xs font-medium min-w-[120px] ${typeColor}`}>
                      {evt.event_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-text-secondary truncate">
                      {Object.entries(evt.payload).slice(0, 3).map(([k, v]) => `${k}: ${v}`).join(' | ')}
                    </span>
                  </div>
                )
              })}
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
