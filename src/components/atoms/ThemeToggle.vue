<template>
  <el-button type="text" @click="toggleTheme">
    <el-icon>
      <Sunny v-if="isDark" />
      <Moon v-else />
    </el-icon>
  </el-button>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Sunny, Moon } from '@element-plus/icons-vue'

const isDark = ref(false)

const emit = defineEmits<{
  change: [theme: string]
}>()

const toggleTheme = () => {
  isDark.value = !isDark.value
  emit('change', isDark.value ? 'dark' : 'light')
}
</script>
