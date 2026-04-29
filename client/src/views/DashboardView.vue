<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type {
  DashboardMetrics,
  DemandForecast,
  ABCAnalysis,
  StockoutRisk,
  ReorderAlert
} from '@/types'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import MetricCard from '@/components/dashboard/MetricCard.vue'
import ForecastChart from '@/components/dashboard/ForecastChart.vue'
import ABCChart from '@/components/dashboard/ABCChart.vue'
import StockoutRisks from '@/components/dashboard/StockoutRisks.vue'

const loading = ref(true)

// Mock dashboard data
const metrics = ref<DashboardMetrics>({
  totalProducts: 2847,
  totalWarehouses: 12,
  totalValue: 4250000,
  turnoverRate: 8.4,
  stockoutRate: 2.3,
  forecastAccuracy: 94.2,
  pendingOrders: 156,
  lowStockItems: 47,
})

const forecasts = ref<DemandForecast[]>([
  {
    productId: 'P001',
    forecasts: [
      { date: '2024-01-15', predicted: 1200, lower: 1050, upper: 1350 },
      { date: '2024-01-22', predicted: 1350, lower: 1180, upper: 1520 },
      { date: '2024-01-29', predicted: 1280, lower: 1100, upper: 1460 },
      { date: '2024-02-05', predicted: 1420, lower: 1230, upper: 1610 },
      { date: '2024-02-12', predicted: 1380, lower: 1190, upper: 1570 },
      { date: '2024-02-19', predicted: 1520, lower: 1310, upper: 1730 },
      { date: '2024-02-26', predicted: 1480, lower: 1270, upper: 1690 },
      { date: '2024-03-04', predicted: 1600, lower: 1380, upper: 1820 },
    ],
    accuracy: 94.5,
    trend: 'up',
  },
])

const abcAnalysis = ref<ABCAnalysis>({
  aItems: { count: 284, percentage: 10, valuePercentage: 70, items: [] },
  bItems: { count: 569, percentage: 20, valuePercentage: 20, items: [] },
  cItems: { count: 1994, percentage: 70, valuePercentage: 10, items: [] },
  lastCalculated: new Date().toISOString(),
})

const stockoutRisks = ref<StockoutRisk[]>([
  {
    productId: 'P1234',
    sku: 'SKU-7891',
    productName: 'Industrial Bearings 6205-2RS',
    currentStock: 45,
    dailyDemand: 12,
    daysOfStock: 3,
    riskLevel: 'critical',
    suggestedAction: 'Order Now',
  },
  {
    productId: 'P2456',
    sku: 'SKU-4523',
    productName: 'Hydraulic Pump HP-200',
    currentStock: 120,
    dailyDemand: 15,
    daysOfStock: 8,
    riskLevel: 'high',
    suggestedAction: 'Expedite Order',
  },
  {
    productId: 'P3789',
    sku: 'SKU-8901',
    productName: 'Conveyor Belt 500mm',
    currentStock: 250,
    dailyDemand: 18,
    daysOfStock: 14,
    riskLevel: 'medium',
    suggestedAction: 'Schedule Reorder',
  },
  {
    productId: 'P4012',
    sku: 'SKU-2345',
    productName: 'Motor Controller VFD-15',
    currentStock: 85,
    dailyDemand: 3,
    daysOfStock: 28,
    riskLevel: 'low',
    suggestedAction: 'Monitor',
  },
])

const reorderAlerts = ref<ReorderAlert[]>([
  {
    id: 'RA001',
    productId: 'P1234',
    sku: 'SKU-7891',
    productName: 'Industrial Bearings 6205-2RS',
    currentStock: 45,
    reorderPoint: 100,
    suggestedQuantity: 500,
    estimatedCost: 2500,
    priority: 'critical',
    createdAt: new Date().toISOString(),
  },
  {
    id: 'RA002',
    productId: 'P2456',
    sku: 'SKU-4523',
    productName: 'Hydraulic Pump HP-200',
    currentStock: 120,
    reorderPoint: 150,
    suggestedQuantity: 200,
    estimatedCost: 15000,
    priority: 'high',
    createdAt: new Date().toISOString(),
  },
])

const recentActivity = ref([
  { id: 1, action: 'Purchase Order Created', item: 'PO-2024-0156', time: '5 min ago', icon: 'Document' },
  { id: 2, action: 'Stock Received', item: 'SKU-4523 (+250 units)', time: '1 hour ago', icon: 'CirclePlus' },
  { id: 3, action: 'Forecast Updated', item: '847 products recalculated', time: '2 hours ago', icon: 'DataLine' },
  { id: 4, action: 'Alert Resolved', item: 'SKU-1234 stockout prevented', time: '4 hours ago', icon: 'Check' },
  { id: 5, action: 'New Supplier Added', item: 'Global Parts Inc.', time: '6 hours ago', icon: 'Plus' },
])

