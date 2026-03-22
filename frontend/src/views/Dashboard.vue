<template>
  <div class="dashboard-page">
    <!-- Stats Cards -->
    <div class="stats-grid">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="stat-card"
        :style="{ '--accent-color': stat.color }"
      >
        <div class="stat-icon">
          <el-icon :size="24">
            <component :is="stat.icon" />
          </el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            <span class="stat-number">{{ stat.value }}</span>
            <span v-if="stat.change" class="stat-change" :class="stat.changeClass">
              <el-icon :size="12"><component :is="stat.changeIcon" /></el-icon>
              {{ stat.change }}
            </span>
          </div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Quick Actions -->
      <div class="quick-actions card">
        <div class="card-header">
          <h3>快捷操作</h3>
        </div>
        <div class="actions-grid">
          <div
            v-for="action in quickActions"
            :key="action.label"
            class="action-item"
            @click="$router.push(action.path)"
          >
            <div class="action-icon" :style="{ background: action.color }">
              <el-icon :size="22">
                <component :is="action.icon" />
              </el-icon>
            </div>
            <span class="action-label">{{ action.label }}</span>
          </div>
        </div>
      </div>

      <!-- Recent Activities -->
      <div class="recent-activities card">
        <div class="card-header">
          <h3>最近活动</h3>
          <el-button text type="primary" @click="$router.push('/activities')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="activity-list">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-status" :class="activity.statusClass"></div>
            <div class="activity-info">
              <div class="activity-name">{{ activity.name }}</div>
              <div class="activity-meta">
                <span><el-icon><Calendar /></el-icon> {{ activity.date }}</span>
                <span><el-icon><Location /></el-icon> {{ activity.venue }}</span>
              </div>
            </div>
            <div class="activity-stats">
              <div class="activity-points">
                <span class="points-value">{{ activity.totalPoint }}</span>
                <span class="points-label">分</span>
              </div>
              <div class="activity-progress">
                <el-progress
                  :percentage="activity.completionRate"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getProgressColor(activity.completionRate)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Latest Announcements -->
      <div class="announcements card">
        <div class="card-header">
          <h3>最新公告</h3>
          <el-button text type="primary" @click="$router.push('/announcements')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="announcement-list">
          <div
            v-for="announcement in recentAnnouncements"
            :key="announcement.id"
            class="announcement-item"
          >
            <div class="announcement-dot"></div>
            <div class="announcement-content">
              <div class="announcement-title">{{ announcement.title }}</div>
              <div class="announcement-date">{{ announcement.createdAt }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Chart -->
      <div class="activity-chart card">
        <div class="card-header">
          <h3>活跃度趋势</h3>
          <div class="chart-legend">
            <span class="legend-item">
              <span class="legend-dot" style="background: #4F46E5;"></span>
              报名数
            </span>
            <span class="legend-item">
              <span class="legend-dot" style="background: #10B981;"></span>
              签到数
            </span>
          </div>
        </div>
        <div ref="chartRef" class="chart-container"></div>
      </div>

      <!-- Top Users -->
      <div class="top-users card">
        <div class="card-header">
          <h3>积分榜 Top 5</h3>
          <el-button text type="primary" @click="$router.push('/users')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="leaderboard">
          <div
            v-for="(user, index) in topUsers"
            :key="user.id"
            class="leaderboard-item"
          >
            <div class="rank" :class="{ top: index < 3 }">
              {{ index + 1 }}
            </div>
            <div class="user-avatar">{{ user.avatarUrl }}</div>
            <div class="user-info">
              <div class="user-name">{{ user.nickname }}</div>
              <div class="user-id">{{ user.studentId }}</div>
            </div>
            <div class="user-points">
              <span class="points-value">{{ user.totalPoints }}</span>
              <span class="points-label">分</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores'
import * as echarts from 'echarts'
import {
  User, Calendar, Bell, TrendCharts, ArrowRight, Checked,
  Location, Plus, Star, DataLine, List
} from '@element-plus/icons-vue'

const store = useAdminStore()
const chartRef = ref(null)

const stats = computed(() => [
  {
    label: '总用户',
    value: store.totalUsers,
    icon: 'User',
    color: '#4F46E5',
    change: '+12%',
    changeClass: 'positive',
    changeIcon: 'ArrowUp'
  },
  {
    label: '进行中活动',
    value: store.activeActivities,
    icon: 'Calendar',
    color: '#10B981',
    change: '+3',
    changeClass: 'positive',
    changeIcon: 'ArrowUp'
  },
  {
    label: '今日签到',
    value: store.todayCheckIns,
    icon: 'Checked',
    color: '#F59E0B'
  },
  {
    label: '总活动数',
    value: store.totalActivities,
    icon: 'TrendCharts',
    color: '#8B5CF6'
  }
])

const quickActions = [
  { label: '新建活动', icon: 'Plus', color: '#4F46E5', path: '/activities' },
  { label: '发布公告', icon: 'Bell', color: '#10B981', path: '/announcements' },
  { label: '用户管理', icon: 'User', color: '#F59E0B', path: '/users' },
  { label: '数据分析', icon: 'TrendCharts', color: '#8B5CF6', path: '/analytics' }
]

const recentActivities = computed(() => {
  return store.activities.slice(0, 5).map(a => ({
    ...a,
    statusClass: a.status === 'completed' ? 'completed' : a.status === 'active' ? 'active' : 'upcoming',
    completionRate: a.signUpCount > 0 ? Math.round((a.completedCount / a.signUpCount) * 100) : 0
  }))
})

const recentAnnouncements = computed(() => store.announcements.slice(0, 4))

const topUsers = computed(() => {
  return [...store.users]
    .sort((a, b) => b.totalPoints - a.totalPoints)
    .slice(0, 5)
})

function getProgressColor(rate) {
  if (rate >= 70) return '#10B981'
  if (rate >= 50) return '#F59E0B'
  return '#EF4444'
}

onMounted(() => {
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)

    const option = {
      grid: { top: 20, right: 20, bottom: 30, left: 40 },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#9CA3AF' }
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
          type: 'line',
          smooth: true,
          data: [120, 132, 101, 134, 90, 230, 210],
          lineStyle: { color: '#4F46E5', width: 3 },
          itemStyle: { color: '#4F46E5' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(79, 70, 229, 0.3)' },
              { offset: 1, color: 'rgba(79, 70, 229, 0)' }
            ])
          }
        },
        {
          name: '签到数',
          type: 'line',
          smooth: true,
          data: [90, 82, 71, 94, 80, 180, 160],
          lineStyle: { color: '#10B981', width: 3 },
          itemStyle: { color: '#10B981' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0)' }
            ])
          }
        }
      ]
    }

    chart.setOption(option)
    window.addEventListener('resize', () => chart.resize())
  }
})
</script>

