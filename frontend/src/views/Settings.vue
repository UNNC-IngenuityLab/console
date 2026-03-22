<template>
  <div class="settings-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>系统设置</h1>
        <p>配置系统参数和管理数据</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- General Settings -->
      <div class="settings-card card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(79, 70, 229, 0.1); color: #4F46E5;">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
          <h3>基础设置</h3>
        </div>
        <el-form :model="generalSettings" label-position="top">
          <el-form-item label="站点名称">
            <el-input v-model="generalSettings.siteName" placeholder="请输入站点名称" />
          </el-form-item>

          <div class="form-row">
            <el-form-item label="二维码有效期（分钟）" class="flex-1">
              <el-input-number v-model="generalSettings.qrExpiry" :min="1" :max="120" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="单次活动最大积分" class="flex-1">
              <el-input-number v-model="generalSettings.maxPoints" :min="10" :max="200" style="width: 100%;" />
            </el-form-item>
          </div>

          <el-form-item>
            <el-button type="primary" @click="saveGeneralSettings">保存设置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Notification Settings -->
      <div class="settings-card card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(16, 185, 129, 0.1); color: #10B981;">
            <el-icon :size="24"><Bell /></el-icon>
          </div>
          <h3>通知设置</h3>
        </div>
        <el-form :model="notificationSettings" label-position="top">
          <el-form-item label="邮件通知">
            <el-switch v-model="notificationSettings.emailEnabled" />
            <div class="form-hint">开启后，用户将收到邮件通知</div>
          </el-form-item>

          <el-form-item label="活动提醒">
            <el-switch v-model="notificationSettings.activityReminders" />
            <div class="form-hint">活动开始前自动提醒已报名用户</div>
          </el-form-item>

          <el-form-item label="升级通知">
            <el-switch v-model="notificationSettings.levelUpNotifications" />
            <div class="form-hint">用户升级时发送通知</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Level Configuration -->
      <div class="settings-card card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B;">
            <el-icon :size="24"><TrendCharts /></el-icon>
          </div>
          <h3>等级配置</h3>
        </div>
        <div class="level-config">
          <div v-for="(level, index) in levelConfig" :key="index" class="level-row">
            <div class="level-badge" :style="{ background: level.color }">
              Lv.{{ index + 1 }}
            </div>
            <div class="level-name">{{ level.name }}</div>
            <div class="level-range">{{ level.range }} 分</div>
          </div>
        </div>
        <div class="level-note">
          <el-icon><InfoFilled /></el-icon>
          等级积分规则：每10分升一级，        </div>
      </div>

      <!-- Security Settings -->
      <div class="settings-card card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(139, 92, 246, 0.1); color: #8B5CF6;">
            <el-icon :size="24"><Lock /></el-icon>
          </div>
          <h3>安全设置</h3>
        </div>
        <el-form :model="securitySettings" label-position="top">
          <el-form-item label="两步验证">
            <el-switch v-model="securitySettings.twoFactorAuth" />
            <div class="form-hint">启用后登录需要两步验证</div>
          </el-form-item>

          <el-form-item label="会话超时（分钟）">
            <el-input-number v-model="securitySettings.sessionTimeout" :min="5" :max="120" style="width: 100%;" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- Danger Zone -->
    <div class="danger-zone card">
      <div class="card-header">
        <div class="header-icon" style="background: rgba(239, 68, 68, 0.1); color: #EF4444;">
          <el-icon :size="24"><Warning /></el-icon>
        </div>
        <h3>危险操作</h3>
      </div>
      <div class="danger-content">
        <div class="danger-item">
          <div class="danger-info">
            <h4>清除活动数据</h4>
            <p>清除所有活动记录，但保留用户数据。</p>
          </div>
          <el-button type="danger" @click="confirmClearActivities">清除活动</el-button>
        </div>
        <div class="danger-item">
          <div class="danger-info">
            <h4>重置数据库</h4>
            <p>清空所有数据恢复到初始状态，此操作不可撤销！</p>
          </div>
          <el-button type="danger" @click="confirmResetDatabase">重置数据库</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminStore } from '@/stores'
