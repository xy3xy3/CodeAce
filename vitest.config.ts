import { defineConfig } from 'vitest/config'
export default defineConfig({
  test: {
    include: ['tests/unit/**/*.test.ts', 'tests/integration/**/*.test.ts'],
    testTimeout: 180000,
    hookTimeout: 30000,
    fileParallelism: false,
  },
  esbuild: { target: 'es2022' },
})
