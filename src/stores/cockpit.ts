import { defineStore } from "pinia"
import { ref } from "vue"
import type { KpiItem, FeedItem, CockpitFilters, LineInput, PieInput, MapInput, GanttInput } from "@/types"

export const useCockpitStore = defineStore("cockpit", () => {
  // State
  const filters = ref<CockpitFilters>({})
  const kpiItems = ref<KpiItem[]>([])
  const feedItems = ref<FeedItem[]>([])
  const lineChartData = ref<LineInput | null>(null)
  const pieChartData = ref<PieInput | null>(null)
  const mapChartData = ref<MapInput | null>(null)
  const ganttChartData = ref<GanttInput | null>(null)

  // Actions
  const fetchKpiData = async () => {
    // TODO: Implement fetch KPI data API call
    console.log("Fetch KPI data")
  }

  const fetchChartData = async () => {
    // TODO: Implement fetch chart data API call
    console.log("Fetch chart data")
  }

  const fetchFeedData = async () => {
    // TODO: Implement fetch feed data API call
    console.log("Fetch feed data")
  }

  const updateFilters = (newFilters: Partial<CockpitFilters>) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const resetFilters = () => {
    filters.value = {}
  }

  return {
    filters,
    kpiItems,
    feedItems,
    lineChartData,
    pieChartData,
    mapChartData,
    ganttChartData,
    fetchKpiData,
    fetchChartData,
    fetchFeedData,
    updateFilters,
    resetFilters,
  }
})
