<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { path: '/dashboard', title: 'Dashboard', icon: 'DataBoard' },
  { path: '/inventory', title: 'Inventory', icon: 'Box' },
  { path: '/forecasting', title: 'Forecasting', icon: 'TrendCharts' },
  { path: '/orders', title: 'Orders', icon: 'ShoppingCart' },
  { path: '/analytics', title: 'Analytics', icon: 'PieChart' },
]

const activeIndex = computed(() => route.path)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="w-64 h-screen bg-gray-900 flex flex-col">
    <!-- Logo -->
    <div class="h-16 flex items-center justify-center border-b border-gray-800">
      <el-icon class="text-primary-500 text-2xl mr-2"><Box /></el-icon>
      <span class="text-xl font-bold text-white">InventoryIQ</span>
    </div>

    <!-- Navigation -->
    <el-menu
      :default-active="activeIndex"
      class="flex-1 border-r-0"
      background-color="#111827"
      text-color="#9ca3af"
      active-text-color="#3b82f6"
      router
    >
      <el-menu-item
        v-for="item in menuItems"
        :key="item.path"
        :index="item.path"
      >
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.title }}</span>
      </el-menu-item>
    </el-menu>

    <!-- User Section -->
    <div class="p-4 border-t border-gray-800">
      <div class="flex items-center mb-3">
        <div class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
          <span class="text-white text-sm font-medium">
            {{ authStore.user?.name?.charAt(0) || 'U' }}
          </span>
        </div>
        <div class="ml-3 flex-1 min-w-0">
          <p class="text-sm font-medium text-white truncate">
            {{ authStore.user?.name || 'User' }}
          </p>
          <p class="text-xs text-gray-400 truncate capitalize">
            {{ authStore.user?.role || 'Guest' }}
          </p>
        </div>
      </div>
      <el-button
        class="w-full"
        type="info"
        plain
        @click="handleLogout"
      >
        <el-icon class="mr-1"><SwitchButton /></el-icon>
        Logout
      </el-button>
    </div>
  </div>
</template>

<style scoped>
:deep(.el-menu) {
  border: none;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(59, 130, 246, 0.1) !important;
}
</style>
