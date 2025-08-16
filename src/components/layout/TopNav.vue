<template>
  <div class="top-nav">
    <div class="nav-left">
      <el-button
        type="text"
        @click="$emit('toggle-sidebar')"
        class="sidebar-toggle"
      >
        <el-icon><Menu /></el-icon>
      </el-button>
      <h1 class="app-title">华为应用榜单数据分析平台</h1>
    </div>
    
    <div class="nav-right">
      <GlobalSearch />
      <NotificationBell :unread-count="5" />
      <ThemeToggle @change="handleThemeChange" />
      <UserMenu :user="user" @logout="$emit('logout')" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Menu } from '@element-plus/icons-vue'
import GlobalSearch from '@/components/atoms/GlobalSearch.vue'
import NotificationBell from '@/components/atoms/NotificationBell.vue'
import ThemeToggle from '@/components/atoms/ThemeToggle.vue'
import UserMenu from '@/components/atoms/UserMenu.vue'

interface Props {
  user?: { name: string; email: string; avatar?: string } | null
}

defineProps<Props>()

defineEmits<{
  'toggle-sidebar': []
  logout: []
}>()

const handleThemeChange = (theme: string) => {
  console.log('Theme changed:', theme)
}
</script>

<style scoped>
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background: var(--el-bg-color);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sidebar-toggle {
  font-size: 18px;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
