<template>
  <div class="users-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>用户管理</h1>
          <p>管理学生账户和积分分配</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value">{{ store.totalUsers }}</span>
            <span class="stat-label">总用户</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ activeUsers }}</span>
            <span class="stat-label">活跃</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="按学号或姓名搜索..."
          :prefix-icon="Search"
          clearable
          style="width: 300px;"
        />
        <el-select v-model="levelFilter" placeholder="等级" clearable style="width: 160px;">
          <el-option label="全部等级" value="" />
          <el-option v-for="i in 10" :key="i" :label="`等级 ${i}`" :value="i" />
        </el-select>
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="table-container card">
      <el-table :data="filteredUsers" style="width: 100%">
        <el-table-column width="80" align="center">
          <template #default="{ row }">
            <div class="user-avatar">{{ row.avatarUrl }}</div>
          </template>
        </el-table-column>

        <el-table-column label="学号" width="130">
          <template #default="{ row }">
            <span class="student-id">{{ row.studentId }}</span>
          </template>
        </el-table-column>

        <el-table-column label="姓名" min-width="150">
          <template #default="{ row }">
            <div class="user-name">{{ row.nickname }}</div>
          </template>
        </el-table-column>

        <el-table-column label="积分" width="120" align="center">
          <template #default="{ row }">
            <div class="points-cell">
              <span class="points-value">{{ row.totalPoints }}</span>
              <el-tag size="small" :type="getPointsTagType(row.totalPoints)">
                {{ getPointsLabel(row.totalPoints) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="等级" width="180">
          <template #default="{ row }">
            <div class="level-cell">
              <div class="level-badge" :style="{ background: getLevelColor(row.totalPoints) }">
                Lv.{{ getLevel(row.totalPoints) }}
              </div>
              <div class="level-name">{{ getLevelName(row.totalPoints) }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="参与活动" width="120" align="center">
          <template #default="{ row }">
            <div class="activity-count" @click="showUserActivities(row)">
              <span class="count-num">{{ row.registeredActivities.length }}</span>
              <span class="count-label">个</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="注册时间" width="130">
          <template #default="{ row }">
            <div class="date-cell">
              <el-icon><Calendar /></el-icon>
              {{ row.createdAt }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <div class="actions-cell">
              <el-tooltip content="调整积分">
                <el-button size="small" type="primary" @click="editPoints(row)">
                  <el-icon><Star /></el-icon>
                  积分
                </el-button>
              </el-tooltip>
              <el-tooltip content="查看详情">
                <el-button size="small" circle @click="viewProfile(row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除">
                <el-button size="small" type="danger" circle @click="deleteUser(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Edit Points Dialog -->
    <el-dialog v-model="showEditDialog" title="调整用户积分" width="450px">
      <div v-if="editingUser" class="edit-form">
        <div class="user-info-card">
          <div class="user-avatar-large">{{ editingUser.avatarUrl }}</div>
          <div class="user-details">
            <div class="user-name">{{ editingUser.nickname }}</div>
            <div class="user-id">{{ editingUser.studentId }}</div>
            <div class="user-level">等级 {{ getLevel(editingUser.totalPoints) }} - {{ getLevelName(editingUser.totalPoints) }}</div>
          </div>
        </div>

        <div class="points-editor">
          <label>积分调整</label>
          <div class="points-control">
            <el-button circle @click="adjustPoints(-10)">-10</el-button>
            <el-button circle @click="adjustPoints(-5)">-5</el-button>
            <el-input-number
              v-model="newPoints"
              :min="0"
              :max="200"
              size="large"
              style="width: 120px;"
            />
            <el-button circle @click="adjustPoints(5)">+5</el-button>
            <el-button circle @click="adjustPoints(10)">+10</el-button>
          </div>
        </div>

        <div class="points-preview">
          <div class="preview-item">
            <span class="preview-label">当前</span>
            <span class="preview-value">{{ editingUser.totalPoints }}</span>
          </div>
          <div class="preview-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="preview-item highlight">
            <span class="preview-label">调整后</span>
            <span class="preview-value">{{ newPoints }}</span>
          </div>
        </div>

        <div class="adjustment-reason">
          <label>调整原因</label>
          <el-input
            v-model="adjustmentReason"
            type="textarea"
            :rows="2"
            placeholder="请输入积分调整原因（用于审计日志）"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="savePoints">
          保存更改
        </el-button>
      </template>
    </el-dialog>

    <!-- User Activities Dialog -->
    <el-dialog v-model="showActivitiesDialog" title="已参与活动" width="600px">
      <div v-if="selectedUser" class="user-activities">
        <div class="user-info-header">
          <span class="user-avatar">{{ selectedUser.avatarUrl }}</span>
          <span class="user-name">{{ selectedUser.nickname }}</span>
          <span class="activities-count">已参与 {{ userActivities.length }} 个活动</span>
        </div>
        <div class="activities-list">
          <div
            v-for="activity in userActivities"
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-status" :class="activity.status"></div>
            <div class="activity-info">
              <div class="activity-name">{{ activity.name }}</div>
              <div class="activity-meta">{{ activity.date }} · {{ activity.venue }}</div>
            </div>
            <el-tag size="small" type="warning">{{ activity.totalPoint }} 分</el-tag>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- User Profile Dialog -->
    <el-dialog v-model="showProfileDialog" title="用户详情" width="500px">
      <div v-if="selectedUser" class="user-profile">
        <div class="profile-header">
          <div class="profile-avatar">{{ selectedUser.avatarUrl }}</div>
          <div class="profile-info">
            <h3>{{ selectedUser.nickname }}</h3>
            <p>{{ selectedUser.studentId }}</p>
          </div>
        </div>
        <div class="profile-stats">
          <div class="profile-stat">
            <div class="stat-value">{{ selectedUser.totalPoints }}</div>
            <div class="stat-label">总积分</div>
          </div>
          <div class="profile-stat">
            <div class="stat-value">Lv.{{ getLevel(selectedUser.totalPoints) }}</div>
            <div class="stat-label">当前等级</div>
          </div>
          <div class="profile-stat">
            <div class="stat-value">{{ selectedUser.registeredActivities.length }}</div>
            <div class="stat-label">活动数</div>
          </div>
        </div>
        <div class="profile-details">
          <div class="detail-row">
            <span class="detail-label">等级名称</span>
            <span class="detail-value">{{ getLevelName(selectedUser.totalPoints) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">距离下一等级</span>
            <span class="detail-value">{{ getPointsToNextLevel(selectedUser.totalPoints) }} 分</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">注册时间</span>
            <span class="detail-value">{{ selectedUser.createdAt }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminStore } from '@/stores'
import {
  Search, Download, Calendar, Star, View, Delete, ArrowRight
} from '@element-plus/icons-vue'

const store = useAdminStore()

const searchQuery = ref('')
const levelFilter = ref('')
const showEditDialog = ref(false)
const showActivitiesDialog = ref(false)
const showProfileDialog = ref(false)
const editingUser = ref(null)
const selectedUser = ref(null)
const newPoints = ref(0)
const adjustmentReason = ref('')

const levelNames = [
  '车库小店', '家族商店', '邻里商店', '社区商店', '区域商店',
  '城市商店', '区域总部', '全国总部', '洲际总部', '世界级总部'
]

const activeUsers = computed(() => {
  return store.users.filter(u => u.registeredActivities.length > 0).length
})

const filteredUsers = computed(() => {
  let result = store.users

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(u =>
      u.studentId.includes(query) ||
      u.nickname.toLowerCase().includes(query)
    )
  }

  if (levelFilter.value) {
    result = result.filter(u => getLevel(u.totalPoints) === levelFilter.value)
  }

  return result.sort((a, b) => b.totalPoints - a.totalPoints)
})

const userActivities = computed(() => {
  if (!selectedUser.value) return []
  return store.activities.filter(a =>
    selectedUser.value.registeredActivities.includes(a.id)
  )
})

function getLevel(points) {
  return Math.min(Math.floor(points / 10) + 1, 10)
}

function getLevelName(points) {
  return levelNames[getLevel(points) - 1]
}

function getLevelColor(points) {
  const level = getLevel(points)
  const colors = [
    '#9CA3AF', '#60A5FA', '#34D399', '#A78BFA', '#F472B6',
    '#FB923C', '#FBBF24', '#4ADE80', '#38BDF8', '#818CF8'
  ]
  return colors[level - 1]
}

function getPointsToNextLevel(points) {
  const currentLevel = getLevel(points)
  if (currentLevel >= 10) return 0
  return (currentLevel * 10) - points
}

function getPointsTagType(points) {
  if (points >= 60) return 'success'
  if (points >= 30) return 'warning'
  return 'info'
}

function getPointsLabel(points) {
  if (points >= 80) return '优秀'
  if (points >= 60) return '良好'
  if (points >= 30) return '一般'
  return '新手'
}

function editPoints(user) {
  editingUser.value = user
  newPoints.value = user.totalPoints
  adjustmentReason.value = ''
  showEditDialog.value = true
}

function adjustPoints(amount) {
  newPoints.value = Math.max(0, Math.min(200, newPoints.value + amount))
}

function savePoints() {
  if (!adjustmentReason.value) {
    ElMessage.warning('请提供调整原因')
    return
  }

  store.updateUser(editingUser.value.id, { totalPoints: newPoints.value })
  ElMessage.success(`${editingUser.value.nickname} 的积分已更新`)
  showEditDialog.value = false
}

function showUserActivities(user) {
  selectedUser.value = user
  showActivitiesDialog.value = true
}

function viewProfile(user) {
  selectedUser.value = user
  showProfileDialog.value = true
}

function deleteUser(user) {
  ElMessageBox.confirm(
    `确定要删除 ${user.nickname} 吗？此操作不可撤销。`,
    '删除用户',
    { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
  ).then(() => {
    store.deleteUser(user.id)
    ElMessage.success('用户删除成功')
  }).catch(() => {})
}

function exportData() {
  ElMessage.success('用户数据导出成功')
}
</script>

<style lang="scss" scoped>
.users-page {
  animation: fadeIn 0.3s ease;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
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

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;

  .stat-value {
    display: block;
    font-family: $font-family-display;
    font-size: 28px;
    font-weight: 700;
    color: $primary-color;
  }

  .stat-label {
    font-size: 13px;
    color: $text-tertiary;
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

.user-avatar {
  font-size: 28px;
  text-align: center;
}

.student-id {
  font-family: monospace;
  font-weight: 600;
  color: $text-secondary;
}

.user-name {
  font-weight: 600;
  color: $text-primary;
}

.points-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;

  .points-value {
    font-family: $font-family-display;
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
  }
}

.level-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.level-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.level-name {
  font-size: 13px;
  color: $text-secondary;
}

.activity-count {
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

.date-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: $text-secondary;
  font-size: 13px;
}

.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: center;
}

// Edit Dialog
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: $bg-primary;
  border-radius: $border-radius;
}

.user-avatar-large {
  font-size: 48px;
}

.user-details {
  .user-name {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .user-id {
    font-size: 14px;
    color: $text-secondary;
    margin-bottom: 2px;
  }

  .user-level {
    font-size: 13px;
    color: $text-tertiary;
  }
}

.points-editor {
  label {
    display: block;
    font-weight: 500;
    color: $text-secondary;
    margin-bottom: 8px;
  }
}

.points-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.points-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 16px;
  background: $bg-primary;
  border-radius: $border-radius;
}

.preview-item {
  text-align: center;

  .preview-label {
    display: block;
    font-size: 12px;
    color: $text-tertiary;
    margin-bottom: 4px;
  }

  .preview-value {
    font-family: $font-family-display;
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
  }

  &.highlight .preview-value {
    color: $primary-color;
  }
}

.preview-arrow {
  color: $text-tertiary;
}

.adjustment-reason {
  label {
    display: block;
    font-weight: 500;
    color: $text-secondary;
    margin-bottom: 8px;
  }
}

// User Activities Dialog
.user-activities {
  .user-info-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 16px;
    border-bottom: 1px solid $border-color;
    margin-bottom: 16px;

    .user-avatar {
      font-size: 32px;
    }

    .user-name {
      font-weight: 600;
      color: $text-primary;
    }

    .activities-count {
      font-size: 13px;
      color: $text-tertiary;
      margin-left: auto;
    }
  }
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: $bg-primary;
  border-radius: $border-radius;
}

.activity-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;

  &.completed { background: $success-color; }
  &.active { background: $primary-color; }
  &.upcoming { background: $text-disabled; }
}

.activity-info {
  flex: 1;

  .activity-name {
    font-weight: 500;
    color: $text-primary;
  }

  .activity-meta {
    font-size: 12px;
    color: $text-tertiary;
  }
}

// User Profile Dialog
.user-profile {
  .profile-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;

    .profile-avatar {
      font-size: 64px;
    }

    .profile-info {
      h3 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 4px;
      }

      p {
        color: $text-secondary;
      }
    }
  }
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.profile-stat {
  text-align: center;
  padding: 16px;
  background: $bg-primary;
  border-radius: $border-radius;

  .stat-value {
    font-family: $font-family-display;
    font-size: 24px;
    font-weight: 700;
    color: $primary-color;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 13px;
    color: $text-tertiary;
  }
}

.profile-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid $border-color;

  &:last-child {
    border-bottom: none;
  }

  .detail-label {
    color: $text-secondary;
  }

  .detail-value {
    font-weight: 500;
    color: $text-primary;
  }
}
</style>
