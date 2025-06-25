module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
  ],
  plugins: ['@typescript-eslint'],
  env: {
    node: true,
    es2022: true,
  },
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: './config/tsconfig.json', // Adjusted to new location
  },
  rules: {
    // Add any specific rules here
    '@typescript-eslint/no-unused-vars': ['warn', { 'argsIgnorePattern': '^_' }],
  },
  ignorePatterns: ['node_modules/', 'dist/', 'playwright-report/', 'playwright/.cache/'],
};
