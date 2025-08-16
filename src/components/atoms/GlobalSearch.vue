<template>
  <el-input
    v-model="searchQuery"
    placeholder="搜索..."
    class="global-search"
    clearable
    @keyup.enter="handleSearch"
  >
    <template #prefix>
      <el-icon><Search /></el-icon>
    </template>
  </el-input>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const searchQuery = ref('')

const handleSearch = () => {
  console.log('Search:', searchQuery.value)
}
</script>

<style scoped>
.global-search {
  width: 200px;
}
</style>
