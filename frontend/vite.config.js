import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    host: '0.0.0.0',
    allowedHosts: [
      'liable-robot-paso-conferencing.trycloudflare.com',
      "dayton-duo-spanking-pleased.trycloudflare.com",
    ],
    cors: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // 特意没有代理整个 /search，因为前端自己也有 /search 页面路由，代理整个 /search 会冲突。
      '/search/protein-embedding': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/search/protein-example': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/tools': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // Local genome static files.
      // Vue reads /jbrowse-static/xxx, Vite forwards to the local Range-capable
      // genome file server. Indexed JBrowse files require HTTP 206 responses.
      '/jbrowse-static': {
        target: 'http://127.0.0.1:9002',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/jbrowse-static/, '')
      }
    },
    },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
