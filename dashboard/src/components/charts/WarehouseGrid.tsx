import type { RouteOptimizeResponse } from '../../types/routes'

interface WarehouseGridProps {
  route: RouteOptimizeResponse
}

export default function WarehouseGrid({ route }: WarehouseGridProps) {
  const padding = 40
  const width = 600
  const height = 400

  if (!route.coordinates || route.coordinates.length === 0) {
    return <p className="text-text-secondary text-center py-10">No route data</p>
  }

  const coords = route.coordinates
  const xs = coords.map((c) => c[0])
  const ys = coords.map((c) => c[1])
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const rangeX = maxX - minX || 1
  const rangeY = maxY - minY || 1

  const scale = (x: number, y: number): [number, number] => [
    padding + ((x - minX) / rangeX) * (width - 2 * padding),
    padding + ((y - minY) / rangeY) * (height - 2 * padding),
  ]

  const scaled = coords.map(([x, y]) => scale(x, y))

  // Grid lines
  const gridRows = 10
  const gridCols = 12
  const gridLines = []
  for (let i = 0; i <= gridRows; i++) {
    const y = padding + (i / gridRows) * (height - 2 * padding)
    gridLines.push(<line key={`h${i}`} x1={padding} y1={y} x2={width - padding} y2={y} stroke="#2a3650" strokeWidth={0.5} />)
  }
  for (let i = 0; i <= gridCols; i++) {
    const x = padding + (i / gridCols) * (width - 2 * padding)
    gridLines.push(<line key={`v${i}`} x1={x} y1={padding} x2={x} y2={height - padding} stroke="#2a3650" strokeWidth={0.5} />)
  }

  // Path
  const pathD = scaled.map(([x, y], i) => `${i === 0 ? 'M' : 'L'} ${x} ${y}`).join(' ')

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ maxHeight: '400px' }}>
      <rect x={0} y={0} width={width} height={height} fill="#0f1729" rx={8} />
      {gridLines}

      {/* Animated route path */}
      <path
        d={pathD}
        fill="none"
        stroke="#06b6d4"
        strokeWidth={2}
        strokeDasharray="8 4"
        strokeLinecap="round"
      >
        <animate
          attributeName="stroke-dashoffset"
          values="24;0"
          dur="1s"
          repeatCount="indefinite"
        />
      </path>

      {/* Stops */}
      {scaled.map(([x, y], i) => (
        <g key={i}>
          <circle
            cx={x}
            cy={y}
            r={i === 0 ? 8 : 6}
            fill={i === 0 ? '#10b981' : '#06b6d4'}
            stroke="#0f1729"
            strokeWidth={2}
          />
          <text
            x={x}
            y={y - 12}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize={10}
            fontFamily="monospace"
          >
            {route.route[i]}
          </text>
          {i === 0 && (
            <text x={x} y={y + 22} textAnchor="middle" fill="#10b981" fontSize={9}>
              START
            </text>
          )}
        </g>
      ))}

      {/* Row labels */}
      {['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map((letter, i) => (
        <text
          key={letter}
          x={padding - 15}
          y={padding + (i / 7) * (height - 2 * padding)}
          fill="#3a4a6a"
          fontSize={10}
          textAnchor="middle"
          dominantBaseline="middle"
        >
          {letter}
        </text>
      ))}
    </svg>
  )
}
