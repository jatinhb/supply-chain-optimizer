<script setup lang="ts">
import type { StockoutRisk } from '@/types'

defineProps<{
  risks: StockoutRisk[]
}>()

const riskColors = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
  critical: 'danger',
} as const

const getRiskType = (level: string) => riskColors[level as keyof typeof riskColors] || 'info'
</script>

<template>
  <el-card>
    <template #header>
      <div class="flex items-center justify-between">
        <span class="font-semibold flex items-center">
          <el-icon class="mr-2 text-red-500"><Warning /></el-icon>
          Stockout Risks
        </span>
        <el-tag>{{ risks.length }} items</el-tag>
      </div>
    </template>

    <div class="space-y-3 max-h-80 overflow-y-auto">
      <div
        v-for="risk in risks"
        :key="risk.productId"
        class="p-3 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-2">
              <span class="font-medium text-gray-900">{{ risk.sku }}</span>
              <el-tag :type="getRiskType(risk.riskLevel)" size="small">
                {{ risk.riskLevel }}
              </el-tag>
            </div>
            <p class="text-sm text-gray-600 mt-1">{{ risk.productName }}</p>
          </div>
          <div class="text-right">
            <p class="text-lg font-semibold text-gray-900">{{ risk.daysOfStock }}d</p>
            <p class="text-xs text-gray-500">stock remaining</p>
          </div>
        </div>
        <div class="mt-2 flex items-center justify-between text-sm">
          <span class="text-gray-500">
            Current: {{ risk.currentStock }} | Daily: {{ risk.dailyDemand }}
          </span>
          <el-button type="primary" size="small" text>
            {{ risk.suggestedAction }}
          </el-button>
        </div>
      </div>

      <el-empty
        v-if="risks.length === 0"
        description="No stockout risks detected"
        :image-size="80"
      />
    </div>
  </el-card>
</template>
