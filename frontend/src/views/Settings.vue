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

        <!-- Toolbar -->
        <div class="level-table-toolbar">
          <el-button type="primary" plain size="small" @click="exportLevels">
            <el-icon><Download /></el-icon> 导出 JSON
          </el-button>
          <el-button plain size="small" @click="showImportDialog = true">
            <el-icon><Upload /></el-icon> 导入 JSON
          </el-button>
          <span v-if="isSavingOrder" class="saving-hint">
            <el-icon class="is-loading"><Loading /></el-icon> 保存中...
          </span>
        </div>

        <el-skeleton v-if="loadingLevels" :rows="5" animated />
        <el-empty v-else-if="!levelConfigs.length" description="暂无等级配置" :image-size="60" />
        <div v-else class="level-table">
          <!-- 表头 -->
          <div class="level-table-head">
            <span class="lcol-drag"></span>
            <span class="lcol-badge"></span>
            <span class="lcol-name">名称</span>
            <span class="lcol-score">积分范围</span>
            <span class="lcol-color">主题色</span>
            <span class="lcol-icon">图标</span>
            <span class="lcol-actions"></span>
          </div>

          <draggable
            v-model="levelConfigs"
            item-key="id"
            handle=".drag-handle"
            ghost-class="ghost-row"
            @start="isDragging = true"
            @end="onDragEnd"
          >
            <template #item="{ element: level }">
              <div>
                <!-- 只读行 -->
                <div v-if="editingLevelId !== level.id" class="level-row" @click="startEdit(level)">
                  <div class="lcol-drag drag-handle" @click.stop>
                    <el-icon><Rank /></el-icon>
                  </div>
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
                    <el-tooltip content="预览">
                      <el-button size="small" circle @click.stop="openPreview(level)">
                        <el-icon><View /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-button size="small" plain @click.stop="startEdit(level)">
                      <el-icon><Edit /></el-icon> 编辑
                    </el-button>
                  </div>
                </div>

                <!-- 编辑行 -->
                <div v-else class="level-row level-row-edit">
                  <div class="edit-panel">
                    <div class="edit-grid">
                      <!-- 左列：基本信息 -->
                      <div class="edit-col-main">
                        <el-form :model="editForm" label-position="left" class="edit-fields-row">
                          <span class="lv-badge" :style="{ background: editForm.bg_color || '#9CA3AF' }">Lv.{{ level.level }}</span>
                          <el-form-item label="名称" class="ef-item">
                            <el-input v-model="editForm.name" style="width: 120px;" />
                          </el-form-item>
                          <el-form-item label="最低积分" class="ef-item">
                            <el-input-number v-model="editForm.min_score" :min="0" :step="1" style="width: 100px;" controls-position="right" />
                          </el-form-item>
                          <el-form-item label="最高积分" class="ef-item">
                            <el-input-number v-model="editForm.max_score" :min="0" :step="1" style="width: 100px;" controls-position="right" placeholder="无上限" />
                          </el-form-item>
                          <el-form-item label="主题色" class="ef-item">
                            <div class="color-pair">
                              <el-color-picker v-model="editForm.bg_color" size="small" />
                              <el-input v-model="editForm.bg_color" placeholder="#9CA3AF" style="width: 86px;" />
                            </div>
                          </el-form-item>
                        </el-form>
                        <el-form-item label="图标 URL" class="ef-item ef-url-full">
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
                      </div>

                      <!-- 右列：描述 -->
                      <div class="edit-col-desc">
                        <el-form-item label="等级描述（中文）" class="ef-item ef-desc-full">
                          <el-input
                            v-model="editForm.description"
                            type="textarea"
                            :rows="3"
                            placeholder="请输入等级描述..."
                            maxlength="500"
                            show-word-limit
                          />
                        </el-form-item>
                        <el-form-item label="等级描述（英文）" class="ef-item ef-desc-full">
                          <el-input
                            v-model="editForm.description_en"
                            type="textarea"
                            :rows="3"
                            placeholder="Enter level description in English..."
                            maxlength="500"
                            show-word-limit
                          />
                        </el-form-item>
                      </div>
                    </div>

                    <!-- 底部操作按钮 -->
                    <div class="edit-actions">
                      <el-button @click="cancelEdit">取消</el-button>
                      <el-button type="primary" :loading="savingLevelId === level.id" @click="saveLevel(level)">保存</el-button>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </draggable>
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

    <!-- Import Dialog -->
    <el-dialog v-model="showImportDialog" title="导入等级配置" width="600px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="JSON 数据">
          <el-input
            v-model="importJsonText"
            type="textarea"
            :rows="10"
            placeholder="粘贴导出的 JSON 数据..."
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="importReplaceExisting">
            替换现有配置（删除所有现有等级后导入）
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" :loading="isImporting" @click="importLevels">
          导入
        </el-button>
      </template>
    </el-dialog>

    <!-- Preview Dialog -->
    <el-dialog v-model="showPreviewDialog" title="等级预览" width="400px" align-center>
      <div v-if="previewLevel" class="level-preview">
        <div class="preview-badge" :style="{ background: previewLevel.bg_color || '#9CA3AF' }">
          <img v-if="previewLevel.icon_url" :src="previewLevel.icon_url" class="preview-icon" @error="$event.target.style.display='none'" />
          <div class="preview-level-text">Lv.{{ previewLevel.level }}</div>
        </div>
        <h2 class="preview-name">{{ previewLevel.name }}</h2>
        <p class="preview-score">
          积分范围: {{ previewLevel.min_score }} – {{ previewLevel.max_score ?? '∞' }}
        </p>
        <p v-if="previewLevel.description" class="preview-desc">
          {{ previewLevel.description }}
        </p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useApiStore } from '@/stores/api'
