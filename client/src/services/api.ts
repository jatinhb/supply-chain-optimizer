import axios from 'axios'
import type {
  Product,
  InventoryItem,
  Warehouse,
  Supplier,
  PurchaseOrder,
  DemandForecast,
  DashboardMetrics,
  ABCAnalysis,
  StockoutRisk,
  OptimizationRecommendation,
  InventoryTrend,
  User,
} from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth
export const authAPI = {
  login: async (email: string, password: string) => {
    const { data } = await api.post<{ user: User; token: string }>('/auth/login/', { email, password })
    return data
  },
  logout: async () => {
    await api.post('/auth/logout/')
  },
  me: async () => {
    const { data } = await api.get<User>('/auth/me/')
    return data
  },
}

// Products
export const productsAPI = {
  getAll: async (params?: { category?: string; search?: string }) => {
    const { data } = await api.get<{ results: Product[]; count: number }>('/products/', { params })
    return data
  },
  getById: async (id: string) => {
    const { data } = await api.get<Product>(`/products/${id}/`)
    return data
  },
  getForecast: async (id: string, weeks = 8) => {
    const { data } = await api.get<DemandForecast>(`/products/${id}/forecast/`, { params: { weeks } })
    return data
  },
}

// Inventory
export const inventoryAPI = {
  getAll: async (params?: { warehouse?: string; status?: string; abcClass?: string }) => {
    const { data } = await api.get<{ results: InventoryItem[]; count: number }>('/inventory/', { params })
    return data
  },
  getOptimization: async () => {
    const { data } = await api.get<OptimizationRecommendation[]>('/inventory/optimization/')
    return data
  },
  getStockoutRisks: async () => {
    const { data } = await api.get<StockoutRisk[]>('/inventory/stockout-risks/')
    return data
  },
  generateReorder: async (productIds: string[]) => {
    const { data } = await api.post<PurchaseOrder>('/inventory/reorder/', { product_ids: productIds })
    return data
  },
}

// Warehouses
export const warehousesAPI = {
  getAll: async () => {
    const { data } = await api.get<Warehouse[]>('/warehouses/')
    return data
  },
}

// Suppliers
export const suppliersAPI = {
  getAll: async () => {
    const { data } = await api.get<Supplier[]>('/suppliers/')
    return data
  },
}

// Purchase Orders
export const ordersAPI = {
  getAll: async (params?: { status?: string }) => {
    const { data } = await api.get<{ results: PurchaseOrder[]; count: number }>('/orders/', { params })
    return data
  },
  getById: async (id: string) => {
    const { data } = await api.get<PurchaseOrder>(`/orders/${id}/`)
    return data
  },
  create: async (order: Partial<PurchaseOrder>) => {
    const { data } = await api.post<PurchaseOrder>('/orders/', order)
    return data
  },
  updateStatus: async (id: string, status: string) => {
    const { data } = await api.patch<PurchaseOrder>(`/orders/${id}/`, { status })
    return data
  },
}

// Analytics
export const analyticsAPI = {
  getDashboard: async () => {
    const { data } = await api.get<DashboardMetrics>('/analytics/dashboard/')
    return data
  },
  getABCAnalysis: async () => {
    const { data } = await api.get<ABCAnalysis[]>('/analytics/abc-analysis/')
    return data
  },
  getTrends: async (days = 30) => {
    const { data } = await api.get<InventoryTrend[]>('/analytics/trends/', { params: { days } })
    return data
  },
}

// Forecasting
export const forecastingAPI = {
  getDemandForecast: async (params?: { category?: string; weeks?: number }) => {
    const { data } = await api.get<DemandForecast[]>('/forecast/demand/', { params })
    return data
  },
  runScenario: async (scenario: { demandChange: number; leadTimeChange: number }) => {
    const { data } = await api.post('/forecast/scenario/', scenario)
    return data
  },
}

export default api
