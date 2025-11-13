<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { DemandForecast } from '@/types'

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps<{
  forecasts: DemandForecast[]
}>()

const chartData = computed(() => {
  if (!props.forecasts.length) return []
  return props.forecasts[0].forecasts
})

const option = computed(() => ({
  title: {
    text: '8-Week Demand Forecast',
    left: 'center',
    textStyle: {
      fontSize: 16,
      fontWeight: 600,
    },
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#fff',
    borderColor: '#e5e7eb',
    borderWidth: 1,
    textStyle: {
      color: '#374151',
    },
  },
  legend: {
    bottom: 0,
    data: ['Predicted', 'Upper Bound', 'Lower Bound'],
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    top: '15%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: chartData.value.map((d) => d.date),
    axisLabel: {
      formatter: (value: string) => {
        const date = new Date(value)
        return `${date.getMonth() + 1}/${date.getDate()}`
      },
    },
  },
  yAxis: {
    type: 'value',
    name: 'Units',
  },
  series: [
    {
      name: 'Predicted',
      type: 'line',
      data: chartData.value.map((d) => d.predicted),
      smooth: true,
      lineStyle: { width: 3, color: '#3b82f6' },
      itemStyle: { color: '#3b82f6' },
    },
    {
      name: 'Upper Bound',
      type: 'line',
      data: chartData.value.map((d) => d.upper),
      lineStyle: { width: 1, type: 'dashed', color: '#9ca3af' },
      itemStyle: { color: '#9ca3af' },
      symbol: 'none',
    },
    {
      name: 'Lower Bound',
      type: 'line',
      data: chartData.value.map((d) => d.lower),
      lineStyle: { width: 1, type: 'dashed', color: '#9ca3af' },
      itemStyle: { color: '#9ca3af' },
      symbol: 'none',
      areaStyle: {
        color: 'rgba(59, 130, 246, 0.1)',
      },
    },
  ],
}))
</script>

<template>
  <el-card>
    <template #header>
      <span class="font-semibold">Demand Forecast</span>
    </template>
    <v-chart :option="option" style="height: 300px" autoresize />
  </el-card>
</template>