import { levelsApi } from '@/api/services'
import draggable from 'vuedraggable'
import { Setting, Bell, TrendCharts, Lock, Warning, InfoFilled, Picture, Edit, Download, Upload, Rank, View, Loading } from '@element-plus/icons-vue'

const store = useApiStore()

const levelConfigs = ref([])
const loadingLevels = ref(false)
const savingLevelId = ref(null)
const savingGeneral = ref(false)
const savingMaintenance = ref(false)
const savingSecurity = ref(false)

// Drag state
const isDragging = ref(false)
const isSavingOrder = ref(false)

// Import/Export state
const showImportDialog = ref(false)
const importJsonText = ref('')
const importReplaceExisting = ref(false)
const isImporting = ref(false)

// Preview state
const showPreviewDialog = ref(false)
const previewLevel = ref(null)

const editingLevelId = ref(null)
const editForm = reactive({
  name: '',
  min_score: 0,
  max_score: null,
  bg_color: null,
  icon_url: null,
  description: '',
  description_en: '',
})

function startEdit(level) {
  editingLevelId.value = level.id
  editForm.name = level.name
  editForm.min_score = Number(level.min_score)
  editForm.max_score = level.max_score != null ? Number(level.max_score) : null
  editForm.bg_color = level.bg_color || null
  editForm.icon_url = level.icon_url || null
  editForm.description = level.description || ''
  editForm.description_en = level.description_en || ''
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
      description: editForm.description || null,
      description_en: editForm.description_en || null,
    })
    // 更新本地数据
    Object.assign(level, {
      name: editForm.name,
      min_score: editForm.min_score,
      max_score: editForm.max_score,
      bg_color: editForm.bg_color,
      icon_url: editForm.icon_url,
      description: editForm.description || null,
      description_en: editForm.description_en || null,
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

// Export levels to JSON file
async function exportLevels() {
  try {
    const res = await levelsApi.export()
    const levels = res.data?.levels || res.data || []
    const jsonStr = JSON.stringify(levels, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `level-configs-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

// Import levels from JSON
async function importLevels() {
  if (!importJsonText.value.trim()) {
    ElMessage.warning('请输入 JSON 数据')
    return
  }

  let levels
  try {
    levels = JSON.parse(importJsonText.value)
    if (!Array.isArray(levels)) {
      ElMessage.error('JSON 格式错误：应为数组')
      return
    }
  } catch (e) {
    ElMessage.error('JSON 格式错误')
    return
  }

  isImporting.value = true
  try {
    await levelsApi.import({
      levels,
      replace_existing: importReplaceExisting.value
    })
    ElMessage.success('导入成功')
    showImportDialog.value = false
    importJsonText.value = ''
    importReplaceExisting.value = false
    await loadLevels()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '导入失败')
  } finally {
    isImporting.value = false
  }
}

// Handle drag end - save new order
async function onDragEnd() {
  if (isDragging.value) return

  // Build level_orders map from current order
  const levelOrders = {}
  levelConfigs.value.forEach((level, index) => {
    levelOrders[level.level] = index
  })

  isSavingOrder.value = true
  try {
    await levelsApi.reorder(levelOrders)
    ElMessage.success('等级排序已保存')
  } catch (e) {
    ElMessage.error('保存排序失败')
    // Reload to reset order
    await loadLevels()
  } finally {
    isSavingOrder.value = false
  }
}

// Open preview dialog
function openPreview(level) {
  previewLevel.value = level
  showPreviewDialog.value = true
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
$col-act:   100px;
$col-drag:  32px;

.level-table {
  border: 1px solid $border-color;
  border-radius: $border-radius;
  overflow: hidden;
}

.level-table-head,
.level-row {
  display: grid;
  grid-template-columns: $col-drag $col-badge minmax(120px, $col-name) $col-score $col-color $col-icon $col-act;
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
  min-height: 52px;
  border-bottom: 1px solid $border-color;
  cursor: pointer;
  transition: background 0.15s;

  &:last-child { border-bottom: none; }
  &:hover { background: rgba(79, 70, 229, 0.03); }
}

.lcol-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.lcol-actions { display: flex; justify-content: flex-end; gap: 8px; }

// ── Drag & Drop ─────────────────────────────────────────────────────────────

.level-table-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

.saving-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: $text-secondary;
  margin-left: auto;

  .is-loading {
    animation: spin 1s linear infinite;
  }
}

.lcol-drag {
  width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drag-handle {
  cursor: grab;
  color: $text-tertiary;
  transition: color 0.15s;

  &:hover { color: $primary-color; }
  &:active { cursor: grabbing; }
}

.ghost-row {
  opacity: 0.5;
  background: rgba(79, 70, 229, 0.1);
}

// ── Edit Panel ───────────────────────────────────────────────────────────────

.edit-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  align-items: start;
}

.edit-col-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.edit-fields-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.edit-col-desc {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ef-item {
  margin-bottom: 0;

  :deep(.el-form-item__label) {
    font-size: 12px;
    color: $text-secondary;
    white-space: nowrap;
  }
}

.ef-url-full {
  width: 100%;
}

.ef-desc-full {
  width: 100%;
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

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 4px;
  border-top: 1px solid $border-color;
}

// ── Level Preview ─────────────────────────────────────────────────────────────

.level-preview {
  text-align: center;
  padding: 20px 0;
}

.preview-badge {
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-md;
}

.preview-icon {
  width: 48px;
  height: 48px;
  object-fit: contain;
  margin-bottom: 8px;
}

.preview-level-text {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.preview-name {
  font-size: 24px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 12px;
}

.preview-score {
  font-size: 14px;
  color: $text-secondary;
  margin-bottom: 8px;
}

.preview-desc {
  font-size: 14px;
  color: $text-secondary;
  line-height: 1.6;
  max-width: 300px;
  margin: 0 auto;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
