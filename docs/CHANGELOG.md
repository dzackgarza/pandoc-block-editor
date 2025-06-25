# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]

## [0.2.0] - 2024-07-26

### Changed
*   **Project Overhaul to Python/Streamlit (V0.2.0):**
    *   Transitioned project from Node.js/TypeScript to Python/Streamlit.
    *   Removed all Node.js/TypeScript specific files, configurations, and dependencies.
    *   Established new Python project structure:
        *   `main.py` (Streamlit app entry point) in root.
        *   `src/` for Python modules.
        *   `tests/` for Pytest tests (unit, e2e).
        *   `.venv` for virtual environment.
        *   `requirements.txt` for Python dependencies.
    *   Installed core Python dependencies: `streamlit`, `pytest`, `playwright`, `pytest-playwright`, `pylint`, `black`.
    *   Created placeholder files:
        *   `main.py`: Basic Streamlit "Hello World" app.
        *   `src/app_logic.py`: Placeholder Python module.
        *   `tests/unit/test_app_logic.py`: Basic Pytest unit tests.
        *   `tests/e2e/test_main_app.py`: Basic Playwright E2E test.
    *   Configured Python linting (`pylint`) and formatting (`black`) via `pyproject.toml`.
    *   Updated `docs/AGENTS.md` to V0.2.0, reflecting the new Python stack and development guidelines.
    *   Updated this `docs/CHANGELOG.md` to V0.2.0.

### Removed
*   All Node.js/TypeScript specific code, configurations (`package.json`, `tsconfig.json`, `vitest.config.ts`, `playwright.config.ts`, `.eslintrc.js`, etc.), and `node_modules`.

## [0.1.1] - 2024-07-26 (Node.js/TypeScript Version)

### Changed
*   Reorganized configuration files (`.eslintrc.js`, `.prettierrc.json`, `tsconfig.json`, `vitest.config.ts`, `playwright.config.ts`) into a `config/` directory.
*   Moved documentation files (`AGENTS.md`, `CHANGELOG.md`) into a `docs/` directory.
*   Updated `package.json` scripts and internal configuration paths to reflect new file locations.

## [0.1.0] - 2024-07-26 (Node.js/TypeScript Version)

### Added
*   **Initial Project Setup (Node.js/TypeScript - V0.1.0):**
    *   Set up project directory structure: `src/`, `tests/` (unit, integration, e2e, visual, safety, scenarios, mocks), `test-fixtures/`.
    *   Initialized `package.json` with project metadata and scripts.
    *   Installed core development dependencies for TypeScript: Vitest, Playwright, ESLint, Prettier.
    *   Configured TypeScript, Vitest, Playwright, ESLint, Prettier.
    *   Added initial test fixtures and placeholder test files.
    *   Created `AGENTS.md` (V0.1) and `CHANGELOG.md` (V0.1.0).
    *   Established the "Pandoc Block Editor: Testing and Validation Plan" as the guiding document.
