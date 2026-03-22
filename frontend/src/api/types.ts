/**
 * TypeScript types for API requests and responses
 */

// =============================================================================
// Base Types
// =============================================================================

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// =============================================================================
// Authentication Types
// =============================================================================

export interface LoginRequest {
  student_id: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserSummary
}

export interface UserSummary {
  id: string
  student_id: string
  nickname: string | null
  avatar_url: string | null
  total_points: number
  level: number
  is_active: boolean
}

// =============================================================================
// User Types
// =============================================================================

export interface UserDetail extends UserSummary {
  openid: string
  created_at: string
  updated_at: string
}

export interface UserListQuery {
  search?: string
  level?: number
  is_active?: boolean
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: string
}

export interface UpdatePointsRequest {
  points: number
  reason: string
}

// =============================================================================
// Activity Types
// =============================================================================

export interface SubActivity {
  id: number
  activity_id: string
  name: string
  point: number
  is_stopped: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface SubActivityCreate {
  name: string
  point: number
  sort_order?: number
}

export interface SubActivityUpdate {
  name?: string
  point?: number
  is_stopped?: boolean
  sort_order?: number
}

export interface Activity {
  id: string
  activity_id: number
  creator_openid: string | null
  name: string
  venue: string
  date_range: string
  start_date: string | null
  end_date: string | null
  total_point: number
  sign_up_count: number
  completed_count: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ActivityDetail extends Activity {
  sub_activities: SubActivity[]
}

export interface ActivityCreate {
  name: string
  venue: string
  date_range: string
  start_date?: string
  end_date?: string
  total_point?: number
  sub_activities?: SubActivityCreate[]
}

export interface ActivityUpdate {
  name?: string
  venue?: string
  date_range?: string
  start_date?: string
  end_date?: string
  total_point?: number
  is_active?: boolean
}

export interface ActivityListQuery {
  search?: string
  is_active?: boolean
  start_date_from?: string
  start_date_to?: string
  page?: number
  page_size?: number
}

// =============================================================================
// Announcement Types
// =============================================================================

export interface Announcement {
  id: string
  creator_openid: string
  title: string
  content: string
  is_active: boolean
  priority: number
  created_at: string
  updated_at: string
}

export interface AnnouncementCreate {
  title: string
  content: string
  priority?: number
}

export interface AnnouncementUpdate {
  title?: string
  content?: string
  is_active?: boolean
  priority?: number
}

// =============================================================================
// Level Config Types
// =============================================================================

export interface LevelConfig {
  id: number
  level: number
  name: string
  name_en: string | null
  name_zh_tw: string | null
  min_score: number
  max_score: number | null
  icon_url: string | null
  icon_dark_url: string | null
  bg_color: string | null
  bg_gradient_start: string | null
  bg_gradient_end: string | null
  description: string | null
  description_en: string | null
  animation_type: string
  sound_url: string | null
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface LevelConfigCreate {
  level: number
  name: string
  name_en?: string
  name_zh_tw?: string
  min_score: number
  max_score?: number
  icon_url?: string
  icon_dark_url?: string
  bg_color?: string
  bg_gradient_start?: string
  bg_gradient_end?: string
  description?: string
  description_en?: string
  animation_type?: string
  sound_url?: string
  is_active?: boolean
  sort_order?: number
}

// =============================================================================
// UI Config Types
// =============================================================================

export interface UIConfig {
  key: string
  value: string
  type: string
  category: string
  label: string
  description: string | null
  min_value: number | null
  max_value: number | null
  allowed_values: any
  updated_at: string
  updated_by: string | null
}

export interface UIConfigGroup {
  [category: string]: {
    [key: string]: UIConfig
  }
}

// =============================================================================
// System Settings Types
// =============================================================================

export interface SystemSettings {
  id: string
  qr_code_expiration_seconds: number
  max_points_per_activity: number
  max_points_per_sub_activity: number
  registration_open: boolean
  new_user_initial_points: number
  leaderboard_top_n: number
  leaderboard_refresh_interval_seconds: number
  activities_per_page: number
  scan_rate_limit_per_minute: number
  maintenance_mode: boolean
  maintenance_message: string | null
  updated_at: string
}

// =============================================================================
// Analytics Types
// =============================================================================

export interface DashboardStats {
  total_users: number
  total_activities: number
  active_activities: number
  total_signups: number
  total_completions: number
  avg_completion_rate: number
  total_points_awarded: number
}

export interface ActivityStats {
  activity_id: string
  activity_name: string
  sign_up_count: number
  completed_count: number
  completion_rate: number
  total_points: number
}

export interface TrendData {
  date: string
  new_users: number
  new_signups: number
  new_completions: number
  points_awarded: number
}

export interface LeaderboardEntry {
  rank: number
  user_id: string
  student_id: string
  nickname: string | null
  avatar_url: string | null
  total_points: number
  level: number
}

export interface LevelDistribution {
  level: number
  level_name: string
  user_count: number
  percentage: number
}

// =============================================================================
// Admin Log Types
// =============================================================================

export interface AdminLog {
  id: number
  admin_openid: string
  action: string
  target_id: string | null
  description: string
  old_value: any
  new_value: any
  ip_address: string | null
  created_at: string
}

// =============================================================================
// QR Code Types
// =============================================================================

export interface QRCodeResponse {
  qr_code_url: string
  activity_id: string
  activity_name: string
  expires_at: string
}
