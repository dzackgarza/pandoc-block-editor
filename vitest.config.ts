import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node', // or 'jsdom' if UI components are tested
    include: ['tests/unit/**/*.test.ts', 'tests/integration/**/*.test.ts', 'tests/safety/**/*.test.ts', 'tests/scenarios/**/*.test.ts'],
    // setupFiles: ['./tests/setup.ts'], // if you need global setup
    coverage: {
      provider: 'v8', // or 'istanbul'
      reporter: ['text', 'json', 'html'],
    },
  },
});
