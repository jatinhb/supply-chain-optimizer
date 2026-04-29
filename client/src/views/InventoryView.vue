<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { InventoryItem, Warehouse } from '@/types'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import { Search, Filter, Download, Plus, Edit, Delete, View } from '@element-plus/icons-vue'

const loading = ref(true)
const searchQuery = ref('')
const selectedWarehouse = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')

// Mock inventory data
const inventory = ref<InventoryItem[]>([
  {
    id: 'INV001',
    productId: 'P1234',
    sku: 'SKU-7891',
    name: 'Industrial Bearings 6205-2RS',
    category: 'Mechanical Parts',
    quantity: 450,
    reorderPoint: 100,
    maxStock: 1000,
    unitCost: 5.00,
    totalValue: 2250,
    warehouseId: 'WH001',
    location: 'A-12-3',
    lastUpdated: '2024-01-15T10:30:00Z',
    status: 'in_stock',
  },
  {
    id: 'INV002',
    productId: 'P2456',
    sku: 'SKU-4523',
    name: 'Hydraulic Pump HP-200',
    category: 'Hydraulics',
    quantity: 85,
    reorderPoint: 150,
    maxStock: 500,
    unitCost: 75.00,
    totalValue: 6375,
    warehouseId: 'WH001',
    location: 'B-05-1',
    lastUpdated: '2024-01-15T09:15:00Z',
    status: 'low_stock',
  },
  {
    id: 'INV003',
    productId: 'P3789',
    sku: 'SKU-8901',
    name: 'Conveyor Belt 500mm',
    category: 'Conveyors',
    quantity: 250,
    reorderPoint: 100,
    maxStock: 800,
    unitCost: 120.00,
    totalValue: 30000,
    warehouseId: 'WH002',
    location: 'C-02-4',
    lastUpdated: '2024-01-15T08:45:00Z',
    status: 'in_stock',
  },
  {
    id: 'INV004',
    productId: 'P4012',
    sku: 'SKU-2345',
    name: 'Motor Controller VFD-15',
    category: 'Electronics',
    quantity: 0,
    reorderPoint: 50,
    maxStock: 200,
    unitCost: 450.00,
    totalValue: 0,
    warehouseId: 'WH001',
    location: 'D-08-2',
    lastUpdated: '2024-01-14T16:20:00Z',
    status: 'out_of_stock',
  },
  {
    id: 'INV005',
    productId: 'P5678',
    sku: 'SKU-6789',
    name: 'Steel Pipe 4" Schedule 40',
    category: 'Raw Materials',
    quantity: 1200,
    reorderPoint: 500,
    maxStock: 3000,
    unitCost: 25.00,
    totalValue: 30000,
    warehouseId: 'WH003',
    location: 'E-01-1',
    lastUpdated: '2024-01-15T11:00:00Z',
    status: 'in_stock',
  },
])

const warehouses = ref<Warehouse[]>([
  { id: 'WH001', name: 'Main Distribution Center', location: 'Chicago, IL', capacity: 50000, currentUtilization: 72 },
  { id: 'WH002', name: 'West Coast Hub', location: 'Los Angeles, CA', capacity: 35000, currentUtilization: 85 },
  { id: 'WH003', name: 'East Regional', location: 'Newark, NJ', capacity: 40000, currentUtilization: 63 },
])

const categories = ['Mechanical Parts', 'Hydraulics', 'Conveyors', 'Electronics', 'Raw Materials']
const statuses = ['in_stock', 'low_stock', 'out_of_stock', 'reserved']

const filteredInventory = computed(() => {
  return inventory.value.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesWarehouse = !selectedWarehouse.value || item.warehouseId === selectedWarehouse.value
    const matchesCategory = !selectedCategory.value || item.category === selectedCategory.value
    const matchesStatus = !selectedStatus.value || item.status === selectedStatus.value
    return matchesSearch && matchesWarehouse && matchesCategory && matchesStatus
  })
})

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    in_stock: 'success',
    low_stock: 'warning',
    out_of_stock: 'danger',
    reserved: 'info',
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    in_stock: 'In Stock',
    low_stock: 'Low Stock',
    out_of_stock: 'Out of Stock',
    reserved: 'Reserved',
  }
  return labels[status] || status
}

const getStockPercentage = (item: InventoryItem) => {
  return Math.round((item.quantity / item.maxStock) * 100)
}

const getStockColor = (item: InventoryItem) => {
  const percentage = getStockPercentage(item)
  if (percentage <= 20) return '#ef4444'
  if (percentage <= 50) return '#f59e0b'
  return '#22c55e'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedWarehouse.value = ''
  selectedCategory.value = ''
  selectedStatus.value = ''
}

