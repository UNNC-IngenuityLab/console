/**
 * Shared helpers and mock data for E2E tests.
 */

// Mock API responses
export const MOCK_LOGIN_RESPONSE = {
  code: 0,
  message: 'success',
  data: {
    access_token: 'mock-jwt-token-for-e2e-testing',
    token_type: 'bearer',
    user: {
      id: 'user123abc456def7890ab12',
      student_id: 'N20230001',
      nickname: 'Test Admin',
      avatar_url: null,
      total_points: '15.00',
      level: 3,
      is_active: true,
    },
  },
}

export const MOCK_USER_ME = {
  code: 0,
  message: 'success',
  data: {
    id: 'user123abc456def7890ab12',
    student_id: 'N20230001',
    nickname: 'Test Admin',
    avatar_url: null,
    total_points: '15.00',
    level: 3,
    is_active: true,
  },
}

export const MOCK_DASHBOARD_STATS = {
  code: 0,
  message: 'success',
  data: {
    total_users: 120,
    total_activities: 15,
    active_activities: 8,
    total_signups: 450,
    total_completions: 320,
    avg_completion_rate: 71.11,
    total_points_awarded: '1580.00',
  },
}

export const MOCK_ACTIVITIES_PAGE = {
  code: 0,
  message: 'success',
  data: {
    items: [
      {
        id: 'act123abc456def789ab123',
        activity_id: 1704067200000,
        name: 'Test Activity Alpha',
        venue: 'Main Hall',
        start_date: '2024-01-15T09:00:00',
        end_date: '2024-01-15T17:00:00',
        total_point: '10.00',
        sign_up_count: 5,
        completed_count: 3,
        is_active: true,
        sub_activity_count: 2,
        created_at: '2024-01-01T00:00:00',
        updated_at: '2024-01-01T00:00:00',
      },
    ],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
  },
}

export const MOCK_USERS_PAGE = {
  code: 0,
  message: 'success',
  data: {
    items: [
      {
        id: 'usr456abc789def0123ab45',
        student_id: 'N20230002',
        nickname: 'Test Student',
        avatar_url: null,
        total_points: '25.00',
        level: 4,
        is_active: true,
      },
    ],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
  },
}

export const MOCK_USER_ACTIVITIES = {
  code: 0,
  message: 'success',
  data: [
    {
      id: 'ra123abc456def789ab12',
      activity_id: 'act123abc456def789ab123',
      activity_name: 'Test Activity Alpha',
      venue: 'Main Hall',
      is_completed: true,
      points_earned: 10.00,
      registered_at: '2024-01-15T08:30:00',
      completed_at: '2024-01-15T17:00:00',
    },
    {
      id: 'ra456def789abc012ab34cd',
      activity_id: 'act456def789abc012ab345',
      activity_name: 'Another Activity',
      venue: 'Room 101',
      is_completed: false,
      points_earned: 0,
      registered_at: '2024-01-20T10:00:00',
      completed_at: null,
    },
  ],
}

export const MOCK_ANNOUNCEMENTS_PAGE = {
  code: 0,
  message: 'success',
  data: {
    items: [
      {
        id: 'ann123abc456def789ab123',
        title: 'Test Announcement',
        content: 'This is a test announcement.',
        is_active: true,
        priority: 1,
        created_at: '2024-01-01T00:00:00',
        updated_at: '2024-01-01T00:00:00',
      },
    ],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
  },
}

export const MOCK_LEADERBOARD = {
  code: 0,
  message: 'success',
  data: [
    {
      rank: 1,
      user_id: 'usr456abc789def0123ab45',
      student_id: 'N20230002',
      nickname: 'Top Student',
      avatar_url: null,
      total_points: '95.00',
      level: 7,
    },
  ],
}

export const MOCK_TREND = {
  code: 0,
  message: 'success',
  data: [],
}

export const MOCK_LEVEL_DIST = {
  code: 0,
  message: 'success',
  data: [{ level: 1, level_name: '车库小店', user_count: 40, percentage: 33.3 }],
}

export const MOCK_ACTIVITY_STATS = {
  code: 0,
  message: 'success',
  data: [],
}

