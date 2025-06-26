# Heading 1 {#h1-id .h1-class key="value"}

This is a paragraph under H1. It contains some *italic* and **bold** text.
It also includes a [link to AIDE](https://aide.aide.com).
And a remote image: ![Placeholder Remote Image](https://via.placeholder.com/150/0000FF/FFFFFF?Text=Remote+Image)
And a local image: ![Placeholder Local Image](images/local_test_image.png) <!-- Assuming images/ is relative to this file or project root for Pandoc -->

## Heading 2 with `code` {#h2-id}

This paragraph has inline `code`.

::: {#semantic-div-1 .theorem type="Pythagorean"}
This is a semantic block, styled as a theorem.
It might contain **strong emphasis** and equations like $a^2 + b^2 = c^2$.
This div has an ID and a class.
:::

Another paragraph here, following the semantic block.

### Heading 3 {#h3-id}

*   Unordered list item 1
*   Unordered list item 2
    *   Nested unordered list item 2.1
    *   Nested unordered list item 2.2
*   Unordered list item 3

1.  Ordered list item 1
2.  Ordered list item 2
    1.  Nested ordered list item 2.1
    2.  Nested ordered list item 2.2
3.  Ordered list item 3

```python
# This is a Python code block
def greet(name):
  """Greets the user."""
  print(f"Hello, {name}!")

greet("World")
```

This is a paragraph with a footnote.[^1]

[^1]: This is the footnote content.

---

## Tables and Other Elements

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1.1 | Cell 1.2 | Cell 1.3 |
| Cell 2.1 | Cell 2.2 | Cell 2.3 |
| Cell 3.1 | Cell 3.2 | Cell 3.3 |

> This is a blockquote.
> It can span multiple lines.
> - And include lists
>   - Or other elements.

## LaTeX Math Equations {#math-section}

Inline math: $E = mc^2$. This equation $\sum_{i=1}^{n} x_i = x_1 + x_2 + \dots + x_n$ is also inline.

Display math:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

Another display equation:
\[
\mathbf{F} = m\mathbf{a}
\]

### LaTeX Environments

A common LaTeX environment:
\begin{equation} \label{eq:lorentz}
\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}
\end{equation}
We can refer to this equation using `\cref{eq:lorentz}`.

Another one:
\begin{align} \label{eq:maxwell}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\epsilon_0} \\
\nabla \cdot \mathbf{B} &= 0 \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0 \left( \mathbf{J} + \epsilon_0 \frac{\partial \mathbf{E}}{\partial t} \right)
\end{align}
We can refer to Maxwell's equations using `\cref{eq:maxwell}`.

This is a reference to a non-existent label: `\cref{eq:nonexistent}`.

::: {#semantic-div-2 .nested-container}
This is an outer semantic block.
It can contain other blocks, including other semantic blocks or normal paragraphs.

This is a paragraph inside the outer semantic block.

::: {#nested-div .definition}
This is a nested semantic block (a definition).
Content within the nested block.
It has its own ID and class.
:::

A paragraph following the nested div, but still inside the outer div.
:::

A final paragraph to conclude the document.
This includes a `\label{final-label}` here.
And a reference `\cref{final-label}`.

---
### Potentially Malformed Block (for testing resilience)

::: {.warning}
This block has an unclosed backtick `
and maybe some other weirdness.
:::

End of document.
