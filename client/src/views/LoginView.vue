<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const loginForm = reactive({
  email: '',
  password: '',
  remember: false,
})

const rules = {
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: 'blur' },
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' },
  ],
}

const formRef = ref()

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(loginForm.email, loginForm.password)
        ElMessage.success('Login successful!')
        router.push('/dashboard')
      } catch (error) {
        ElMessage.error('Invalid credentials. Please try again.')
      } finally {
        loading.value = false
      }
    }
  })
}

// Demo credentials auto-fill
const fillDemoCredentials = () => {
  loginForm.email = 'admin@supplychain.io'
  loginForm.password = 'demo123'
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
          <el-icon :size="32" class="text-white"><Box /></el-icon>
        </div>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          SupplyChain<span class="text-blue-600">IQ</span>
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          AI-Powered Supply Chain Optimization Platform
        </p>
      </div>

      <!-- Login Form -->
      <el-card class="shadow-xl">
        <el-form
          ref="formRef"
          :model="loginForm"
          :rules="rules"
          label-position="top"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="Email Address" prop="email">
            <el-input
              v-model="loginForm.email"
              placeholder="Enter your email"
              size="large"
              :prefix-icon="Message"
            />
          </el-form-item>

          <el-form-item label="Password" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="Enter your password"
              size="large"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>

          <el-form-item>
            <div class="flex items-center justify-between w-full">
              <el-checkbox v-model="loginForm.remember">Remember me</el-checkbox>
              <el-link type="primary" :underline="false">Forgot password?</el-link>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="w-full"
              @click="handleLogin"
            >
              Sign In
            </el-button>
          </el-form-item>
        </el-form>

        <el-divider>Or</el-divider>

        <el-button
          size="large"
          class="w-full"
          @click="fillDemoCredentials"
        >
          <el-icon class="mr-2"><User /></el-icon>
          Use Demo Credentials
        </el-button>
      </el-card>

      <!-- Features -->
      <div class="grid grid-cols-3 gap-4 text-center">
        <div class="p-3">
          <el-icon :size="24" class="text-blue-600 mb-2"><TrendCharts /></el-icon>
          <p class="text-xs text-gray-600">Demand Forecasting</p>
        </div>
        <div class="p-3">
          <el-icon :size="24" class="text-green-600 mb-2"><Goods /></el-icon>
          <p class="text-xs text-gray-600">Inventory Optimization</p>
        </div>
        <div class="p-3">
          <el-icon :size="24" class="text-purple-600 mb-2"><DataAnalysis /></el-icon>
          <p class="text-xs text-gray-600">Smart Analytics</p>
        </div>
      </div>

      <!-- Footer -->
      <p class="text-center text-xs text-gray-500">
        © 2024 SupplyChainIQ. Built with Vue 3, Django & Prophet ML.
      </p>
    </div>
  </div>
</template>

<script lang="ts">
import { Message, Lock, User, Box, TrendCharts, Goods, DataAnalysis } from '@element-plus/icons-vue'

export default {
  components: {
    Message,
    Lock,
    User,
    Box,
    TrendCharts,
    Goods,
    DataAnalysis,
  },
}
</script>
