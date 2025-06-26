#!/usr/bin/env python3
"""
PyQt6-based Pandoc Block Editor with custom syntax highlighting.
Replaces the Streamlit version to eliminate height restrictions and provide
professional-grade text editing capabilities.
"""

import sys
import time
import json
import os
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QScrollArea, QFrame, QLabel, QPushButton,
    QMenuBar, QFileDialog, QMessageBox, QToolBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import (
    QFont, QFontMetrics, QTextCharFormat, QColor, QSyntaxHighlighter, 
    QTextDocument, QAction, QKeySequence
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Import our existing pandoc utilities
import pandoc_utils


class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    """Custom syntax highlighter for Markdown with beautiful colors."""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self.setup_highlighting_rules()
        
    def setup_highlighting_rules(self):
        """Setup syntax highlighting rules for Markdown."""
        # Heading formats
        self.heading_formats = {}
        colors = ['#1f2937', '#374151', '#4b5563', '#6b7280', '#9ca3af', '#d1d5db']
        
        for i in range(1, 7):
            format = QTextCharFormat()
            format.setForeground(QColor(colors[i-1]))
            format.setFontWeight(QFont.Weight.Bold)
            format.setFontPointSize(16 - i)
            self.heading_formats[f'h{i}'] = format
        
        # Bold and italic
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Weight.Bold)
        self.bold_format.setForeground(QColor('#111827'))
        
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(QColor('#374151'))
        
        # Code blocks and inline code
        self.code_format = QTextCharFormat()
        self.code_format.setBackground(QColor('#f3f4f6'))
        self.code_format.setForeground(QColor('#dc2626'))
        self.code_format.setFontFamily('Monaco, Menlo, Ubuntu Mono, monospace')
        
        # Links
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor('#3b82f6'))
        self.link_format.setFontUnderline(True)
        
        # Blockquotes
        self.quote_format = QTextCharFormat()
        self.quote_format.setForeground(QColor('#6b7280'))
        self.quote_format.setFontItalic(True)
        
        # Lists
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor('#4b5563'))
    
    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to a block of text."""
        if not text:
            return
            
        # Headings
        if text.startswith('#'):
            level = 0
            for char in text:
                if char == '#':
                    level += 1
                else:
                    break
            if level <= 6 and level > 0:
                self.setFormat(0, len(text), self.heading_formats[f'h{level}'])
                return
        
        # Code blocks
        if text.startswith('```'):
            self.setFormat(0, len(text), self.code_format)
            return
        
        # Blockquotes
        if text.startswith('>'):
            self.setFormat(0, len(text), self.quote_format)
            return
        
        # Lists
        if text.lstrip().startswith(('- ', '* ', '+ ')) or text.lstrip()[:1].isdigit():
            if '. ' in text[:10]:  # Numbered list
                self.setFormat(0, len(text), self.list_format)
                return
            elif text.lstrip().startswith(('- ', '* ', '+ ')):  # Bullet list
                self.setFormat(0, len(text), self.list_format)
                return
        
        # Inline formatting
        self.highlight_inline_formatting(text)
    
    def highlight_inline_formatting(self, text: str) -> None:
        """Highlight inline markdown formatting like bold, italic, code, links."""
        import re
        
        # Inline code `code`
        for match in re.finditer(r'`([^`]+)`', text):
            self.setFormat(match.start(), match.end() - match.start(), self.code_format)
        
        # Bold **text** or __text__
        for match in re.finditer(r'\*\*(.+?)\*\*|__(.+?)__', text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)
        
        # Italic *text* or _text_
        for match in re.finditer(r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)', text):
            self.setFormat(match.start(), match.end() - match.start(), self.italic_format)
        
        # Links [text](url)
        for match in re.finditer(r'\[([^\]]+)\]\([^)]+\)', text):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)


class BlockEditor(QTextEdit):
    """Individual block editor with perfect size fitting."""
    
    contentChanged = pyqtSignal(str, str)  # block_id, content
    
    def __init__(self, block_id: str, content: str = "", parent=None):
        super().__init__(parent)
        self.block_id = block_id
        self.setPlainText(content)
        
        # Setup editor properties
        self.setup_editor()
        
        # Setup syntax highlighting
        self.highlighter = MarkdownSyntaxHighlighter(self.document())
        
        # Connect change signals
        self.textChanged.connect(self.on_text_changed)
        
        # Auto-resize to content
        self.auto_resize_timer = QTimer()
        self.auto_resize_timer.setSingleShot(True)
        self.auto_resize_timer.timeout.connect(self.resize_to_content)
        self.textChanged.connect(lambda: self.auto_resize_timer.start(100))
        
        # Initial resize
        QTimer.singleShot(50, self.resize_to_content)
    
    def setup_editor(self):
        """Configure the text editor appearance and behavior."""
        # Font
        font = QFont('Monaco', 13)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # No scrollbars - we'll size to content
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Minimal margins
        self.setContentsMargins(4, 4, 4, 4)
        
        # Word wrap
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Styling
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background: #ffffff;
                padding: 4px;
                selection-background-color: #3b82f6;
                selection-color: white;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
        """)
    
    def resize_to_content(self):
        """Resize the editor to fit its content perfectly."""
        document = self.document()
        document.setTextWidth(self.viewport().width())
        
        # Calculate required height
        content_height = document.size().height()
        
        # Add some padding for comfort
        padding = 8
        
        # Set minimum height for empty blocks
        min_height = 30
        
        # Calculate final height
        final_height = max(min_height, int(content_height + padding))
        
        # Set the height
        self.setFixedHeight(final_height)
    
    def on_text_changed(self):
        """Handle text changes."""
        content = self.toPlainText()
        self.contentChanged.emit(self.block_id, content)


