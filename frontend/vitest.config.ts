/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: '../tests/frontend/setup.ts',
    include: ['../tests/frontend/**/*.test.{ts,tsx}'],
    css: true,
    reporters: ['default', 'html'],
    outputFile: {
      html: '../tests/reports/frontend_report.html',
    },
  },
})
