
# Pandoc Block Editor: Testing and Validation Plan

**Document Version:** 1.0
**Date:** July 26, 2024
**Target App Version:** "Imaginary" Pandoc Block Editor (as per specifications emphasizing block-based editing, local file I/O, and specific rendering logic)

## 1. Introduction

This document outlines the testing and validation strategy for the Pandoc Block Editor. The primary goals of this plan are to:

1.  **Ensure User Expectation Alignment:** Verify that the application's editing features and live rendering behave as intuitively expected by a user familiar with Markdown and LaTeX.
2.  **Guarantee Rendered Content Correctness:** Validate that Markdown and embedded LaTeX are rendered accurately in the preview pane, with special attention to mathematical expressions, structural elements, and cross-referencing commands like `\cref`.
3.  **Prioritize Application Safety & Data Integrity:** Establish a high level of confidence that the application will not corrupt, mangle, or lose user document data during open, edit, or save operations.

This plan is tailored to the "imaginary" version of the application, which emphasizes a block-based, dual-pane (editor/preview) interface, local "disk" file operations, and a specific Pandoc AST-driven rendering pipeline.

## 2. Testing Philosophy

*   **User-Centric:** Tests will be designed around user workflows and expected outcomes.
*   **Block as the Unit:** The "paired block" (raw Markdown input and its rendered HTML output) is a fundamental unit for many tests.
*   **Safety First:** Preventing data loss or corruption is paramount. Rigorous testing of file I/O and content transformation is critical.
*   **Correctness over Completeness (for Unresolved Externals):** For features like `\cref` to external documents, the preview should render them gracefully (e.g., as text `\cref{label_name} [unresolved]`) rather than breaking or misinterpreting the source. The source integrity of such commands must be maintained.
*   **Iterative Testing:** Testing will be an ongoing activity throughout development, aligned with feature implementation.

## 3. Types of Testing

*   **Unit Tests:**
    *   **Scope:** Individual functions, modules, and classes.
    *   **Examples:** Markdown-to-`EditorBlock` parsing logic, `EditorBlock`-to-Markdown reconstruction, Pandoc service call wrappers (mocking actual Pandoc), utility functions.
*   **Integration Tests:**
    *   **Scope:** Interactions between components.
    *   **Examples:** Editing a block's Markdown and verifying the preview update via Pandoc, testing the "Add Block" functionality from UI to internal state to render.
*   **End-to-End (E2E) / UI Tests:**
    *   **Scope:** Simulating full user workflows through the UI.
    *   **Examples:** Opening a file, editing multiple blocks, adding new blocks, observing scroll-sync and top-alignment, saving the file, and verifying the saved content.
*   **Visual Regression Tests:**
    *   **Scope:** Detecting unintended changes in the visual appearance of rendered blocks.
    *   **Tools:** (To be decided, e.g., Playwright with image comparison, Percy, Applitools).
    *   **Examples:** Ensuring consistent rendering of headings, semantic blocks, math, and code blocks across changes.
*   **Safety and Data Integrity Tests:**
    *   **Scope:** Focused on the robustness of file operations and content handling to prevent data loss or corruption.
    *   **Examples:** Round-trip testing (load -> save -> load -> compare), testing with malformed Markdown, large files, rapid edits.
*   **User Expectation Alignment Tests (Scenario-Based):**
    *   **Scope:** Based on specific user stories and expected behaviors for common academic writing tasks.
    *   **Examples:** "User edits a LaTeX equation in a block; preview updates immediately and correctly," "User adds a new theorem block; it appears correctly styled in the preview."

## 4. Key Areas to Test

### 4.1. Block-Based Editing & UI Interaction

*   **Paired Block Rendering:**
    *   Each raw Markdown input block in the editor pane has a corresponding, correctly rendered HTML preview block.
    *   Editor and Viewer block IDs are correctly assigned and match.
