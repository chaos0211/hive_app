<template>
  <el-menu
    :default-active="activePath"
    :collapse="collapsed"
    class="side-nav"
    @select="handleSelect"
  >
    <el-menu-item index="/cockpit">
      <el-icon><Odometer /></el-icon>
      <span>驾驶舱</span>
    </el-menu-item>
    
    <el-sub-menu index="/rank">
      <template #title>
        <el-icon><TrendCharts /></el-icon>
        <span>华为应用榜单</span>
      </template>
      <el-menu-item index="/rank/list">榜单列表</el-menu-item>
      <el-menu-item index="/rank/compare">应用对比</el-menu-item>
    </el-sub-menu>
    
    <el-sub-menu index="/analysis">
      <template #title>
        <el-icon><PieChart /></el-icon>
        <span>数据分析</span>
      </template>
      <el-menu-item index="/analysis/overview">总览</el-menu-item>
      <el-menu-item index="/analysis/category">分类维度</el-menu-item>
      <el-menu-item index="/analysis/region">地区维度</el-menu-item>
      <el-menu-item index="/analysis/keywords">关键词</el-menu-item>
    </el-sub-menu>
    
    <el-sub-menu index="/forecast">
      <template #title>
        <el-icon><TrendCharts /></el-icon>
        <span>数据预测</span>
      </template>
      <el-menu-item index="/forecast/create">新建预测</el-menu-item>
      <el-menu-item index="/forecast/list">预测记录</el-menu-item>
    </el-sub-menu>
    
    <el-sub-menu index="/hive">
      <template #title>
        <el-icon><DataBoard /></el-icon>
        <span>Hive 数据</span>
      </template>
      <el-menu-item index="/hive/jobs">任务中心</el-menu-item>
      <el-menu-item index="/hive/quality">数据质量</el-menu-item>
      <el-menu-item index="/hive/partitions">分区预览</el-menu-item>
    </el-sub-menu>
    
    <el-menu-item index="/users">
      <el-icon><User /></el-icon>
      <span>用户管理</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { Odometer, TrendCharts, PieChart, DataBoard, User } from '@element-plus/icons-vue'

interface Props {
  activePath: string
  collapsed?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  navigate: [path: string]
}>()

const handleSelect = (index: string) => {
  emit('navigate', index)
}
</script>

<style scoped>
.side-nav {
  height: 100%;
  border-right: none;
}
</style>