class BlockContainer(QFrame):
    """Container for a single block with ID and editor."""
    
    deleteRequested = pyqtSignal(str)  # block_id
    
    def __init__(self, block_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.block_data = block_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the block container UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        
        # Block ID label - tiny and compact
        id_label = QLabel(f"Block ID: {self.block_data['id']}")
        id_label.setStyleSheet("""
            color: #9ca3af;
            font-size: 8px;
            font-family: Monaco, monospace;
            margin: 0;
            padding: 1px 3px;
        """)
        layout.addWidget(id_label)
        
        # Block editor
        self.editor = BlockEditor(
            self.block_data['id'], 
            self.block_data['content']
        )
        layout.addWidget(self.editor)
        
        self.setLayout(layout)
        
        # Styling
        self.setStyleSheet("""
            BlockContainer {
                background: white;
                border-radius: 6px;
                margin: 2px;
                border: 1px solid #e5e7eb;
            }
        """)


class PreviewPane(QWebEngineView):
    """HTML preview pane using WebEngine for perfect rendering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_preview()
    
    def setup_preview(self):
        """Setup the preview pane."""
        # Basic styling for the preview
        self.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background: white;
            }
        """)
        
        # Load initial empty content
        self.update_preview([])
    
    def update_preview(self, blocks: List[Dict[str, Any]]):
        """Update the preview with current blocks."""
        # Combine all block content
        full_content = ""
        for block in blocks:
            content = block.get('content', '').strip()
            if content:
                full_content += content + "\n\n"
        
        if not full_content.strip():
            full_content = "# Empty Document\n\nStart typing to see your content here."
        
        # Convert to HTML
        try:
            html_content = pandoc_utils.convert_markdown_to_html(full_content)
            
            # Wrap in a nice HTML template
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Preview</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                        line-height: 1.7;
                        color: #374151;
                        max-width: none;
                        margin: 16px;
                        padding: 16px;
                        background: #ffffff;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #111827;
                        font-weight: 600;
                        margin-top: 1.5rem;
                        margin-bottom: 0.5rem;
                    }}
                    h1 {{
                        border-bottom: 2px solid #e5e7eb;
                        padding-bottom: 8px;
                        font-weight: 700;
                    }}
                    p {{
                        margin-bottom: 1rem;
                    }}
                    code {{
                        background: #f3f4f6;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-size: 0.9em;
                        color: #dc2626;
                        border: 1px solid #e5e7eb;
                        font-family: Monaco, Menlo, Ubuntu Mono, monospace;
                    }}
                    pre {{
                        background: #f9fafb;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        padding: 16px;
                        overflow-x: auto;
                        font-size: 13px;
                        line-height: 1.5;
                    }}
                    pre code {{
                        background: none;
                        border: none;
                        padding: 0;
                        color: #374151;
                    }}
                    blockquote {{
                        border-left: 4px solid #3b82f6;
                        background: #eff6ff;
                        padding: 12px 16px;
                        margin: 12px 0;
                        border-radius: 0 6px 6px 0;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 1rem 0;
                    }}
                    th, td {{
                        border: 1px solid #e5e7eb;
                        padding: 8px 12px;
                        text-align: left;
                    }}
                    th {{
                        background: #f9fafb;
                        font-weight: 600;
                    }}
                </style>
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                <script>
                window.MathJax = {{
                  tex: {{
                    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                    processEscapes: true
                  }},
                  options: {{
                    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
                  }}
                }};
                </script>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            self.setHtml(full_html)
            
        except Exception as e:
            error_html = f"""
            <html><body style="font-family: monospace; color: red; padding: 20px;">
                <h3>Preview Error</h3>
                <p>Error converting markdown to HTML: {str(e)}</p>
                <pre>{full_content[:500]}...</pre>
            </body></html>
            """
            self.setHtml(error_html)


