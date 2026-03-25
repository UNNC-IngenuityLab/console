<template>
  <div class="analytics-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>数据分析</h1>
        <p>活动参与度和用户表现的综合洞察</p>
      </div>
      <div class="header-actions">
        <el-radio-group v-model="trendDays" size="small" @change="loadTrendChart">
          <el-radio-button :label="7">近7天</el-radio-button>
          <el-radio-button :label="30">近30天</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-grid">
      <div class="summary-card" v-loading="store.loading.analytics">
        <div class="summary-icon" style="background: rgba(79, 70, 229, 0.1); color: #4F46E5;">
          <el-icon :size="24"><User /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ store.dashboardStats?.total_users ?? '-' }}</div>
          <div class="summary-label">总用户数</div>
        </div>
      </div>

      <div class="summary-card" v-loading="store.loading.analytics">
        <div class="summary-icon" style="background: rgba(16, 185, 129, 0.1); color: #10B981;">
          <el-icon :size="24"><Calendar /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ store.dashboardStats?.total_activities ?? '-' }}</div>
          <div class="summary-label">总活动数</div>
        </div>
      </div>

      <div class="summary-card" v-loading="store.loading.analytics">
        <div class="summary-icon" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B;">
          <el-icon :size="24"><Checked /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ store.dashboardStats?.total_completions ?? '-' }}</div>
          <div class="summary-label">总完成签到</div>
        </div>
      </div>

      <div class="summary-card" v-loading="store.loading.analytics">
        <div class="summary-icon" style="background: rgba(139, 92, 246, 0.1); color: #8B5CF6;">
          <el-icon :size="24"><TrendCharts /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ store.dashboardStats ? store.dashboardStats.avg_completion_rate.toFixed(1) : '-' }}%</div>
          <div class="summary-label">平均完成率</div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <!-- Activity Stats -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>活动完成情况 Top 10</h3>
        </div>
        <div v-if="activityStats.length" class="activity-stats-list">
          <div
            v-for="stat in activityStats"
            :key="stat.activity_id"
            class="stat-item"
          >
            <div class="stat-info">
              <div class="stat-name">{{ stat.activity_name }}</div>
              <div class="stat-meta">{{ stat.completed_count }} / {{ stat.sign_up_count }} 已完成</div>
            </div>
            <div class="stat-progress">
              <el-progress
                :percentage="Math.round(stat.completion_rate)"
                :stroke-width="10"
                :show-text="true"
                :color="getProgressColor(Math.round(stat.completion_rate))"
              />
            </div>
          </div>
        </div>
        <el-skeleton v-else-if="loadingActivityStats" :rows="5" animated />
        <el-empty v-else description="暂无数据" :image-size="60" />
      </div>

      <!-- User Engagement Trend -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>用户活跃趋势</h3>
        </div>
        <div ref="trendChartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="bottom-row">
      <!-- Leaderboard -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>积分排行榜</h3>
        </div>
        <div v-if="store.leaderboard.length" class="leaderboard-list">
          <div
            v-for="entry in store.leaderboard.slice(0, 10)"
            :key="entry.user_id"
            class="lb-item"
          >
            <div class="lb-rank" :class="{ top: entry.rank <= 3 }">{{ entry.rank }}</div>
            <div class="lb-info">
              <div class="lb-name">{{ entry.nickname || entry.student_id }}</div>
              <div class="lb-id">Lv.{{ entry.level }} · {{ entry.student_id }}</div>
            </div>
            <div class="lb-points">{{ entry.total_points }} 分</div>
          </div>
        </div>
        <el-skeleton v-else-if="store.loading.analytics" :rows="5" animated />
        <el-empty v-else description="暂无数据" :image-size="60" />
      </div>

      <!-- Level Distribution -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>等级分布</h3>
        </div>
        <div v-if="store.levelDistribution.length" class="level-distribution">
          <div
            v-for="level in store.levelDistribution"
            :key="level.level"
            class="level-bar"
          >
            <div class="level-info">
              <span class="level-number">Lv.{{ level.level }}</span>
              <span class="level-name">{{ level.level_name }}</span>
            </div>
            <div class="level-progress">
              <div
                class="level-fill"
                :style="{ width: level.percentage + '%', background: levelColors[level.level - 1] || '#9CA3AF' }"
              ></div>
            </div>
            <span class="level-count">{{ level.user_count }}</span>
          </div>
        </div>
        <el-skeleton v-else-if="store.loading.analytics" :rows="5" animated />
        <el-empty v-else description="暂无数据" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApiStore } from '@/stores/api'
