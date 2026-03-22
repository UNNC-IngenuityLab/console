<template>
  <div class="announcements-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>公告管理</h1>
        <p>发布和管理平台公告通知</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        发布公告
      </el-button>
    </div>

    <!-- Announcements List -->
    <div v-loading="store.loading.announcements" class="announcements-list">
      <div
        v-for="announcement in store.announcements"
        :key="announcement.id"
        class="announcement-card card"
      >
        <div class="announcement-header">
          <div class="announcement-status">
            <el-tag :type="announcement.is_active ? 'success' : 'info'" size="small">
              {{ announcement.is_active ? '已发布' : '已下线' }}
            </el-tag>
            <el-tag v-if="announcement.priority > 0" type="warning" size="small" style="margin-left: 8px;">
              优先级 {{ announcement.priority }}
            </el-tag>
          </div>
          <div class="announcement-actions">
            <el-button size="small" circle @click="editAnnouncement(announcement)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" type="danger" circle @click="deleteAnnouncement(announcement)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="announcement-content">
          <h3 class="announcement-title">{{ announcement.title }}</h3>
          <p class="announcement-text">{{ announcement.content }}</p>
        </div>

        <div class="announcement-footer">
          <div class="announcement-meta">
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              {{ announcement.created_at?.split('T')[0] }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!store.loading.announcements && !store.announcements.length" description="暂无公告">
      <el-button type="primary" @click="showCreateDialog = true">
        发布第一条公告
      </el-button>
    </el-empty>

    <!-- Pagination -->
    <div class="pagination-wrapper" v-if="store.announcementsPagination.total > store.announcementsPagination.pageSize">
      <el-pagination
        v-model:current-page="store.announcementsPagination.page"
        v-model:page-size="store.announcementsPagination.pageSize"
        :total="store.announcementsPagination.total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingAnnouncement ? '编辑公告' : '发布公告'"
      width="600px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form :model="announcementForm" label-position="top">
        <el-form-item label="标题" required>
          <el-input
            v-model="announcementForm.title"
            placeholder="请输入公告标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="内容" required>
          <el-input
            v-model="announcementForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="优先级" class="flex-1">
            <el-input-number
              v-model="announcementForm.priority"
              :min="0"
              :max="100"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item v-if="editingAnnouncement" label="状态" class="flex-1">
            <el-switch
              v-model="announcementForm.is_active"
              active-text="已发布"
              inactive-text="下线"
            />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAnnouncement">
          {{ editingAnnouncement ? '更新' : '发布' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useApiStore } from '@/stores/api'
import { Plus, Edit, Delete, Calendar, View } from '@element-plus/icons-vue'

const store = useApiStore()

const showCreateDialog = ref(false)
const editingAnnouncement = ref(null)
const saving = ref(false)

const announcementForm = reactive({
  title: '',
  content: '',
  priority: 0,
  is_active: true
})

function editAnnouncement(announcement) {
  editingAnnouncement.value = announcement
  announcementForm.title = announcement.title
  announcementForm.content = announcement.content
  announcementForm.priority = announcement.priority ?? 0
  announcementForm.is_active = announcement.is_active
  showCreateDialog.value = true
}

async function saveAnnouncement() {
  if (!announcementForm.title || !announcementForm.content) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  saving.value = true
  try {
    if (editingAnnouncement.value) {
      const success = await store.updateAnnouncement(editingAnnouncement.value.id, {
        title: announcementForm.title,
        content: announcementForm.content,
        priority: announcementForm.priority,
        is_active: announcementForm.is_active
      })
      if (success) ElMessage.success('公告更新成功')
    } else {
      const success = await store.createAnnouncement({
        title: announcementForm.title,
        content: announcementForm.content,
        priority: announcementForm.priority
      })
      if (success) ElMessage.success('公告发布成功')
    }
    resetForm()
    showCreateDialog.value = false
  } finally {
    saving.value = false
  }
}

async function deleteAnnouncement(announcement) {
  try {
    await ElMessageBox.confirm(
      `确定要删除公告"${announcement.title}"吗？`,
      '删除公告',
      { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    const success = await store.deleteAnnouncement(announcement.id)
    if (success) ElMessage.success('公告删除成功')
  } catch (e) {}
}

function resetForm() {
  editingAnnouncement.value = null
  announcementForm.title = ''
  announcementForm.content = ''
  announcementForm.priority = 0
  announcementForm.is_active = true
}

function handlePageChange(page) {
  store.announcementsPagination.page = page
  store.fetchAnnouncements()
}

onMounted(() => {
  store.fetchAnnouncements()
})
</script>

<style lang="scss" scoped>
.announcements-page { animation: fadeIn 0.3s ease; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-title {
  h1 { font-size: 24px; font-weight: 700; color: $text-primary; margin-bottom: 4px; }
  p { font-size: 14px; color: $text-secondary; }
}

.announcements-list { display: flex; flex-direction: column; gap: 16px; }

.announcement-card {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: 20px;
  box-shadow: $shadow-sm;
  transition: all $transition-fast;

  &:hover { box-shadow: $shadow-md; }
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.announcement-actions { display: flex; gap: 8px; }

.announcement-title {
  font-size: 18px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 8px;
}

.announcement-text {
  font-size: 14px;
  color: $text-secondary;
  line-height: 1.6;
}

.announcement-footer { border-top: 1px solid $border-color; padding-top: 16px; margin-top: 16px; }

.announcement-meta { display: flex; gap: 20px; }

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: $text-tertiary;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.form-row {
  display: flex;
  gap: 16px;
  .flex-1 { flex: 1; }
}
</style>
