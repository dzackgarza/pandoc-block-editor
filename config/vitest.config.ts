import { defineConfig } from 'vitest/config';

import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node', // or 'jsdom' if UI components are tested
    include: [
      path.resolve(__dirname, '../tests/unit/**/*.test.ts'),
      path.resolve(__dirname, '../tests/integration/**/*.test.ts'),
      path.resolve(__dirname, '../tests/safety/**/*.test.ts'),
      path.resolve(__dirname, '../tests/scenarios/**/*.test.ts'),
    ],
    // setupFiles: [path.resolve(__dirname, '../tests/setup.ts')], // if you need global setup
    coverage: {
      provider: 'v8', // or 'istanbul'
      reporter: ['text', 'json', 'html'],
      reportsDirectory: path.resolve(__dirname, '../coverage'), // Optional: specify absolute path
    },
  },
});
