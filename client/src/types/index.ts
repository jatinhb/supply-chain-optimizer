export type StockStatus = 'in_stock' | 'low_stock' | 'out_of_stock' | 'overstock' | 'reserved'

export type ABCClass = 'A' | 'B' | 'C'

export interface Product {
  id: string
  sku: string
  name: string
  category: string
  description?: string
  unitCost: number
  unitPrice: number
  supplier: string
  leadTimeDays: number
  minOrderQty?: number
  abcClass: ABCClass
}

export interface InventoryItem {
  id: string
  productId: string
  sku: string
  name: string
  category: string
  quantity: number
  reorderPoint: number
  maxStock: number
  unitCost: number
  totalValue: number
  warehouseId: string
  location: string
  lastUpdated: string
  status: StockStatus
}

export interface Warehouse {
  id: string
  name: string
  code?: string
  location: string
  capacity: number
  currentUtilization: number
  isActive?: boolean
}

export interface Supplier {
  id: string
  name: string
  contactEmail?: string
  leadTimeDays: number
  reliabilityScore: number
  minOrderValue?: number
}

export interface PurchaseOrder {
  id: string
  supplierId: string
  supplierName: string
  items: PurchaseOrderItem[]
  totalAmount: number
  status: 'draft' | 'pending' | 'approved' | 'shipped' | 'delivered' | 'cancelled'
  createdAt: string
  expectedDelivery: string
  priority: 'low' | 'medium' | 'high' | 'critical'
}

export interface PurchaseOrderItem {
  productId: string
  sku: string
  name: string
  quantity: number
  unitCost: number
  totalCost: number
}

export interface DemandForecast {
  productId: string
  sku?: string
  productName?: string
  forecasts: ForecastPoint[]
  accuracy: number
  trend: 'up' | 'down' | 'stable'
}

export interface ForecastPoint {
  date: string
  predicted: number
  lower: number
  upper: number
  actual?: number
}

export interface DashboardMetrics {
  totalProducts: number
  totalWarehouses: number
  totalValue: number
  turnoverRate: number
  stockoutRate: number
  forecastAccuracy: number
  pendingOrders: number
  lowStockItems: number
}

export interface ABCAnalysis {
  aItems: ABCClassData
  bItems: ABCClassData
  cItems: ABCClassData
  lastCalculated: string
}

export interface ABCClassData {
  count: number
  percentage: number
  valuePercentage: number
  items: Product[]
}

export interface StockoutRisk {
  productId: string
  sku: string
  productName: string
  currentStock: number
  dailyDemand: number
  daysOfStock: number
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  suggestedAction: string
}

export interface ReorderAlert {
  id: string
  productId: string
  sku: string
  productName: string
  currentStock: number
  reorderPoint: number
  suggestedQuantity: number
  estimatedCost: number
  priority: 'low' | 'medium' | 'high' | 'critical'
  createdAt: string
}

export interface OptimizationRecommendation {
  id: string
  type: 'reorder' | 'markdown' | 'transfer' | 'discontinue'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  productId: string
  sku: string
  productName: string
  description: string
  potentialSavings: number
  suggestedAction: string
}

export interface InventoryTrend {
  date: string
  value: number
  units: number
  turnover: number
}

export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'manager' | 'analyst' | 'viewer'
  token?: string
}
