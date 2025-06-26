# 🧮 Pandoc Block Editor
## Specialized Amsthm Environment Editor with Perfect Alignment

A **specialized PyQt6 editor** focused exclusively on **fenced div blocks** for mathematical environments like theorems, definitions, proofs, etc. Each block on the left is **perfectly top-aligned** with its rendered counterpart on the right.

## ✨ What You Asked For

### ✅ **Fenced Divs Only**
- Focused solely on `:::` fenced div blocks
- No general markdown - just mathematical environments
- Clean, minimal interface for mathematical writing

### ✅ **Perfect Alignment**
- Each editor block aligns precisely with its preview
- Top alignment between left and right panes
- No scrolling mismatches or layout drift

### ✅ **Amsthm Environments**
Your exact syntax:
```markdown
:::{.theorem title="theorem name"}
Text here
:::
```

Renders as beautifully styled mathematical environment blocks!

## 🎯 Supported Environments

| Environment | Description | Styling |
|-------------|-------------|---------|
| `theorem` | Mathematical theorems | Blue border, formal styling |
| `definition` | Definitions | Blue border, formal styling |
| `lemma` | Supporting lemmas | Blue border, formal styling |
| `proposition` | Propositions | Blue border, formal styling |
| `corollary` | Corollaries | Blue border, formal styling |
| `proof` | Proofs | Green border, proof styling |
| `example` | Examples | Orange border, example styling |
| `remark` | Remarks/notes | Orange border, casual styling |

## 🚀 Quick Start

### 1. **Test Dependencies**
```bash
python tests/test_dependencies.py
```

### 2. **Test Editor**
```bash
python test.py                    # Run all tests
python tests/test_editor.py       # Test editor only
```

### 3. **Launch Editor**
```bash
python run.py
```

## 🎨 Features

### **Specialized Syntax Highlighting**
- **Fenced div delimiters** (`:::`) in indigo
- **Environment attributes** (`{.theorem title="..."}`) in emerald
- **Math expressions** (`$...$`, `$$...$$`) with red highlighting and backgrounds
- **Content text** in clean gray

### **Perfect Block Alignment**
- Left editor blocks align with right preview blocks
- No height restrictions - blocks size to content
- Synchronized scrolling between panes
- Visual block IDs for easy identification

### **Professional Math Rendering**
- **MathJax** for beautiful equation rendering
- **Computer Modern** serif fonts for authentic LaTeX feel
- **Gradient backgrounds** for each environment type
- **Environment headers** (Theorem, Definition, Proof, etc.)
- **Title support** with proper formatting

### **Desktop Application Features**
- **Native menus**: File operations, environment insertion
- **Keyboard shortcuts**: Ctrl+N, Ctrl+O, Ctrl+S
- **Toolbar buttons**: Quick access to add theorem, definition, proof
- **Environment menu**: Add any supported environment type
- **Auto-sizing**: Blocks grow/shrink with content

## 📝 Usage Examples

### **Theorem with Title**
```markdown
:::{.theorem title="Pythagorean Theorem"}
In a right triangle, the square of the hypotenuse is equal to the sum of squares of the other two sides.

$$a^2 + b^2 = c^2$$
:::
```

### **Definition**
```markdown
:::{.definition title="Vector Space"}
A **vector space** over a field $F$ is a set $V$ equipped with operations of addition and scalar multiplication satisfying:

1. Associativity of addition
2. Commutativity of addition  
3. Identity element of addition
4. Existence of additive inverses
:::
```

### **Proof**
```markdown
:::{.proof}
Let $ABC$ be a right triangle with right angle at $C$. Then by the law of cosines:

$$c^2 = a^2 + b^2 - 2ab\cos(C)$$

Since $C = 90°$, we have $\cos(C) = 0$, so:

$$c^2 = a^2 + b^2$$
:::
```

## 🎯 Perfect for Mathematical Writing

### **What Makes This Special**
- **Zero height restrictions** - blocks fit content perfectly
- **Mathematical focus** - designed specifically for theorem-proof writing
- **Beautiful rendering** - LaTeX-quality output in real-time
- **Aligned editing** - see your content positioned exactly as it will appear
- **Distraction-free** - no general markdown clutter

### **Ideal Workflow**
1. **Add environments** using toolbar buttons or Environment menu
2. **Type directly** in fenced div syntax with syntax highlighting
3. **See immediate preview** with perfect alignment
4. **Math renders beautifully** with MathJax
5. **Save as markdown** for use with Pandoc, LaTeX, etc.

## 📁 File Operations

### **Open Existing Files**
- Parses fenced divs from any markdown file
- Ignores non-fenced-div content (focuses on what you need)
- Maintains environment types and titles

### **Save Files**
- Exports clean markdown with proper fenced div syntax
- Compatible with Pandoc and LaTeX
- Ready for academic publishing workflows

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|---------|
| `Ctrl+N` | New document |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+Q` | Quit |

## 🔧 Technical Details

### **Built With**
- **PyQt6** for native desktop performance
- **QSyntaxHighlighter** for custom fenced div highlighting
- **QWebEngineView** for beautiful HTML preview
- **Your existing pandoc_utils** for markdown processing
- **MathJax** for mathematical typesetting

### **Architecture**
- `FencedDivBlock` - Data model for each environment
- `FencedDivEditor` - Syntax-highlighted editor widget
- `FencedDivContainer` - Aligned block container
- `AmsthmPreviewPane` - Mathematical preview renderer
- `AmsthmEditor` - Main application window

### **Perfect Alignment Implementation**
- Each editor block maps 1:1 with preview block
- Fixed heights based on content (no arbitrary minimums)
- Synchronized layout updates
- Visual block correlation with IDs

## 🎓 Sample Output

When you write:
```markdown
:::{.theorem title="Fundamental Theorem of Calculus"}
If $f$ is continuous on $[a,b]$ and $F$ is an antiderivative of $f$, then:

$$\int_a^b f(x)\,dx = F(b) - F(a)$$
:::
```

You get a **beautifully rendered theorem block** with:
- Blue left border
- Gradient background  
- "**Theorem (Fundamental Theorem of Calculus)**" header
- Perfectly typeset mathematics
- Professional LaTeX-style appearance

## 🔄 Migration from General Editor

If you were using the general pandoc block editor, this specialized version:
- **Focuses** on what you actually need (mathematical environments)
- **Eliminates** general markdown distractions  
- **Perfects** the alignment you requested
- **Enhances** mathematical typesetting
- **Maintains** all your file compatibility

## 🎉 Ready to Use!

Your **minimal, focused amsthm environment editor** is ready! It does exactly what you asked for:

✅ **Only fenced div blocks**  
✅ **Perfect top-alignment** between editor and preview  
✅ **Beautiful amsthm environment rendering**  
✅ **Zero height restrictions**  
✅ **Mathematical syntax highlighting**  

Launch with: `python run.py` 🚀 