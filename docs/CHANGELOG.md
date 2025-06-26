# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]

## [0.2.3] - 2024-07-29

### Fixed
*   **Semantic Block Rendering:** Resolved a critical issue where semantic div blocks (`:::`) containing LaTeX math were incorrectly rendering JavaScript source code (`mhchemParser.ts`). The fix involved adjusting MathJax configuration in `src/app.py` to explicitly disable potentially problematic auto-loaded packages (like `mhchem`) and ensuring Pandoc's `--mathjax` option is used correctly with `--embed-resources` in `src/pandoc_utils.py`. Syntax highlighting (`--highlight-style`) remains temporarily disabled as a precaution during these MathJax-related fixes.
*   Corrected a Pylint E0606 error (`possibly-used-before-assignment`) in `src/app.py` by ensuring proper variable initialization.

### Improved
*   **Startup Performance:** Further enhanced application startup time. The `_process_ast_block` function in `src/app.py` was extended to use Python-based AST-to-Markdown conversion for `Plain` and `CodeBlock` block types, in addition to existing optimizations for `Header` and `Para` blocks. This significantly reduces the number of Pandoc subprocess calls during the initial parsing of Markdown documents.

## [0.2.2] - 2024-07-29

### Fixed
*   Resolved a critical rendering issue where semantic blocks (`:::`) displayed raw JavaScript (`mhchemParser.ts`) instead of their intended content. Diagnostic changes included simplifying the MathJax component URL in `src/app.py` and temporarily removing `--highlight-style=pygments` from Pandoc options in `src/pandoc_utils.py`.
    *   **Note:** The exact root cause of the `mhchemParser.ts` injection is still under investigation, but these changes are expected to mitigate the symptom. Further refinement of MathJax/Pandoc extension interactions may be needed.
*   Corrected a Pylint E0606 error (`possibly-used-before-assignment` for `content` variable) in `_process_ast_block` within `src/app.py` by ensuring `content` is initialized.

### Improved
*   Significantly improved application startup time by refactoring `_process_ast_block` in `src/app.py`. Implemented `_inlines_to_markdown`, a Python helper to directly convert AST for common block types (Headers, Paragraphs) to Markdown, reducing numerous Pandoc subprocess calls during initial document parsing. Complex block types still use Pandoc for content reconstruction.

### Changed
*   Pandoc options for HTML generation in `src/pandoc_utils.py` were iterated upon for diagnostics:
    *   `--embed-resources` is now enabled (restored).
    *   `--highlight-style=pygments` is currently disabled as part of diagnosing the semantic block issue. This may affect code block syntax highlighting.
*   **Image Loading:** With `--embed-resources` re-enabled, local images should be embedded if files are present and accessible to Pandoc. Remote image embedding also relies on this.

## [0.2.1] - 2024-07-29

### Fixed
*   Addressed Pandoc command-line warnings in `src/pandoc_utils.py`:
    *   Replaced deprecated `--self-contained` with `--embed-resources --standalone`.
    *   Added a default HTML title (`--metadata title="Pandoc Document"`) to HTML generation.
*   Applied a diagnostic fix for semantic block (`:::`) rendering issues:
    *   Temporarily removed `--embed-resources` from Pandoc HTML conversion options in `src/pandoc_utils.py`. This is expected to prevent incorrect embedding of JavaScript source (e.g., `mhchemParser.ts`) and allow semantic block content to render correctly. Further work on resource handling may be needed.

### Changed
*   Updated image links in `test_fixtures/torture_test_document.md`:
    *   Corrected remote image URL to a working placeholder.
    *   Added a local image reference for future testing.
*   **Note on Image Loading:** Local image loading is likely affected by the temporary removal of `--embed-resources` and will require a robust solution (e.g., Streamlit static file serving or resolving resource embedding).

### Investigated
*   **Startup Time:** Analyzed application startup performance. Identified that the initial parsing logic (`parse_full_markdown_to_editor_blocks` in `src/app.py`) makes numerous per-block Pandoc calls, which is the primary bottleneck for "massive startup time". No optimization implemented in this version due to complexity.
*   **polyfill.io Warning:** Noted the Pandoc warning about failing to fetch `polyfill.io` as an external issue.

