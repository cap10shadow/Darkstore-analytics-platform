import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import OverviewPage from './pages/OverviewPage'
import OrdersPage from './pages/OrdersPage'
import InventoryPage from './pages/InventoryPage'
import ForecastPage from './pages/ForecastPage'
import RoutesPage from './pages/RoutesPage'
import AnomaliesPage from './pages/AnomaliesPage'
import AffinityPage from './pages/AffinityPage'
import SimulationPage from './pages/SimulationPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/overview" replace />} />
        <Route path="/overview" element={<OverviewPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/forecast" element={<ForecastPage />} />
        <Route path="/routes" element={<RoutesPage />} />
        <Route path="/anomalies" element={<AnomaliesPage />} />
        <Route path="/affinity" element={<AffinityPage />} />
        <Route path="/simulation" element={<SimulationPage />} />
      </Route>
    </Routes>
  )
}
