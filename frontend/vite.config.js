import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/analyze': 'http://localhost:8000',
      '/approve': 'http://localhost:8000',
      '/reject':  'http://localhost:8000',
    }
  }
})
