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
    <div class="announcements-list">
      <div
        v-for="announcement in store.announcements"
        :key="announcement.id"
        class="announcement-card card"
      >
        <div class="announcement-header">
          <div class="announcement-status">
            <el-tag :type="announcement.status === 'published' ? 'success' : 'info'" size="small">
              {{ announcement.status === 'published' ? '已发布' : '草稿' }}
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
              {{ announcement.createdAt }}
            </span>
            <span class="meta-item">
              <el-icon><View /></el-icon>
              {{ Math.floor(Math.random() * 500) + 100 }} 次阅读
            </span>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!store.announcements.length" description="暂无公告">
      <el-button type="primary" @click="showCreateDialog = true">
        发布第一条公告
      </el-button>
    </el-empty>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingAnnouncement ? '编辑公告' : '发布公告'"
      width="600px"
      :close-on-click-modal="false"
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

        <el-form-item label="状态">
          <el-radio-group v-model="announcementForm.status">
            <el-radio label="published">立即发布</el-radio>
            <el-radio label="draft">保存草稿</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAnnouncement">
          {{ editingAnnouncement ? '更新' : '发布' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminStore } from '@/stores'
import { Plus, Edit, Delete, Calendar, View } from '@element-plus/icons-vue'

const store = useAdminStore()

const showCreateDialog = ref(false)
const editingAnnouncement = ref(null)

const announcementForm = reactive({
  title: '',
  content: '',
  status: 'published'
})

function editAnnouncement(announcement) {
  editingAnnouncement.value = announcement
  announcementForm.title = announcement.title
  announcementForm.content = announcement.content
  announcementForm.status = announcement.status
  showCreateDialog.value = true
}

function saveAnnouncement() {
  if (!announcementForm.title || !announcementForm.content) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  if (editingAnnouncement.value) {
    const index = store.announcements.findIndex(a => a.id === editingAnnouncement.value.id)
    if (index > -1) {
      store.announcements[index] = {
        ...store.announcements[index],
        title: announcementForm.title,
        content: announcementForm.content,
        status: announcementForm.status
      }
    }
    ElMessage.success('公告更新成功')
  } else {
    store.addAnnouncement({
      title: announcementForm.title,
      content: announcementForm.content,
      status: announcementForm.status
    })
    ElMessage.success('公告发布成功')
  }

  resetForm()
  showCreateDialog.value = false
}

function deleteAnnouncement(announcement) {
  ElMessageBox.confirm(
    `确定要删除公告"${announcement.title}"吗？`,
    '删除公告',
    { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
  ).then(() => {
    store.deleteAnnouncement(announcement.id)
    ElMessage.success('公告删除成功')
  }).catch(() => {})
}

function resetForm() {
  editingAnnouncement.value = null
  announcementForm.title = ''
  announcementForm.content = ''
  announcementForm.status = 'published'
}
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
</style>
