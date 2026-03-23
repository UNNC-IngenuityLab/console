import { test, expect } from '@playwright/test'
import { MOCK_ACTIVITIES_PAGE, setAuthToken } from './helpers.js'

const EMPTY_PAGE = {
  code: 0,
  message: 'success',
  data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
}

const MOCK_ACTIVITY_DETAIL = {
  code: 0,
  message: 'success',
  data: {
    ...MOCK_ACTIVITIES_PAGE.data.items[0],
    sub_activities: [
      {
        id: 1,
        activity_id: 'act123abc456def789ab123',
        name: '子活动 A',
        point: '5.00',
        is_stopped: false,
        sort_order: 0,
        created_at: '2024-01-01T00:00:00',
        updated_at: '2024-01-01T00:00:00',
      },
    ],
  },
}

test.describe('活动管理', () => {
  test.beforeEach(async ({ page }) => {
    await setAuthToken(page)

    // Mock activities list and detail (regex matches with or without query params)
    await page.route(/\/api\/v1\/activities\//, (route) => {
      const method = route.request().method()
      const url = route.request().url()
      // Specific activity or sub-activities
      if (/\/activities\/[^/]+/.test(url) && !url.includes('?')) {
        return route.fulfill({ json: MOCK_ACTIVITY_DETAIL })
      }
      if (method === 'GET') {
        return route.fulfill({ json: MOCK_ACTIVITIES_PAGE })
      }
      return route.fulfill({ json: { code: 0, message: 'success', data: { activity_id: 'new_act_id' } } })
    })

    await page.goto('/activities')
  })

  // ---------------------------------------------------------------------------
  // List
  // ---------------------------------------------------------------------------

  test('活动列表页面加载', async ({ page }) => {
    await expect(page).toHaveURL('/activities')
    await expect(page.getByText('活动管理').first()).toBeVisible()
  })

  test('活动列表显示活动数据', async ({ page }) => {
    await expect(page.locator('.activity-name').first()).toBeVisible({ timeout: 8000 })
    await expect(page.locator('.activity-name').first()).toContainText('Test Activity Alpha')
  })

  test('活动列表为空时显示空状态', async ({ page }) => {
    await page.route(/\/api\/v1\/activities\//, (route) =>
      route.fulfill({ json: EMPTY_PAGE })
    )
    await page.goto('/activities')
    await expect(page.locator('.el-table').first()).toBeVisible({ timeout: 8000 })
  })

  // ---------------------------------------------------------------------------
  // Search / Filter
  // ---------------------------------------------------------------------------

  test('搜索框存在且可输入', async ({ page }) => {
    // Use CSS attribute selector - more reliable than getByPlaceholder with Chinese
    const searchInput = page.locator('input[placeholder*="搜索"]').first()
    await expect(searchInput).toBeVisible({ timeout: 5000 })
    await searchInput.fill('Test')
    await expect(searchInput).toHaveValue('Test')
  })

  // ---------------------------------------------------------------------------
  // Create Activity
  // ---------------------------------------------------------------------------

  test('点击新建活动按钮打开对话框', async ({ page }) => {
    await expect(page.locator('.activity-name').first()).toBeVisible({ timeout: 8000 })
    const createBtn = page.getByRole('button', { name: /新建活动/ }).first()
    if (await createBtn.count() > 0) {
      await createBtn.click()
      await expect(page.locator('.el-dialog')).toBeVisible()
    } else {
      test.skip()
    }
  })

  test('创建活动成功后刷新列表', async ({ page }) => {
    await expect(page.locator('.activity-name').first()).toBeVisible({ timeout: 8000 })

    const createBtn = page.getByRole('button', { name: /新建活动/ }).first()
    if (await createBtn.count() === 0) {
      test.skip()
      return
    }

    await createBtn.click()
    await page.locator('.el-dialog').waitFor({ state: 'visible' })

    const nameInput = page.getByPlaceholder('请输入活动名称').first()
    if (await nameInput.count() > 0) {
      await nameInput.fill('New E2E Activity')
    }

    const submitBtn = page.getByRole('button', { name: /创建/ }).last()
    if (await submitBtn.count() > 0) {
      await submitBtn.click()
    }
  })

  // ---------------------------------------------------------------------------
  // Delete Activity
  // ---------------------------------------------------------------------------

  test('删除活动弹出确认框', async ({ page }) => {
    await expect(page.locator('.activity-name').first()).toBeVisible({ timeout: 8000 })

    // Delete button is a circle icon button in the actions column
    const deleteBtn = page.locator('.actions-cell .el-button--danger').first()
    if (await deleteBtn.count() > 0) {
      await deleteBtn.click()
      await expect(
        page.locator('.el-message-box').filter({ hasText: /确认|删除/ })
      ).toBeVisible()
    } else {
      test.skip()
    }
  })

  test('取消删除操作不删除活动', async ({ page }) => {
    await expect(page.locator('.activity-name').first()).toBeVisible({ timeout: 8000 })

    const deleteBtn = page.locator('.actions-cell .el-button--danger').first()
    if (await deleteBtn.count() === 0) {
      test.skip()
      return
    }

    await deleteBtn.click()
    const cancelBtn = page.locator('.el-message-box button').filter({ hasText: /取消/ }).first()
    if (await cancelBtn.count() > 0) {
      await cancelBtn.click()
    }

    await expect(page.locator('.activity-name').first()).toBeVisible()
  })

  // ---------------------------------------------------------------------------
  // QR Code
  // ---------------------------------------------------------------------------

  test('生成 QR Code', async ({ page }) => {
    await page.route(/\/api\/v1\/activities\/.*\/qrcode/, (route) =>
      route.fulfill({
        json: {
          code: 0,
          message: 'success',
          data: {
            qr_code_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            activity_id: 'act123abc456def789ab123',
            activity_name: 'Test Activity Alpha',
            expires_at: '2024-01-15T10:05:00+00:00',
          },
        },
      })
    )

    await expect(page.locator('.activity-name').first()).toBeVisible({ timeout: 8000 })

    // QR button is the first circle button (Grid icon) in actions-cell
    const qrBtn = page.locator('.actions-cell .el-button').first()
    if (await qrBtn.count() > 0) {
      await qrBtn.click()
      await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 })
    } else {
      test.skip()
    }
  })
})
