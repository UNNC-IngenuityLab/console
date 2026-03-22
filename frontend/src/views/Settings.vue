<template>
  <div class="settings-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>系统设置</h1>
        <p>配置系统参数和管理数据</p>
      </div>
    </div>

    <div v-loading="store.loading.settings" class="settings-grid">
      <!-- General Settings -->
      <div class="settings-card card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(79, 70, 229, 0.1); color: #4F46E5;">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
          <h3>基础设置</h3>
        </div>
        <el-form :model="generalSettings" label-position="top">
          <div class="form-row">
            <el-form-item label="二维码有效期（秒）" class="flex-1">
              <el-input-number
                v-model="generalSettings.qr_code_expiration_seconds"
                :min="30"
                :max="3600"
                :step="30"
                style="width: 100%;"
              />
            </el-form-item>
            <el-form-item label="单次活动最大积分" class="flex-1">
              <el-input-number
                v-model="generalSettings.max_points_per_activity"
                :min="0"
                :max="500"
                style="width: 100%;"
              />
            </el-form-item>
          </div>

          <div class="form-row">
            <el-form-item label="排行榜显示人数" class="flex-1">
              <el-input-number
                v-model="generalSettings.leaderboard_top_n"
                :min="1"
                :max="100"
                style="width: 100%;"
              />
            </el-form-item>
            <el-form-item label="每页活动数量" class="flex-1">
              <el-input-number
                v-model="generalSettings.activities_per_page"
                :min="5"
                :max="100"
                style="width: 100%;"
              />
            </el-form-item>
          </div>

          <el-form-item label="用户注册">
            <div class="switch-row">
              <el-switch v-model="generalSettings.registration_open" />
              <span class="form-hint">{{ generalSettings.registration_open ? '开放注册' : '关闭注册' }}</span>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="savingGeneral" @click="saveGeneralSettings">保存设置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Maintenance Settings -->
      <div class="settings-card card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B;">
            <el-icon :size="24"><Warning /></el-icon>
          </div>
          <h3>维护模式</h3>
        </div>
        <el-form :model="maintenanceSettings" label-position="top">
          <el-form-item label="维护模式">
            <div class="switch-row">
              <el-switch
                v-model="maintenanceSettings.maintenance_mode"
                active-color="#EF4444"
              />
              <span class="form-hint" :style="{ color: maintenanceSettings.maintenance_mode ? '#EF4444' : '' }">
                {{ maintenanceSettings.maintenance_mode ? '系统维护中，普通用户无法访问' : '系统正常运行' }}
              </span>
            </div>
          </el-form-item>

          <el-form-item label="维护提示信息">
            <el-input
              v-model="maintenanceSettings.maintenance_message"
              type="textarea"
              :rows="3"
              placeholder="系统维护中，请稍后再试..."
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="savingMaintenance" @click="saveMaintenanceSettings">保存设置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Level Configuration -->
      <div class="settings-card card level-config-card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B;">
            <el-icon :size="24"><TrendCharts /></el-icon>
          </div>
          <h3>等级配置</h3>
        </div>
        <el-skeleton v-if="loadingLevels" :rows="5" animated />
        <el-empty v-else-if="!levelConfigs.length" description="暂无等级配置" :image-size="60" />
        <div v-else class="level-table">
          <!-- 表头 -->
          <div class="level-table-head">
            <span class="lcol-badge"></span>
            <span class="lcol-name">名称</span>
            <span class="lcol-score">积分范围</span>
            <span class="lcol-color">主题色</span>
            <span class="lcol-icon">图标</span>
            <span class="lcol-actions"></span>
          </div>

          <template v-for="level in levelConfigs" :key="level.id">
            <!-- 只读行 -->
            <div v-if="editingLevelId !== level.id" class="level-row" @click="startEdit(level)">
              <div class="lcol-badge">
                <span class="lv-badge" :style="{ background: level.bg_color || '#9CA3AF' }">Lv.{{ level.level }}</span>
              </div>
              <div class="lcol-name">{{ level.name }}</div>
              <div class="lcol-score">
                <span class="score-range">{{ level.min_score }} – {{ level.max_score != null ? level.max_score : '∞' }}</span>
              </div>
              <div class="lcol-color">
                <span class="color-swatch" :style="{ background: level.bg_color || '#9CA3AF' }"></span>
                <span class="color-hex">{{ level.bg_color || '—' }}</span>
              </div>
              <div class="lcol-icon">
                <img v-if="level.icon_url" :src="level.icon_url" class="icon-thumb" @error="$event.target.style.opacity=0" />
                <span v-else class="no-icon">—</span>
              </div>
              <div class="lcol-actions">
                <el-button size="small" plain @click.stop="startEdit(level)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
              </div>
            </div>

            <!-- 编辑行 -->
            <div v-else class="level-row level-row-edit">
              <div class="edit-panel">
                <div class="edit-panel-top">
                  <span class="lv-badge" :style="{ background: editForm.bg_color || '#9CA3AF' }">Lv.{{ level.level }}</span>
                  <el-form-item label="名称" class="ef-item">
                    <el-input v-model="editForm.name" style="width: 130px;" />
                  </el-form-item>
                  <el-form-item label="最低积分" class="ef-item">
                    <el-input-number v-model="editForm.min_score" :min="0" :step="1" style="width: 110px;" controls-position="right" />
                  </el-form-item>
                  <el-form-item label="最高积分" class="ef-item">
                    <el-input-number v-model="editForm.max_score" :min="0" :step="1" style="width: 110px;" controls-position="right" placeholder="无上限" />
                  </el-form-item>
                  <el-form-item label="主题色" class="ef-item">
                    <div class="color-pair">
                      <el-color-picker v-model="editForm.bg_color" size="small" />
                      <el-input v-model="editForm.bg_color" placeholder="#9CA3AF" style="width: 86px;" />
                    </div>
                  </el-form-item>
                </div>
                <div class="edit-panel-bottom">
                  <el-form-item label="图标 URL" class="ef-item ef-url">
                    <div class="icon-url-row">
                      <el-input v-model="editForm.icon_url" placeholder="https://example.com/level.png" clearable>
                        <template #prefix><el-icon><Picture /></el-icon></template>
                      </el-input>
                      <img
                        v-if="editForm.icon_url"
                        :src="editForm.icon_url"
                        class="icon-preview-sm"
                        @error="$event.target.style.opacity=0"
                        @load="$event.target.style.opacity=1"
                      />
                    </div>
                  </el-form-item>
                  <div class="edit-btns">
                    <el-button @click="cancelEdit">取消</el-button>
                    <el-button type="primary" :loading="savingLevelId === level.id" @click="saveLevel(level)">保存</el-button>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Security Settings -->
      <div class="settings-card card">
        <div class="card-header">
          <div class="header-icon" style="background: rgba(139, 92, 246, 0.1); color: #8B5CF6;">
            <el-icon :size="24"><Lock /></el-icon>
          </div>
          <h3>扫码限制</h3>
        </div>
        <el-form :model="securitySettings" label-position="top">
          <el-form-item label="每分钟扫码限制次数">
            <el-input-number
              v-model="securitySettings.scan_rate_limit_per_minute"
              :min="1"
              :max="60"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="新用户初始积分">
            <el-input-number
              v-model="securitySettings.new_user_initial_points"
              :min="0"
              :max="100"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="savingSecurity" @click="saveSecuritySettings">保存设置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useApiStore } from '@/stores/api'
