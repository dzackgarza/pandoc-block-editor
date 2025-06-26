# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]

### Added
*   Created `test_fixtures/torture_test_document.md` with a comprehensive set of Markdown elements to drive development and testing.
*   Implemented initial Markdown parsing using `pypandoc` to convert full documents into an AST, then segmenting the AST into `EditorBlock` structures. Each block's Markdown content is reconstructed from its specific AST elements. (in `src/app.py` and `src/pandoc_utils.py`)
*   Implemented initial Markdown-to-HTML rendering for individual blocks using `pypandoc`, including support for MathJax and Pygments syntax highlighting. (in `src/pandoc_utils.py` and used by `src/app.py`)
*   Added basic unit tests for `pandoc_utils.py` covering AST parsing, AST-to-Markdown conversion, and Markdown-to-HTML conversion.
*   Added unit tests for `app.py` helper functions (`create_editor_block`, `parse_full_markdown_to_editor_blocks`, `reconstruct_markdown_from_editor_blocks`).
*   Updated E2E tests (`tests/e2e/test_main_app.py`) to verify:
    *   Loading of the `torture_test_document.md` by default.
    *   Presence of content from the torture test document in editor and preview panes.
    *   Functionality of the new sidebar UI for adding blocks.
    *   Basic MathJax and code syntax highlighting rendering in previews.

### Changed
*   **UI Refactoring (`src/app.py`, `src/ui_elements.py`):**
    *   Replaced hidden buttons and custom JavaScript-driven file menu with a Streamlit sidebar-based menu for "File" (Open, Save, Exit simulation) and "Edit" (Add Block) operations.
    *   Integrated the debug view toggle into the sidebar.
    *   Removed old custom HTML/JS components for file menu and floating add button from `src/ui_elements.py`.
*   **Core Logic (`src/pandoc_utils.py`):**
    *   Replaced placeholder functions with `pypandoc`-based implementations for:
        *   `parse_markdown_to_ast_json`
        *   `convert_ast_json_to_markdown`
        *   `convert_markdown_to_html` (with MathJax and Pygments options)
*   **Application Startup (`src/app.py`):**
    *   Now loads `test_fixtures/torture_test_document.md` by default.
    *   Uses the implemented Pandoc utilities to parse the document into blocks and render previews.
*   **Styling and Quality:**
    *   Applied `black` formatting to all Python files.
    *   Addressed Pylint warnings across the codebase (line lengths, imports, unused variables, etc.).
    *   Added `pylint` to `requirements.txt`.

### Fixed
*   Ensured `pylint` is installed as a dev dependency and run as part of quality checks.

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