onMounted(() => {
  // Simulate loading
  setTimeout(() => {
    loading.value = false
  }, 800)
})
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <Sidebar />

    <div class="flex-1 flex flex-col overflow-hidden">
      <Header />

      <main class="flex-1 overflow-y-auto p-6">
        <div v-loading="loading">
          <!-- Page Header -->
          <div class="mb-6">
            <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p class="text-gray-600">Real-time supply chain insights and analytics</p>
          </div>

          <!-- Metrics Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <MetricCard
              title="Total Products"
              :value="metrics.totalProducts.toLocaleString()"
              icon="Box"
              color="blue"
              :change="5.2"
            />
            <MetricCard
              title="Inventory Value"
              :value="'$' + (metrics.totalValue / 1000000).toFixed(2) + 'M'"
              icon="Money"
              color="green"
              :change="12.4"
            />
            <MetricCard
              title="Forecast Accuracy"
              :value="metrics.forecastAccuracy + '%'"
              icon="TrendCharts"
              color="purple"
              :change="2.1"
            />
            <MetricCard
              title="Stockout Rate"
              :value="metrics.stockoutRate + '%'"
              icon="Warning"
              color="red"
              :change="-1.3"
              :inverse="true"
            />
          </div>

          <!-- Charts Row -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <ForecastChart :forecasts="forecasts" />
            <ABCChart :analysis="abcAnalysis" />
          </div>

          <!-- Alerts and Activity Row -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <StockoutRisks :risks="stockoutRisks" />

            <!-- Reorder Alerts -->
            <el-card>
              <template #header>
                <div class="flex items-center justify-between">
                  <span class="font-semibold flex items-center">
                    <el-icon class="mr-2 text-orange-500"><Bell /></el-icon>
                    Reorder Alerts
                  </span>
                  <el-badge :value="reorderAlerts.length" type="warning" />
                </div>
              </template>

              <div class="space-y-3">
                <div
                  v-for="alert in reorderAlerts"
                  :key="alert.id"
                  class="p-3 rounded-lg border border-gray-200 hover:border-warning-300 transition-colors"
                >
                  <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center space-x-2">
                      <el-tag
                        :type="alert.priority === 'critical' ? 'danger' : 'warning'"
                        size="small"
                      >
                        {{ alert.priority }}
                      </el-tag>
                      <span class="font-medium">{{ alert.sku }}</span>
                    </div>
                    <span class="text-sm text-gray-500">
                      {{ alert.currentStock }}/{{ alert.reorderPoint }} units
                    </span>
                  </div>
                  <p class="text-sm text-gray-600">{{ alert.productName }}</p>
                  <div class="mt-2 flex items-center justify-between">
                    <span class="text-sm">
                      Suggested: <strong>{{ alert.suggestedQuantity }}</strong> units
                      (~${{ alert.estimatedCost.toLocaleString() }})
                    </span>
                    <el-button type="primary" size="small">Create PO</el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </div>

          <!-- Quick Stats and Activity -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Quick Stats -->
            <el-card>
              <template #header>
                <span class="font-semibold">Quick Stats</span>
              </template>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Pending Orders</span>
                  <el-tag>{{ metrics.pendingOrders }}</el-tag>
                </div>
                <el-divider class="my-2" />
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Low Stock Items</span>
                  <el-tag type="warning">{{ metrics.lowStockItems }}</el-tag>
                </div>
                <el-divider class="my-2" />
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Warehouses</span>
                  <el-tag type="success">{{ metrics.totalWarehouses }}</el-tag>
                </div>
                <el-divider class="my-2" />
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">Turnover Rate</span>
                  <el-tag type="info">{{ metrics.turnoverRate }}x</el-tag>
                </div>
              </div>
            </el-card>

            <!-- Recent Activity -->
            <el-card class="lg:col-span-2">
              <template #header>
                <div class="flex items-center justify-between">
                  <span class="font-semibold">Recent Activity</span>
                  <el-link type="primary" :underline="false">View All</el-link>
                </div>
              </template>
              <el-timeline>
                <el-timeline-item
                  v-for="activity in recentActivity"
                  :key="activity.id"
                  :timestamp="activity.time"
                  placement="top"
                >
                  <div class="flex items-center space-x-2">
                    <span class="font-medium">{{ activity.action }}</span>
                    <el-tag size="small" type="info">{{ activity.item }}</el-tag>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </el-card>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script lang="ts">
import { Bell, Box, Money, TrendCharts, Warning } from '@element-plus/icons-vue'

export default {
  components: {
    Bell,
    Box,
    Money,
    TrendCharts,
    Warning,
  },
}
</script>