import { levelsApi } from '@/api/services'
import { Setting, Bell, TrendCharts, Lock, Warning, InfoFilled, Picture, Edit } from '@element-plus/icons-vue'

const store = useApiStore()

const levelConfigs = ref([])
const loadingLevels = ref(false)
const savingLevelId = ref(null)
const savingGeneral = ref(false)
const savingMaintenance = ref(false)
const savingSecurity = ref(false)

const editingLevelId = ref(null)
const editForm = reactive({
  name: '',
  min_score: 0,
  max_score: null,
  bg_color: null,
  icon_url: null,
})

function startEdit(level) {
  editingLevelId.value = level.id
  editForm.name = level.name
  editForm.min_score = Number(level.min_score)
  editForm.max_score = level.max_score != null ? Number(level.max_score) : null
  editForm.bg_color = level.bg_color || null
  editForm.icon_url = level.icon_url || null
}

function cancelEdit() {
  editingLevelId.value = null
}

const generalSettings = reactive({
  qr_code_expiration_seconds: 300,
  max_points_per_activity: 100,
  leaderboard_top_n: 50,
  activities_per_page: 20,
  registration_open: true,
})

const maintenanceSettings = reactive({
  maintenance_mode: false,
  maintenance_message: '',
})

const securitySettings = reactive({
  scan_rate_limit_per_minute: 10,
  new_user_initial_points: 0,
})

async function loadSettings() {
  await store.fetchSettings()
  if (store.settings) {
    const s = store.settings
    generalSettings.qr_code_expiration_seconds = s.qr_code_expiration_seconds
    generalSettings.max_points_per_activity = Number(s.max_points_per_activity)
    generalSettings.leaderboard_top_n = s.leaderboard_top_n
    generalSettings.activities_per_page = s.activities_per_page
    generalSettings.registration_open = s.registration_open
    maintenanceSettings.maintenance_mode = s.maintenance_mode
    maintenanceSettings.maintenance_message = s.maintenance_message || ''
    securitySettings.scan_rate_limit_per_minute = s.scan_rate_limit_per_minute
    securitySettings.new_user_initial_points = Number(s.new_user_initial_points)
  }
}

async function loadLevels() {
  loadingLevels.value = true
  try {
    const res = await levelsApi.list()
    levelConfigs.value = (res.data || []).map(l => ({ ...l }))
  } catch (e) {
  } finally {
    loadingLevels.value = false
  }
}

