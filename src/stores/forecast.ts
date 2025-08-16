import { defineStore } from "pinia"
import { ref } from "vue"
import type { ForecastTask, ForecastDetail } from "@/types"

export const useForecastStore = defineStore("forecast", () => {
  // State
  const tasks = ref<ForecastTask[]>([])
  const currentTask = ref<ForecastTask | null>(null)
  const taskDetail = ref<ForecastDetail | null>(null)
  const loading = ref(false)

  // Actions
  const fetchTasks = async () => {
    loading.value = true
    try {
      // TODO: Implement fetch tasks API call
      console.log("Fetch forecast tasks")
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData: any) => {
    loading.value = true
    try {
      // TODO: Implement create task API call
      console.log("Create forecast task:", taskData)
    } finally {
      loading.value = false
    }
  }

  const fetchTaskDetail = async (taskId: string) => {
    loading.value = true
    try {
      // TODO: Implement fetch task detail API call
      console.log("Fetch task detail:", taskId)
    } finally {
      loading.value = false
    }
  }

  const deleteTask = async (taskId: string) => {
    // TODO: Implement delete task API call
    console.log("Delete task:", taskId)
  }

  const rerunTask = async (taskId: string) => {
    // TODO: Implement rerun task API call
    console.log("Rerun task:", taskId)
  }

  return {
    tasks,
    currentTask,
    taskDetail,
    loading,
    fetchTasks,
    createTask,
    fetchTaskDetail,
    deleteTask,
    rerunTask,
  }
})
