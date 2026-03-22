<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>

    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="login-title">Leo 管理后台</h1>
          <p class="login-subtitle">校园活动激励平台</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="学号"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <div class="login-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form>

        <div class="login-footer">
          <p class="hint">
            <el-icon :size="14"><InfoFilled /></el-icon>
            使用学号和密码登录管理后台
          </p>
        </div>
      </div>

      <div class="login-features">
        <div class="feature">
          <el-icon :size="24"><Lock /></el-icon>
          <span>安全登录</span>
        </div>
        <div class="feature">
          <el-icon :size="24"><DataLine /></el-icon>
          <span>实时数据</span>
        </div>
        <div class="feature">
          <el-icon :size="24"><UserFilled /></el-icon>
          <span>用户管理</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, InfoFilled, DataLine, UserFilled } from '@element-plus/icons-vue'
import { useApiStore } from '@/stores/api'

const router = useRouter()
const store = useApiStore()
const formRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入学号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const success = await store.login(form.username, form.password)
    if (success) {
      ElMessage.success('欢迎回来，管理员！')
      router.push('/dashboard')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s infinite ease-in-out;

  &.shape-1 {
    width: 600px;
    height: 600px;
    background: linear-gradient(135deg, $primary-color, $primary-light);
    top: -200px;
    right: -100px;
  }

  &.shape-2 {
    width: 400px;
    height: 400px;
    background: linear-gradient(135deg, $success-color, #34D399);
    bottom: -100px;
    left: -100px;
    animation-delay: -5s;
  }

  &.shape-3 {
    width: 300px;
    height: 300px;
    background: linear-gradient(135deg, $warning-color, #FBBF24);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-delay: -10s;
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(20px, -20px) scale(1.05); }
  50% { transform: translate(-10px, 10px) scale(0.95); }
  75% { transform: translate(-20px, -10px) scale(1.02); }
}

.login-container {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.login-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px 36px;
  width: 400px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
  color: $primary-color;

  svg {
    width: 100%;
    height: 100%;
  }
}

.login-title {
  font-family: $font-family-display;
  font-size: 26px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 4px;
}

.login-subtitle {
  font-size: 14px;
  color: $text-tertiary;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.forgot-link {
  font-size: 13px;
  color: $primary-color;

  &:hover { text-decoration: underline; }
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
}

.login-footer {
  margin-top: 20px;
  text-align: center;
}

.hint {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: $text-tertiary;
  background: $bg-secondary;
  padding: 8px 16px;
  border-radius: 8px;

  code {
    background: $bg-tertiary;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: monospace;
  }
}

.login-features {
  display: flex;
  gap: 48px;

  .feature {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    color: rgba(255, 255, 255, 0.6);

    span { font-size: 13px; }
  }
}
</style>
