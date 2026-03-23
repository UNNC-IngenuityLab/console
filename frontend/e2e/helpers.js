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
        date_range: '2024-01-15 ~ 2024-01-16',
        start_date: '2024-01-15',
        end_date: '2024-01-16',
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
