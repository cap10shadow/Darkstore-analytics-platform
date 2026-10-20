import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    proxy: {
      '/api/v1': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/chat': {
        target: 'http://127.0.0.1:8020',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/chat/, '/api/v1/chat'),
      },
      '/health': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
