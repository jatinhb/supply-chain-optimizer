<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const loading = ref(true)
const dateRange = ref('30d')

// KPI Metrics
const kpis = ref({
  inventoryTurnover: { value: 8.4, change: 12.5, target: 10 },
  fillRate: { value: 97.2, change: 2.1, target: 98 },
  stockoutRate: { value: 2.3, change: -1.3, target: 2 },
  avgLeadTime: { value: 4.2, change: -8.5, target: 5 },
  carryingCost: { value: 245000, change: -5.2, target: 250000 },
  orderAccuracy: { value: 99.1, change: 0.8, target: 99 },
})

// Inventory Turnover Trend
const turnoverChartOption = ref({
  tooltip: { trigger: 'axis' },
  legend: { data: ['Turnover Rate', 'Target'], top: 10 },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  },
  yAxis: { type: 'value', name: 'Turnover Rate' },
  series: [
    {
      name: 'Turnover Rate',
      type: 'line',
      data: [7.2, 7.5, 7.8, 8.0, 7.9, 8.2, 8.1, 8.3, 8.5, 8.4, 8.6, 8.4],
      smooth: true,
      itemStyle: { color: '#3b82f6' },
      areaStyle: { color: 'rgba(59, 130, 246, 0.1)' },
    },
    {
      name: 'Target',
      type: 'line',
      data: Array(12).fill(10),
      lineStyle: { type: 'dashed', color: '#ef4444' },
      symbol: 'none',
    },
  ],
})

// Category Performance
const categoryChartOption = ref({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['Revenue', 'Profit Margin %'], top: 10 },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ['Mechanical', 'Electronics', 'Hydraulics', 'Raw Materials', 'Conveyors'],
  },
  yAxis: [
    { type: 'value', name: 'Revenue ($K)' },
    { type: 'value', name: 'Margin %', max: 50 },
  ],
  series: [
    {
      name: 'Revenue',
      type: 'bar',
      data: [450, 380, 320, 280, 220],
      itemStyle: { color: '#3b82f6' },
    },
    {
      name: 'Profit Margin %',
      type: 'line',
      yAxisIndex: 1,
      data: [32, 28, 35, 18, 42],
      itemStyle: { color: '#22c55e' },
    },
  ],
})

// Supplier Performance
const supplierChartOption = ref({
  tooltip: { trigger: 'item' },
  legend: { top: 10 },
  series: [
    {
      name: 'Order Volume',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' },
      },
      data: [
        { value: 35, name: 'Global Industrial', itemStyle: { color: '#3b82f6' } },
        { value: 25, name: 'TechParts Intl', itemStyle: { color: '#22c55e' } },
        { value: 20, name: 'MetalWorks Co', itemStyle: { color: '#f59e0b' } },
        { value: 12, name: 'Precision Ltd', itemStyle: { color: '#8b5cf6' } },
        { value: 8, name: 'Others', itemStyle: { color: '#6b7280' } },
      ],
    },
  ],
})

// Cost Breakdown
const costChartOption = ref({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { top: 10 },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ['Q1', 'Q2', 'Q3', 'Q4'],
  },
  yAxis: { type: 'value', name: 'Cost ($K)' },
  series: [
    { name: 'Holding Cost', type: 'bar', stack: 'total', data: [62, 58, 55, 60], itemStyle: { color: '#3b82f6' } },
    { name: 'Ordering Cost', type: 'bar', stack: 'total', data: [28, 32, 30, 35], itemStyle: { color: '#22c55e' } },
    { name: 'Stockout Cost', type: 'bar', stack: 'total', data: [15, 12, 8, 10], itemStyle: { color: '#ef4444' } },
    { name: 'Transport Cost', type: 'bar', stack: 'total', data: [45, 48, 52, 50], itemStyle: { color: '#f59e0b' } },
  ],
})

// Supplier scorecards
const suppliers = ref([
  { name: 'Global Industrial Supply', onTime: 98, quality: 99.2, leadTime: 3.5, score: 95 },
  { name: 'TechParts International', onTime: 94, quality: 98.8, leadTime: 5.2, score: 88 },
  { name: 'MetalWorks Co.', onTime: 96, quality: 97.5, leadTime: 4.8, score: 85 },
  { name: 'Precision Components Ltd', onTime: 92, quality: 99.5, leadTime: 6.0, score: 82 },
])

