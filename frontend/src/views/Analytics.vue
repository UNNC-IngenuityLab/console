<template>
  <div class="analytics-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>数据分析</h1>
        <p>活动参与度和用户表现的综合洞察</p>
      </div>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 300px;"
        />
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-grid">
      <div class="summary-card">
        <div class="summary-icon" style="background: rgba(79, 70, 229, 0.1); color: #4F46E5;">
          <el-icon :size="24"><User /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ store.totalUsers }}</div>
          <div class="summary-label">总用户数</div>
        </div>
        <div class="summary-trend positive">
          <el-icon><ArrowUp /></el-icon>
          +12%
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-icon" style="background: rgba(16, 185, 129, 0.1); color: #10B981;">
          <el-icon :size="24"><Calendar /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ store.totalActivities }}</div>
          <div class="summary-label">总活动数</div>
        </div>
        <div class="summary-trend positive">
          <el-icon><ArrowUp /></el-icon>
          +3
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-icon" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B;">
          <el-icon :size="24"><Checked /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ totalCheckIns }}</div>
          <div class="summary-label">总签到数</div>
        </div>
        <div class="summary-trend positive">
          <el-icon><ArrowUp /></el-icon>
          +28%
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-icon" style="background: rgba(139, 92, 246, 0.1); color: #8B5CF6;">
          <el-icon :size="24"><TrendCharts /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-value">{{ avgCompletion }}%</div>
          <div class="summary-label">平均完成率</div>
        </div>
        <div class="summary-trend positive">
          <el-icon><ArrowUp /></el-icon>
          +5%
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <!-- Activity Completion Funnel -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>活动完成漏斗</h3>
        </div>
        <div class="funnel-container">
          <div
            v-for="(stage, index) in funnelStages"
            :key="index"
            class="funnel-stage"
            :style="{ width: stage.width + '%' }"
          >
            <div class="funnel-bar" :style="{ background: stage.color }">
              <div class="funnel-label">{{ stage.label }}</div>
              <div class="funnel-value">{{ stage.value }}</div>
            </div>
            <div v-if="index < funnelStages.length - 1" class="funnel-rate">
              {{ stage.rate }}% 转化率
            </div>
          </div>
        </div>
      </div>

      <!-- User Engagement Trend -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>用户活跃趋势</h3>
          <div class="time-selector">
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button label="7d">近7天</el-radio-button>
              <el-radio-button label="30d">近30天</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div ref="chartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- Activity Performance -->
    <div class="performance-section card">
      <div class="card-header">
        <h3>活动完成情况</h3>
        <div class="legend">
          <span class="legend-item">
            <span class="legend-dot" style="background: #10B981;"></span>
            高 (≥70%)
          </span>
          <span class="legend-item">
            <span class="legend-dot" style="background: #F59E0B;"></span>
            中 (50-69%)
          </span>
          <span class="legend-item">
            <span class="legend-dot" style="background: #EF4444;"></span>
            低 (&lt;50%)
          </span>
        </div>
      </div>
      <div class="performance-list">
        <div
          v-for="activity in activityPerformance"
          :key="activity.id"
          class="performance-item"
        >
          <div class="performance-info">
            <div class="performance-name">{{ activity.name }}</div>
            <div class="performance-meta">
              {{ activity.completedCount }} / {{ activity.signUpCount }} 已完成
            </div>
          </div>
          <div class="performance-progress">
            <el-progress
              :percentage="activity.rate"
              :stroke-width="16"
              :text-inside="true"
              :color="getProgressColor(activity.rate)"
            />
          </div>
          <div class="performance-status" :class="activity.statusClass">
            {{ activity.rate }}%
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="bottom-row">
      <!-- Points Distribution -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>积分分布</h3>
        </div>
        <div ref="distributionChartRef" class="chart-container"></div>
      </div>

      <!-- Level Distribution -->
      <div class="chart-card card">
        <div class="card-header">
          <h3>等级分布</h3>
        </div>
        <div class="level-distribution">
          <div
            v-for="level in levelDistribution"
            :key="level.level"
            class="level-bar"
          >
            <div class="level-info">
              <span class="level-number">Lv.{{ level.level }}</span>
              <span class="level-name">{{ level.name }}</span>
            </div>
            <div class="level-progress">
              <div
                class="level-fill"
                :style="{ width: level.percentage + '%', background: level.color }"
              ></div>
            </div>
            <span class="level-count">{{ level.count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores'
import { User, Calendar, Checked, TrendCharts, Download, ArrowUp } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const store = useAdminStore()

const dateRange = ref([])
const timeRange = ref('7d')
const chartRef = ref(null)
const distributionChartRef = ref(null)

const levelNames = [
  '车库小店', '家族商店', '邻里商店', '社区商店', '区域商店',
  '城市商店', '区域总部', '全国总部', '洲际总部', '世界级总部'
]

const levelColors = [
  '#9CA3AF', '#60A5FA', '#34D399', '#A78BFA', '#F472B6',
  '#FB923C', '#FBBF24', '#4ADE80', '#38BDF8', '#818CF8'
]

const totalCheckIns = computed(() => store.checkIns.length)

const avgCompletion = computed(() => {
  if (!store.activities.length) return 0
  const rates = store.activities.map(a =>
    a.signUpCount > 0 ? Math.round((a.completedCount / a.signUpCount) * 100) : 0
  )
  return Math.round(rates.reduce((s, r) => s + r, 0) / rates.length)
})

const funnelStages = computed(() => {
  const totalSignUps = store.activities.reduce((s, a) => s + a.signUpCount, 0)
  const totalCompleted = store.activities.reduce((s, a) => s + a.completedCount, 0)
  const avgRate = totalSignUps > 0 ? Math.round((totalCompleted / totalSignUps) * 100) : 0

  return [
    { label: '已报名', value: totalSignUps, width: 100, color: '#4F46E5', rate: 100 },
    { label: '已参加', value: Math.round(totalSignUps * 0.85), width: 85, color: '#10B981', rate: 85 },
    { label: '已完成', value: totalCompleted, width: avgRate, color: '#F59E0B', rate: avgRate }
  ]
})

const activityPerformance = computed(() => {
  return store.activities.map(a => {
    const rate = a.signUpCount > 0 ? Math.round((a.completedCount / a.signUpCount) * 100) : 0
    return { ...a, rate, statusClass: rate >= 70 ? 'high' : rate >= 50 ? 'medium' : 'low' }
  }).sort((a, b) => b.rate - a.rate)
})

const levelDistribution = computed(() => {
  const distribution = Array(10).fill(0).map((_, i) => ({
    level: i + 1,
    name: levelNames[i],
    count: 0,
    color: levelColors[i]
  }))

  store.users.forEach(user => {
    const level = Math.min(Math.floor(user.totalPoints / 10) + 1, 10)
    distribution[level - 1].count++
  })

  const maxCount = Math.max(...distribution.map(d => d.count), 1)
  return distribution.map(d => ({ ...d, percentage: Math.round((d.count / maxCount) * 100) }))
})

function getProgressColor(rate) {
  if (rate >= 70) return '#10B981'
  if (rate >= 50) return '#F59E0B'
  return '#EF4444'
}

function exportReport() {
  // Export logic
}

onMounted(() => {
  // Trend Chart
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    const days = timeRange.value === '7d' ? 7 : 30
    const labels = Array.from({ length: days }, (_, i) => {
      const d = new Date()
      d.setDate(d.getDate() - (days - 1 - i))
      return `${d.getMonth() + 1}/${d.getDate()}`
    })

    chart.setOption({
      grid: { top: 20, right: 20, bottom: 40, left: 50 },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#9CA3AF', rotate: 45 }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: '#E5E7EB', type: 'dashed' } },
        axisLabel: { color: '#9CA3AF' }
      },
      series: [
        {
          name: '报名数',
          type: 'bar',
          data: generateRandomData(days, 50, 150),
          itemStyle: { color: '#4F46E5', borderRadius: [4, 4, 0, 0] },
          barWidth: '40%'
        },
        {
          name: '签到数',
          type: 'line',
          data: generateRandomData(days, 30, 120),
          smooth: true,
          lineStyle: { color: '#10B981', width: 3 },
          itemStyle: { color: '#10B981' }
        }
      ]
    })

    window.addEventListener('resize', () => chart.resize())
  }

  // Distribution Chart
  if (distributionChartRef.value) {
    const chart = echarts.init(distributionChartRef.value)

    const ranges = ['0-19', '20-39', '40-59', '60-79', '80+']
    const data = [
      store.users.filter(u => u.totalPoints < 20).length,
      store.users.filter(u => u.totalPoints >= 20 && u.totalPoints < 40).length,
      store.users.filter(u => u.totalPoints >= 40 && u.totalPoints < 60).length,
      store.users.filter(u => u.totalPoints >= 60 && u.totalPoints < 80).length,
      store.users.filter(u => u.totalPoints >= 80).length
    ]

    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        labelLine: { show: false },
        data: data.map((value, index) => ({
          value,
          name: ranges[index],
          itemStyle: { color: ['#EF4444', '#F59E0B', '#3B82F6', '#8B5CF6', '#10B981'][index] }
        }))
      }]
    })

    window.addEventListener('resize', () => chart.resize())
  }
})

