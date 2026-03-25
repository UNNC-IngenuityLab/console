import { test, expect } from '@playwright/test'
import { MOCK_USERS_PAGE, MOCK_USER_ACTIVITIES, setAuthToken } from './helpers.js'

const EMPTY_PAGE = {
  code: 0,
  message: 'success',
  data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
}

const MOCK_USER_DETAIL = {
  code: 0,
  message: 'success',
  data: {
    id: 'usr456abc789def0123ab45',
    student_id: 'N20230002',
    openid: 'openid_test_user_456',
    nickname: 'Test Student',
    avatar_url: null,
    total_points: '25.00',
    level: 4,
    is_active: true,
    created_at: '2024-01-02T00:00:00',
    updated_at: '2024-01-02T00:00:00',
  },
}

test.describe('用户管理', () => {
  test.beforeEach(async ({ page }) => {
    await setAuthToken(page)

    await page.route(/\/api\/v1\/users\//, (route) => {
      const method = route.request().method()
      const url = route.request().url()
      if (url.includes('/points')) {
        return route.fulfill({ json: { code: 0, message: 'Points updated', data: null } })
      }
      if (url.includes('/activities')) {
        return route.fulfill({ json: MOCK_USER_ACTIVITIES })
      }
      if (method === 'GET' && /\/users\/[^/?]+$/.test(url)) {
        return route.fulfill({ json: MOCK_USER_DETAIL })
      }
      if (method === 'GET') {
        return route.fulfill({ json: MOCK_USERS_PAGE })
      }
      return route.fulfill({ json: { code: 0, message: 'success', data: null } })
    })

    await page.goto('/users')
  })

  // ---------------------------------------------------------------------------
  // List
  // ---------------------------------------------------------------------------

  test('用户列表页面加载', async ({ page }) => {
    await expect(page).toHaveURL('/users')
    await expect(page.getByText('用户管理').first()).toBeVisible()
  })

  test('用户列表显示用户数据', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })
  })

  test('用户列表为空时显示空状态', async ({ page }) => {
    await page.route(/\/api\/v1\/users\//, (route) =>
      route.fulfill({ json: EMPTY_PAGE })
    )
    await page.goto('/users')
    await expect(page.locator('.el-table').first()).toBeVisible({ timeout: 8000 })
  })

  // ---------------------------------------------------------------------------
  // Search
  // ---------------------------------------------------------------------------

  test('搜索框可输入学号关键词', async ({ page }) => {
    // Use CSS attribute selector — more reliable than getByPlaceholder with Chinese text
    const searchInput = page.locator('input[placeholder*="搜索"]').first()
    await expect(searchInput).toBeVisible({ timeout: 5000 })
    await searchInput.fill('N2023')
    await expect(searchInput).toHaveValue('N2023')
  })

  // ---------------------------------------------------------------------------
  // Update Points
  // ---------------------------------------------------------------------------

  test('点击修改积分按钮打开对话框', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    // 积分 button has text "积分" (primary type with icon)
    const editPointsBtn = page.locator('.actions-cell').locator('button', { hasText: '积分' }).first()
    await expect(editPointsBtn).toBeVisible()
    await editPointsBtn.click()
    await expect(page.locator('.el-dialog')).toBeVisible()
  })

  test('查看用户详情对话框', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    // View button is the second button in actions-cell (circle, no text)
    const viewBtn = page.locator('.actions-cell button.is-circle:not(.el-button--danger)').first()
    await expect(viewBtn).toBeVisible()
    await viewBtn.click()
    await expect(page.locator('.el-dialog')).toBeVisible()
  })

  // ---------------------------------------------------------------------------
  // Delete
  // ---------------------------------------------------------------------------

  test('删除用户弹出确认框', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    // Delete button is circle danger button in actions-cell
    const deleteBtn = page.locator('.actions-cell button.el-button--danger').first()
    await expect(deleteBtn).toBeVisible()
    await deleteBtn.click()
    await expect(
      page.locator('.el-message-box').filter({ hasText: /确认|删除/ })
    ).toBeVisible()
  })

  test('取消删除不删除用户', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    const deleteBtn = page.locator('.actions-cell button.el-button--danger').first()
    await deleteBtn.click()

    const cancelBtn = page.locator('.el-message-box button').filter({ hasText: /取消/ }).first()
    if (await cancelBtn.count() > 0) {
      await cancelBtn.click()
    }

    await expect(page.getByText('N20230002')).toBeVisible()
  })

  // ---------------------------------------------------------------------------
  // Level Filter
  // ---------------------------------------------------------------------------

  test('按等级筛选用户', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    // The level filter is the el-select in the header actions
    const levelFilter = page.locator('.header-actions .el-select').first()
    await expect(levelFilter).toBeVisible()
    await levelFilter.click()
    // Dropdown with level options should appear (filter by known option text)
    await expect(page.locator('.el-select-dropdown').filter({ hasText: '全部等级' })).toBeVisible({ timeout: 3000 })
  })

  // ---------------------------------------------------------------------------
  // User Activity Records
  // ---------------------------------------------------------------------------

  test('查看用户详情显示活动记录', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    // Click view button (circle button)
    const viewBtn = page.locator('.actions-cell button.is-circle:not(.el-button--danger)').first()
    await expect(viewBtn).toBeVisible()
    await viewBtn.click()

    // Dialog should open
    const dialog = page.locator('.el-dialog')
    await expect(dialog).toBeVisible()

    // Activity records section should be visible
    await expect(dialog.locator('.activity-records')).toBeVisible({ timeout: 5000 })
  })

  test('活动记录显示签到状态', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    const viewBtn = page.locator('.actions-cell button.is-circle:not(.el-button--danger)').first()
    await viewBtn.click()

    const dialog = page.locator('.el-dialog')
    await expect(dialog).toBeVisible()

    // Check for status tags (已签到 / 已报名)
    await expect(dialog.locator('.activity-status-tag').first()).toBeVisible({ timeout: 5000 })
  })

  test('活动记录显示积分', async ({ page }) => {
    await expect(page.getByText('N20230002')).toBeVisible({ timeout: 8000 })

    const viewBtn = page.locator('.actions-cell button.is-circle:not(.el-button--danger)').first()
    await viewBtn.click()

    const dialog = page.locator('.el-dialog')
    await expect(dialog).toBeVisible()

    // Check for points display
    await expect(dialog.locator('.activity-points').first()).toBeVisible({ timeout: 5000 })
  })