*   **Live Rendering:**
    *   Changes in an editor block's Markdown trigger a (debounced) re-render of its corresponding preview block *only*.
    *   Rendering is accurate for various Markdown constructs.
*   **Visual Alignment:**
    *   The top of an editor input area is visually aligned with the top of its rendered content in the preview.
*   **Scroll-Syncing:**
    *   Scrolling in the editor pane brings corresponding preview blocks into view, and vice-versa. Test with documents of various lengths and block sizes.
*   **Adding Blocks:**
    *   "Add Block" button correctly appends a new, default `EditorBlock` to the internal structure and renders a new paired row in the UI.

### 4.2. Markdown Parsing & `EditorBlock` Representation

*   **Input Format Parsing:**
    *   Correct parsing of various Markdown elements (headings, all fenced div types, paragraphs, lists, code blocks, tables, horizontal rules, blockquotes) into the internal `EditorBlock[]` structure.
    *   Accurate extraction of `id`, `kind`, `content`, `attributes` (for semantic/heading), and `level` (for heading) for each block.
*   **Handling Content Outside Fenced Divs:**
    *   Paragraphs, lists, etc., not within explicit `:::` blocks are correctly identified and encapsulated as their own `EditorBlock`s (e.g., `kind: 'paragraph'`).
*   **Attribute Extraction:**
    *   Attributes from fenced divs (e.g., `{.myclass title="My Title"}`) and heading IDs (`{#my-heading}`) are correctly parsed into `block.attributes`.

### 4.3. Rendering Logic (Pandoc AST -> HTML per Block)

*   **Standard Markdown Elements:** Correct HTML rendering for paragraphs, lists (ordered/unordered, nested), bold, italic, links, images (placeholders if not embedded).
*   **LaTeX Math Rendering:**
    *   Inline math (`$...$`, `\(...\)`) and display math (`$$...$$`, `\[...\]`) are correctly typeset by MathJax.
    *   Common LaTeX math environments (`equation`, `align`, `pmatrix`, `cases`, etc.) are rendered correctly by MathJax.
*   **(Imagined) LaTeX `figure` Environment:**
    *   Verify that Markdown containing `\begin{figure}...\end{figure}` (if supported by Pandoc setup for HTML preview) renders as a styled block or placeholder.
*   **Syntax Highlighting:**
    *   Fenced code blocks are correctly syntax-highlighted according to their specified language.
*   **Malformed Markdown within a Block:**
    *   If a single `EditorBlock` contains severely malformed Markdown that Pandoc cannot parse for HTML conversion:
        *   An error message is displayed *within that specific block's preview component*.
        *   Other blocks in the document continue to render normally.
        *   The application remains stable.
        *   The malformed raw Markdown is preserved in the editor component for correction.
*   **Semantic Block Rendering (Fenced Divs):**
    *   All Pandoc `Div` elements (from `:::`) are rendered as visually distinct semantic blocks in the preview.
    *   Styling reflects the block's type/class.

### 4.4. Cross-References (`\cref`, `\label`, etc.)

*   **`\label` Handling:**
    *   `\label{some-label}` in the Markdown source is preserved.
    *   It does not cause rendering errors in the preview.
    *   The label text itself might be made visible in the preview near its definition for user convenience (e.g., a small tag "label: some-label").
*   **`\cref` (and `\ref`, etc.) Rendering in Preview:**
    *   The raw TeX command `\cref{some-label}` in Markdown source **must not** be wrapped in extraneous tags like `<code>...</code>` or `....{=tex}` spans by Pandoc in the HTML preview. It should be passed through as text or recognized by MathJax if it's a MathJax-supported macro.
    *   **Preview Behavior:**
        *   **If `some-label` is defined in the *current document*:** Render as "cref(some-label)" or similar, ideally making "some-label" the actual text/number if resolvable by a simplified client-side pass (advanced).
        *   **If `some-label` is undefined or presumed external:** Render as "cref(some-label) [unresolved]" or just the literal text `\cref{some-label}`. The key is graceful display without breaking the preview or altering the source.
