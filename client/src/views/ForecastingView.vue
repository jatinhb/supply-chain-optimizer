<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
])

const loading = ref(true)
const selectedProduct = ref('P001')
const forecastHorizon = ref(12)
const modelType = ref('prophet')

// Mock products for selection
const products = [
  { id: 'P001', name: 'Industrial Bearings 6205-2RS', sku: 'SKU-7891' },
  { id: 'P002', name: 'Hydraulic Pump HP-200', sku: 'SKU-4523' },
  { id: 'P003', name: 'Conveyor Belt 500mm', sku: 'SKU-8901' },
  { id: 'P004', name: 'Motor Controller VFD-15', sku: 'SKU-2345' },
]

// Mock forecast data
const historicalData = [
  { date: '2023-07', actual: 980 },
  { date: '2023-08', actual: 1050 },
  { date: '2023-09', actual: 1120 },
  { date: '2023-10', actual: 1080 },
  { date: '2023-11', actual: 1200 },
  { date: '2023-12', actual: 1350 },
  { date: '2024-01', actual: 1280 },
]

const forecastData = [
  { date: '2024-02', predicted: 1320, lower: 1180, upper: 1460 },
  { date: '2024-03', predicted: 1380, lower: 1220, upper: 1540 },
  { date: '2024-04', predicted: 1420, lower: 1250, upper: 1590 },
  { date: '2024-05', predicted: 1350, lower: 1170, upper: 1530 },
  { date: '2024-06', predicted: 1280, lower: 1090, upper: 1470 },
  { date: '2024-07', predicted: 1240, lower: 1040, upper: 1440 },
  { date: '2024-08', predicted: 1300, lower: 1090, upper: 1510 },
  { date: '2024-09', predicted: 1380, lower: 1160, upper: 1600 },
  { date: '2024-10', predicted: 1450, lower: 1220, upper: 1680 },
  { date: '2024-11', predicted: 1520, lower: 1280, upper: 1760 },
  { date: '2024-12', predicted: 1600, lower: 1350, upper: 1850 },
  { date: '2025-01', predicted: 1480, lower: 1230, upper: 1730 },
]

const forecastChartOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
  },
  legend: {
    data: ['Historical', 'Forecast', 'Upper Bound', 'Lower Bound'],
    top: 10,
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    containLabel: true,
  },
  dataZoom: [
    { type: 'inside', start: 0, end: 100 },
    { type: 'slider', start: 0, end: 100 },
  ],
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: [
      ...historicalData.map((d) => d.date),
      ...forecastData.map((d) => d.date),
    ],
  },
  yAxis: {
    type: 'value',
    name: 'Demand (Units)',
  },
  series: [
    {
      name: 'Historical',
      type: 'line',
      data: [...historicalData.map((d) => d.actual), ...Array(forecastData.length).fill(null)],
      itemStyle: { color: '#3b82f6' },
      lineStyle: { width: 2 },
      symbol: 'circle',
      symbolSize: 8,
    },
    {
      name: 'Forecast',
      type: 'line',
      data: [...Array(historicalData.length).fill(null), ...forecastData.map((d) => d.predicted)],
      itemStyle: { color: '#8b5cf6' },
      lineStyle: { width: 2, type: 'dashed' },
      symbol: 'diamond',
      symbolSize: 8,
    },
    {
      name: 'Upper Bound',
      type: 'line',
      data: [...Array(historicalData.length).fill(null), ...forecastData.map((d) => d.upper)],
      lineStyle: { opacity: 0 },
      areaStyle: { color: 'rgba(139, 92, 246, 0.1)' },
      stack: 'confidence',
      symbol: 'none',
    },
    {
      name: 'Lower Bound',
      type: 'line',
      data: [...Array(historicalData.length).fill(null), ...forecastData.map((d) => d.lower)],
      lineStyle: { opacity: 0 },
      areaStyle: { color: 'rgba(139, 92, 246, 0.1)' },
      stack: 'confidence',
      symbol: 'none',
    },
  ],
})

const seasonalityChartOption = ref({
  tooltip: {
    trigger: 'axis',
  },
  xAxis: {
    type: 'category',
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  },
  yAxis: {
    type: 'value',
    name: 'Seasonal Factor',
  },
  series: [
    {
      type: 'bar',
      data: [0.92, 0.88, 0.95, 1.02, 1.08, 1.05, 0.98, 1.02, 1.10, 1.12, 1.15, 1.20],
      itemStyle: {
        color: (params: { dataIndex: number }) => {
          const value = [0.92, 0.88, 0.95, 1.02, 1.08, 1.05, 0.98, 1.02, 1.10, 1.12, 1.15, 1.20][params.dataIndex]
          return value >= 1 ? '#22c55e' : '#f59e0b'
        },
      },
    },
  ],
})

const modelMetrics = ref({
  mape: 4.2,
  rmse: 127.5,
  mae: 98.3,
  r2: 0.94,
})

const runForecast = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 1500)
}

