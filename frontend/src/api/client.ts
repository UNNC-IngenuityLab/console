/**
 * Axios HTTP client configuration
 *
 * API 地址通过环境变量 VITE_API_BASE_URL 配置
 *
 * 开发环境示例 (.env.development):
 *   VITE_API_BASE_URL=http://localhost:8000
 *   VITE_API_BASE_URL=http://localhost:8080
 *
 * 生产环境示例 (.env.production):
 *   VITE_API_BASE_URL=http://your-server.com:8000
 *   VITE_API_BASE_URL=https://api.yourdomain.com
 *   # 如果前后端同域部署（Nginx 反向代理），可以使用相对路径:
 *   VITE_API_BASE_URL=/api
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

// 从环境变量读取 API 地址，开发环境默认走同源代理 /api（避免 CORS）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 请求超时时间（可通过环境变量配置）
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10)

/**
 * Create axios instance with default config
 */
const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request interceptor - adds auth token
 */
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor - handles errors
 */
client.interceptors.response.use(
  (response) => {
    // API returns { code, message, data } wrapper
    const { data } = response
    if (data.code === 0) {
      return data
    } else {
      ElMessage.error(data.message || 'Request failed')
      return Promise.reject(new Error(data.message || 'Request failed'))
    }
  },
  (error) => {
    // Handle network errors and non-2xx responses
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          ElMessage.error('Unauthorized - please login again')
          localStorage.removeItem('access_token')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('Forbidden - you do not have permission')
          break
        case 404:
          ElMessage.error('Resource not found')
          break
        case 500:
          ElMessage.error('Server error - please try again later')
          break
        default:
          ElMessage.error(data?.message || error.message || 'Request failed')
      }
    } else if (error.request) {
      ElMessage.error('Network error - please check your connection')
    } else {
      ElMessage.error(error.message || 'Unknown error occurred')
    }
    return Promise.reject(error)
  }
)

export default client

// 导出配置供调试使用
export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
}
