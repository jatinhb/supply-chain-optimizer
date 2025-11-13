<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  title: string
  subtitle?: string
}>()

const searchQuery = ref('')
</script>

<template>
  <header class="bg-white border-b border-gray-200 px-6 py-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
      </div>

      <div class="flex items-center space-x-4">
        <!-- Search -->
        <el-input
          v-model="searchQuery"
          placeholder="Search products..."
          prefix-icon="Search"
          class="w-64"
        />

        <!-- Notifications -->
        <el-badge :value="5" :max="99">
          <el-button :icon="'Bell'" circle />
        </el-badge>

        <!-- Settings -->
        <el-button :icon="'Setting'" circle />
      </div>
    </div>
  </header>
</template>
