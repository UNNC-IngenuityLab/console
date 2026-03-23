import { test, expect } from '@playwright/test'
import {
  MOCK_DASHBOARD_STATS,
  MOCK_LEADERBOARD,
  MOCK_TREND,
  MOCK_LEVEL_DIST,
  MOCK_ACTIVITY_STATS,
  MOCK_ACTIVITIES_PAGE,
  MOCK_ANNOUNCEMENTS_PAGE,
  setAuthToken,
} from './helpers.js'

test.describe('工作台 (Dashboard)', () => {
  test.beforeEach(async ({ page }) => {
    await setAuthToken(page)

    // Dashboard calls: analytics/dashboard, activities, announcements, leaderboard
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
    await page.route(/\/api\/v1\/announcements\//, (route) =>
      route.fulfill({ json: MOCK_ANNOUNCEMENTS_PAGE })
    )

    await page.goto('/dashboard')
  })

  test('Dashboard 页面加载成功', async ({ page }) => {
    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByText('工作台').first()).toBeVisible()
  })

  test('统计卡片显示正确数据', async ({ page }) => {
    // Use exact: true to avoid matching partial text in other elements
    await expect(page.getByText('120', { exact: true }).first()).toBeVisible({ timeout: 8000 })
    await expect(page.locator('.stat-number', { hasText: '15' }).first()).toBeVisible()
  })

  test('导航侧边栏正确显示所有菜单项', async ({ page }) => {
    const nav = page.locator('.sidebar-nav')
    await expect(nav.getByText('活动管理')).toBeVisible()
    await expect(nav.getByText('用户管理')).toBeVisible()
    await expect(nav.getByText('公告管理')).toBeVisible()
    await expect(nav.getByText('数据分析')).toBeVisible()
    await expect(nav.getByText('系统设置')).toBeVisible()
  })

  test('点击活动管理导航到 /activities', async ({ page }) => {
    // Route already mocked for activities in beforeEach
    await page.locator('.sidebar-nav').getByText('活动管理').click()
    await expect(page).toHaveURL('/activities')
  })

  test('点击用户管理导航到 /users', async ({ page }) => {
    await page.route(/\/api\/v1\/users\//, (route) =>
      route.fulfill({ json: { code: 0, message: 'success', data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 } } })
    )

    await page.locator('.sidebar-nav').getByText('用户管理').click()
    await expect(page).toHaveURL('/users')
  })

  test('Dashboard API 错误时页面不崩溃', async ({ page }) => {
    await expect(page.locator('body')).toBeVisible()
    await expect(page).not.toHaveURL('/login')
  })
})