<style lang="scss" scoped>
.dashboard-page { animation: fadeIn 0.3s ease; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: $shadow-sm;
  transition: all $transition-normal;

  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--accent-color) 10%, transparent);
  color: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content { flex: 1; }

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 4px;
}

.stat-number {
  font-family: $font-family-display;
  font-size: 32px;
  font-weight: 700;
  color: $text-primary;
}

.stat-change {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
  &.positive { color: $success-color; }
}

.stat-label {
  font-size: 14px;
  color: $text-secondary;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.card {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: 20px;
  box-shadow: $shadow-sm;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  h3 { font-size: 16px; font-weight: 600; color: $text-primary; }
}

.quick-actions { grid-column: span 1; }

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  background: $bg-primary;
  border-radius: $border-radius;
  cursor: pointer;
  transition: all $transition-fast;

  &:hover {
    background: $bg-secondary;
    transform: translateY(-2px);
  }
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.action-label {
  font-size: 13px;
  font-weight: 500;
  color: $text-secondary;
}

.recent-activities { grid-column: span 2; }

.activity-list { display: flex; flex-direction: column; }

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid $border-color;
  &:last-child { border-bottom: none; padding-bottom: 0; }
}

.activity-status {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  &.completed { background: $success-color; }
  &.active { background: $primary-color; }
  &.upcoming { background: $text-disabled; }
}

.activity-info { flex: 1; min-width: 0; }
.activity-name { font-weight: 600; color: $text-primary; margin-bottom: 4px; }
.activity-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: $text-tertiary;
  span { display: flex; align-items: center; gap: 4px; }
}

.activity-stats { width: 120px; text-align: right; }
.activity-points {
  margin-bottom: 6px;
  .points-value {
    font-family: $font-family-display;
    font-size: 20px;
    font-weight: 700;
    color: $primary-color;
  }
  .points-label { font-size: 12px; color: $text-tertiary; }
}

.announcements { grid-column: span 1; }
.announcement-list { display: flex; flex-direction: column; }

.announcement-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid $border-color;
  &:last-child { border-bottom: none; padding-bottom: 0; }
}

.announcement-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $primary-color;
  margin-top: 6px;
  flex-shrink: 0;
}

.announcement-title { font-weight: 500; color: $text-primary; margin-bottom: 4px; }
.announcement-date { font-size: 12px; color: $text-tertiary; }

.activity-chart { grid-column: span 2; }

.chart-legend { display: flex; gap: 16px; }
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: $text-secondary;
}
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }
.chart-container { height: 250px; }

.top-users { grid-column: span 1; }
.leaderboard { display: flex; flex-direction: column; }

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid $border-color;
  &:last-child { border-bottom: none; }
}

.rank {
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

  &.top {
    background: linear-gradient(135deg, #F59E0B, #FBBF24);
    color: #fff;
  }
}

.user-avatar { font-size: 24px; }
.user-info { flex: 1; min-width: 0; }
.user-name { font-weight: 600; color: $text-primary; }
.user-id { font-size: 12px; color: $text-tertiary; }

.user-points {
  text-align: right;
  .points-value {
    font-family: $font-family-display;
    font-size: 18px;
    font-weight: 700;
    color: $primary-color;
  }
  .points-label { font-size: 11px; color: $text-tertiary; }
}
</style>
