/**
 * API service functions
 * All backend API calls go through these functions
 */

import client from './client'
import type {
  Activity,
  ActivityCreate,
  ActivityDetail,
  ActivityListQuery,
  ActivityStats,
  ActivityUpdate,
  AdminLog,
  Announcement,
  AnnouncementCreate,
  AnnouncementUpdate,
  DashboardStats,
  LeaderboardEntry,
  LevelConfig,
  LevelConfigCreate,
  LevelDistribution,
  LoginRequest,
  LoginResponse,
  PaginatedResponse,
  QRCodeResponse,
  SubActivity,
  SubActivityCreate,
  SubActivityUpdate,
  SystemSettings,
  TrendData,
  UIConfig,
  UIConfigGroup,
  UpdatePointsRequest,
  UserDetail,
  UserListQuery,
  UserSummary,
} from './types'

// =============================================================================
// Authentication API
// =============================================================================

export const authApi = {
  /**
   * Admin login
   */
  login: (data: LoginRequest) =>
    client.post<ApiResponse<LoginResponse>>('/api/v1/auth/login', data),

  /**
   * Logout
   */
  logout: () => client.post<ApiResponse>('/api/v1/auth/logout'),

  /**
   * Get current user info
   */
  me: () => client.get<ApiResponse<UserSummary>>('/api/v1/auth/me'),
}

// =============================================================================
// Users API
// =============================================================================

export const usersApi = {
  /**
   * List users with filters and pagination
   */
  list: (params: UserListQuery) =>
    client.get<ApiResponse<PaginatedResponse<UserSummary>>, UserListQuery>('/api/v1/users/', {
      params,
    }),

  /**
   * Get user by ID
   */
  get: (id: string) => client.get<ApiResponse<UserDetail>>(`/api/v1/users/${id}`),

  /**
   * Update user points
   */
  updatePoints: (id: string, data: UpdatePointsRequest) =>
    client.put<ApiResponse>(`/api/v1/users/${id}/points`, data),

  /**
   * Update user
   */
  update: (id: string, data: Partial<UserSummary>) =>
    client.put<ApiResponse>(`/api/v1/users/${id}`, data),

  /**
   * Delete user
   */
  delete: (id: string) => client.delete<ApiResponse>(`/api/v1/users/${id}`),
}

// =============================================================================
// Activities API
// =============================================================================

export const activitiesApi = {
  /**
   * List activities with filters and pagination
   */
  list: (params: ActivityListQuery = {}) =>
    client.get<ApiResponse<PaginatedResponse<Activity>>, ActivityListQuery>('/api/v1/activities/', {
      params,
    }),

  /**
   * Get activity by ID with sub-activities
   */
  get: (id: string) => client.get<ApiResponse<ActivityDetail>>(`/api/v1/activities/${id}`),

  /**
   * Create activity
   */
  create: (data: ActivityCreate) =>
    client.post<ApiResponse<{ activity_id: string }>>('/api/v1/activities/', data),

  /**
   * Update activity
   */
  update: (id: string, data: ActivityUpdate) =>
    client.put<ApiResponse>(`/api/v1/activities/${id}`, data),

  /**
   * Delete activity
   */
  delete: (id: string) => client.delete<ApiResponse>(`/api/v1/activities/${id}`),

  /**
   * Generate QR code for check-in
   */
  generateQR: (id: string) =>
    client.post<ApiResponse<QRCodeResponse>>(`/api/v1/activities/${id}/qrcode`),

  // Sub-activities
  createSubActivity: (activityId: string, data: SubActivityCreate) =>
    client.post<ApiResponse<{ sub_activity_id: number }>>(
      `/api/v1/activities/${activityId}/sub-activities`,
      data
    ),

  updateSubActivity: (subActivityId: number, data: SubActivityUpdate) =>
    client.put<ApiResponse>(`/api/v1/activities/sub-activities/${subActivityId}`, data),

  deleteSubActivity: (subActivityId: number) =>
    client.delete<ApiResponse>(`/api/v1/activities/sub-activities/${subActivityId}`),
}

// =============================================================================
// Announcements API
// =============================================================================

export const announcementsApi = {
  /**
   * List announcements with pagination
   */
  list: (params: { is_active?: boolean; page?: number; page_size?: number } = {}) =>
    client.get<ApiResponse<PaginatedResponse<Announcement>>>('/api/v1/announcements/', {
      params,
    }),

  /**
   * Get announcement by ID
   */
  get: (id: string) => client.get<ApiResponse<Announcement>>(`/api/v1/announcements/${id}`),

  /**
   * Create announcement
   */
  create: (data: AnnouncementCreate) =>
    client.post<ApiResponse<{ announcement_id: string }>>('/api/v1/announcements/', data),

  /**
   * Update announcement
   */
  update: (id: string, data: AnnouncementUpdate) =>
    client.put<ApiResponse>(`/api/v1/announcements/${id}`, data),

  /**
   * Delete announcement
   */
  delete: (id: string) => client.delete<ApiResponse>(`/api/v1/announcements/${id}`),
}

