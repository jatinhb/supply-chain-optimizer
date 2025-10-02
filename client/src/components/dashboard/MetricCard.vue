<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  icon?: string
  color?: string
  change?: number
  inverse?: boolean
}>()
</script>

<template>
  <el-card shadow="hover" class="metric-card">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm font-medium text-gray-500">{{ title }}</p>
        <p class="mt-2 text-3xl font-bold text-gray-900">{{ value }}</p>
        <p
          v-if="change !== undefined"
          class="mt-2 text-sm font-medium"
          :class="(inverse ? change <= 0 : change >= 0) ? 'text-green-600' : 'text-red-600'"
        >
          {{ change >= 0 ? '+' : '' }}{{ change }}%
        </p>
      </div>
      <div
        v-if="icon"
        class="rounded-lg p-3"
        :class="`bg-${color || 'blue'}-100 text-${color || 'blue'}-600`"
      >
        <el-icon :size="24"><component :is="icon" /></el-icon>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.metric-card {
  height: 100%;
}
</style>