onMounted(() => {
  setTimeout(() => {
    loading.value = false
  }, 600)
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
              <h1 class="text-2xl font-bold text-gray-900">Inventory Management</h1>
              <p class="text-gray-600">Track and manage stock levels across all warehouses</p>
            </div>
            <div class="flex space-x-3">
              <el-button :icon="Download">Export</el-button>
              <el-button type="primary" :icon="Plus">Add Product</el-button>
            </div>
          </div>

          <!-- Summary Cards -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <el-card shadow="hover" class="text-center">
              <p class="text-3xl font-bold text-gray-900">{{ inventory.length }}</p>
              <p class="text-sm text-gray-500">Total SKUs</p>
            </el-card>
            <el-card shadow="hover" class="text-center">
              <p class="text-3xl font-bold text-green-600">
                {{ inventory.filter(i => i.status === 'in_stock').length }}
              </p>
              <p class="text-sm text-gray-500">In Stock</p>
            </el-card>
            <el-card shadow="hover" class="text-center">
              <p class="text-3xl font-bold text-yellow-600">
                {{ inventory.filter(i => i.status === 'low_stock').length }}
              </p>
              <p class="text-sm text-gray-500">Low Stock</p>
            </el-card>
            <el-card shadow="hover" class="text-center">
              <p class="text-3xl font-bold text-red-600">
                {{ inventory.filter(i => i.status === 'out_of_stock').length }}
              </p>
              <p class="text-sm text-gray-500">Out of Stock</p>
            </el-card>
          </div>

          <!-- Filters -->
          <el-card class="mb-6">
            <div class="flex flex-wrap items-center gap-4">
              <el-input
                v-model="searchQuery"
                placeholder="Search by name or SKU..."
                :prefix-icon="Search"
                class="w-64"
                clearable
              />
              <el-select
                v-model="selectedWarehouse"
                placeholder="All Warehouses"
                clearable
                class="w-48"
              >
                <el-option
                  v-for="wh in warehouses"
                  :key="wh.id"
                  :label="wh.name"
                  :value="wh.id"
                />
              </el-select>
              <el-select
                v-model="selectedCategory"
                placeholder="All Categories"
                clearable
                class="w-48"
              >
                <el-option
                  v-for="cat in categories"
                  :key="cat"
                  :label="cat"
                  :value="cat"
                />
              </el-select>
              <el-select
                v-model="selectedStatus"
                placeholder="All Statuses"
                clearable
                class="w-40"
              >
                <el-option
                  v-for="status in statuses"
                  :key="status"
                  :label="getStatusLabel(status)"
                  :value="status"
                />
              </el-select>
              <el-button @click="clearFilters" :icon="Filter">Clear</el-button>
            </div>
          </el-card>

          <!-- Inventory Table -->
          <el-card>
            <el-table
              :data="filteredInventory"
              style="width: 100%"
              :default-sort="{ prop: 'quantity', order: 'ascending' }"
            >
              <el-table-column prop="sku" label="SKU" width="120" sortable />
              <el-table-column prop="name" label="Product Name" min-width="200" />
              <el-table-column prop="category" label="Category" width="150" sortable />
              <el-table-column label="Stock Level" width="200">
                <template #default="{ row }">
                  <div class="space-y-1">
                    <div class="flex items-center justify-between text-sm">
                      <span>{{ row.quantity }} / {{ row.maxStock }}</span>
                      <span class="text-gray-500">{{ getStockPercentage(row) }}%</span>
                    </div>
                    <el-progress
                      :percentage="getStockPercentage(row)"
                      :color="getStockColor(row)"
                      :show-text="false"
                      :stroke-width="6"
                    />
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Reorder Point" width="120" align="center">
                <template #default="{ row }">
                  <span :class="row.quantity <= row.reorderPoint ? 'text-red-600 font-semibold' : ''">
                    {{ row.reorderPoint }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="Value" width="120" sortable>
                <template #default="{ row }">
                  ${{ row.totalValue.toLocaleString() }}
                </template>
              </el-table-column>
              <el-table-column prop="location" label="Location" width="100" />
              <el-table-column label="Status" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ getStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Last Updated" width="140">
                <template #default="{ row }">
                  {{ formatDate(row.lastUpdated) }}
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="150" fixed="right">
                <template #default>
                  <el-button-group size="small">
                    <el-button :icon="View" />
                    <el-button :icon="Edit" />
                    <el-button :icon="Delete" type="danger" />
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>

            <div class="flex justify-end mt-4">
              <el-pagination
                background
                layout="total, sizes, prev, pager, next"
                :total="filteredInventory.length"
                :page-sizes="[10, 25, 50, 100]"
              />
            </div>
          </el-card>
        </div>
      </main>
    </div>
  </div>
</template>
