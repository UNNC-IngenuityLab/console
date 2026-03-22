/**
 * Pinia store that uses the real API
 * Replace the mock store with this file for production use
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  authApi,
  usersApi,
  activitiesApi,
  announcementsApi,
  analyticsApi,
  settingsApi,
  adminLogsApi,
} from '../api/services'
import type {
  User,
  Activity,
  Announcement,
  SystemSettings,
  AdminLog,
  DashboardStats,
  LeaderboardEntry,
  LevelDistribution,
} from '../api/types'

export const useApiStore = defineStore('api', () => {
  // Auth state
  const isAuthenticated = ref(!!localStorage.getItem('access_token'))
  const currentUser = ref<User | null>(null)

  // Loading states
  const loading = ref({
    users: false,
    activities: false,
    announcements: false,
    settings: false,
    analytics: false,
  })

  // Error state
  const error = ref<string | null>(null)

  // Data caches
  const users = ref<User[]>([])
  const activities = ref<Activity[]>([])
  const announcements = ref<Announcement[]>([])
  const settings = ref<SystemSettings | null>(null)
  const dashboardStats = ref<DashboardStats | null>(null)
  const leaderboard = ref<LeaderboardEntry[]>([])
  const levelDistribution = ref<LevelDistribution[]>([])
  const adminLogs = ref<AdminLog[]>([])

  // Pagination states
  const usersPagination = ref({ page: 1, total: 0, pageSize: 20, totalPages: 1 })
  const activitiesPagination = ref({ page: 1, total: 0, pageSize: 20, totalPages: 1 })
  const announcementsPagination = ref({ page: 1, total: 0, pageSize: 20, totalPages: 1 })
  const adminLogsPagination = ref({ page: 1, total: 0, pageSize: 50, totalPages: 1 })

  // Computed
  const totalUsers = computed(() => dashboardStats.value?.total_users ?? 0)
  const totalActivities = computed(() => dashboardStats.value?.total_activities ?? 0)
  const activeActivities = computed(
    () => dashboardStats.value?.active_activities ?? 0
  )
  const todayCheckIns = computed(() => {
    // Would need analytics API for this
    return 0
  })

  // Auth methods
  async function login(studentId: string, password: string) {
    try {
      const response = await authApi.login({ student_id: studentId, password })
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token)
        isAuthenticated.value = true
        currentUser.value = response.data.user
        return true
      }
      return false
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      return false
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    isAuthenticated.value = false
    currentUser.value = null
  }

  async function fetchCurrentUser() {
    if (!isAuthenticated.value) return null

    try {
      const response = await authApi.me()
      currentUser.value = response.data
      return response.data
    } catch (err) {
      logout()
      return null
    }
  }

  // User methods
  async function fetchUsers(params = {}) {
    loading.value.users = true
    error.value = null

    try {
      const response = await usersApi.list({
        page: usersPagination.value.page,
        page_size: usersPagination.value.pageSize,
        ...params,
      })
      users.value = response.data.items
      usersPagination.value = {
        page: response.data.page,
        total: response.data.total,
        pageSize: response.data.page_size,
        totalPages: response.data.total_pages,
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch users'
    } finally {
      loading.value.users = false
    }
  }

  async function updateUser(id: string, data: Partial<User>) {
    try {
      await usersApi.update(id, data)
      await fetchUsers() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update user'
      return false
    }
  }

  async function updateUserPoints(id: string, points: number, reason: string) {
    try {
      await usersApi.updatePoints(id, { points, reason })
      await fetchUsers() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update points'
      return false
    }
  }

  async function deleteUser(id: string) {
    try {
      await usersApi.delete(id)
      await fetchUsers() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete user'
      return false
    }
  }

  // Activity methods
  async function fetchActivities(params = {}) {
    loading.value.activities = true
    error.value = null

    try {
      const response = await activitiesApi.list({
        page: activitiesPagination.value.page,
        page_size: activitiesPagination.value.pageSize,
        ...params,
      })
      activities.value = response.data.items
      activitiesPagination.value = {
        page: response.data.page,
        total: response.data.total,
        pageSize: response.data.page_size,
        totalPages: response.data.total_pages,
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch activities'
    } finally {
      loading.value.activities = false
    }
  }

  async function createActivity(data: any) {
    try {
      await activitiesApi.create(data)
      await fetchActivities() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create activity'
      return false
    }
  }

  async function updateActivity(id: string, data: any) {
    try {
      await activitiesApi.update(id, data)
      await fetchActivities() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update activity'
      return false
    }
  }

  async function deleteActivity(id: string) {
    try {
      await activitiesApi.delete(id)
      await fetchActivities() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete activity'
      return false
    }
  }

  async function generateQRCode(activityId: string) {
    try {
      const response = await activitiesApi.generateQR(activityId)
      return response.data.qr_code_url
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to generate QR code'
      return null
    }
  }

  // Announcement methods
  async function fetchAnnouncements(params = {}) {
    loading.value.announcements = true
    error.value = null

    try {
      const response = await announcementsApi.list({
        page: announcementsPagination.value.page,
        page_size: announcementsPagination.value.pageSize,
        ...params,
      })
      announcements.value = response.data.items
      announcementsPagination.value = {
        page: response.data.page,
        total: response.data.total,
        pageSize: response.data.page_size,
        totalPages: response.data.total_pages,
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch announcements'
    } finally {
      loading.value.announcements = false
    }
  }

  async function createAnnouncement(data: any) {
    try {
      await announcementsApi.create(data)
      await fetchAnnouncements() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create announcement'
      return false
    }
  }

  async function updateAnnouncement(id: string, data: any) {
    try {
      await announcementsApi.update(id, data)
      await fetchAnnouncements() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update announcement'
      return false
    }
  }

  async function deleteAnnouncement(id: string) {
    try {
      await announcementsApi.delete(id)
      await fetchAnnouncements() // Refresh list
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete announcement'
      return false
    }
  }

  // Settings methods
  async function fetchSettings() {
    loading.value.settings = true
    error.value = null

    try {
      const response = await settingsApi.get()
      settings.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch settings'
    } finally {
      loading.value.settings = false
    }
  }

  async function updateSettings(data: Partial<SystemSettings>) {
    try {
      await settingsApi.update(data)
      await fetchSettings() // Refresh
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update settings'
      return false
    }
  }

  // Analytics methods
  async function fetchDashboardStats() {
    loading.value.analytics = true
    error.value = null

    try {
      const response = await analyticsApi.dashboard()
      dashboardStats.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch analytics'
    } finally {
      loading.value.analytics = false
    }
  }

  async function fetchLeaderboard(limit = 50) {
    try {
      const response = await analyticsApi.leaderboard({ limit })
      leaderboard.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch leaderboard'
    }
  }

  async function fetchLevelDistribution() {
    try {
      const response = await analyticsApi.levelDistribution()
      levelDistribution.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch level distribution'
    }
  }

  // Admin logs methods
  async function fetchAdminLogs(params = {}) {
    try {
      const response = await adminLogsApi.list({
        page: adminLogsPagination.value.page,
        page_size: adminLogsPagination.value.pageSize,
        ...params,
      })
      adminLogs.value = response.data.items
      adminLogsPagination.value = {
        page: response.data.page,
        total: response.data.total,
        pageSize: response.data.page_size,
        totalPages: response.data.total_pages,
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch admin logs'
    }
  }

  return {
    // State
    isAuthenticated,
    currentUser,
    loading,
    error,
    users,
    activities,
    announcements,
    settings,
    dashboardStats,
    leaderboard,
    levelDistribution,
    adminLogs,
    usersPagination,
    activitiesPagination,
    announcementsPagination,
    adminLogsPagination,

    // Computed
    totalUsers,
    totalActivities,
    activeActivities,
    todayCheckIns,

    // Auth methods
    login,
    logout,
    fetchCurrentUser,

    // User methods
    fetchUsers,
    updateUser,
    updateUserPoints,
    deleteUser,

    // Activity methods
    fetchActivities,
    createActivity,
    updateActivity,
    deleteActivity,
    generateQRCode,

    // Announcement methods
    fetchAnnouncements,
    createAnnouncement,
    updateAnnouncement,
    deleteAnnouncement,

    // Settings methods
    fetchSettings,
    updateSettings,

    // Analytics methods
    fetchDashboardStats,
    fetchLeaderboard,
    fetchLevelDistribution,

    // Admin logs methods
    fetchAdminLogs,
  }
})