export const MOCK_LEVELS = {
  code: 0,
  message: 'success',
  data: [
    {
      id: 1,
      level: 1,
      name: '车库小店',
      name_en: 'Garage Shop',
      name_zh_tw: '車庫小店',
      min_score: '0.00',
      max_score: '10.00',
      icon_url: '/assets/levels/level-1.png',
      icon_dark_url: null,
      bg_color: '#9E9E9E',
      bg_gradient_start: null,
      bg_gradient_end: null,
      description: '创业起步',
      description_en: 'Startup Beginning',
      animation_type: 'none',
      sound_url: null,
      is_active: true,
      sort_order: 0,
      created_at: '2024-01-01T00:00:00',
      updated_at: '2024-01-01T00:00:00',
    },
    {
      id: 2,
      level: 2,
      name: '城市小店',
      name_en: 'City Shop',
      name_zh_tw: '城市小店',
      min_score: '10.00',
      max_score: '25.00',
      icon_url: '/assets/levels/level-2.png',
      icon_dark_url: null,
      bg_color: '#2196F3',
      bg_gradient_start: null,
      bg_gradient_end: null,
      description: '小有成就',
      description_en: 'Some Achievement',
      animation_type: 'none',
      sound_url: null,
      is_active: true,
      sort_order: 1,
      created_at: '2024-01-01T00:00:00',
      updated_at: '2024-01-01T00:00:00',
    },
  ],
}

export const MOCK_LEVELS_EXPORT = {
  code: 0,
  message: 'success',
  data: {
    levels: [
      {
        level: 1,
        name: '车库小店',
        min_score: '0.00',
        max_score: '10.00',
        is_active: true,
      },
    ],
    exported_at: '2024-01-01T00:00:00',
  },
}

export const MOCK_UI_CONFIG = {
  code: 0,
  message: 'success',
  data: {
    general: {
      app_name: {
        key: 'app_name',
        value: 'IngenuityLab',
        type: 'text',
        category: 'general',
        label: '应用名称',
        description: null,
        min_value: null,
        max_value: null,
        allowed_values: null,
        updated_at: '2024-01-01T00:00:00',
        updated_by: 'admin',
      },
    },
  },
}

export const MOCK_SYSTEM_SETTINGS = {
  code: 0,
  message: 'success',
  data: {
    id: 'system',
    qr_code_expiration_seconds: 300,
    max_points_per_activity: '50.00',
    max_points_per_sub_activity: '10.00',
    registration_open: true,
    new_user_initial_points: '0.00',
    leaderboard_top_n: 10,
    leaderboard_refresh_interval_seconds: 300,
    activities_per_page: 10,
    scan_rate_limit_per_minute: 10,
    maintenance_mode: false,
    maintenance_message: null,
    updated_at: '2024-01-01T00:00:00',
  },
}

/**
 * Set localStorage access token to simulate a logged-in state.
 * Must be called before page.goto() — uses addInitScript which runs before page JS.
 */
export async function setAuthToken(page) {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'mock-jwt-token-for-e2e-testing')
  })
}

/**
 * Clear auth token to simulate logged-out state.
 */
export async function clearAuthToken(page) {
  await page.addInitScript(() => {
    localStorage.removeItem('access_token')
  })
}

/**
 * Mock all common API endpoints for an authenticated session.
 * Uses regex patterns so query params don't break matching.
 * Call this BEFORE page.goto().
 */
export async function mockAuthenticatedApis(page) {
  await page.route(/\/api\/v1\/auth\/me/, (route) =>
    route.fulfill({ json: MOCK_USER_ME })
  )
  await page.route(/\/api\/v1\/analytics\/dashboard/, (route) =>
    route.fulfill({ json: MOCK_DASHBOARD_STATS })
  )
  await page.route(/\/api\/v1\/analytics\/leaderboard/, (route) =>
    route.fulfill({ json: MOCK_LEADERBOARD })
  )
  await page.route(/\/api\/v1\/analytics\/trend/, (route) =>
    route.fulfill({ json: MOCK_TREND })
  )
  await page.route(/\/api\/v1\/analytics\/level-distribution/, (route) =>
    route.fulfill({ json: MOCK_LEVEL_DIST })
  )
  await page.route(/\/api\/v1\/analytics\/activity-stats/, (route) =>
    route.fulfill({ json: MOCK_ACTIVITY_STATS })
  )
  await page.route(/\/api\/v1\/activities\//, (route) =>
    route.fulfill({ json: MOCK_ACTIVITIES_PAGE })
  )
  await page.route(/\/api\/v1\/users\//, (route) =>
    route.fulfill({ json: MOCK_USERS_PAGE })
  )
  await page.route(/\/api\/v1\/announcements\//, (route) =>
    route.fulfill({ json: MOCK_ANNOUNCEMENTS_PAGE })
  )
}
