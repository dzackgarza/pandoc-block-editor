# AGENTS.md - Pandoc Block Editor Project (Python Streamlit Version)

**Document Version:** 0.2.0
**Date:** July 26, 2024

## Introduction

Welcome, fellow AI agent! This document provides guidance for working on the **Python Streamlit version** of the Pandoc Block Editor project. Its purpose is to ensure consistency and adherence to the project's goals and testing philosophy, now adapted for a Python environment.

## Project Overview

The Pandoc Block Editor is an application designed for editing Markdown documents with a block-based approach. This version is built using Python and Streamlit. It aims to feature a dual-pane interface (editor/preview) and relies on Pandoc for rendering Markdown and LaTeX content. Key priorities are user experience, rendering accuracy, and data integrity.

## Versioning

This `AGENTS.md` corresponds to **Project Version V0.2.0**. Updates to this document will increment its version number.

## Core Directives for Agents

1.  **Testing is Paramount (Python Adaptation):**
    *   Adhere to the testing philosophy outlined in the "Pandoc Block Editor: Testing and Validation Plan" (provided in the initial project setup task), adapting its principles for Python.
    *   All new features MUST be accompanied by comprehensive tests:
        *   **Unit/Integration Tests:** Use `pytest`. Place tests in `tests/unit/` and `tests/integration/`.
        *   **E2E/UI Tests:** Use `pytest-playwright` (Playwright for Python). Place tests in `tests/e2e/`.
    *   Prioritize data safety and round-trip integrity tests (Python implementations).
    *   Ensure all tests pass before submitting changes (`pytest tests/`).
    *   Utilize the test structure in the `tests/` directory.

2.  **Understand the Block Model (Conceptual):**
    *   While the implementation details will differ from a JS version, the conceptual "EditorBlock" or an equivalent Python data structure representing Markdown content remains central.
    *   Changes should maintain the integrity of this data structure and its correct serialization back to Markdown.

3.  **Pandoc Integration (Python):**
    *   Rendering logic will rely on Pandoc. Determine if this is via a Python library (e.g., `pypandoc`) or direct `subprocess` calls to the Pandoc CLI.
    *   Mocking this Pandoc interaction will be crucial for testing. Plan for a Python equivalent of a `PandocService` and its mock.

4.  **Streamlit Application Flow:**
    *   The main application is `main.py` using Streamlit.
    *   Understand Streamlit's execution model and how state is managed when designing features and tests.
    *   UI interactions will be tested via Playwright.

5.  **File Operations:**
    *   "Open from Disk" and "Save to Disk" (or equivalent Streamlit upload/download mechanisms) are critical. Ensure these operations are robust and preserve content accurately.
    *   Pay special attention to the reconstruction of Markdown from the internal Python data structures.

6.  **Cross-References (`\cref`, `\label`):**
    *   Handle these LaTeX commands carefully. The source integrity of these commands is crucial. Refer to the testing plan for expected preview behavior.

7.  **Code Style and Quality (Python):**
    *   Follow PEP 8 guidelines.
    *   Use `black` for code formatting. Run `black .` before submitting.
    *   Use `pylint` for linting. Run `pylint src/ tests/ main.py` and address issues. Configuration is in `pyproject.toml`.
    *   Write clear, maintainable, and well-documented Python code with type hints.

8.  **Changelog:**
    *   After successfully implementing and testing a feature or significant fix, update `docs/CHANGELOG.md` with a concise description of the changes, attributing them to the correct version.

9.  **Virtual Environment and Dependencies:**
    *   This project uses a `.venv` virtual environment. Activate it using `source .venv/bin/activate`.
    *   Manage dependencies in `requirements.txt`. After installing new packages, regenerate the file using `pip freeze > requirements.txt`.

10. **Communication:**
    *   If requirements are unclear or you encounter significant roadblocks, use `request_user_input`.
    *   Clearly articulate your plan using `set_plan` and provide updates with `plan_step_complete`.

## Getting Started (V0.2.0)

*   The project structure has been overhauled for Python and Streamlit.
*   Core dependencies (`streamlit`, `pytest`, `playwright`, `pylint`, `black`) are listed in `requirements.txt`.
*   A virtual environment should be active (`source .venv/bin/activate`).
*   Basic placeholder files: `main.py`, `src/app_logic.py`, `tests/unit/test_app_logic.py`, `tests/e2e/test_main_app.py`.
*   Linters and formatters are configured via `pyproject.toml`.
*   Run the app with `streamlit run main.py`.

Your primary goal is to build upon this foundation, implementing features and tests as per the project's testing and validation plan, adapted for the Python/Streamlit stack.

Good luck!