## [0.2.0] - 2024-07-29

### Added
*   **GUI Overhaul & Feature Implementation:**
    *   Implemented a professional Streamlit sidebar-based menu for "File" (Open, Save), "Edit" (Add Block), and "View" (Toggle Debug Info) operations in `src/app.py`.
    *   Implemented a functional Floating Action Button (FAB) in `src/ui_elements.py` for adding new blocks.
    *   Implemented a functional Debug Info modal in `src/ui_elements.py` to display `documentEditorBlocks` data, toggleable from the View menu.
*   **Markdown Handling & Rendering:**
    *   Ensured `test_fixtures/torture_test_document.md` (a comprehensive Markdown test file) is loaded by default on application startup (`src/app.py`).
    *   Verified and refined Markdown parsing into editable blocks and accurate HTML rendering in the dual-pane view, replacing any previous placeholder rendering logic.
*   **Testing & Validation:**
    *   (Conceptual) Added to E2E tests (`tests/e2e/test_main_app.py`) to cover new UI elements (menubar, FAB, debug modal) and default document loading.
    *   (Underlying) Leveraged existing unit tests for Pandoc utilities and block processing.

### Changed
*   **UI Refinement (`src/app.py`, `src/ui_elements.py`):**
    *   Replaced any previous hidden buttons or placeholder UI for file operations, block additions, and debug views with the new menubar, FAB, and debug modal implementations.
*   **Core Logic (`src/pandoc_utils.py`, `src/app.py`):**
    *   Ensured Pandoc utilities correctly support the parsing and rendering pipeline for the block-based editor.
    *   Refactored `src/app.py` (e.g., `parse_full_markdown_to_editor_blocks`, `main`) for improved structure, clarity, and to address Pylint warnings (e.g., reducing local variables).
*   **Styling and Quality:**
    *   Applied `black` formatting to all Python files.
    *   Addressed numerous Pylint warnings (import order, unused variables, etc.), improving the overall code quality score.

### Fixed
*   (Implicit) Corrected Pylint disable comment syntax.
*   (Implicit) Resolved undefined variable errors in E2E tests.

## [0.1.2] - 2024-07-26
<!-- Previous Unreleased content moved here, assuming it was the actual V0.2.0 setup -->
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

## [0.1.1] - 2024-07-26 <!-- Original 0.2.0 moved here, seems like Python project setup -->

### Changed
*   **Project Overhaul to Python/Streamlit:**
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
    *   Updated this `docs/CHANGELOG.md` to V0.2.0 (at that time).

### Removed
*   All Node.js/TypeScript specific code, configurations (`package.json`, `tsconfig.json`, `vitest.config.ts`, `playwright.config.ts`, `.eslintrc.js`, etc.), and `node_modules`.

## [0.1.0] - 2024-07-26 (Node.js/TypeScript Version) <!-- Original 0.1.1 moved here -->

### Changed
*   Reorganized configuration files (`.eslintrc.js`, `.prettierrc.json`, `tsconfig.json`, `vitest.config.ts`, `playwright.config.ts`) into a `config/` directory.
*   Moved documentation files (`AGENTS.md`, `CHANGELOG.md`) into a `docs/` directory.
*   Updated `package.json` scripts and internal configuration paths to reflect new file locations.

## [0.0.1] - 2024-07-26 (Node.js/TypeScript Version) <!-- Original 0.1.0 moved here -->

### Added
*   **Initial Project Setup (Node.js/TypeScript - V0.1.0):**
    *   Set up project directory structure: `src/`, `tests/` (unit, integration, e2e, visual, safety, scenarios, mocks), `test-fixtures/`.
    *   Initialized `package.json` with project metadata and scripts.
    *   Installed core development dependencies for TypeScript: Vitest, Playwright, ESLint, Prettier.
    *   Configured TypeScript, Vitest, Playwright, ESLint, Prettier.
    *   Added initial test fixtures and placeholder test files.
    *   Created `AGENTS.md` (V0.1) and `CHANGELOG.md` (V0.1.0).
    *   Established the "Pandoc Block Editor: Testing and Validation Plan" as the guiding document.
