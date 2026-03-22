<template>
  <div class="activities-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>活动管理</h1>
          <p>创建、管理和追踪所有校园活动</p>
        </div>
        <div class="header-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索活动..."
            :prefix-icon="Search"
            clearable
            style="width: 280px;"
            @input="handleSearch"
          />
          <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 140px;" @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="进行中" value="active" />
            <el-option label="已停用" value="inactive" />
          </el-select>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建活动
          </el-button>
        </div>
      </div>
    </div>

    <!-- Activities Table -->
    <div class="table-container card">
      <el-table
        v-loading="store.loading.activities"
        :data="store.activities"
        style="width: 100%"
      >
        <el-table-column width="60" align="center">
          <template #default="{ row }">
            <div class="status-indicator" :class="row.is_active ? 'active' : 'completed'"></div>
          </template>
        </el-table-column>

        <el-table-column label="活动名称" min-width="200">
          <template #default="{ row }">
            <div class="activity-cell">
              <div class="activity-name">{{ row.name }}</div>
              <div class="activity-venue">{{ row.venue }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="日期" min-width="180">
          <template #default="{ row }">
            <div class="date-cell">
              <el-icon><Calendar /></el-icon>
              {{ row.date_range }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="积分" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="warning" effect="plain">
              {{ row.total_point }} 分
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="完成进度" min-width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <div class="progress-stats">
                {{ row.completed_count }} / {{ row.sign_up_count }} 已完成
              </div>
              <el-progress
                :percentage="getProgress(row)"
                :stroke-width="8"
                :show-text="false"
                :color="getProgressColor(getProgress(row))"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column label="子任务" width="120" align="center">
          <template #default="{ row }">
            <div class="subtask-count" @click="showSubTasks(row)">
              <span class="count-num">{{ row.sub_activity_count ?? row.sub_activities?.length ?? 0 }}</span>
              <span class="count-label">项</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <div class="actions-cell">
              <el-tooltip content="签到码">
                <el-button size="small" circle @click="generateQR(row)">
                  <el-icon><Grid /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑">
                <el-button size="small" circle @click="editActivity(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除">
                <el-button size="small" type="danger" circle @click="deleteActivity(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="store.activitiesPagination.page"
          v-model:page-size="store.activitiesPagination.pageSize"
          :total="store.activitiesPagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingActivity ? '编辑活动' : '新建活动'"
      width="600px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form v-loading="loadingEdit" :model="activityForm" label-position="top">
        <el-form-item label="活动名称" required>
          <el-input v-model="activityForm.name" placeholder="请输入活动名称" />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="日期范围" required class="flex-1">
            <el-input
              v-model="activityForm.date_range"
              placeholder="如: 2025.04.22 09:00~17:00"
            />
          </el-form-item>
          <el-form-item label="地点" required class="flex-1">
            <el-input v-model="activityForm.venue" placeholder="请输入地点" />
          </el-form-item>
        </div>

        <el-form-item label="子活动">
          <div class="sub-activities">
            <div
              v-for="(sub, index) in activityForm.subActivities"
              :key="index"
              class="sub-item"
            >
              <el-input v-model="sub.name" placeholder="子活动名称" style="flex: 1;" />
              <el-input-number v-model="sub.point" :min="1" :max="50" style="width: 120px;" />
              <el-button
                type="danger"
                circle
                :disabled="activityForm.subActivities.length <= 1"
                @click="activityForm.subActivities.splice(index, 1)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" plain @click="addSubActivity" style="width: 100%;">
              <el-icon><Plus /></el-icon>
              添加子活动
            </el-button>
          </div>
        </el-form-item>

        <div class="total-points">
          <span>总积分:</span>
          <span class="points-value">{{ totalPoints }}</span>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveActivity">
          {{ editingActivity ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- QR Code Dialog -->
    <el-dialog v-model="showQRDialog" title="活动签到码" width="400px" align-center>
      <div class="qr-container">
        <div class="qr-code">
          <div v-if="qrCodeUrl" class="qr-image">
            <img :src="qrCodeUrl" alt="QR Code" style="width: 200px; height: 200px;" />
          </div>
          <div v-else class="qr-placeholder">
            <el-icon :size="80"><Grid /></el-icon>
          </div>
        </div>
        <div class="qr-info">
          <h4>{{ qrActivity?.name }}</h4>
          <p>扫码签到参与此活动</p>
          <div class="qr-meta">
            <span><el-icon><Calendar /></el-icon> {{ qrActivity?.date_range }}</span>
            <span><el-icon><Location /></el-icon> {{ qrActivity?.venue }}</span>
          </div>
          <div v-if="qrExpiresAt" class="qr-expires">
            有效期至: {{ qrExpiresAt }}
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Sub-tasks Dialog -->
    <el-dialog v-model="showSubTasksDialog" :title="`${currentActivity?.name} - 子任务列表`" width="500px">
      <div class="sub-tasks-list">
        <div
          v-for="(sub, index) in currentActivity?.sub_activities"
          :key="sub.id"
          class="sub-task-item"
        >
          <div class="sub-task-index">{{ index + 1 }}</div>
          <div class="sub-task-info">
            <div class="sub-task-name">{{ sub.name }}</div>
          </div>
          <el-tag type="warning" size="small">{{ sub.point }} 分</el-tag>
        </div>
        <el-empty v-if="!currentActivity?.sub_activities?.length" description="暂无子任务" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useApiStore } from '@/stores/api'
import { activitiesApi } from '@/api/services'
import {
  Search, Plus, Calendar, List, Grid, Edit, Delete,
  Location, Download, Share, Check
} from '@element-plus/icons-vue'

const store = useApiStore()

const searchQuery = ref('')
const statusFilter = ref('')
const showCreateDialog = ref(false)
const showQRDialog = ref(false)
const showSubTasksDialog = ref(false)
const qrActivity = ref(null)
const qrCodeUrl = ref('')
const qrExpiresAt = ref('')
const currentActivity = ref(null)
const editingActivity = ref(null)
const saving = ref(false)
const loadingEdit = ref(false)
let originalSubActivities = []

const activityForm = reactive({
  name: '',
  date_range: '',
  venue: '',
  subActivities: [{ name: '', point: 5 }]
})

const totalPoints = computed(() => {
  return activityForm.subActivities.reduce((sum, sub) => sum + (sub.point || 0), 0)
})

function getProgress(activity) {
  if (!activity.sign_up_count) return 0
  return Math.round((activity.completed_count / activity.sign_up_count) * 100)
}

function getProgressColor(progress) {
  if (progress >= 70) return '#10B981'
  if (progress >= 50) return '#F59E0B'
  return '#EF4444'
}

function addSubActivity() {
  activityForm.subActivities.push({ name: '', point: 5 })
}

async function generateQR(activity) {
  qrActivity.value = activity
  qrCodeUrl.value = ''
  qrExpiresAt.value = ''
  showQRDialog.value = true
  try {
    const res = await activitiesApi.generateQR(activity.id)
    qrCodeUrl.value = res.data.qr_code_url
    qrExpiresAt.value = res.data.expires_at
  } catch (e) {
    // 错误已由 client 处理
  }
}

async function showSubTasks(activity) {
  currentActivity.value = activity
  // 如果没有 sub_activities，从 API 获取详情
  if (!activity.sub_activities) {
    try {
      const res = await activitiesApi.get(activity.id)
      currentActivity.value = res.data
    } catch (e) {}
  }
  showSubTasksDialog.value = true
}

async function editActivity(activity) {
  editingActivity.value = activity
  activityForm.name = activity.name
  activityForm.date_range = activity.date_range
  activityForm.venue = activity.venue
  activityForm.subActivities = [{ name: '', point: 5 }]
  originalSubActivities = []
  showCreateDialog.value = true
  loadingEdit.value = true
  try {
    const res = await activitiesApi.get(activity.id)
    const detail = res.data
    originalSubActivities = detail.sub_activities || []
    activityForm.subActivities = originalSubActivities.length
      ? originalSubActivities.map(s => ({ id: s.id, name: s.name, point: Number(s.point) }))
      : [{ name: '', point: 5 }]
  } catch (e) {
    // 详情加载失败，保持空白
  } finally {
    loadingEdit.value = false
  }
}

async function saveActivity() {
  if (!activityForm.name || !activityForm.date_range || !activityForm.venue) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  const validSubs = activityForm.subActivities.filter(s => s.name)
  saving.value = true

  try {
    if (editingActivity.value) {
      const success = await store.updateActivity(editingActivity.value.id, {
        name: activityForm.name,
        date_range: activityForm.date_range,
        venue: activityForm.venue,
        total_point: totalPoints.value
      })

      // 同步子活动：删除已移除的，更新已修改的，新增未有 id 的
      const currentSubs = activityForm.subActivities.filter(s => s.name)
      const currentIds = new Set(currentSubs.filter(s => s.id).map(s => s.id))

      for (const orig of originalSubActivities) {
        if (!currentIds.has(orig.id)) {
          await activitiesApi.deleteSubActivity(orig.id)
        }
      }
      for (const [i, sub] of currentSubs.entries()) {
        if (sub.id) {
          const orig = originalSubActivities.find(s => s.id === sub.id)
          if (orig && (orig.name !== sub.name || Number(orig.point) !== sub.point)) {
            await activitiesApi.updateSubActivity(sub.id, { name: sub.name, point: sub.point, sort_order: i })
          }
        } else {
          await activitiesApi.createSubActivity(editingActivity.value.id, { name: sub.name, point: sub.point, sort_order: i })
        }
      }

      if (success) ElMessage.success('活动更新成功')
    } else {
      const success = await store.createActivity({
        name: activityForm.name,
        date_range: activityForm.date_range,
        venue: activityForm.venue,
        total_point: totalPoints.value,
        sub_activities: validSubs.map((s, i) => ({ name: s.name, point: s.point, sort_order: i }))
      })
      if (success) ElMessage.success('活动创建成功')
    }
    resetForm()
    showCreateDialog.value = false
  } finally {
    saving.value = false
  }
}

async function deleteActivity(activity) {
  try {
    await ElMessageBox.confirm(
      `确定要删除"${activity.name}"吗？此操作不可撤销。`,
      '删除活动',
      { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    const success = await store.deleteActivity(activity.id)
    if (success) ElMessage.success('活动删除成功')
  } catch (e) {}
}

function resetForm() {
  editingActivity.value = null
  activityForm.name = ''
  activityForm.date_range = ''
  activityForm.venue = ''
  activityForm.subActivities = [{ name: '', point: 5 }]
}

function handleSearch() {
  const params = {}
  if (searchQuery.value) params.search = searchQuery.value
  if (statusFilter.value === 'active') params.is_active = true
  if (statusFilter.value === 'inactive') params.is_active = false
  store.activitiesPagination.page = 1
  store.fetchActivities(params)
}

function handlePageChange(page) {
  store.activitiesPagination.page = page
  store.fetchActivities({ search: searchQuery.value || undefined })
}

function handleSizeChange(size) {
  store.activitiesPagination.pageSize = size
  store.activitiesPagination.page = 1
  store.fetchActivities()
}

onMounted(() => {
  store.fetchActivities()
})
</script>

<style lang="scss" scoped>
.activities-page {
  animation: fadeIn 0.3s ease;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-title {
  h1 {
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 4px;
  }

  p {
    font-size: 14px;
    color: $text-secondary;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

.table-container {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 12px 8px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;

  &.completed { background: $success-color; }
  &.active { background: $primary-color; }
}

.activity-cell {
  .activity-name {
    font-weight: 600;
    color: $text-primary;
  }

  .activity-venue {
    font-size: 13px;
    color: $text-tertiary;
  }
}

.date-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: $text-secondary;
  font-size: 13px;
}

.progress-cell {
  .progress-stats {
    font-size: 12px;
    color: $text-tertiary;
    margin-bottom: 4px;
  }
}

.subtask-count {
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
  padding: 6px 12px;
  background: $primary-bg;
  border-radius: 16px;
  cursor: pointer;
  transition: all $transition-fast;

  &:hover {
    background: color-mix(in srgb, $primary-color 15%, transparent);
  }

  .count-num {
    font-family: $font-family-display;
    font-size: 18px;
    font-weight: 700;
    color: $primary-color;
  }

  .count-label {
    font-size: 12px;
    color: $text-tertiary;
  }
}

.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.form-row {
  display: flex;
  gap: 16px;

  .flex-1 {
    flex: 1;
  }
}

.sub-activities {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.sub-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.total-points {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: $bg-secondary;
  border-radius: $border-radius;
  margin-top: 16px;

  span:first-child {
    font-weight: 500;
    color: $text-secondary;
  }

  .points-value {
    font-family: $font-family-display;
    font-size: 24px;
    font-weight: 700;
    color: $primary-color;
  }
}

.qr-container {
  text-align: center;
}

.qr-code {
  margin-bottom: 20px;
}

.qr-image {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  background: #fff;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-placeholder {
  width: 200px;
  height: 200px;
  background: $bg-secondary;
  border-radius: $border-radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  color: $text-tertiary;
}

.qr-info {
  margin-bottom: 20px;

  h4 {
    font-size: 18px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 4px;
  }

  p {
    font-size: 14px;
    color: $text-tertiary;
    margin-bottom: 12px;
  }
}

.qr-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 13px;
  color: $text-secondary;

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.qr-expires {
  margin-top: 8px;
  font-size: 12px;
  color: $text-tertiary;
}

.sub-tasks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sub-task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: $bg-primary;
  border-radius: $border-radius;
}

.sub-task-index {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: $primary-color;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.sub-task-info {
  flex: 1;
}

.sub-task-name {
  font-weight: 500;
  color: $text-primary;
}
</style>
