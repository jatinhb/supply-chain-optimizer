<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { PurchaseOrder } from '@/types'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import { Search, Plus, View, Edit, Check, Close } from '@element-plus/icons-vue'

const loading = ref(true)
const searchQuery = ref('')
const selectedStatus = ref('')
const activeTab = ref('all')

// Mock purchase orders
const orders = ref<PurchaseOrder[]>([
  {
    id: 'PO-2024-0156',
    supplierId: 'SUP001',
    supplierName: 'Global Industrial Supply',
    items: [
      { productId: 'P001', sku: 'SKU-7891', name: 'Industrial Bearings', quantity: 500, unitCost: 5.00, totalCost: 2500 },
      { productId: 'P002', sku: 'SKU-4523', name: 'Hydraulic Pump', quantity: 50, unitCost: 75.00, totalCost: 3750 },
    ],
    totalAmount: 6250,
    status: 'pending',
    createdAt: '2024-01-15T10:30:00Z',
    expectedDelivery: '2024-01-25T00:00:00Z',
    priority: 'high',
  },
  {
    id: 'PO-2024-0155',
    supplierId: 'SUP002',
    supplierName: 'TechParts International',
    items: [
      { productId: 'P004', sku: 'SKU-2345', name: 'Motor Controller VFD-15', quantity: 100, unitCost: 450.00, totalCost: 45000 },
    ],
    totalAmount: 45000,
    status: 'approved',
    createdAt: '2024-01-14T15:20:00Z',
    expectedDelivery: '2024-02-01T00:00:00Z',
    priority: 'critical',
  },
  {
    id: 'PO-2024-0154',
    supplierId: 'SUP003',
    supplierName: 'MetalWorks Co.',
    items: [
      { productId: 'P005', sku: 'SKU-6789', name: 'Steel Pipe 4"', quantity: 1000, unitCost: 25.00, totalCost: 25000 },
    ],
    totalAmount: 25000,
    status: 'shipped',
    createdAt: '2024-01-12T09:00:00Z',
    expectedDelivery: '2024-01-18T00:00:00Z',
    priority: 'medium',
  },
  {
    id: 'PO-2024-0153',
    supplierId: 'SUP001',
    supplierName: 'Global Industrial Supply',
    items: [
      { productId: 'P003', sku: 'SKU-8901', name: 'Conveyor Belt 500mm', quantity: 200, unitCost: 120.00, totalCost: 24000 },
    ],
    totalAmount: 24000,
    status: 'delivered',
    createdAt: '2024-01-08T11:45:00Z',
    expectedDelivery: '2024-01-15T00:00:00Z',
    priority: 'low',
  },
  {
    id: 'PO-2024-0152',
    supplierId: 'SUP004',
    supplierName: 'Precision Components Ltd',
    items: [
      { productId: 'P001', sku: 'SKU-7891', name: 'Industrial Bearings', quantity: 300, unitCost: 5.00, totalCost: 1500 },
    ],
    totalAmount: 1500,
    status: 'cancelled',
    createdAt: '2024-01-05T14:30:00Z',
    expectedDelivery: '2024-01-12T00:00:00Z',
    priority: 'low',
  },
])

const statuses = ['pending', 'approved', 'shipped', 'delivered', 'cancelled']

const filteredOrders = computed(() => {
  return orders.value.filter((order) => {
    const matchesSearch =
      order.id.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      order.supplierName.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = !selectedStatus.value || order.status === selectedStatus.value
    const matchesTab = activeTab.value === 'all' || order.status === activeTab.value
    return matchesSearch && matchesStatus && matchesTab
  })
})

const orderStats = computed(() => ({
  total: orders.value.length,
  pending: orders.value.filter((o) => o.status === 'pending').length,
  approved: orders.value.filter((o) => o.status === 'approved').length,
  shipped: orders.value.filter((o) => o.status === 'shipped').length,
  delivered: orders.value.filter((o) => o.status === 'delivered').length,
  totalValue: orders.value.reduce((sum, o) => sum + o.totalAmount, 0),
}))

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    approved: 'primary',
    shipped: 'info',
    delivered: 'success',
    cancelled: 'danger',
  }
  return types[status] || 'info'
}

const getPriorityType = (priority: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: 'success',
  }
  return types[priority] || 'info'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

// Expandable row data
const expandedRows = ref<string[]>([])

