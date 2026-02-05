<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ABCAnalysis } from '@/types'

use([PieChart, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps<{
  analysis: ABCAnalysis
}>()

const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} items ({d}%)',
  },
  legend: {
    bottom: 10,
    left: 'center',
  },
  series: [
    {
      name: 'ABC Analysis',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: {
        show: false,
        position: 'center',
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold',
        },
      },
      labelLine: {
        show: false,
      },
      data: [
        {
          value: props.analysis.aItems.count,
          name: 'Class A (High Value)',
          itemStyle: { color: '#22c55e' },
        },
        {
          value: props.analysis.bItems.count,
          name: 'Class B (Medium)',
          itemStyle: { color: '#f59e0b' },
        },
        {
          value: props.analysis.cItems.count,
          name: 'Class C (Low Value)',
          itemStyle: { color: '#3b82f6' },
        },
      ],
    },
  ],
}))
</script>

<template>
  <el-card>
    <template #header>
      <span class="font-semibold">ABC Analysis</span>
    </template>
    <v-chart :option="option" style="height: 250px" autoresize />
    <div class="grid grid-cols-3 gap-2 mt-4 text-center text-sm">
      <div class="p-2 bg-green-50 rounded">
        <p class="font-semibold text-green-700">A Items</p>
        <p class="text-green-600">{{ analysis.aItems.valuePercentage }}% value</p>
      </div>
      <div class="p-2 bg-yellow-50 rounded">
        <p class="font-semibold text-yellow-700">B Items</p>
        <p class="text-yellow-600">{{ analysis.bItems.valuePercentage }}% value</p>
      </div>
      <div class="p-2 bg-blue-50 rounded">
        <p class="font-semibold text-blue-700">C Items</p>
        <p class="text-blue-600">{{ analysis.cItems.valuePercentage }}% value</p>
      </div>
    </div>
  </el-card>
</template>
