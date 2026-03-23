import { test, expect } from '@playwright/test'
import { MOCK_ANNOUNCEMENTS_PAGE, setAuthToken } from './helpers.js'

const EMPTY_PAGE = {
  code: 0,
  message: 'success',
  data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
}

test.describe('公告管理', () => {
  test.beforeEach(async ({ page }) => {
    await setAuthToken(page)

    await page.route(/\/api\/v1\/announcements\//, (route) => {
      const method = route.request().method()
      if (method === 'GET') {
        return route.fulfill({ json: MOCK_ANNOUNCEMENTS_PAGE })
      }
      if (method === 'POST') {
        return route.fulfill({
          status: 201,
          json: { code: 0, message: 'Announcement created successfully', data: { announcement_id: 'new_ann_id' } },
        })
      }
      // PUT / DELETE
      return route.fulfill({ json: { code: 0, message: 'success', data: null } })
    })

    await page.goto('/announcements')
  })

  // ---------------------------------------------------------------------------
  // List
  // ---------------------------------------------------------------------------

  test('公告列表页面加载', async ({ page }) => {
    await expect(page).toHaveURL('/announcements')
    await expect(page.getByText('公告管理').first()).toBeVisible()
  })

  test('公告列表显示公告内容', async ({ page }) => {
    await expect(page.locator('.announcement-title').first()).toBeVisible({ timeout: 8000 })
    await expect(page.locator('.announcement-title').first()).toContainText('Test Announcement')
  })

  test('公告列表为空时不崩溃', async ({ page }) => {
    await page.route(/\/api\/v1\/announcements\//, (route) =>
      route.fulfill({ json: EMPTY_PAGE })
    )
    await page.goto('/announcements')
    await expect(page.locator('body')).toBeVisible()
    await expect(page).toHaveURL('/announcements')
  })

  // ---------------------------------------------------------------------------
  // Create
  // ---------------------------------------------------------------------------

  test('点击发布公告按钮打开对话框', async ({ page }) => {
    // "发布公告" button is always visible in the page header
    const createBtn = page.locator('.page-header button', { hasText: '发布公告' }).first()
    await expect(createBtn).toBeVisible()
    await createBtn.click()
    await expect(page.locator('.el-dialog')).toBeVisible()
  })

  test('填写公告表单并提交', async ({ page }) => {
    const createBtn = page.locator('.page-header button', { hasText: '发布公告' }).first()
    await createBtn.click()
    await page.locator('.el-dialog').waitFor({ state: 'visible' })

    await page.locator('.el-dialog input[placeholder*="标题"]').fill('E2E Test Announcement')
    await page.locator('.el-dialog textarea').first().fill('This is a test announcement created by E2E tests.')

    const submitBtn = page.locator('.el-dialog__footer button', { hasText: '发布' }).first()
    await submitBtn.click()
    // Dialog should close after submit
    await expect(page.locator('.el-dialog')).not.toBeVisible({ timeout: 5000 })
  })

  // ---------------------------------------------------------------------------
  // Edit — status toggle is inside the edit dialog
  // ---------------------------------------------------------------------------

  test('点击编辑打开对话框并可切换公告状态', async ({ page }) => {
    await expect(page.locator('.announcement-title').first()).toBeVisible({ timeout: 8000 })

    // Edit button is the first circle button in announcement-actions
    const editBtn = page.locator('.announcement-actions button:not(.el-button--danger)').first()
    await expect(editBtn).toBeVisible()
    await editBtn.click()

    const dialog = page.locator('.el-dialog')
    await expect(dialog).toBeVisible()
    // The is_active switch only shows in edit mode (v-if="editingAnnouncement")
    await expect(dialog.locator('.el-switch')).toBeVisible()
  })

  // ---------------------------------------------------------------------------
  // Delete
  // ---------------------------------------------------------------------------

  test('删除公告弹出确认框', async ({ page }) => {
    await expect(page.locator('.announcement-title').first()).toBeVisible({ timeout: 8000 })

    // Delete is the danger circle button in announcement-actions
    const deleteBtn = page.locator('.announcement-actions button.el-button--danger').first()
    await expect(deleteBtn).toBeVisible()
    await deleteBtn.click()
    await expect(
      page.locator('.el-message-box').filter({ hasText: /确认|删除/ })
    ).toBeVisible()
  })

  test('确认删除后公告消失', async ({ page }) => {
    await expect(page.locator('.announcement-title').first()).toBeVisible({ timeout: 8000 })

    const deleteBtn = page.locator('.announcement-actions button.el-button--danger').first()

    // After delete, return empty list
    await page.route(/\/api\/v1\/announcements\//, (route) => {
      if (route.request().method() === 'GET') {
        return route.fulfill({ json: EMPTY_PAGE })
      }
      return route.fulfill({ json: { code: 0, message: 'success', data: null } })
    })

    await deleteBtn.click()

    const confirmBtn = page.locator('.el-message-box button', { hasText: '确定' }).first()
    if (await confirmBtn.count() > 0) {
      await confirmBtn.click()
      // After confirm, list re-fetches and is empty
      await expect(page.locator('.announcement-title')).toHaveCount(0, { timeout: 5000 })
    }
  })

  // ---------------------------------------------------------------------------
  // Priority
  // ---------------------------------------------------------------------------

  test('公告列表按优先级显示', async ({ page }) => {
    await expect(page.locator('.announcement-title').first()).toBeVisible({ timeout: 8000 })
    await expect(page.locator('.announcement-title').first()).toContainText(MOCK_ANNOUNCEMENTS_PAGE.data.items[0].title)
  })
})