const toggleExpand = (orderId: string) => {
  const index = expandedRows.value.indexOf(orderId)
  if (index > -1) {
    expandedRows.value.splice(index, 1)
  } else {
    expandedRows.value.push(orderId)
  }
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
              <h1 class="text-2xl font-bold text-gray-900">Purchase Orders</h1>
              <p class="text-gray-600">Manage and track supplier orders</p>
            </div>
            <el-button type="primary" :icon="Plus">Create Order</el-button>
          </div>

          <!-- Stats Cards -->
          <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <el-card shadow="hover" class="text-center cursor-pointer" @click="activeTab = 'all'">
              <p class="text-2xl font-bold text-gray-900">{{ orderStats.total }}</p>
              <p class="text-sm text-gray-500">Total Orders</p>
            </el-card>
            <el-card shadow="hover" class="text-center cursor-pointer" @click="activeTab = 'pending'">
              <p class="text-2xl font-bold text-yellow-600">{{ orderStats.pending }}</p>
              <p class="text-sm text-gray-500">Pending</p>
            </el-card>
            <el-card shadow="hover" class="text-center cursor-pointer" @click="activeTab = 'approved'">
              <p class="text-2xl font-bold text-blue-600">{{ orderStats.approved }}</p>
              <p class="text-sm text-gray-500">Approved</p>
            </el-card>
            <el-card shadow="hover" class="text-center cursor-pointer" @click="activeTab = 'shipped'">
              <p class="text-2xl font-bold text-purple-600">{{ orderStats.shipped }}</p>
              <p class="text-sm text-gray-500">In Transit</p>
            </el-card>
            <el-card shadow="hover" class="text-center">
              <p class="text-2xl font-bold text-green-600">{{ formatCurrency(orderStats.totalValue) }}</p>
              <p class="text-sm text-gray-500">Total Value</p>
            </el-card>
          </div>

          <!-- Filters -->
          <el-card class="mb-6">
            <div class="flex flex-wrap items-center gap-4">
              <el-input
                v-model="searchQuery"
                placeholder="Search by PO# or supplier..."
                :prefix-icon="Search"
                class="w-64"
                clearable
              />
              <el-select
                v-model="selectedStatus"
                placeholder="All Statuses"
                clearable
                class="w-40"
              >
                <el-option
                  v-for="status in statuses"
                  :key="status"
                  :label="status.charAt(0).toUpperCase() + status.slice(1)"
                  :value="status"
                />
              </el-select>
              <el-radio-group v-model="activeTab">
                <el-radio-button value="all">All</el-radio-button>
                <el-radio-button value="pending">Pending</el-radio-button>
                <el-radio-button value="approved">Approved</el-radio-button>
                <el-radio-button value="shipped">Shipped</el-radio-button>
                <el-radio-button value="delivered">Delivered</el-radio-button>
              </el-radio-group>
            </div>
          </el-card>

          <!-- Orders Table -->
          <el-card>
            <el-table
              :data="filteredOrders"
              style="width: 100%"
              :row-key="(row: PurchaseOrder) => row.id"
              :expand-row-keys="expandedRows"
            >
              <el-table-column type="expand">
                <template #default="{ row }">
                  <div class="p-4 bg-gray-50">
                    <h4 class="font-semibold mb-3">Order Items</h4>
                    <el-table :data="row.items" size="small">
                      <el-table-column prop="sku" label="SKU" width="120" />
                      <el-table-column prop="name" label="Product" />
                      <el-table-column prop="quantity" label="Qty" width="80" align="center" />
                      <el-table-column label="Unit Cost" width="100" align="right">
                        <template #default="{ row: item }">
                          {{ formatCurrency(item.unitCost) }}
                        </template>
                      </el-table-column>
                      <el-table-column label="Total" width="120" align="right">
                        <template #default="{ row: item }">
                          {{ formatCurrency(item.totalCost) }}
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="id" label="PO Number" width="140">
                <template #default="{ row }">
                  <span
                    class="text-blue-600 cursor-pointer hover:underline"
                    @click="toggleExpand(row.id)"
                  >
                    {{ row.id }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="supplierName" label="Supplier" min-width="180" />
              <el-table-column label="Items" width="80" align="center">
                <template #default="{ row }">
                  {{ row.items.length }}
                </template>
              </el-table-column>
              <el-table-column label="Total Amount" width="130" align="right">
                <template #default="{ row }">
                  <span class="font-semibold">{{ formatCurrency(row.totalAmount) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="Priority" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getPriorityType(row.priority)" size="small">
                    {{ row.priority }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Status" width="110">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Created" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.createdAt) }}
                </template>
              </el-table-column>
              <el-table-column label="Expected" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.expectedDelivery) }}
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button-group size="small">
                    <el-button :icon="View" title="View" />
                    <el-button
                      v-if="row.status === 'pending'"
                      :icon="Check"
                      type="success"
                      title="Approve"
                    />
                    <el-button
                      v-if="row.status === 'pending'"
                      :icon="Close"
                      type="danger"
                      title="Cancel"
                    />
                    <el-button
                      v-if="row.status !== 'delivered' && row.status !== 'cancelled'"
                      :icon="Edit"
                      title="Edit"
                    />
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>

            <div class="flex justify-between items-center mt-4">
              <span class="text-sm text-gray-500">
                Showing {{ filteredOrders.length }} of {{ orders.length }} orders
              </span>
              <el-pagination
                background
                layout="prev, pager, next"
                :total="filteredOrders.length"
                :page-size="10"
              />
            </div>
          </el-card>
        </div>
      </main>
    </div>
  </div>
</template>