function generateRandomData(count, min, max) {
  return Array.from({ length: count }, () =>
    Math.floor(Math.random() * (max - min + 1)) + min
  )
}
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

.summary-trend { display: flex; align-items: center; gap: 2px; font-size: 13px; font-weight: 500;
  &.positive { color: $success-color; }
}

.charts-row { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-bottom: 20px; }

.chart-card { background: $bg-card; border-radius: $border-radius-lg; padding: 20px; box-shadow: $shadow-sm; }

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
  h3 { font-size: 16px; font-weight: 600; color: $text-primary; }
}

.legend { display: flex; gap: 16px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: $text-secondary; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }

.funnel-container { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.funnel-stage { transition: all 0.3s ease; }
.funnel-bar { height: 50px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; }
.funnel-label { font-size: 12px; opacity: 0.9; }
.funnel-value { font-size: 18px; font-weight: 700; }
.funnel-rate { font-size: 11px; color: $text-tertiary; margin-top: 4px; }

.chart-container { height: 280px; }

.performance-section { background: $bg-card; border-radius: $border-radius-lg; padding: 20px; margin-bottom: 20px; box-shadow: $shadow-sm; }

.performance-list { display: flex; flex-direction: column; gap: 16px; max-height: 400px; overflow-y: auto; }

.performance-item { display: flex; align-items: center; gap: 16px; }

.performance-info { width: 200px; flex-shrink: 0;
  .performance-name { font-weight: 500; color: $text-primary; }
  .performance-meta { font-size: 12px; color: $text-tertiary; }
}

.performance-progress { flex: 1; }

.performance-status { width: 60px; text-align: right; font-weight: 600;
  &.high { color: $success-color; }
  &.medium { color: $warning-color; }
  &.low { color: $danger-color; }
}

.bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.level-distribution { display: flex; flex-direction: column; gap: 12px; }

.level-bar { display: flex; align-items: center; gap: 12px; }

.level-info { width: 140px; display: flex; gap: 8px;
  .level-number { font-size: 12px; font-weight: 600; color: $text-secondary; }
  .level-name { font-size: 12px; color: $text-tertiary; }
}

.level-progress { flex: 1; height: 24px; background: $bg-secondary; border-radius: 12px; overflow: hidden; }
.level-fill { height: 100%; border-radius: 12px; transition: width 0.5s ease; }
.level-count { width: 30px; text-align: right; font-weight: 600; color: $text-primary; }
</style>
