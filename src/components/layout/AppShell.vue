<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <TopNav
        :user="user"
        @toggle-sidebar="toggleSidebar"
        @logout="handleLogout"
      />
    </el-header>
    <el-container>
      <el-aside :width="sidebarWidth" class="app-sidebar">
        <SideNav
          :active-path="$route.path"
          :collapsed="!isSidebarOpen"
          @navigate="handleNavigate"
        />
      </el-aside>
      <el-main class="app-main">
        <PageContainer>
          <router-view />
        </PageContainer>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TopNav from './TopNav.vue'
import SideNav from './SideNav.vue'
import PageContainer from './PageContainer.vue'

const router = useRouter()
const authStore = useAuthStore()

// State
const isSidebarOpen = ref(true)
const theme = ref<'light' | 'dark'>('light')

// Computed
const user = computed(() => authStore.user)
const sidebarWidth = computed(() => isSidebarOpen.value ? '240px' : '64px')

// Methods
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleNavigate = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.app-shell {
  height: 100vh;
}

.app-header {
  padding: 0;
  border-bottom: 1px solid var(--el-border-color);
}

.app-sidebar {
  border-right: 1px solid var(--el-border-color);
  transition: width 0.3s;
}

.app-main {
  padding: 0;
  background-color: var(--el-bg-color-page);
}
</style>
