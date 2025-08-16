import { defineStore } from "pinia"
import { ref, computed } from "vue"
import type { User } from "@/types"

export const useAuthStore = defineStore("auth", () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem("token"))

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRoles = computed(() => user.value?.roles || [])

  // Actions
  const login = async (username: string, password: string) => {
    // TODO: Implement login API call
    console.log("Login:", { username, password })
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem("token")
  }

  const register = async (userData: {
    username: string
    email: string
    phone?: string
    password: string
  }) => {
    // TODO: Implement register API call
    console.log("Register:", userData)
  }

  const fetchUserProfile = async () => {
    // TODO: Implement fetch user profile API call
    console.log("Fetch user profile")
  }

  const hasRole = (role: string) => {
    return userRoles.value.includes(role)
  }

  const hasAnyRole = (roles: string[]) => {
    return roles.some((role) => userRoles.value.includes(role))
  }

  return {
    user,
    token,
    isAuthenticated,
    userRoles,
    login,
    logout,
    register,
    fetchUserProfile,
    hasRole,
    hasAnyRole,
  }
})