*   **Source Integrity:** Editing around `\cref` or `\label` commands does not corrupt them.

### 4.5. File Operations ("Open from Disk" / "Save to Disk")

*   **Open from "Disk":**
    *   Successfully loads a valid `.md` file.
    *   Correctly parses the Markdown into the `documentEditorBlocks` array structure.
    *   Populates the editor and preview panes accurately.
    *   Handles empty files or files with unusual (but valid) Markdown.
*   **Save to "Disk":**
    *   Correctly reconstructs the full, raw Markdown string from the current `documentEditorBlocks` state.
    *   The saved Markdown accurately reflects all content and structural changes made by the user.
    *   Generated Markdown for headings (`#{level} ... {#id}`) and semantic blocks (`::: {#id .type attr="val"}...:::`) is correct and Pandoc-parsable.
    *   Content from generic blocks (paragraphs, lists) is included correctly.
    *   The "Save" operation successfully triggers a file download with the correct content and `.md` extension.
*   **File Operation Errors:** (While the "imaginary" spec de-emphasizes error handling, basic file I/O errors should be considered for stability)
    *   Graceful handling if a selected file for "Open" is unreadable (though browser handles this mostly).

### 4.6. Safety and Data Integrity (Crucial)

*   **Round-Trip Integrity:**
    1.  Load a complex Markdown document.
    2.  Save it immediately without changes. Verify the saved content is identical to the original.
    3.  Load the saved document. Verify the internal `EditorBlock` structure is identical (or semantically equivalent) to the initially loaded structure.
    4.  Make a minor edit to one block. Save.
    5.  Load the newly saved document. Verify only the edited block's content changed, and the rest of the document structure/content remains identical to the state before the minor edit.
*   **No Data Mutilation:**
    *   Ensure that non-standard or complex Markdown/LaTeX constructs that the editor might not fully "understand" for interactive editing are still preserved verbatim in the raw Markdown `content` of blocks and correctly saved.
    *   The application should never "interpret" and then "re-serialize" Markdown in a way that loses information or changes semantics unintentionally, especially for raw LaTeX snippets.
*   **Handling of Large Files:** Test with reasonably large Markdown files (e.g., 500KB, 1MB) to check for performance issues during load, edit, and save that might lead to data corruption if operations are interrupted.
*   **Robustness Against Malformed Input:**
    *   While individual blocks can show errors, the overall application should not crash when loading/editing documents with malformed Markdown.
    *   Saving a document containing a block with malformed Markdown should save the malformed Markdown as-is within that block's content.

## 5. Test Fixtures and Scaffolding

### 5.1. Sample Markdown Documents (`test-fixtures/` directory)

A suite of `.md` files is essential:

*   `empty.md`: An empty file.
*   `simple_paragraph.md`: Single paragraph of text.
*   `headings.md`: Various levels of headings, with and without explicit IDs.
*   `fenced_divs_simple.md`: Basic fenced divs with different class names.
*   `fenced_divs_attributes.md`: Fenced divs with various attributes (title, custom keys).
*   `fenced_divs_nested.md`: Nested fenced divs.
*   `content_outside_divs.md`: Document with paragraphs, lists, etc., interspersed with fenced divs.
*   `lists_tables.md`: Complex nested lists (ordered/unordered) and various table syntaxes.
*   `code_blocks.md`: Fenced code blocks with different languages, indented code blocks.
*   `math_inline.md`: Various inline LaTeX math examples.
*   `math_display.md`: Various display LaTeX math examples (`$$...$$`, `\[...\]`).
*   `math_environments.md`: LaTeX environments like `align`, `equation`, `pmatrix`, `cases`.
*   `latex_figure_env.md`: (If `\figure` support is being tested) Markdown with `\begin{figure}...\end{figure}`.
*   `cross_references.md`: Document with `\label{...}` definitions and `\cref{...}`, `\ref{...}` calls, including some to non-existent labels.
*   `malformed_block_content.md`: A document where one block contains intentionally broken Markdown syntax (e.g., unclosed list, unterminated fenced block).
*   `mixed_complex_document.md`: A large document combining many of the above features (similar to `defaultunitdoc.md` or `backend/defaultdoc.md`).
*   `very_long_document.md`: For scroll-sync and performance testing.

