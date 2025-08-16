<template>
  <el-badge :value="unreadCount" :hidden="unreadCount === 0">
    <el-button type="text" @click="showNotifications">
      <el-icon><Bell /></el-icon>
    </el-button>
  </el-badge>
</template>

<script setup lang="ts">
import { Bell } from '@element-plus/icons-vue'

interface Props {
  unreadCount: number
}

defineProps<Props>()

const showNotifications = () => {
  console.log('Show notifications')
}
</script>