class PandocBlockEditor(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.block_containers = []
        self.current_file = None
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        
        self.setup_ui()
        self.load_default_content()
    
    def setup_ui(self):
        """Setup the main UI."""
        self.setWindowTitle("Pandoc Block Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left pane - Editor
        self.editor_pane = self.setup_editor_pane()
        splitter.addWidget(self.editor_pane)
        
        # Right pane - Preview
        self.preview_pane = PreviewPane()
        splitter.addWidget(self.preview_pane)
        
        # Set splitter ratios
        splitter.setSizes([700, 700])
        
        # Set central widget
        self.setCentralWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def setup_menu_bar(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # New
        new_action = QAction('New', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        # Open
        open_action = QAction('Open...', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Save
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # Save As
        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        # Add Block
        add_block_action = QAction('Add Block', self)
        add_block_action.setShortcut(QKeySequence('Ctrl+B'))
        add_block_action.triggered.connect(self.add_new_block)
        edit_menu.addAction(add_block_action)
    
    def setup_toolbar(self):
        """Setup the toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add Block button
        add_block_btn = QPushButton("➕ Add Block")
        add_block_btn.clicked.connect(self.add_new_block)
        toolbar.addWidget(add_block_btn)
        
        toolbar.addSeparator()
        
        # Save button
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_file)
        toolbar.addWidget(save_btn)
    
    def setup_editor_pane(self):
        """Setup the scrollable editor pane."""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create container widget
        container = QWidget()
        self.editor_layout = QVBoxLayout(container)
        self.editor_layout.setContentsMargins(8, 8, 8, 8)
        self.editor_layout.setSpacing(4)
        
        # Add stretch to push blocks to top
        self.editor_layout.addStretch()
        
        scroll_area.setWidget(container)
        
        # Styling
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f9fafb;
            }
            QWidget {
                background: #f9fafb;
            }
        """)
        
        return scroll_area
    
    def load_default_content(self):
        """Load default content into the editor."""
        default_content = """# Pandoc Block Editor

## Quick Start
Start editing your **Markdown** content here.

### Features
- Live preview with Pandoc rendering
- Block-based editing
- Math support with MathJax: $E = mc^2$

```python
# Code blocks work too
print("Hello, world!")
```

> Blockquotes and other Markdown elements render properly.

---

Ready to start editing!
"""
        
        # Parse content into blocks (reuse existing parsing logic)
        try:
            from app import parse_full_markdown_to_editor_blocks
            self.blocks = parse_full_markdown_to_editor_blocks(default_content)
        except ImportError:
            # Fallback to simple splitting
            self.blocks = self.simple_parse_to_blocks(default_content)
        
        self.rebuild_editor_ui()
        self.schedule_preview_update()
    
    def simple_parse_to_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Simple fallback parser for splitting content into blocks."""
        blocks = []
        lines = content.split('\n')
        current_block = []
        block_id = 0
        
        for line in lines:
            if line.startswith('#') and current_block:
                # New heading - save previous block
                if current_block:
                    block_content = '\n'.join(current_block).strip()
                    if block_content:
                        blocks.append({
                            'id': f'block_{block_id}',
                            'content': block_content,
                            'kind': 'paragraph'
                        })
                        block_id += 1
                current_block = [line]
            else:
                current_block.append(line)
        
        # Add final block
        if current_block:
            block_content = '\n'.join(current_block).strip()
            if block_content:
                blocks.append({
                    'id': f'block_{block_id}',
                    'content': block_content,
                    'kind': 'paragraph'
                })
        
        return blocks if blocks else [{'id': 'block_0', 'content': '', 'kind': 'paragraph'}]
    
    def rebuild_editor_ui(self):
        """Rebuild the editor UI with current blocks."""
        # Clear existing containers
        for container in self.block_containers:
            container.setParent(None)
        self.block_containers.clear()
        
        # Add blocks
        for block in self.blocks:
            container = BlockContainer(block)
            container.editor.contentChanged.connect(self.on_block_content_changed)
            container.deleteRequested.connect(self.delete_block)
            
            # Insert before the stretch
            self.editor_layout.insertWidget(
                self.editor_layout.count() - 1, 
                container
            )
            self.block_containers.append(container)
    
    @pyqtSlot(str, str)
    def on_block_content_changed(self, block_id: str, content: str):
        """Handle block content changes."""
        # Update the block data
        for block in self.blocks:
            if block['id'] == block_id:
                block['content'] = content
                break
        
        # Schedule preview update
        self.schedule_preview_update()
    
    def schedule_preview_update(self):
        """Schedule a preview update with debouncing."""
        self.update_timer.start(500)  # 500ms delay for debouncing
    
    def update_preview(self):
        """Update the preview pane."""
        self.preview_pane.update_preview(self.blocks)
    
    def add_new_block(self):
        """Add a new empty block."""
        new_id = f"block_{len(self.blocks)}"
        new_block = {
            'id': new_id,
            'content': '',
            'kind': 'paragraph'
        }
        self.blocks.append(new_block)
        
        # Add to UI
        container = BlockContainer(new_block)
        container.editor.contentChanged.connect(self.on_block_content_changed)
        container.deleteRequested.connect(self.delete_block)
        
        self.editor_layout.insertWidget(
            self.editor_layout.count() - 1, 
            container
        )
        self.block_containers.append(container)
        
        # Focus the new block
        container.editor.setFocus()
    
    def delete_block(self, block_id: str):
        """Delete a block."""
        # Remove from data
        self.blocks = [b for b in self.blocks if b['id'] != block_id]
        
        # Rebuild UI
        self.rebuild_editor_ui()
        self.schedule_preview_update()
    
    def new_document(self):
        """Create a new document."""
        if self.blocks and any(b['content'].strip() for b in self.blocks):
            reply = QMessageBox.question(
                self, 'New Document',
                'Unsaved changes will be lost. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.blocks = [{'id': 'block_0', 'content': '', 'kind': 'paragraph'}]
        self.current_file = None
        self.rebuild_editor_ui()
        self.schedule_preview_update()
        self.setWindowTitle("Pandoc Block Editor")
    
    def open_file(self):
        """Open a markdown file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Markdown File', '', 'Markdown Files (*.md *.markdown);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse content into blocks
                try:
                    from app import parse_full_markdown_to_editor_blocks
                    self.blocks = parse_full_markdown_to_editor_blocks(content)
                except ImportError:
                    self.blocks = self.simple_parse_to_blocks(content)
                
                self.current_file = file_path
                self.rebuild_editor_ui()
                self.schedule_preview_update()
                self.setWindowTitle(f"Pandoc Block Editor - {os.path.basename(file_path)}")
                self.statusBar().showMessage(f"Opened {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to open file:\n{str(e)}')
    
    def save_file(self):
        """Save the current document."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save the document with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Markdown File', '', 'Markdown Files (*.md);;All Files (*)'
        )
        
        if file_path:
            self.save_to_file(file_path)
    
    def save_to_file(self, file_path: str):
        """Save blocks to a file."""
        try:
            # Reconstruct markdown from blocks
            content = ""
            for block in self.blocks:
                block_content = block.get('content', '').strip()
                if block_content:
                    content += block_content + "\n\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = file_path
            self.setWindowTitle(f"Pandoc Block Editor - {os.path.basename(file_path)}")
            self.statusBar().showMessage(f"Saved {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save file:\n{str(e)}')


def main():
    """Main function to run the PyQt application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Pandoc Block Editor")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Pandoc Block Editor")
    
    # Create and show main window
    window = PandocBlockEditor()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