import { Setting, Bell, TrendCharts, Lock, Warning, InfoFilled } from '@element-plus/icons-vue'

const store = useAdminStore()

const generalSettings = reactive({
  siteName: store.settings.siteName || 'Leo the Billionaire',
  qrExpiry: store.settings.qrExpiry || 30,
  maxPoints: store.settings.maxPoints || 100
})

const notificationSettings = reactive({
  emailEnabled: true,
  activityReminders: true,
  levelUpNotifications: true
})

const securitySettings = reactive({
  twoFactorAuth: false,
  sessionTimeout: 60
})

const levelConfig = [
  { name: '车库小店', range: '0-9', color: '#9CA3AF' },
  { name: '家族商店', range: '10-19', color: '#60A5FA' },
  { name: '邻里商店', range: '20-29', color: '#34D399' },
  { name: '社区商店', range: '30-39', color: '#A78BFA' },
  { name: '区域商店', range: '40-49', color: '#F472B6' },
  { name: '城市商店', range: '50-59', color: '#FB923C' },
  { name: '区域总部', range: '60-69', color: '#FBBF24' },
  { name: '全国总部', range: '70-79', color: '#4ADE80' },
  { name: '洲际总部', range: '80-89', color: '#38BDF8' },
  { name: '世界级总部', range: '90+', color: '#818CF8' }
]

function saveGeneralSettings() {
  store.updateSettings(generalSettings)
  ElMessage.success('基础设置保存成功')
}

function saveNotificationSettings() {
  ElMessage.success('通知设置保存成功')
}

function saveSecuritySettings() {
  ElMessage.success('安全设置保存成功')
}

function confirmClearActivities() {
  ElMessageBox.confirm(
    '确定要清除所有活动数据吗？此操作不可撤销。',
    '清除活动数据',
    { type: 'warning', confirmButtonText: '确定清除', cancelButtonText: '取消' }
  ).then(() => {
    ElMessage.success('活动数据已清除')
  }).catch(() => {})
}

function confirmResetDatabase() {
  ElMessageBox.prompt(
    '此操作将清空所有数据！请输入 "RESET" 确认操作。',
    '重置数据库',
    {
      type: 'error',
      confirmButtonText: '确认重置',
      cancelButtonText: '取消',
      inputPattern: /^RESET$/,
      inputErrorMessage: '请输入 RESET 翻页确认'
    }
  ).then(() => {
    location.reload()
  }).catch(() => {})
}
</script>

<style lang="scss" scoped>
.settings-page { animation: fadeIn 0.3s ease; }

.page-header { margin-bottom: 24px; }

.header-title {
  h1 { font-size: 24px; font-weight: 700; color: $text-primary; margin-bottom: 4px; }
  p { font-size: 14px; color: $text-secondary; }
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.settings-card {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: 24px;
  box-shadow: $shadow-sm;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid $border-color;
  h3 { font-size: 16px; font-weight: 600; color: $text-primary; }
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-row { display: flex; gap: 16px; .flex-1 { flex: 1; } }

.form-hint { font-size: 12px; color: $text-tertiary; margin-top: 4px; }

.level-config { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }

.level-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: $bg-primary;
  border-radius: $border-radius;
}

.level-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.level-name { flex: 1; font-weight: 500; color: $text-primary; }
.level-range { font-size: 13px; color: $text-tertiary; }

.level-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: $bg-primary;
  border-radius: $border-radius;
  font-size: 13px;
  color: $text-secondary;
  .el-icon { color: $primary-color; margin-top: 2px; }
}

.danger-zone {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: 24px;
  box-shadow: $shadow-sm;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.danger-content { display: flex; flex-direction: column; gap: 16px; }

.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(239, 68, 68, 0.05);
  border-radius: $border-radius;
}

.danger-info {
  h4 { font-size: 14px; font-weight: 600; color: $text-primary; margin-bottom: 4px; }
  p { font-size: 13px; color: $text-secondary; }
}
</style>
