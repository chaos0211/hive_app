import { defineStore } from "pinia"
import { ref } from "vue"
import type { RankRow } from "@/types"

export const useRankStore = defineStore("rank", () => {
  // State
  const rankList = ref<RankRow[]>([])
  const selectedApps = ref<string[]>([])
  const loading = ref(false)

  // Actions
  const fetchRankList = async (filters?: any) => {
    loading.value = true
    try {
      // TODO: Implement fetch rank list API call
      console.log("Fetch rank list:", filters)
    } finally {
      loading.value = false
    }
  }

  const fetchAppDetail = async (appId: string) => {
    // TODO: Implement fetch app detail API call
    console.log("Fetch app detail:", appId)
  }

  const addToCompare = (appId: string) => {
    if (!selectedApps.value.includes(appId) && selectedApps.value.length < 5) {
      selectedApps.value.push(appId)
    }
  }

  const removeFromCompare = (appId: string) => {
    const index = selectedApps.value.indexOf(appId)
    if (index > -1) {
      selectedApps.value.splice(index, 1)
    }
  }

  const clearCompare = () => {
    selectedApps.value = []
  }

  return {
    rankList,
    selectedApps,
    loading,
    fetchRankList,
    fetchAppDetail,
    addToCompare,
    removeFromCompare,
    clearCompare,
  }
})
