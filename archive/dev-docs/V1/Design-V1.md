Pandoc Block Editor: Design Document (Imaginary Version)
Version: Imaginary, based on specifications provided on July 26, 2024
Project Goal (Inferred): To provide a web-based, Pandoc-powered editor for structured Markdown documents, particularly for academic and technical writing. The application emphasizes a block-based editing experience where raw Markdown input blocks are directly paired with their live, Pandoc-rendered HTML previews, focusing on visual alignment and synchronized scrolling. File operations are handled via "disk" (local storage for persistence, and simulated local file system interaction for open/save).
1. Introduction & Overview
The application is a Markdown editor designed around the concept of "paired blocks." It leverages Pandoc for rendering individual blocks of content, providing a live preview alongside the raw Markdown input. The primary interface is a two-pane layout:
Editor Pane (Left): Contains a sequence of input widgets, each corresponding to a block of Markdown from the document.
Preview Pane (Right): Displays the Pandoc-rendered HTML output for each corresponding block from the editor pane.
The core philosophy is to treat the document as a series of distinct, editable blocks, allowing users to focus on specific sections while seeing an immediate, accurately rendered preview.
2. Core UI Components and Functionality
2.1. Main Content Area (Document Editor & Preview)
This is the central workspace.
Header Controls:
"Open from Disk" Button: (Imagined Feature) Initiates a process to allow the user to select a Markdown file from their local "disk." The content of this file populates the editor.
"Save to Disk" Button: (Imagined Feature) Gathers the raw Markdown from all current editor blocks, concatenates them, and initiates a download of this content as a .md file to the user's local "disk."
"Add Block" Button: Appends a new, empty block to the end of the document structure. This new block provides a fresh Markdown input area in the editor pane and a corresponding placeholder in the preview pane.
Document Flow Area (#document-flow-area):
Visuals: This area displays a sequence of "paired block rows." Each row contains an editor widget (raw Markdown input) on the left and its corresponding rendered HTML preview on the right. Blocks are top-aligned to ensure the start of the raw Markdown visually corresponds with the start of its rendered output.
Behavior:
Paired Blocks:
Editor Component (Left):
Displays an "Editor ID" for the block.
Provides a contenteditable area for raw Markdown input.
The content here is plain Markdown.
Viewer Component (Right):
Displays a "Viewer ID" matching the editor's block ID.
Shows the Pandoc-rendered HTML output for that block's Markdown content.
Mathematical expressions (LaTeX) within the Markdown are typeset by MathJax.
Code blocks within the Markdown are syntax-highlighted by Pandoc.
(Imagined) Standard LaTeX environments like \begin{figure}...\end{figure} found in the Markdown are rendered appropriately (e.g., as styled blocks or image placeholders if applicable).
Live Rendering: Changes made in an editor widget trigger a re-render (debounced) of its corresponding viewer widget.
Scroll-Syncing: Scrolling in the editor pane attempts to keep the corresponding blocks in the preview pane in view, and vice-versa. The synchronization is based on the paired block structure.
3. Core Features & Functionality
3.1. Document Editing and Structuring (Block-Based)
The application views and manages a document as an ordered sequence of "Editor Blocks."
EditorBlock Representation:
Each EditorBlock internally holds:
id: A unique identifier.
kind: Categorizes the block, e.g., 'semantic' (for fenced divs), 'heading', or 'paragraph' (for general content).
content: The raw Markdown string for that block.
attributes (for 'semantic'/'heading' blocks): Key-value pairs extracted from Pandoc AST (e.g., from fenced div attributes or heading attributes).
level (for 'heading' blocks): The heading level.
Input Format & Parsing into Blocks (on "Open from Disk"):
The raw Markdown from the opened file is processed by pandocService.parseToAst to get a full Pandoc Abstract Syntax Tree (AST).
This AST's blocks array is traversed:
Pandoc Header elements become EditorBlocks of kind: 'heading'. The ID, level, and inline content (converted back to a Markdown string) are extracted.
Pandoc Div elements (representing any fenced div, e.g., ::: {.myclass attr="val"} or just :::) become EditorBlocks of kind: 'semantic'. The ID, classes (the first class might be used as a blockType), attributes, and inner Pandoc blocks (converted back to a Markdown string for content) are extracted.
Any other Pandoc block elements (e.g., Para, BulletList, CodeBlock that are not inside a Div) are grouped or individually converted into EditorBlocks of a generic kind (e.g., kind: 'paragraph' or kind: 'content'). Their raw Markdown representation is generated using pandocService.convertAstToMarkdown on that specific AST block.
3.2. Live Preview with Pandoc & MathJax
The right-hand viewer component of each paired block provides a live, rendered preview.
Pandoc Conversion per Block:
When an editor widget's content changes, its raw Markdown string (block.content) is taken.
This Markdown string is individually processed by pandocService.parseToAst to get an AST fragment for just that block.
This AST fragment is then converted to HTML using pandocService.convertAstToHtml. This call includes options like --mathjax and --highlight-style pygments.
Error Handling within a Block: If Pandoc fails to parse or convert the Markdown for a specific block (e.g., due to severely malformed Markdown within that block's content), an error message is displayed in that block's viewer component. Other blocks in the document remain unaffected and continue to render normally.
MathJax Typesetting: After new HTML for a block is inserted into its viewer component, MathJax.typesetPromise() is called on that specific component (or a broader scope if necessary) to render any LaTeX mathematics.
Syntax Highlighting: Pandoc's --highlight-style pygments handles syntax highlighting for code segments within the Markdown of a block.
(Imagined) LaTeX figure Environment Rendering: If Markdown like \begin{figure}...\end{figure} is present in a block's content, the Pandoc conversion process (potentially with specific extensions or filters, though not detailed in current pandoc.service.ts) would aim to produce a recognizable HTML structure, styled to represent a figure.
3.3. Paired Block Management
Block Identification: Each EditorBlock (and its corresponding editor/viewer UI) is associated with a unique ID. This ID is crucial for matching the editor input to its preview, for scroll-syncing, and for managing updates. These IDs are typically embedded as HTML id attributes in the rendered output by Pandoc (e.g., from {#my-id} syntax in Markdown).
Adding Blocks: Clicking "Add Block" appends a new EditorBlock to the internal documentEditorBlocks array (e.g., a default empty semantic block :::\n\n::: or just an empty paragraph). This triggers a re-render of the document flow, adding a new paired row.
Visual Alignment: CSS ensures that the top of an editor widget is aligned with the top of its corresponding viewer widget.
3.4. File Operations (Imagined Features)
"Open from Disk":
User is prompted to select a .md file.
The file content (a single Markdown string) is read.
This string is parsed into the documentEditorBlocks array as described in section 3.1.
The document-flow-area is populated with paired editor/viewer widgets for these blocks.
"Save to Disk":
The application iterates through the documentEditorBlocks array.
For each EditorBlock, its current raw Markdown content (from the editor widget) is retrieved.
These Markdown strings are concatenated in order, typically with double newlines (\n\n) as separators, to reconstruct the full document's Markdown. (Specific syntax for headings and fenced divs is reconstructed from block properties, e.g., #{level} content {#id} for headings, ::: {#id .type}\ncontent\n::: for semantic blocks).
The resulting single Markdown string is offered to the user as a .md file download.
3.5. Persistence (Session Continuity)
Autosave to "Disk" (Local Storage): The current state of documentEditorBlocks (specifically, their raw Markdown content and structural information like ID, kind, type) is periodically saved to the browser's local storage.
Restore from "Disk": On application load, if persisted data is found in local storage, the documentEditorBlocks are reconstructed from this data, allowing the user to resume their previous session.
4. Rendering Algorithm & Block Parsing (Deep Dive)
The core of the application's unique editing experience lies in how it segments the document and renders blocks.
Initial Segmentation (parseMarkdownToEditorBlocks):
A full Markdown document string is first parsed by pandocService.parseToAst into a complete Pandoc AST.
The ast.blocks array is iterated:
Header AST nodes: Directly map to EditorBlock with kind: 'heading'. Content is derived by converting the header's inline AST elements back to Markdown. The ID is taken from the header's attributes or generated.
Div AST nodes: These represent fenced divs. All Divs are treated as distinct semantic units and map to EditorBlock with kind: 'semantic'.
The id is taken from the Div's attributes or generated.
The first class in the Div's class list can be stored as block.blockType.
All attributes ([key, value] pairs) from the Div are stored in block.attributes.
The content of this EditorBlock is generated by passing the Div's inner Pandoc blocks to pandocService.convertAstToMarkdown. This ensures the content within the ::: ::: is preserved as Markdown.
Content Outside Fenced Divs (and not Headings): Any other top-level Pandoc AST blocks (e.g., Para, BulletList, BlockQuote, CodeBlock if not already wrapped in a Div) are treated as individual EditorBlocks.
A new ID is generated for each.
They might be assigned a kind: 'paragraph' or a generic kind: 'semantic' with blockType: 'remark' (or similar default).
Their content is the Markdown obtained by passing that single AST block to pandocService.convertAstToMarkdown. This ensures that even standalone paragraphs or lists are treated as manageable blocks.
Rendering a Single Block's Preview:
The raw Markdown string from editorBlock.content is the source.
This string is passed to pandocService.convertAstToHtml(await pandocService.parseToAst(markdownContentOfBlock), null).
The key is that Pandoc processes this fragment of Markdown. Because it's Pandoc, it correctly handles all standard Markdown syntax, LaTeX math (with --mathjax), code blocks (with highlighting), etc., within that block.
Pandoc's AST processing ensures that attributes (like IDs) on elements within the block's Markdown are preserved in the resulting HTML, facilitating styling and potential future interactions.
If parseToAst or convertAstToHtml fails for this specific block's content (e.g., due to an unrecoverable syntax error in that block's Markdown that Pandoc cannot handle even leniently), the catch block for this operation populates the corresponding viewer component with an error message specific to that block. The rest of the document rendering proceeds.
Reconstructing Full Document for "Save to Disk":
The collectMarkdownFromEditorBlocks() function iterates documentEditorBlocks.
For heading blocks: '#'.repeat(level) + content + {#id}.
For semantic blocks (originally from Divs or other content): ::: {#id .blockType attr="val"}\ncontent\n::: (attributes are iterated and added). If it was a generic paragraph block, it might just output its content directly if it doesn't need wrapping. The system aims to reproduce Pandoc-parsable Markdown.
5. Key User Workflows
Application Startup:
Pandoc service initializes.
Application attempts to load documentEditorBlocks from "disk" (local storage).
If not found, a default empty document (perhaps one empty block) is created.
The document-flow-area is rendered with editor/viewer pairs.
Opening a File from "Disk":
User clicks "Open from Disk".
(Simulated) File picker appears. User selects a .md file.
File content is read.
Markdown is parsed into documentEditorBlocks.
document-flow-area is re-rendered.
Editing Content in a Block:
User focuses on a contenteditable Markdown input area for a block.
User types/modifies Markdown.
On input (debounced), only that block's corresponding viewer component is re-rendered using its new Markdown content. MathJax re-typesets if needed for that block.
Adding a New Block:
User clicks "Add Block".
A new default EditorBlock is added to the documentEditorBlocks array.
The document-flow-area is re-rendered to include the new paired editor/viewer row.
Saving the Document to "Disk":
User clicks "Save to Disk".
Raw Markdown is collected from all editor blocks and reconstructed into a single string.
(Simulated) File download prompt appears for a .md file with the reconstructed Markdown.
The current documentEditorBlocks are also saved to "disk" (local storage) for session persistence.
6. Styling and Visuals
Theme: A dark theme is applied for comfortable long-form writing.
Paired Block Aesthetics:
Clear visual separation between the editor (left) and viewer (right) components within each row.
Top-alignment is critical: The first line of Markdown in an editor widget should visually align horizontally with the first line of its rendered output in the viewer widget. Padding and margins are carefully managed to achieve this.
Subtle borders or background differences enhance the distinction of paired rows.
Editor and Viewer IDs are displayed for clarity and debugging.
This revised design document reflects the specified emphasis on block-based editing, local file "disk" operations, and the core rendering mechanics based on processing individual Markdown blocks through Pandoc's AST pipeline.
