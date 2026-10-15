import path from 'node:path'
import { defineConfig, loadEnv } from 'vite' // Added loadEnv here
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // The 3rd argument '' tells Vite to load ALL variables, even without the VITE_ prefix.
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    envPrefix: 'VITE_',
    server: {
      port: 3000, // Forces your Vite frontend to run on port 3000
      proxy: {
        '/api': {
          // Explicitly points to your Python API on port 8000
          target: env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
