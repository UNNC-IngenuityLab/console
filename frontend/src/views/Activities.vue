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
          />
          <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 140px;">
            <el-option label="全部" value="" />
            <el-option label="即将开始" value="upcoming" />
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="completed" />
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
      <el-table :data="filteredActivities" style="width: 100%">
        <el-table-column width="60" align="center">
          <template #default="{ row }">
            <div class="status-indicator" :class="row.status"></div>
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

        <el-table-column label="日期" width="130">
          <template #default="{ row }">
            <div class="date-cell">
              <el-icon><Calendar /></el-icon>
              {{ row.date }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="积分" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="warning" effect="plain">
              {{ row.totalPoint }} 分
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="完成进度" min-width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <div class="progress-stats">
                {{ row.completedCount }} / {{ row.signUpCount }} 已完成
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
              <span class="count-num">{{ row.subActivities.length }}</span>
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
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingActivity ? '编辑活动' : '新建活动'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="activityForm" label-position="top">
        <el-form-item label="活动名称" required>
          <el-input v-model="activityForm.name" placeholder="请输入活动名称" />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="日期" required class="flex-1">
            <el-date-picker
              v-model="activityForm.date"
              type="date"
              placeholder="选择日期"
              style="width: 100%;"
              value-format="YYYY-MM-DD"
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
        <el-button type="primary" @click="saveActivity">
          {{ editingActivity ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- QR Code Dialog -->
    <el-dialog v-model="showQRDialog" title="活动签到码" width="400px" align-center>
      <div class="qr-container">
        <div class="qr-code">
          <div class="qr-placeholder">
            <el-icon :size="80"><Grid /></el-icon>
          </div>
        </div>
        <div class="qr-info">
          <h4>{{ qrActivity?.name }}</h4>
          <p>扫码签到参与此活动</p>
          <div class="qr-meta">
            <span><el-icon><Calendar /></el-icon> {{ qrActivity?.date }}</span>
            <span><el-icon><Location /></el-icon> {{ qrActivity?.venue }}</span>
          </div>
        </div>
        <div class="qr-actions">
          <el-button type="primary">
            <el-icon><Download /></el-icon>
            下载二维码
          </el-button>
          <el-button>
            <el-icon><Share /></el-icon>
            分享
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- Sub-tasks Dialog -->
    <el-dialog v-model="showSubTasksDialog" :title="`${currentActivity?.name} - 子任务列表`" width="500px">
      <div class="sub-tasks-list">
        <div
          v-for="(sub, index) in currentActivity?.subActivities"
          :key="sub.id"
          class="sub-task-item"
        >
          <div class="sub-task-index">{{ index + 1 }}</div>
          <div class="sub-task-info">
            <div class="sub-task-name">{{ sub.name }}</div>
          </div>
          <el-tag type="warning" size="small">{{ sub.point }} 分</el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminStore } from '@/stores'
import {
  Search, Plus, Calendar, List, Grid, Edit, Delete,
  Location, Download, Share, Check
} from '@element-plus/icons-vue'

const store = useAdminStore()

const searchQuery = ref('')
const statusFilter = ref('')
const showCreateDialog = ref(false)
const showQRDialog = ref(false)
const showSubTasksDialog = ref(false)
const qrActivity = ref(null)
const currentActivity = ref(null)
const editingActivity = ref(null)

const activityForm = reactive({
  name: '',
  date: '',
  venue: '',
  subActivities: [{ name: '', point: 5 }]
})

const filteredActivities = computed(() => {
  let result = store.activities

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(a =>
      a.name.toLowerCase().includes(query) ||
      a.venue.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    result = result.filter(a => a.status === statusFilter.value)
  }

  return result
})

const totalPoints = computed(() => {
  return activityForm.subActivities.reduce((sum, sub) => sum + (sub.point || 0), 0)
})

function getProgress(activity) {
  if (!activity.signUpCount) return 0
  return Math.round((activity.completedCount / activity.signUpCount) * 100)
}

function getProgressColor(progress) {
  if (progress >= 70) return '#10B981'
  if (progress >= 50) return '#F59E0B'
  return '#EF4444'
}

function addSubActivity() {
  activityForm.subActivities.push({ name: '', point: 5 })
}

function generateQR(activity) {
  qrActivity.value = activity
  showQRDialog.value = true
}

function showSubTasks(activity) {
  currentActivity.value = activity
  showSubTasksDialog.value = true
}

function editActivity(activity) {
  editingActivity.value = activity
  activityForm.name = activity.name
  activityForm.date = activity.date
  activityForm.venue = activity.venue
  activityForm.subActivities = activity.subActivities.map(s => ({ ...s }))
  showCreateDialog.value = true
}

function saveActivity() {
  if (!activityForm.name || !activityForm.date || !activityForm.venue) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  const validSubs = activityForm.subActivities.filter(s => s.name)

  if (editingActivity.value) {
    store.updateActivity(editingActivity.value.id, {
      name: activityForm.name,
      date: activityForm.date,
      venue: activityForm.venue,
      subActivities: validSubs,
      totalPoint: totalPoints.value
    })
    ElMessage.success('活动更新成功')
  } else {
    store.addActivity({
      name: activityForm.name,
      date: activityForm.date,
      venue: activityForm.venue,
      subActivities: validSubs,
      totalPoint: totalPoints.value,
      status: 'upcoming'
    })
    ElMessage.success('活动创建成功')
  }

  resetForm()
  showCreateDialog.value = false
}

function deleteActivity(activity) {
  ElMessageBox.confirm(
    `确定要删除"${activity.name}"吗？此操作不可撤销。`,
    '删除活动',
    { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
  ).then(() => {
    store.deleteActivity(activity.id)
    ElMessage.success('活动删除成功')
  }).catch(() => {})
}

function resetForm() {
  editingActivity.value = null
  activityForm.name = ''
  activityForm.date = ''
  activityForm.venue = ''
  activityForm.subActivities = [{ name: '', point: 5 }]
}
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

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;

  &.completed { background: $success-color; }
  &.active { background: $primary-color; }
  &.upcoming { background: $text-disabled; }
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
  font-size: 14px;
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

.qr-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
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