### 5.2. Mocking Strategy

*   **`PandocService` Mock:**
    *   For unit/integration tests of frontend logic.
    *   Allows mocking `parseToAst` and `convertAstToHtml` to return predefined ASTs or HTML strings, isolating UI logic from actual Pandoc WASM execution.
    *   Can simulate Pandoc errors for specific inputs.
*   **Browser API Mocks:**
    *   `localStorage` mock for testing autosave/restore persistence logic.
    *   DOM manipulation mocks (if not using a full E2E framework like Playwright which handles a real browser environment). `document.getElementById`, `createElement`, `contenteditable` behavior, event dispatching.

### 5.3. Test Data Generators

*   Functions to programmatically create `EditorBlock[]` arrays with specific configurations.
*   Functions to generate complex Markdown strings for specific test cases.

### 5.4. Assertion Helpers

*   `expectEditorBlocksToMatch(actual: EditorBlock[], expected: EditorBlock[])`: Deep comparison of block arrays.
*   `expectRenderedHtmlToContain(blockId: string, expectedSubstring: string)`: Checks preview output for a specific block.
*   `expectBlockAlignment(editorBlockEl: HTMLElement, viewerBlockEl: HTMLElement)`: Checks visual top-alignment.
*   `expectRawMarkdown сохранен(savedMarkdown: string, originalBlocks: EditorBlock[])`: Verifies saved Markdown accurately represents block state.

## 6. Features to Enhance Testability & Safety

While the "imaginary" spec de-emphasizes some user feedback, these features can be built with testing and safety as primary drivers:

*   **Internal Consistency Checks:**
    *   Periodic checks (e.g., during debounced rendering) to ensure `documentEditorBlocks` maintains a valid state (e.g., unique IDs, valid `kind`). Log errors aggressively if inconsistencies are found.
*   **"View Reconstructed Markdown" Debug Feature:**
    *   A developer/debug tool to display the complete Markdown string that *would be saved* based on the current `documentEditorBlocks` state, without actually triggering a download. Useful for verifying the `collectMarkdownFromEditorBlocks` logic.
*   **Strict Mode for Pandoc Parsing (Optional/Debug):**
    *   Allow configuring the `PandocService` to use stricter Pandoc parsing options during testing to catch more subtle Markdown issues early.
*   **Block-Level Hash/Checksum (Advanced):**
    *   For round-trip testing, store a hash of each block's raw Markdown content upon loading.
    *   When saving and re-loading, if a block was not touched by the user, its hash should remain the same. This can detect unintentional modifications by the application.
*   **Backup on Save (Simple Local Storage):**
    *   Before "Save to Disk" overwrites a conceptual "current file" in local storage (if implementing session persistence this way), save the *previous* version to a different key (e.g., `filename.md.backup`). This provides a single-step undo for catastrophic save issues.

## 7. Test Execution and Reporting

*   **Automated Tests:** Unit and integration tests should be runnable via CLI scripts (e.g., `npm test`).
*   **CI Integration:** Automated tests should run in a Continuous Integration environment (e.g., GitHub Actions) on every push/PR.
*   **E2E Test Framework:** (To be selected, e.g., Playwright, Cypress). E2E tests will cover key user flows.
*   **Manual Testing Checklist:** For features difficult to automate or requiring subjective visual/usability checks, a manual testing checklist will be maintained.

By implementing this testing and validation plan, we aim to build a Pandoc Block Editor that is reliable, correct, and, most importantly, safe for users to entrust with their valuable academic documents.