import { analyticsApi } from '@/api/services'
import { User, Calendar, Checked, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const store = useApiStore()

const trendDays = ref(7)
const trendChartRef = ref(null)
const activityStats = ref([])
const loadingActivityStats = ref(false)

const levelColors = [
  '#9CA3AF', '#60A5FA', '#34D399', '#A78BFA', '#F472B6',
  '#FB923C', '#FBBF24', '#4ADE80', '#38BDF8', '#818CF8'
]

function getProgressColor(rate) {
  if (rate >= 70) return '#10B981'
  if (rate >= 50) return '#F59E0B'
  return '#EF4444'
}

let trendChart = null

async function loadTrendChart() {
  if (!trendChartRef.value) return

  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
    window.addEventListener('resize', () => trendChart?.resize())
  }

  trendChart.showLoading()
  try {
    const res = await analyticsApi.trend({ days: trendDays.value })
    const data = res.data || []
    const labels = data.map(d => d.date.slice(5))
    const signups = data.map(d => d.new_signups)
    const completions = data.map(d => d.new_completions)

    trendChart.hideLoading()
    trendChart.setOption({
      grid: { top: 20, right: 20, bottom: 40, left: 50 },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#9CA3AF', rotate: labels.length > 15 ? 45 : 0 }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: '#E5E7EB', type: 'dashed' } },
        axisLabel: { color: '#9CA3AF' }
      },
      tooltip: { trigger: 'axis' },
      series: [
        {
          name: '报名数',
          type: 'bar',
          data: signups,
          itemStyle: { color: '#4F46E5', borderRadius: [4, 4, 0, 0] },
          barWidth: '40%'
        },
        {
          name: '完成数',
          type: 'line',
          data: completions,
          smooth: true,
          lineStyle: { color: '#10B981', width: 3 },
          itemStyle: { color: '#10B981' }
        }
      ]
    })
  } catch (e) {
    trendChart.hideLoading()
  }
}

async function loadActivityStats() {
  loadingActivityStats.value = true
  try {
    const res = await analyticsApi.activityStats({ limit: 10 })
    activityStats.value = res.data || []
  } catch (e) {
  } finally {
    loadingActivityStats.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchDashboardStats(),
    store.fetchLeaderboard(50),
    store.fetchLevelDistribution(),
    loadActivityStats(),
  ])
  loadTrendChart()
})
</script>

<style lang="scss" scoped>
.analytics-page { animation: fadeIn 0.3s ease; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }

.header-title {
  h1 { font-size: 24px; font-weight: 700; color: $text-primary; margin-bottom: 4px; }
  p { font-size: 14px; color: $text-secondary; }
}

.header-actions { display: flex; gap: 12px; }

.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }

.summary-card {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: $shadow-sm;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-content { flex: 1;
  .summary-value { font-family: $font-family-display; font-size: 28px; font-weight: 700; color: $text-primary; }
  .summary-label { font-size: 13px; color: $text-secondary; }
}

.charts-row { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-bottom: 20px; }

.chart-card { background: $bg-card; border-radius: $border-radius-lg; padding: 20px; box-shadow: $shadow-sm; }

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
  h3 { font-size: 16px; font-weight: 600; color: $text-primary; }
}

.chart-container { height: 280px; }

.activity-stats-list { display: flex; flex-direction: column; gap: 12px; max-height: 280px; overflow-y: auto; }

.stat-item { display: flex; align-items: center; gap: 12px; }

.stat-info { width: 160px; flex-shrink: 0;
  .stat-name { font-weight: 500; color: $text-primary; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .stat-meta { font-size: 12px; color: $text-tertiary; }
}

.stat-progress { flex: 1; }

.bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.leaderboard-list { display: flex; flex-direction: column; gap: 8px; max-height: 320px; overflow-y: auto; }

.lb-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid $border-color;
  &:last-child { border-bottom: none; }
}

.lb-rank {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: $bg-secondary;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: $text-secondary;
  flex-shrink: 0;

  &.top {
    background: linear-gradient(135deg, #F59E0B, #FBBF24);
    color: #fff;
  }
}

.lb-info { flex: 1;
  .lb-name { font-weight: 500; color: $text-primary; font-size: 14px; }
  .lb-id { font-size: 12px; color: $text-tertiary; }
}

.lb-points { font-family: $font-family-display; font-weight: 700; color: $primary-color; }

.level-distribution { display: flex; flex-direction: column; gap: 12px; }

.level-bar { display: flex; align-items: center; gap: 12px; }

.level-info { width: 130px; display: flex; gap: 8px;
  .level-number { font-size: 12px; font-weight: 600; color: $text-secondary; }
  .level-name { font-size: 12px; color: $text-tertiary; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
}

.level-progress { flex: 1; height: 24px; background: $bg-secondary; border-radius: 12px; overflow: hidden; }
.level-fill { height: 100%; border-radius: 12px; transition: width 0.5s ease; }
.level-count { width: 30px; text-align: right; font-weight: 600; color: $text-primary; }
</style>
