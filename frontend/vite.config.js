import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [vue()],
    server: {
      // 开发服务器监听地址（0.0.0.0 允许外部访问）
      host: env.VITE_DEV_HOST || '0.0.0.0',
      // 开发服务器端口（从环境变量读取，默认 5173）
      port: parseInt(env.VITE_DEV_PORT || '5173', 10),
      // 启动时自动打开浏览器
      open: env.VITE_DEV_OPEN === 'true' || true,
      // 严格端口（如果端口被占用则失败，不自动尝试下一个端口）
      strictPort: env.VITE_DEV_STRICT_PORT === 'true',
      // 代理配置（可选：如果需要代理 API 请求）
      // proxy: {
      //   '/api': {
      //     target: env.VITE_API_BASE_URL || 'http://localhost:8000',
      //     changeOrigin: true,
      //   }
      // }
    },
    build: {
      // 生产环境输出目录
      outDir: 'dist',
      // 生成 source map 用于调试
      sourcemap: false,
      // 资源内联限制
      assetsInlineLimit: 4096,
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/styles/variables.scss" as *;`
        }
      }
    }
  }
})