// =============================================================================
// Level Configuration API
// =============================================================================

export const levelsApi = {
  /**
   * List all level configurations
   */
  list: (params: { is_active?: boolean } = {}) =>
    client.get<ApiResponse<LevelConfig[]>>('/api/v1/levels/', { params }),

  /**
   * Export level configs as JSON
   */
  export: () => client.get<ApiResponse<{ levels: LevelConfig[]; exported_at: string }>>('/api/v1/levels/export'),

  /**
   * Import level configs from JSON
   */
  import: (data: { levels: LevelConfigCreate[]; replace_existing?: boolean }) =>
    client.post<ApiResponse<{ imported_count: number }>>('/api/v1/levels/import', data),

  /**
   * Get level config by ID
   */
  get: (id: number) => client.get<ApiResponse<LevelConfig>>(`/api/v1/levels/${id}`),

  /**
   * Create level config
   */
  create: (data: LevelConfigCreate) =>
    client.post<ApiResponse<{ level_id: number }>>('/api/v1/levels/', data),

  /**
   * Update level config
   */
  update: (id: number, data: Partial<LevelConfigCreate>) =>
    client.put<ApiResponse>(`/api/v1/levels/${id}`, data),

  /**
   * Delete level config
   */
  delete: (id: number) => client.delete<ApiResponse>(`/api/v1/levels/${id}`),

  /**
   * Reorder levels
   */
  reorder: (level_orders: Record<number, number>) =>
    client.put<ApiResponse>('/api/v1/levels/reorder', { level_orders }),
}

// =============================================================================
// UI Configuration API
// =============================================================================

export const uiConfigApi = {
  /**
   * Get all UI configs grouped by category
   */
  getAll: () => client.get<ApiResponse<UIConfigGroup>>('/api/v1/config/ui'),

  /**
   * Get UI configs by category
   */
  getByCategory: (category: string) =>
    client.get<ApiResponse<Record<string, UIConfig>>>(`/api/v1/config/ui/category/${category}`),

  /**
   * Get single UI config by key
   */
  get: (key: string) => client.get<ApiResponse<UIConfig>>(`/api/v1/config/ui/key/${key}`),

  /**
   * Update single UI config
   */
  update: (key: string, value: string) =>
    client.put<ApiResponse>(`/api/v1/config/ui/${key}`, { value }),

  /**
   * Batch update UI configs
   */
  batchUpdate: (configs: Record<string, string>) =>
    client.put<ApiResponse>('/api/v1/config/ui/batch', { configs }),
}

// =============================================================================
// System Settings API
// =============================================================================

export const settingsApi = {
  /**
   * Get system settings
   */
  get: () => client.get<ApiResponse<SystemSettings>>('/api/v1/settings/'),

  /**
   * Update system settings
   */
  update: (data: Partial<SystemSettings>) =>
    client.put<ApiResponse>('/api/v1/settings/', data),
}

// =============================================================================
// Analytics API
// =============================================================================

export const analyticsApi = {
  /**
   * Get dashboard statistics
   */
  dashboard: () => client.get<ApiResponse<DashboardStats>>('/api/v1/analytics/dashboard'),

  /**
   * Get activity completion statistics
   */
  activityStats: (params: { limit?: number } = {}) =>
    client.get<ApiResponse<ActivityStats[]>>('/api/v1/analytics/activity-stats', { params }),

  /**
   * Get user activity trend data
   */
  trend: (params: { days?: number } = {}) =>
    client.get<ApiResponse<TrendData[]>>('/api/v1/analytics/trend', { params }),

  /**
   * Get leaderboard data
   */
  leaderboard: (params: { limit?: number } = {}) =>
    client.get<ApiResponse<LeaderboardEntry[]>>('/api/v1/analytics/leaderboard', { params }),

  /**
   * Get level distribution
   */
  levelDistribution: () =>
    client.get<ApiResponse<LevelDistribution[]>>('/api/v1/analytics/level-distribution'),
}

// =============================================================================
// Admin Logs API
// =============================================================================

export const adminLogsApi = {
  /**
   * List admin logs with filters
   */
  list: (params: {
    action?: string
    admin_openid?: string
    target_id?: string
    page?: number
    page_size?: number
  } = {}) => client.get<ApiResponse<PaginatedResponse<AdminLog>>>('/api/v1/admin-logs/', { params }),

  /**
   * Export logs as CSV
   */
  export: (params: {
    action?: string
    admin_openid?: string
    target_id?: string
    limit?: number
  } = {}) =>
    client.get('/api/v1/admin-logs/export', {
      params,
      responseType: 'blob',
    }),
}