const getScoreColor = (score: number) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'warning'
  return 'danger'
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
              <h1 class="text-2xl font-bold text-gray-900">Analytics & Reports</h1>
              <p class="text-gray-600">Comprehensive supply chain performance insights</p>
            </div>
            <div class="flex items-center space-x-3">
              <el-select v-model="dateRange" class="w-32">
                <el-option value="7d" label="Last 7 days" />
                <el-option value="30d" label="Last 30 days" />
                <el-option value="90d" label="Last 90 days" />
                <el-option value="1y" label="Last year" />
              </el-select>
              <el-button>
                <el-icon class="mr-2"><Download /></el-icon>
                Export Report
              </el-button>
            </div>
          </div>

          <!-- KPI Cards -->
          <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-2xl font-bold text-blue-600">{{ kpis.inventoryTurnover.value }}x</p>
                <p class="text-xs text-gray-500">Inventory Turnover</p>
                <el-tag :type="kpis.inventoryTurnover.change >= 0 ? 'success' : 'danger'" size="small" class="mt-1">
                  {{ kpis.inventoryTurnover.change >= 0 ? '+' : '' }}{{ kpis.inventoryTurnover.change }}%
                </el-tag>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-2xl font-bold text-green-600">{{ kpis.fillRate.value }}%</p>
                <p class="text-xs text-gray-500">Fill Rate</p>
                <el-tag :type="kpis.fillRate.change >= 0 ? 'success' : 'danger'" size="small" class="mt-1">
                  {{ kpis.fillRate.change >= 0 ? '+' : '' }}{{ kpis.fillRate.change }}%
                </el-tag>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-2xl font-bold text-red-600">{{ kpis.stockoutRate.value }}%</p>
                <p class="text-xs text-gray-500">Stockout Rate</p>
                <el-tag :type="kpis.stockoutRate.change <= 0 ? 'success' : 'danger'" size="small" class="mt-1">
                  {{ kpis.stockoutRate.change }}%
                </el-tag>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-2xl font-bold text-purple-600">{{ kpis.avgLeadTime.value }}d</p>
                <p class="text-xs text-gray-500">Avg Lead Time</p>
                <el-tag :type="kpis.avgLeadTime.change <= 0 ? 'success' : 'danger'" size="small" class="mt-1">
                  {{ kpis.avgLeadTime.change }}%
                </el-tag>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-2xl font-bold text-orange-600">${{ (kpis.carryingCost.value / 1000).toFixed(0) }}K</p>
                <p class="text-xs text-gray-500">Carrying Cost</p>
                <el-tag :type="kpis.carryingCost.change <= 0 ? 'success' : 'danger'" size="small" class="mt-1">
                  {{ kpis.carryingCost.change }}%
                </el-tag>
              </div>
            </el-card>
            <el-card shadow="hover">
              <div class="text-center">
                <p class="text-2xl font-bold text-teal-600">{{ kpis.orderAccuracy.value }}%</p>
                <p class="text-xs text-gray-500">Order Accuracy</p>
                <el-tag :type="kpis.orderAccuracy.change >= 0 ? 'success' : 'danger'" size="small" class="mt-1">
                  +{{ kpis.orderAccuracy.change }}%
                </el-tag>
              </div>
            </el-card>
          </div>

          <!-- Charts Row 1 -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <el-card>
              <template #header>
                <span class="font-semibold">Inventory Turnover Trend</span>
              </template>
              <v-chart :option="turnoverChartOption" style="height: 300px" autoresize />
            </el-card>
            <el-card>
              <template #header>
                <span class="font-semibold">Category Performance</span>
              </template>
              <v-chart :option="categoryChartOption" style="height: 300px" autoresize />
            </el-card>
          </div>

          <!-- Charts Row 2 -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <el-card>
              <template #header>
                <span class="font-semibold">Supplier Order Distribution</span>
              </template>
              <v-chart :option="supplierChartOption" style="height: 300px" autoresize />
            </el-card>
            <el-card>
              <template #header>
                <span class="font-semibold">Cost Breakdown by Quarter</span>
              </template>
              <v-chart :option="costChartOption" style="height: 300px" autoresize />
            </el-card>
          </div>

          <!-- Supplier Scorecard -->
          <el-card>
            <template #header>
              <div class="flex items-center justify-between">
                <span class="font-semibold">Supplier Performance Scorecard</span>
                <el-link type="primary" :underline="false">View All Suppliers</el-link>
              </div>
            </template>
            <el-table :data="suppliers" style="width: 100%">
              <el-table-column prop="name" label="Supplier" min-width="200" />
              <el-table-column label="On-Time Delivery" width="150" align="center">
                <template #default="{ row }">
                  <div class="flex items-center justify-center space-x-2">
                    <el-progress
                      type="circle"
                      :percentage="row.onTime"
                      :width="50"
                      :stroke-width="4"
                      :color="row.onTime >= 95 ? '#22c55e' : row.onTime >= 90 ? '#f59e0b' : '#ef4444'"
                    />
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Quality Rate" width="150" align="center">
                <template #default="{ row }">
                  <div class="flex items-center justify-center space-x-2">
                    <el-progress
                      type="circle"
                      :percentage="row.quality"
                      :width="50"
                      :stroke-width="4"
                      :color="row.quality >= 99 ? '#22c55e' : row.quality >= 97 ? '#f59e0b' : '#ef4444'"
                    />
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Avg Lead Time" width="130" align="center">
                <template #default="{ row }">
                  <span :class="row.leadTime <= 4 ? 'text-green-600' : row.leadTime <= 5 ? 'text-yellow-600' : 'text-red-600'">
                    {{ row.leadTime }} days
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="Overall Score" width="150" align="center">
                <template #default="{ row }">
                  <el-tag :type="getScoreColor(row.score)" size="large">
                    {{ row.score }}/100
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Trend" width="100" align="center">
                <template #default>
                  <el-icon :size="20" class="text-green-500"><Top /></el-icon>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </main>
    </div>
  </div>
</template>

<script lang="ts">
import { Download, Top } from '@element-plus/icons-vue'

export default {
  components: {
    Download,
    Top,
  },
}
</script>
