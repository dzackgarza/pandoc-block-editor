#!/usr/bin/env python3
"""
Amsthm Fenced Div Editor - Specialized editor for mathematical environments.
Focuses specifically on fenced divs for theorem, definition, proof, etc.
"""

import sys
import os
import re
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QScrollArea, QFrame, QLabel, QPushButton,
    QMenuBar, QFileDialog, QMessageBox, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import (
    QFont, QTextCharFormat, QColor, QSyntaxHighlighter, 
    QTextDocument, QAction, QKeySequence
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Import our existing pandoc utilities
import pandoc_utils


class FencedDivSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter specifically for fenced div environments."""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self.setup_highlighting_rules()
        
    def setup_highlighting_rules(self):
        """Setup syntax highlighting for fenced divs."""
        # Fenced div delimiters :::
        self.delimiter_format = QTextCharFormat()
        self.delimiter_format.setForeground(QColor('#6366f1'))  # Indigo
        self.delimiter_format.setFontWeight(QFont.Weight.Bold)
        
        # Environment attributes {.theorem title="..."}
        self.attr_format = QTextCharFormat()
        self.attr_format.setForeground(QColor('#059669'))  # Emerald
        self.attr_format.setFontWeight(QFont.Weight.Bold)
        
        # Environment content
        self.content_format = QTextCharFormat()
        self.content_format.setForeground(QColor('#374151'))  # Gray
        
        # Math expressions
        self.math_format = QTextCharFormat()
        self.math_format.setForeground(QColor('#0550ae'))  # Professional blue
        self.math_format.setBackground(QColor('#f6f8fa'))  # Light blue-gray bg
        self.math_format.setFontItalic(True)
    
    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to fenced div blocks."""
        if not text.strip():
            return
        
        # Highlight fenced div delimiters
        if text.strip().startswith(':::'):
            if '{' in text and '}' in text:
                # Opening delimiter with attributes
                delimiter_end = text.find('{')
                self.setFormat(0, delimiter_end, self.delimiter_format)
                
                # Highlight attributes
                attr_start = text.find('{')
                attr_end = text.find('}') + 1
                self.setFormat(attr_start, attr_end - attr_start, self.attr_format)
            else:
                # Closing delimiter
                self.setFormat(0, len(text), self.delimiter_format)
        else:
            # Content - highlight math expressions
            self.setFormat(0, len(text), self.content_format)
            
            # Inline math $...$
            for match in re.finditer(r'\$([^$]+)\$', text):
                self.setFormat(match.start(), match.end() - match.start(), self.math_format)
            
            # Display math $$...$$
            for match in re.finditer(r'\$\$([^$]+)\$\$', text):
                self.setFormat(match.start(), match.end() - match.start(), self.math_format)


class FencedDivBlock:
    """Represents a single fenced div block."""
    
    def __init__(self, block_id: str, env_type: str = "theorem", title: str = "", content: str = ""):
        self.id = block_id
        self.env_type = env_type
        self.title = title
        self.content = content
    
    def to_markdown(self) -> str:
        """Convert to fenced div markdown."""
        if self.title:
            return f":::{{.{self.env_type} title=\"{self.title}\"}}\n{self.content}\n:::"
        else:
            return f":::{{.{self.env_type}}}\n{self.content}\n:::"
    
    @classmethod
    def from_markdown(cls, markdown: str, block_id: str) -> 'FencedDivBlock':
        """Parse fenced div from markdown."""
        lines = markdown.strip().split('\n')
        
        if not lines or not lines[0].startswith(':::'):
            return cls(block_id, content=markdown)
        
        # Parse opening line
        opening = lines[0]
        env_type = "theorem"  # default
        title = ""
        
        # Extract environment type and title
        if '{' in opening:
            attr_match = re.search(r'\{\.(\w+)(?:\s+title="([^"]*)")?\}', opening)
            if attr_match:
                env_type = attr_match.group(1)
                title = attr_match.group(2) or ""
        
        # Extract content (everything between opening and closing :::)
        content_lines = []
        for line in lines[1:]:
            if line.strip() == ':::':
                break
            content_lines.append(line)
        
        content = '\n'.join(content_lines)
        return cls(block_id, env_type, title, content)


class FencedDivEditor(QTextEdit):
    """Editor for a single fenced div block."""
    
    contentChanged = pyqtSignal(str, object)  # block_id, FencedDivBlock
    
    def __init__(self, block: FencedDivBlock, parent=None):
        super().__init__(parent)
        self.block = block
        self.setPlainText(block.to_markdown())
        
        self.setup_editor()
        self.highlighter = FencedDivSyntaxHighlighter(self.document())
        
        # Connect signals
        self.textChanged.connect(self.on_text_changed)
        
        # Auto-resize
        self.auto_resize_timer = QTimer()
        self.auto_resize_timer.setSingleShot(True)
        self.auto_resize_timer.timeout.connect(self.resize_to_content)
        self.textChanged.connect(lambda: self.auto_resize_timer.start(100))
        
        QTimer.singleShot(50, self.resize_to_content)
    
    def setup_editor(self):
        """Configure the editor."""
        font = QFont('JetBrains Mono', 12)
        if not font.exactMatch():
            font = QFont('Monaco', 12)
        if not font.exactMatch():
            font = QFont('Consolas', 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Professional mathematical editor styling
        self.setStyleSheet("""
            QTextEdit {
                background: #fafbfc;
                border: 1px solid #e1e8ed;
                border-radius: 6px;
                padding: 12px;
                selection-background-color: #0969da;
                selection-color: white;
                color: #24292f;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #0969da;
                background: #ffffff;
                box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.1);
            }
            QTextEdit:hover {
                border-color: #d0d7de;
                background: #ffffff;
            }
        """)
    
    def resize_to_content(self):
        """Resize editor to fit content."""
        document = self.document()
        document.setTextWidth(self.viewport().width())
        
        content_height = document.size().height()
        min_height = 80  # Minimum for fenced divs
        final_height = max(min_height, int(content_height + 16))
        
        self.setFixedHeight(final_height)
    
    def on_text_changed(self):
        """Handle text changes and parse the fenced div."""
        markdown = self.toPlainText()
        updated_block = FencedDivBlock.from_markdown(markdown, self.block.id)
        self.block = updated_block
        self.contentChanged.emit(self.block.id, self.block)


class FencedDivContainer(QFrame):
    """Container for a fenced div with dropdown and editor."""
    
    environmentChanged = pyqtSignal(str, str)  # block_id, new_env_type
    
    def __init__(self, block: FencedDivBlock, parent=None):
        super().__init__(parent)
        self.block = block
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the container UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)
        
        # Top row with environment dropdown
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Environment type dropdown
        self.env_dropdown = QComboBox()
        self.env_dropdown.addItems([
            'theorem', 'definition', 'lemma', 'proposition', 'corollary',
            'proof', 'example', 'remark'
        ])
        self.env_dropdown.setCurrentText(self.block.env_type)
        self.env_dropdown.currentTextChanged.connect(self.on_environment_changed)
        self.env_dropdown.setStyleSheet("""
            QComboBox {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
                color: #475569;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #cbd5e1;
                background: #f1f5f9;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
            }
        """)
        
        top_layout.addWidget(self.env_dropdown)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # Editor
        self.editor = FencedDivEditor(self.block)
        layout.addWidget(self.editor)
        
        self.setLayout(layout)
        
        # Professional mathematical styling
        self.setStyleSheet("""
            FencedDivContainer {
                background: #fefefe;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin: 3px 0px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            FencedDivContainer:hover {
                border-color: #cbd5e1;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
            }
        """)
    
    def on_environment_changed(self, new_env_type: str):
        """Handle environment type change."""
        if new_env_type != self.block.env_type:
            self.block.env_type = new_env_type
            self.environmentChanged.emit(self.block.id, new_env_type)
            # Update the editor content to reflect the change
            self.editor.setPlainText(self.block.to_markdown())


class AmsthmPreviewPane(QWebEngineView):
    """Preview pane specifically for amsthm environments."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_preview()
    
    def setup_preview(self):
        """Setup the preview pane."""
        self.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background: #ffffff;
                margin: 4px;
            }
        """)
    
    def update_preview(self, blocks: List[FencedDivBlock]):
        """Update preview with amsthm-styled blocks."""
        if not blocks:
            self.setHtml("""
                <html><body style="padding: 20px; font-family: serif;">
                    <p style="color: #6b7280;">No environments yet. Add a theorem, definition, or proof!</p>
                </body></html>
            """)
            return
        
        # Combine all blocks into markdown
        full_markdown = ""
        for block in blocks:
            full_markdown += block.to_markdown() + "\n\n"
        
        try:
            # Convert to HTML with pandoc
            html_content = pandoc_utils.convert_markdown_to_html(full_markdown)
            
            # Wrap with amsthm-specific styling
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Amsthm Preview</title>
                <style>
                    body {{
                        font-family: "Computer Modern", "Latin Modern Roman", "Times New Roman", serif;
                        line-height: 1.6;
                        color: #212529;
                        max-width: none;
                        margin: 0;
                        padding: 20px;
                        background: #ffffff;
                        font-size: 15px;
                    }}
                    
                    /* Elegant Amsthm environment styling */
                    .theorem, .definition, .lemma, .proposition, .corollary {{
                        border-left: 3px solid #495057;
                        background: #f8f9fa;
                        margin: 20px 0;
                        padding: 18px 24px;
                        border-radius: 0 6px 6px 0;
                        box-shadow: 0 2px 8px rgba(73, 80, 87, 0.08);
                        font-style: italic;
                    }}
                    
                    .proof {{
                        border-left: 3px solid #28a745;
                        background: #f8fff9;
                        margin: 20px 0;
                        padding: 18px 24px;
                        border-radius: 0 6px 6px 0;
                        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.08);
                    }}
                    
                    .example, .remark {{
                        border-left: 3px solid #fd7e14;
                        background: #fffbf7;
                        margin: 20px 0;
                        padding: 18px 24px;
                        border-radius: 0 6px 6px 0;
                        box-shadow: 0 2px 8px rgba(253, 126, 20, 0.08);
                    }}
                    
                    /* Environment headers */
                    .theorem::before {{ content: "Theorem"; }}
                    .definition::before {{ content: "Definition"; }}
                    .lemma::before {{ content: "Lemma"; }}
                    .proposition::before {{ content: "Proposition"; }}
                    .corollary::before {{ content: "Corollary"; }}
                    .proof::before {{ content: "Proof"; }}
                    .example::before {{ content: "Example"; }}
                    .remark::before {{ content: "Remark"; }}
                    
                    .theorem::before, .definition::before, .lemma::before, 
                    .proposition::before, .corollary::before, .proof::before,
                    .example::before, .remark::before {{
                        font-weight: bold;
                        font-style: italic;
                        margin-right: 8px;
                        color: inherit;
                    }}
                    
                    /* Title styling */
                    [title]::before {{
                        content: attr(data-env-type) " (" attr(title) ")";
                    }}
                    
                    /* Math styling */
                    .MathJax {{
                        font-size: 1.1em !important;
                    }}
                    
                    /* Paragraph spacing within environments */
                    .theorem p, .definition p, .lemma p, .proposition p, 
                    .corollary p, .proof p, .example p, .remark p {{
                        margin: 8px 0;
                    }}
                    
                    .theorem p:first-child, .definition p:first-child, 
                    .lemma p:first-child, .proposition p:first-child,
                    .corollary p:first-child, .proof p:first-child,
                    .example p:first-child, .remark p:first-child {{
                        margin-top: 0;
                    }}
                    
                    .theorem p:last-child, .definition p:last-child,
                    .lemma p:last-child, .proposition p:last-child,
                    .corollary p:last-child, .proof p:last-child,
                    .example p:last-child, .remark p:last-child {{
                        margin-bottom: 0;
                    }}
                </style>
                
                <!-- MathJax -->
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
                
                // Process titles for environment headers
                document.addEventListener('DOMContentLoaded', function() {{
                    const envs = document.querySelectorAll('[title]');
                    envs.forEach(env => {{
                        const title = env.getAttribute('title');
                        const className = env.className;
                        if (title && className) {{
                            env.setAttribute('data-env-type', className.charAt(0).toUpperCase() + className.slice(1));
                        }}
                    }});
                }});
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
                <p>Error rendering amsthm environments: {str(e)}</p>
            </body></html>
            """
            self.setHtml(error_html)


class AmsthmEditor(QMainWindow):
    """Main amsthm fenced div editor."""
    
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.block_containers = []
        self.current_file = None
        
        # Update timer for preview
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        
        self.setup_ui()
        self.load_sample_content()
    
    def setup_ui(self):
        """Setup the main UI."""
        self.setWindowTitle("Amsthm Environment Editor")
        self.setGeometry(100, 100, 1400, 800)
        
        # Professional dark theme for mathematical work
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
                color: #212529;
            }
            QMenuBar {
                background: #ffffff;
                border-bottom: 1px solid #e9ecef;
                padding: 4px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #e9ecef;
            }
            QStatusBar {
                background: #ffffff;
                border-top: 1px solid #e9ecef;
                color: #6c757d;
            }
        """)
        
        # Menu bar
        self.setup_menu_bar()
        
        # Main splitter - perfect alignment
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #dee2e6;
                width: 2px;
            }
            QSplitter::handle:hover {
                background: #adb5bd;
            }
        """)
        
        # Left pane - synchronized scrolling editor
        self.editor_pane = self.setup_editor_pane()
        splitter.addWidget(self.editor_pane)
        
        # Right pane - preview
        self.preview_pane = AmsthmPreviewPane()
        splitter.addWidget(self.preview_pane)
        
        # Equal split
        splitter.setSizes([700, 700])
        
        self.setCentralWidget(splitter)
        self.statusBar().showMessage("Ready - Professional mathematical environment editor")
    
    def setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open...', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # Environment menu
        env_menu = menubar.addMenu('Environment')
        
        for env_type in ['theorem', 'definition', 'lemma', 'proof', 'example', 'remark']:
            action = QAction(f'Add {env_type.title()}', self)
            action.triggered.connect(lambda checked, t=env_type: self.add_environment(t))
            env_menu.addAction(action)
    

    
    def setup_editor_pane(self):
        """Setup the synchronized editor pane with floating button."""
        # Create main container that will hold both scroll area and floating button
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for blocks
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        self.editor_layout = QVBoxLayout(container)
        self.editor_layout.setContentsMargins(16, 16, 16, 16)
        self.editor_layout.setSpacing(12)  # More generous spacing
        self.editor_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Top-align all content
        self.editor_layout.addStretch()
        
        scroll_area.setWidget(container)
        
        # Professional mathematical paper background
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #fcfcfc;
            }
            QScrollArea > QWidget > QWidget {
                background: #fcfcfc;
            }
        """)
        
        main_layout.addWidget(scroll_area)
        
        # Floating add button
        self.floating_button = QPushButton("➕")
        self.floating_button.setFixedSize(56, 56)
        self.floating_button.clicked.connect(lambda: self.add_environment('remark'))  # Default to remark
        self.floating_button.setStyleSheet("""
            QPushButton {
                background: rgba(99, 102, 241, 0.9);
                border: none;
                border-radius: 28px;
                color: white;
                font-size: 24px;
                font-weight: bold;
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
            }
            QPushButton:hover {
                background: rgba(99, 102, 241, 1.0);
                box-shadow: 0 6px 16px rgba(99, 102, 241, 0.5);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: rgba(79, 70, 229, 1.0);
                box-shadow: 0 2px 8px rgba(79, 70, 229, 0.4);
            }
        """)
        
        # Position floating button in bottom-left
        self.floating_button.setParent(main_container)
        
        # Override resizeEvent to position floating button
        def resize_event(event):
            super(QWidget, main_container).resizeEvent(event)
            self.floating_button.move(20, main_container.height() - 76)
        
        main_container.resizeEvent = resize_event
        
        return main_container
    
    def load_sample_content(self):
        """Load torture test content with comprehensive mathematical environments."""
        try:
            # Try to load torture test document
            with open('torture_test.md', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.blocks = self.parse_fenced_divs(content)
            if not self.blocks:
                # Fallback to sample if no fenced divs found
                self.load_fallback_content()
        except FileNotFoundError:
            # Fallback if torture test file doesn't exist
            self.load_fallback_content()
        
        self.rebuild_editor_ui()
        self.schedule_preview_update()
    
    def load_fallback_content(self):
        """Load fallback content if torture test not available."""
        self.blocks = [
            FencedDivBlock("block_0", "remark", "", 
                          "Welcome to the Amsthm Environment Editor!\n\nUse the dropdown to change environment types, and click the ➕ button to add new blocks.")
        ]
    
    def rebuild_editor_ui(self):
        """Rebuild the editor UI."""
        # Clear existing containers
        for container in self.block_containers:
            container.setParent(None)
        self.block_containers.clear()
        
        # Add new containers
        for block in self.blocks:
            container = FencedDivContainer(block)
            container.editor.contentChanged.connect(self.on_block_content_changed)
            
            self.editor_layout.insertWidget(
                self.editor_layout.count() - 1,
                container
            )
            self.block_containers.append(container)
    
    @pyqtSlot(str, object)
    def on_block_content_changed(self, block_id: str, updated_block: FencedDivBlock):
        """Handle block content changes."""
        for i, block in enumerate(self.blocks):
            if block.id == block_id:
                self.blocks[i] = updated_block
                break
        
        self.schedule_preview_update()
    
    def schedule_preview_update(self):
        """Schedule preview update with debouncing."""
        self.update_timer.start(300)
    
    def update_preview(self):
        """Update the preview pane."""
        self.preview_pane.update_preview(self.blocks)
    
    def add_environment(self, env_type: str):
        """Add a new environment."""
        new_id = f"block_{len(self.blocks)}"
        new_block = FencedDivBlock(new_id, env_type, "", "Enter content here...")
        self.blocks.append(new_block)
        
        # Add to UI
        container = FencedDivContainer(new_block)
        container.editor.contentChanged.connect(self.on_block_content_changed)
        
        self.editor_layout.insertWidget(
            self.editor_layout.count() - 1,
            container
        )
        self.block_containers.append(container)
        
        # Focus new block
        container.editor.setFocus()
        self.schedule_preview_update()
    
    def new_document(self):
        """Create new document."""
        self.blocks = []
        self.current_file = None
        self.rebuild_editor_ui()
        self.schedule_preview_update()
        self.setWindowTitle("Amsthm Environment Editor")
    
    def open_file(self):
        """Open markdown file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Markdown File', '', 'Markdown Files (*.md);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse fenced divs from content
                self.blocks = self.parse_fenced_divs(content)
                self.current_file = file_path
                self.rebuild_editor_ui()
                self.schedule_preview_update()
                self.setWindowTitle(f"Amsthm Editor - {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to open file:\n{str(e)}')
    
    def save_file(self):
        """Save current document."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save with new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Markdown File', '', 'Markdown Files (*.md);;All Files (*)'
        )
        
        if file_path:
            self.save_to_file(file_path)
    
    def save_to_file(self, file_path: str):
        """Save blocks to file."""
        try:
            content = ""
            for block in self.blocks:
                content += block.to_markdown() + "\n\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = file_path
            self.setWindowTitle(f"Amsthm Editor - {os.path.basename(file_path)}")
            self.statusBar().showMessage(f"Saved {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save file:\n{str(e)}')
    
    def parse_fenced_divs(self, content: str) -> List[FencedDivBlock]:
        """Parse fenced divs from markdown content."""
        blocks = []
        
        # Split on fenced div boundaries
        parts = re.split(r'\n(?=:::)', content)
        
        block_id = 0
        for part in parts:
            part = part.strip()
            if part.startswith(':::') and part.endswith(':::'):
                block = FencedDivBlock.from_markdown(part, f"block_{block_id}")
                blocks.append(block)
                block_id += 1
        
        return blocks if blocks else [FencedDivBlock("block_0", "theorem", "", "")]


def main():
    """Run the amsthm editor."""
    app = QApplication(sys.argv)
    
    app.setApplicationName("Amsthm Environment Editor")
    app.setApplicationVersion("1.0")
    
    window = AmsthmEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main() 