onMounted(() => {
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
          <div class="flex items-center justify-between mb-6">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Demand Forecasting</h1>
              <p class="text-gray-600">AI-powered demand predictions using Prophet & XGBoost</p>
            </div>
            <el-button type="primary" @click="runForecast">
              <el-icon class="mr-2"><Refresh /></el-icon>
              Generate Forecast
            </el-button>
          </div>

          <!-- Configuration Panel -->
          <el-card class="mb-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Product</label>
                <el-select v-model="selectedProduct" class="w-full">
                  <el-option
                    v-for="product in products"
                    :key="product.id"
                    :label="`${product.sku} - ${product.name}`"
                    :value="product.id"
                  />
                </el-select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Forecast Horizon</label>
                <el-select v-model="forecastHorizon" class="w-full">
                  <el-option :value="4" label="4 weeks" />
                  <el-option :value="8" label="8 weeks" />
                  <el-option :value="12" label="12 weeks" />
                  <el-option :value="26" label="26 weeks" />
                  <el-option :value="52" label="52 weeks" />
                </el-select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Model Type</label>
                <el-select v-model="modelType" class="w-full">
                  <el-option value="prophet" label="Prophet (Recommended)" />
                  <el-option value="xgboost" label="XGBoost" />
                  <el-option value="ensemble" label="Ensemble" />
                  <el-option value="arima" label="ARIMA" />
                </el-select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Confidence Level</label>
                <el-select class="w-full" model-value="95">
                  <el-option :value="80" label="80%" />
                  <el-option :value="90" label="90%" />
                  <el-option :value="95" label="95%" />
                  <el-option :value="99" label="99%" />
                </el-select>
              </div>
            </div>
          </el-card>

          <!-- Model Performance Metrics -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-3xl font-bold text-blue-600">{{ modelMetrics.mape }}%</p>
                <p class="text-sm text-gray-500">MAPE</p>
                <p class="text-xs text-gray-400">Mean Absolute % Error</p>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-3xl font-bold text-green-600">{{ modelMetrics.r2 }}</p>
                <p class="text-sm text-gray-500">R² Score</p>
                <p class="text-xs text-gray-400">Model Fit Quality</p>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-3xl font-bold text-purple-600">{{ modelMetrics.rmse }}</p>
                <p class="text-sm text-gray-500">RMSE</p>
                <p class="text-xs text-gray-400">Root Mean Square Error</p>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-3xl font-bold text-orange-600">{{ modelMetrics.mae }}</p>
                <p class="text-sm text-gray-500">MAE</p>
                <p class="text-xs text-gray-400">Mean Absolute Error</p>
              </div>
            </el-card>
          </div>

          <!-- Main Forecast Chart -->
          <el-card class="mb-6">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="font-semibold">Demand Forecast - Industrial Bearings 6205-2RS</span>
                <div class="flex items-center space-x-4">
                  <el-tag type="success">Trend: +12.5%</el-tag>
                  <el-tag type="info">Accuracy: 94.2%</el-tag>
                </div>
              </div>
            </template>
            <v-chart :option="forecastChartOption" style="height: 400px" autoresize />
          </el-card>

          <!-- Secondary Charts -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Seasonality Chart -->
            <el-card>
              <template #header>
                <span class="font-semibold">Monthly Seasonality Pattern</span>
              </template>
              <v-chart :option="seasonalityChartOption" style="height: 300px" autoresize />
            </el-card>

            <!-- Forecast Summary -->
            <el-card>
              <template #header>
                <span class="font-semibold">Forecast Summary</span>
              </template>
              <div class="space-y-4">
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p class="text-sm text-gray-500">Total Forecasted Demand</p>
                    <p class="text-2xl font-bold">16,220 units</p>
                  </div>
                  <el-icon :size="32" class="text-blue-500"><TrendCharts /></el-icon>
                </div>
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p class="text-sm text-gray-500">Peak Demand Month</p>
                    <p class="text-2xl font-bold">December 2024</p>
                  </div>
                  <el-tag type="danger">1,600 units</el-tag>
                </div>
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p class="text-sm text-gray-500">Recommended Safety Stock</p>
                    <p class="text-2xl font-bold">485 units</p>
                  </div>
                  <el-tag type="warning">+15% buffer</el-tag>
                </div>
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p class="text-sm text-gray-500">Optimal Reorder Quantity</p>
                    <p class="text-2xl font-bold">750 units</p>
                  </div>
                  <el-tag type="success">EOQ Model</el-tag>
                </div>
              </div>
            </el-card>
          </div>

          <!-- External Factors -->
          <el-card>
            <template #header>
              <span class="font-semibold">External Factors Considered</span>
            </template>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="p-4 border rounded-lg">
                <div class="flex items-center space-x-3 mb-2">
                  <el-icon :size="24" class="text-blue-500"><Calendar /></el-icon>
                  <span class="font-medium">Holidays & Events</span>
                </div>
                <p class="text-sm text-gray-600">
                  12 public holidays, 3 industry events factored into predictions
                </p>
              </div>
              <div class="p-4 border rounded-lg">
                <div class="flex items-center space-x-3 mb-2">
                  <el-icon :size="24" class="text-green-500"><Promotion /></el-icon>
                  <span class="font-medium">Promotions</span>
                </div>
                <p class="text-sm text-gray-600">
                  Q4 promotional campaigns expected to increase demand by 18%
                </p>
              </div>
              <div class="p-4 border rounded-lg">
                <div class="flex items-center space-x-3 mb-2">
                  <el-icon :size="24" class="text-purple-500"><DataLine /></el-icon>
                  <span class="font-medium">Market Trends</span>
                </div>
                <p class="text-sm text-gray-600">
                  Industry growth rate of 8.5% YoY incorporated in baseline
                </p>
              </div>
            </div>
          </el-card>
        </div>
      </main>
    </div>
  </div>
</template>

<script lang="ts">
import { Refresh, TrendCharts, Calendar, Promotion, DataLine } from '@element-plus/icons-vue'

export default {
  components: {
    Refresh,
    TrendCharts,
    Calendar,
    Promotion,
    DataLine,
  },
}
</script>