async function saveLevel(level) {
  savingLevelId.value = level.id
  try {
    await levelsApi.update(level.id, {
      name: editForm.name,
      min_score: editForm.min_score,
      max_score: editForm.max_score ?? null,
      bg_color: editForm.bg_color || null,
      icon_url: editForm.icon_url || null,
    })
    // 更新本地数据
    Object.assign(level, {
      name: editForm.name,
      min_score: editForm.min_score,
      max_score: editForm.max_score,
      bg_color: editForm.bg_color,
      icon_url: editForm.icon_url,
    })
    ElMessage.success(`Lv.${level.level} 保存成功`)
    editingLevelId.value = null
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    savingLevelId.value = null
  }
}

async function saveGeneralSettings() {
  savingGeneral.value = true
  try {
    const success = await store.updateSettings({
      qr_code_expiration_seconds: generalSettings.qr_code_expiration_seconds,
      max_points_per_activity: generalSettings.max_points_per_activity,
      leaderboard_top_n: generalSettings.leaderboard_top_n,
      activities_per_page: generalSettings.activities_per_page,
      registration_open: generalSettings.registration_open,
    })
    if (success) ElMessage.success('基础设置保存成功')
  } finally {
    savingGeneral.value = false
  }
}

async function saveMaintenanceSettings() {
  savingMaintenance.value = true
  try {
    const success = await store.updateSettings({
      maintenance_mode: maintenanceSettings.maintenance_mode,
      maintenance_message: maintenanceSettings.maintenance_message || null,
    })
    if (success) ElMessage.success('维护设置保存成功')
  } finally {
    savingMaintenance.value = false
  }
}

async function saveSecuritySettings() {
  savingSecurity.value = true
  try {
    const success = await store.updateSettings({
      scan_rate_limit_per_minute: securitySettings.scan_rate_limit_per_minute,
      new_user_initial_points: securitySettings.new_user_initial_points,
    })
    if (success) ElMessage.success('扫码设置保存成功')
  } finally {
    savingSecurity.value = false
  }
}

onMounted(() => {
  loadSettings()
  loadLevels()
})
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

.form-hint { font-size: 13px; color: $text-secondary; margin-left: 8px; }

.switch-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-config-card {}

// ── Level Table ─────────────────────────────────────────────────────────────

$col-badge: 52px;
$col-name:  1fr;
$col-score: 110px;
$col-color: 100px;
$col-icon:  48px;
$col-act:   72px;

.level-table {
  border: 1px solid $border-color;
  border-radius: $border-radius;
  overflow: hidden;
}

.level-table-head,
.level-row {
  display: grid;
  grid-template-columns: $col-badge $col-name $col-score $col-color $col-icon $col-act;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
}

.level-table-head {
  height: 38px;
  background: $bg-primary;
  border-bottom: 1px solid $border-color;
  font-size: 12px;
  font-weight: 600;
  color: $text-secondary;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.level-row {
  height: 52px;
  border-bottom: 1px solid $border-color;
  cursor: pointer;
  transition: background 0.15s;

  &:last-child { border-bottom: none; }
  &:hover { background: rgba(79, 70, 229, 0.03); }
}

.level-row-edit {
  display: block;
  height: auto;
  padding: 16px;
  cursor: default;
  background: rgba(79, 70, 229, 0.03);
  border-bottom: 1px solid $border-color;

  &:last-child { border-bottom: none; }
  &:hover { background: rgba(79, 70, 229, 0.03); }
}

.lv-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  flex-shrink: 0;
}

.score-range {
  font-size: 13px;
  color: $text-secondary;
  font-variant-numeric: tabular-nums;
}

.color-swatch {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid rgba(0,0,0,.12);
  flex-shrink: 0;
  vertical-align: middle;
  margin-right: 6px;
}

.color-hex {
  font-size: 12px;
  color: $text-secondary;
  font-family: monospace;
  vertical-align: middle;
}

.lcol-color { display: flex; align-items: center; }

.icon-thumb {
  width: 28px;
  height: 28px;
  object-fit: contain;
  border-radius: 4px;
  border: 1px solid $border-color;
  background: #fff;
}

.no-icon {
  font-size: 13px;
  color: $text-secondary;
}

.lcol-actions { display: flex; justify-content: flex-end; }

// ── Edit Panel ───────────────────────────────────────────────────────────────

.edit-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.edit-panel-top,
.edit-panel-bottom {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}

.ef-item {
  margin-bottom: 0;

  :deep(.el-form-item__label) {
    font-size: 12px;
    padding-bottom: 4px;
    line-height: 1.4;
    color: $text-secondary;
  }
}

.ef-url {
  flex: 1;
  min-width: 260px;
}

.color-pair {
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon-url-row {
  display: flex;
  align-items: center;
  gap: 8px;

  .el-input { flex: 1; }
}

.icon-preview-sm {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 4px;
  border: 1px solid $border-color;
  background: #fff;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.edit-btns {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}
</style>
