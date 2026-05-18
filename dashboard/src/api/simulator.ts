import { post } from './client'
import type { SimulationRequest, SimulationResponse } from '../types/simulator'

export const runSimulation = (req: SimulationRequest) =>
  post<SimulationResponse>('/api/v1/simulate/scenario', req)
