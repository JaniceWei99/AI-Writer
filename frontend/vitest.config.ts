/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

const frontendNodeModules = resolve(__dirname, 'node_modules')

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@testing-library/react': resolve(frontendNodeModules, '@testing-library/react'),
      '@testing-library/jest-dom': resolve(frontendNodeModules, '@testing-library/jest-dom'),
      'react-markdown': resolve(frontendNodeModules, 'react-markdown'),
      'react': resolve(frontendNodeModules, 'react'),
      'react-dom': resolve(frontendNodeModules, 'react-dom'),
      'axios': resolve(frontendNodeModules, 'axios'),
    },
  },
  server: {
    fs: {
      allow: [resolve(__dirname, '..')],
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: resolve(__dirname, 'src/test-setup.ts'),
    include: ['../tests/frontend/**/*.test.{ts,tsx}'],
    css: true,
    reporters: ['default'],
  },
})
