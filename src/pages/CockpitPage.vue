<template>
  <div class="cockpit-page">
    <h1>驾驶舱</h1>
    
    <!-- Filters -->
    <FilterBar
      :initial="filters"
      @apply="handleFiltersApply"
      @reset="handleFiltersReset"
    />
    
    <!-- KPI Grid -->
    <KpiGrid :items="kpiItems" />
    
    <!-- Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <CardEchartsLine :data="lineChartData" />
      </el-col>
      <el-col :span="12">
        <CardEchartsPie :data="pieChartData" />
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <CardEchartsMapCN :data="mapChartData" />
      </el-col>
      <el-col :span="8">
        <LiveFeedPanel :items="feedItems" @refresh="fetchFeedData" />
      </el-col>
    </el-row>
    
    <el-row class="charts-row">
      <el-col :span="24">
        <CardEchartsGantt :data="ganttChartData" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCockpitStore } from '@/stores/cockpit'
import FilterBar from '@/components/cockpit/FilterBar.vue'
import KpiGrid from '@/components/cockpit/KpiGrid.vue'
import CardEchartsLine from '@/components/cockpit/CardEchartsLine.vue'
import CardEchartsPie from '@/components/cockpit/CardEchartsPie.vue'
import CardEchartsMapCN from '@/components/cockpit/CardEchartsMapCN.vue'
import LiveFeedPanel from '@/components/cockpit/LiveFeedPanel.vue'
import CardEchartsGantt from '@/components/cockpit/CardEchartsGantt.vue'

const cockpitStore = useCockpitStore()

// Computed properties from store
const filters = ref(cockpitStore.filters)
const kpiItems = ref(cockpitStore.kpiItems)
const feedItems = ref(cockpitStore.feedItems)
const lineChartData = ref(cockpitStore.lineChartData)
const pieChartData = ref(cockpitStore.pieChartData)
const mapChartData = ref(cockpitStore.mapChartData)
const ganttChartData = ref(cockpitStore.ganttChartData)

// Methods
const handleFiltersApply = (newFilters: any) => {
  cockpitStore.updateFilters(newFilters)
  fetchData()
}

const handleFiltersReset = () => {
  cockpitStore.resetFilters()
  fetchData()
}

const fetchData = async () => {
  await Promise.all([
    cockpitStore.fetchKpiData(),
    cockpitStore.fetchChartData(),
    cockpitStore.fetchFeedData()
  ])
}

const fetchFeedData = () => {
  cockpitStore.fetchFeedData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.cockpit-page {
  padding: 20px;
}

.charts-row {
  margin-top: 20px;
}
</style>
