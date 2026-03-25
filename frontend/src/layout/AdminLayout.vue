<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <transition name="fade">
            <span v-if="!isCollapsed" class="logo-text">Leo 管理后台</span>
          </transition>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <transition name="fade">
            <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
          </transition>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <el-icon :size="18">
            <component :is="isCollapsed ? 'DArrowRight' : 'DArrowLeft'" />
          </el-icon>
          <transition name="fade">
            <span v-if="!isCollapsed">收起菜单</span>
          </transition>
        </button>
        <button class="logout-btn" @click="logout">
          <el-icon :size="18"><SwitchButton /></el-icon>
          <transition name="fade">
            <span v-if="!isCollapsed">退出登录</span>
          </transition>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="main-wrapper" :class="{ collapsed: isCollapsed }">
      <!-- Header -->
      <header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ currentPageTitle }}</h1>
          <div class="breadcrumb">
            <span>首页</span>
            <el-icon :size="14"><ArrowRight /></el-icon>
            <span>{{ currentPageTitle }}</span>
          </div>
        </div>
        <div class="header-right">
          <el-badge :value="activeNotifications" :max="99" class="notification-badge">
            <el-button :icon="Bell" circle />
          </el-badge>
          <el-button :icon="FullScreen" circle @click="toggleFullscreen" />
          <div class="header-divider"></div>
          <el-dropdown trigger="click" placement="bottom-end">
            <div class="user-dropdown">
              <el-avatar :size="36" class="user-avatar-header">
                <el-icon :size="20"><User /></el-icon>
              </el-avatar>
              <div class="user-info">
                <span class="user-name">管理员</span>
                <span class="user-role">超级管理员</span>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="User">个人中心</el-dropdown-item>
                <el-dropdown-item :icon="Setting" @click="$router.push('/settings')">系统设置</el-dropdown-item>
                <el-dropdown-item divided :icon="SwitchButton" @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- Page Content -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Bell, FullScreen, User, Setting, SwitchButton,
  ArrowRight, ArrowDown, DArrowLeft, DArrowRight,
  Odometer, Calendar, Message, UserFilled, TrendCharts, Tools
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const isCollapsed = ref(false)

const activeNotifications = ref(0)


const menuItems = [
  { path: '/dashboard', label: '工作台', icon: 'Odometer' },
  { path: '/activities', label: '活动管理', icon: 'Calendar' },
  { path: '/announcements', label: '公告管理', icon: 'Message' },
  { path: '/users', label: '用户管理', icon: 'User' },
  { path: '/analytics', label: '数据分析', icon: 'TrendCharts' },
  { path: '/settings', label: '系统设置', icon: 'Setting' }
]

const pageTitles = {
  '/dashboard': '工作台',
  '/activities': '活动管理',
  '/announcements': '公告管理',
  '/users': '用户管理',
  '/analytics': '数据分析',
  '/settings': '系统设置'
}

const currentPageTitle = computed(() => pageTitles[route.path] || '工作台')

function isActive(path) {
  return route.path === path
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

function logout() {
  sessionStorage.removeItem('admin_logged_in')
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

// Sidebar Styles
.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  transition: all $transition-normal;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);

  &.collapsed {
    width: 72px;

    .sidebar-header {
      padding: 16px 14px;
    }

    .logo {
      justify-content: center;
    }

    .nav-item {
      justify-content: center;
      padding: 14px;
      margin: 2px 8px;

      .el-icon {
        margin: 0;
      }
    }

    .sidebar-footer {
      padding: 12px 8px;
    }

    .collapse-btn, .logout-btn {
      justify-content: center;
      padding: 10px;

      span {
        display: none;
      }
    }
  }
}

.sidebar-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #818CF8;
  flex-shrink: 0;

  svg {
    width: 26px;
    height: 26px;
  }
}

.logo-text {
  font-family: $font-family-display;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 8px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin: 2px 4px;
  border-radius: 8px;
  color: #94A3B8;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all $transition-fast;
  position: relative;

  .el-icon {
    flex-shrink: 0;
    color: #64748B;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    color: #fff;

    .el-icon {
      color: #94A3B8;
    }
  }

  &.active {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(129, 140, 248, 0.1) 100%);
    color: #fff;

    .el-icon {
      color: #818CF8;
    }

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 20px;
      background: #818CF8;
      border-radius: 0 3px 3px 0;
    }
  }
}

.nav-label {
  flex: 1;
  white-space: nowrap;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.collapse-btn, .logout-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 16px;
  border-radius: 8px;
  background: none;
  border: none;
  color: #64748B;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all $transition-fast;
  font-family: inherit;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    color: #fff;
  }
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #F87171;
}

// Main Wrapper
.main-wrapper {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left $transition-normal;

  &.collapsed {
    margin-left: 72px;
  }
}

// Header Styles
.header {
  height: $header-height;
  background: $bg-card;
  border-bottom: 1px solid $border-color;
  padding: 0 $content-padding;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: $text-primary;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: $text-tertiary;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.notification-badge {
  :deep(.el-badge__content) {
    background: $danger-color;
    border: none;
  }
}

.header-divider {
  width: 1px;
  height: 24px;
  background: $border-color;
  margin: 0 8px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 10px;
  transition: background $transition-fast;

  &:hover {
    background: $bg-secondary;
  }
}

.user-avatar-header {
  background: linear-gradient(135deg, #6366F1, #818CF8);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.user-role {
  font-size: 11px;
  color: $text-tertiary;
}

// Content
.content {
  flex: 1;
  padding: $content-padding;
  overflow-y: auto;
  background: $bg-primary;
}

// Transitions
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-enter-active,
.page-leave-active {
  transition: all 0.25s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
