<template>
  <el-dropdown @command="handleCommand">
    <el-button type="text" class="user-menu">
      <el-avatar :size="32" :src="user?.avatar">
        {{ user?.name?.charAt(0) }}
      </el-avatar>
      <span class="username">{{ user?.name }}</span>
      <el-icon><ArrowDown /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="profile">个人资料</el-dropdown-item>
        <el-dropdown-item command="settings">设置</el-dropdown-item>
        <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ArrowDown } from '@element-plus/icons-vue'

interface Props {
  user?: { name: string; email: string; avatar?: string } | null
}

defineProps<Props>()

const emit = defineEmits<{
  logout: []
}>()

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      console.log('Open profile')
      break
    case 'settings':
      console.log('Open settings')
      break
    case 'logout':
      emit('logout')
      break
  }
}
</script>

<style scoped>
.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-size: 14px;
}
</style>
