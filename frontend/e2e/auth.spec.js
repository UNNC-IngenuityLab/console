import { test, expect } from '@playwright/test'
import {
  MOCK_LOGIN_RESPONSE,
  MOCK_USER_ME,
  MOCK_DASHBOARD_STATS,
  MOCK_LEADERBOARD,
  MOCK_TREND,
  MOCK_LEVEL_DIST,
  MOCK_ACTIVITY_STATS,
  MOCK_ACTIVITIES_PAGE,
  MOCK_ANNOUNCEMENTS_PAGE,
  setAuthToken,
  clearAuthToken,
} from './helpers.js'

// =============================================================================
// Login Page
// =============================================================================

test.describe('登录页面', () => {
  test.beforeEach(async ({ page }) => {
    await clearAuthToken(page)
    await page.goto('/login')
  })

  test('登录页面正确渲染', async ({ page }) => {
    await expect(page).toHaveTitle(/Leo 管理后台/)
    await expect(page.getByText('Leo 管理后台')).toBeVisible()
    await expect(page.getByText('校园活动激励平台')).toBeVisible()
    await expect(page.getByPlaceholder('学号')).toBeVisible()
    await expect(page.getByPlaceholder('密码')).toBeVisible()
    await expect(page.getByRole('button', { name: /登 录/ })).toBeVisible()
  })

  test('登录成功后跳转到 Dashboard', async ({ page }) => {
    await page.route(/\/api\/v1\/auth\/login/, (route) =>
      route.fulfill({ json: MOCK_LOGIN_RESPONSE })
    )
    await page.route(/\/api\/v1\/analytics\/dashboard/, (route) =>
      route.fulfill({ json: MOCK_DASHBOARD_STATS })
    )
    await page.route(/\/api\/v1\/analytics\/leaderboard/, (route) =>
      route.fulfill({ json: MOCK_LEADERBOARD })
    )
    await page.route(/\/api\/v1\/analytics\//, (route) =>
      route.fulfill({ json: { code: 0, message: 'success', data: [] } })
    )
    await page.route(/\/api\/v1\/activities\//, (route) =>
      route.fulfill({ json: MOCK_ACTIVITIES_PAGE })
    )
    await page.route(/\/api\/v1\/announcements\//, (route) =>
      route.fulfill({ json: MOCK_ANNOUNCEMENTS_PAGE })
    )

    await page.getByPlaceholder('学号').fill('N20230001')
    await page.getByPlaceholder('密码').fill('correct_password')
    await page.getByRole('button', { name: /登 录/ }).click()

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 })
  })

  test('提交空表单时显示验证错误', async ({ page }) => {
    await page.getByRole('button', { name: /登 录/ }).click()
    await expect(page.getByText('请输入学号')).toBeVisible()
  })

  test('只填学号不填密码时显示密码验证错误', async ({ page }) => {
    await page.getByPlaceholder('学号').fill('N20230001')
    await page.getByRole('button', { name: /登 录/ }).click()
    await expect(page.getByText('请输入密码')).toBeVisible()
  })

  test('登录失败时显示错误提示', async ({ page }) => {
    await page.route(/\/api\/v1\/auth\/login/, (route) =>
      route.fulfill({
        status: 401,
        json: { code: 401, message: 'Invalid student ID or password', data: null },
      })
    )

    await page.getByPlaceholder('学号').fill('N20230001')
    await page.getByPlaceholder('密码').fill('wrong_password')
    await page.getByRole('button', { name: /登 录/ }).click()

    await expect(page).toHaveURL('/login')
  })

  test('按 Enter 键触发登录', async ({ page }) => {
    await page.route(/\/api\/v1\/auth\/login/, (route) =>
      route.fulfill({ json: MOCK_LOGIN_RESPONSE })
    )
    await page.route(/\/api\/v1\/analytics\//, (route) =>
      route.fulfill({ json: { code: 0, message: 'success', data: [] } })
    )
    await page.route(/\/api\/v1\/activities\//, (route) =>
      route.fulfill({ json: MOCK_ACTIVITIES_PAGE })
    )
    await page.route(/\/api\/v1\/announcements\//, (route) =>
      route.fulfill({ json: MOCK_ANNOUNCEMENTS_PAGE })
    )

    await page.getByPlaceholder('学号').fill('N20230001')
    await page.getByPlaceholder('密码').fill('password')
    await page.getByPlaceholder('密码').press('Enter')

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 })
  })
})

// =============================================================================
// Auth Guard (redirect to login)
// =============================================================================

test.describe('认证守卫', () => {
  test('未登录时访问 /dashboard 重定向到登录页', async ({ page }) => {
    await clearAuthToken(page)
    await page.goto('/dashboard')
    await expect(page).toHaveURL('/login')
  })

  test('未登录时访问 /activities 重定向到登录页', async ({ page }) => {
    await clearAuthToken(page)
    await page.goto('/activities')
    await expect(page).toHaveURL('/login')
  })

  test('未登录时访问 /users 重定向到登录页', async ({ page }) => {
    await clearAuthToken(page)
    await page.goto('/users')
    await expect(page).toHaveURL('/login')
  })

  test('已登录时访问根路径重定向到 /dashboard', async ({ page }) => {
    await setAuthToken(page)
    await page.route(/\/api\/v1\//, (route) =>
      route.fulfill({ json: { code: 0, message: 'success', data: null } })
    )
    await page.goto('/')
    await expect(page).toHaveURL('/dashboard')
  })
})

// =============================================================================
// Logout
// =============================================================================

test.describe('退出登录', () => {
  test.beforeEach(async ({ page }) => {
    await setAuthToken(page)
    await page.route(/\/api\/v1\/analytics\//, (route) =>
      route.fulfill({ json: { code: 0, message: 'success', data: [] } })
    )
    await page.route(/\/api\/v1\/activities\//, (route) =>
      route.fulfill({ json: { code: 0, message: 'success', data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 } } })
    )
    await page.route(/\/api\/v1\/announcements\//, (route) =>
      route.fulfill({ json: { code: 0, message: 'success', data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 } } })
    )
    await page.goto('/dashboard')
  })

  test('退出后跳转到登录页', async ({ page }) => {
    await page.route(/\/api\/v1\/auth\/logout/, (route) =>
      route.fulfill({ json: { code: 0, message: 'Logged out successfully', data: null } })
    )

    // Logout button is .logout-btn in the sidebar footer
    const logoutBtn = page.locator('.logout-btn')
    await expect(logoutBtn).toBeVisible({ timeout: 5000 })
    await logoutBtn.click()
    await expect(page).toHaveURL('/login', { timeout: 5000 })
  })
})
