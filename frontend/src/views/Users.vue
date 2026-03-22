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
            <span class="stat-value">{{ store.usersPagination.total }}</span>
            <span class="stat-label">总用户</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="按学号或昵称搜索..."
          :prefix-icon="Search"
          clearable
          style="width: 300px;"
          @input="handleSearch"
        />
        <el-select v-model="levelFilter" placeholder="等级" clearable style="width: 160px;" @change="handleSearch">
          <el-option label="全部等级" value="" />
          <el-option v-for="i in 10" :key="i" :label="`等级 ${i}`" :value="i" />
        </el-select>
      </div>
    </div>

    <!-- Users Table -->
    <div class="table-container card">
      <el-table
        v-loading="store.loading.users"
        :data="store.users"
        style="width: 100%"
      >
        <el-table-column label="学号" width="130">
          <template #default="{ row }">
            <span class="student-id">{{ row.student_id }}</span>
          </template>
        </el-table-column>

        <el-table-column label="昵称" min-width="150">
          <template #default="{ row }">
            <div class="user-name">{{ row.nickname || row.student_id }}</div>
          </template>
        </el-table-column>

        <el-table-column label="积分" width="120" align="center">
          <template #default="{ row }">
            <div class="points-cell">
              <span class="points-value">{{ row.total_points }}</span>
              <el-tag size="small" :type="getPointsTagType(Number(row.total_points))">
                {{ getPointsLabel(Number(row.total_points)) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="等级" width="180">
          <template #default="{ row }">
            <div class="level-cell">
              <div class="level-badge" :style="{ background: getLevelColor(row.level) }">
                Lv.{{ row.level }}
              </div>
              <div class="level-name">{{ getLevelName(row.level) }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" align="center">
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

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="store.usersPagination.page"
          v-model:page-size="store.usersPagination.pageSize"
          :total="store.usersPagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- Edit Points Dialog -->
    <el-dialog v-model="showEditDialog" title="调整用户积分" width="450px">
      <div v-if="editingUser" class="edit-form">
        <div class="user-info-card">
          <div class="user-details">
            <div class="user-name">{{ editingUser.nickname || editingUser.student_id }}</div>
            <div class="user-id">{{ editingUser.student_id }}</div>
            <div class="user-level">等级 {{ editingUser.level }} - {{ getLevelName(editingUser.level) }}</div>
          </div>
        </div>

        <div class="points-editor">
          <label>积分调整（新积分值）</label>
          <div class="points-control">
            <el-button circle @click="adjustPoints(-10)">-10</el-button>
            <el-button circle @click="adjustPoints(-5)">-5</el-button>
            <el-input-number
              v-model="newPoints"
              :min="0"
              :max="9999"
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
            <span class="preview-value">{{ editingUser.total_points }}</span>
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
        <el-button type="primary" :loading="saving" @click="savePoints">
          保存更改
        </el-button>
      </template>
    </el-dialog>

    <!-- User Profile Dialog -->
    <el-dialog v-model="showProfileDialog" title="用户详情" width="500px">
      <div v-if="selectedUser" class="user-profile">
        <div class="profile-header">
          <div class="profile-info">
            <h3>{{ selectedUser.nickname || selectedUser.student_id }}</h3>
            <p>{{ selectedUser.student_id }}</p>
          </div>
        </div>
        <div class="profile-stats">
          <div class="profile-stat">
            <div class="stat-value">{{ selectedUser.total_points }}</div>
            <div class="stat-label">总积分</div>
          </div>
          <div class="profile-stat">
            <div class="stat-value">Lv.{{ selectedUser.level }}</div>
            <div class="stat-label">当前等级</div>
          </div>
          <div class="profile-stat">
            <div class="stat-value">{{ selectedUser.is_active ? '正常' : '禁用' }}</div>
            <div class="stat-label">账户状态</div>
          </div>
        </div>
        <div class="profile-details">
          <div class="detail-row">
            <span class="detail-label">等级名称</span>
            <span class="detail-value">{{ getLevelName(selectedUser.level) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">学号</span>
            <span class="detail-value">{{ selectedUser.student_id }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useApiStore } from '@/stores/api'
import {
  Search, Download, Calendar, Star, View, Delete, ArrowRight
} from '@element-plus/icons-vue'

const store = useApiStore()

const searchQuery = ref('')
const levelFilter = ref('')
const showEditDialog = ref(false)
const showProfileDialog = ref(false)
const editingUser = ref(null)
const selectedUser = ref(null)
const newPoints = ref(0)
const adjustmentReason = ref('')
const saving = ref(false)

const levelNames = [
  '车库小店', '家族商店', '邻里商店', '社区商店', '区域商店',
  '城市商店', '区域总部', '全国总部', '洲际总部', '世界级总部'
]

const levelColors = [
  '#9CA3AF', '#60A5FA', '#34D399', '#A78BFA', '#F472B6',
  '#FB923C', '#FBBF24', '#4ADE80', '#38BDF8', '#818CF8'
]

function getLevelName(level) {
  return levelNames[(level || 1) - 1] || '未知'
}

function getLevelColor(level) {
  return levelColors[(level || 1) - 1] || '#9CA3AF'
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
  newPoints.value = Number(user.total_points)
  adjustmentReason.value = ''
  showEditDialog.value = true
}

function adjustPoints(amount) {
  newPoints.value = Math.max(0, newPoints.value + amount)
}

async function savePoints() {
  if (!adjustmentReason.value) {
    ElMessage.warning('请提供调整原因')
    return
  }
  saving.value = true
  try {
    const success = await store.updateUserPoints(editingUser.value.id, newPoints.value, adjustmentReason.value)
    if (success) {
      ElMessage.success(`${editingUser.value.nickname || editingUser.value.student_id} 的积分已更新`)
      showEditDialog.value = false
    }
  } finally {
    saving.value = false
  }
}

function viewProfile(user) {
  selectedUser.value = user
  showProfileDialog.value = true
}

async function deleteUser(user) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${user.nickname || user.student_id} 吗？此操作不可撤销。`,
      '删除用户',
      { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    const success = await store.deleteUser(user.id)
    if (success) ElMessage.success('用户删除成功')
  } catch (e) {}
}

function handleSearch() {
  const params = {}
  if (searchQuery.value) params.search = searchQuery.value
  if (levelFilter.value) params.level = levelFilter.value
  store.usersPagination.page = 1
  store.fetchUsers(params)
}

function handlePageChange(page) {
  store.usersPagination.page = page
  store.fetchUsers({ search: searchQuery.value || undefined, level: levelFilter.value || undefined })
}

function handleSizeChange(size) {
  store.usersPagination.pageSize = size
  store.usersPagination.page = 1
  store.fetchUsers()
}

onMounted(() => {
  store.fetchUsers()
})
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

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 12px 8px;
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

// User Profile Dialog
.user-profile {
  .profile-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;

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
