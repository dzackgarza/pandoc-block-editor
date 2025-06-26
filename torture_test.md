# Mathematical Analysis - Torture Test Document

:::{.definition title="Metric Space"}
A **metric space** is a set $X$ together with a function $d: X \times X \to \mathbb{R}$ such that for all $x, y, z \in X$:

1. $d(x, y) \geq 0$ with equality if and only if $x = y$
2. $d(x, y) = d(y, x)$ (symmetry)  
3. $d(x, z) \leq d(x, y) + d(y, z)$ (triangle inequality)

The function $d$ is called a **metric** or **distance function**.
:::

:::{.theorem title="Banach Fixed Point Theorem"}
Let $(X, d)$ be a complete metric space and let $T: X \to X$ be a contraction mapping, i.e., there exists $0 \leq k < 1$ such that

$$d(T(x), T(y)) \leq k \cdot d(x, y)$$

for all $x, y \in X$. Then $T$ has a unique fixed point.
:::

:::{.proof}
**Existence:** Choose any $x_0 \in X$ and define the sequence $(x_n)$ by $x_{n+1} = T(x_n)$.

We show that $(x_n)$ is Cauchy. For $m > n$:

$$d(x_m, x_n) \leq d(x_m, x_{m-1}) + d(x_{m-1}, x_{m-2}) + \cdots + d(x_{n+1}, x_n)$$

Since $d(x_{i+1}, x_i) = d(T(x_i), T(x_{i-1})) \leq k \cdot d(x_i, x_{i-1})$, we have:

$$d(x_{n+1}, x_n) \leq k^n d(x_1, x_0)$$

Therefore:
$$d(x_m, x_n) \leq k^n d(x_1, x_0) \sum_{i=0}^{m-n-1} k^i = k^n d(x_1, x_0) \frac{1-k^{m-n}}{1-k} \leq \frac{k^n}{1-k} d(x_1, x_0)$$

As $n \to \infty$, this approaches 0, so $(x_n)$ is Cauchy.

**Uniqueness:** Suppose $x$ and $y$ are both fixed points. Then:
$$d(x, y) = d(T(x), T(y)) \leq k \cdot d(x, y)$$

Since $k < 1$, this implies $d(x, y) = 0$, so $x = y$.
:::

:::{.lemma title="Contraction Lemma"}
If $T: X \to X$ is a contraction with constant $k < 1$, then for any $x \in X$:

$$d(x, T(x)) \leq \frac{1}{1-k} d(x, T(x))$$
:::

:::{.corollary}
Every contraction mapping on a complete metric space has a unique fixed point, and the sequence of iterates converges to this fixed point.
:::

:::{.definition title="Cauchy Sequence"}
A sequence $(x_n)$ in a metric space $(X, d)$ is called **Cauchy** if for every $\varepsilon > 0$, there exists $N \in \mathbb{N}$ such that for all $m, n \geq N$:

$$d(x_m, x_n) < \varepsilon$$
:::

:::{.theorem title="Intermediate Value Theorem"}
Let $f: [a, b] \to \mathbb{R}$ be continuous. If $f(a) \cdot f(b) < 0$, then there exists $c \in (a, b)$ such that $f(c) = 0$.
:::

:::{.proof}
Without loss of generality, assume $f(a) < 0 < f(b)$.

Define $S = \{x \in [a, b] : f(x) < 0\}$. Since $a \in S$, we have $S \neq \emptyset$. Also, $S$ is bounded above by $b$.

Let $c = \sup S$. We claim that $f(c) = 0$.

**Case 1:** Suppose $f(c) > 0$. By continuity, there exists $\delta > 0$ such that $f(x) > 0$ for all $x \in (c - \delta, c + \delta)$. But then $c - \delta/2$ would be an upper bound for $S$, contradicting $c = \sup S$.

**Case 2:** Suppose $f(c) < 0$. By continuity, there exists $\delta > 0$ such that $f(x) < 0$ for all $x \in (c - \delta, c + \delta)$. Then $c + \delta/2 \in S$, contradicting $c$ being an upper bound.

Therefore, $f(c) = 0$.
:::

:::{.example title="Weierstrass Approximation"}
Consider the function $f(x) = |x|$ on $[-1, 1]$. This can be uniformly approximated by polynomials:

$$p_n(x) = \sqrt{\frac{2}{\pi}} \sum_{k=0}^{n} \frac{(-1)^k}{2k+1} \left(\frac{x^{2k+1}}{2k+1}\right)$$

The error satisfies:
$$\|f - p_n\|_\infty \leq \frac{C}{\sqrt{n}}$$

for some constant $C > 0$.
:::

:::{.remark}
The Banach Fixed Point Theorem is fundamental in many areas:

- **Differential Equations**: Picard's existence theorem
- **Optimization**: Gradient descent convergence  
- **Numerical Analysis**: Iterative methods
- **Economics**: Existence of equilibria

The key insight is that contractivity ensures both existence and uniqueness, while completeness guarantees convergence.
:::

:::{.definition title="Topology"}
A **topology** on a set $X$ is a collection $\mathcal{T}$ of subsets of $X$ satisfying:

1. $\emptyset, X \in \mathcal{T}$
2. Arbitrary unions of sets in $\mathcal{T}$ are in $\mathcal{T}$
3. Finite intersections of sets in $\mathcal{T}$ are in $\mathcal{T}$

The pair $(X, \mathcal{T})$ is called a **topological space**.
:::

:::{.theorem title="Heine-Borel Theorem"}
A subset $K$ of $\mathbb{R}^n$ is compact if and only if it is closed and bounded.
:::

:::{.proof}
**($\Rightarrow$)** Suppose $K$ is compact.

*Boundedness:* The collection $\{B(0, n) : n \in \mathbb{N}\}$ is an open cover of $\mathbb{R}^n$, hence of $K$. By compactness, finitely many balls cover $K$, so $K$ is bounded.

*Closedness:* Let $(x_n)$ be a sequence in $K$ converging to $x \in \mathbb{R}^n$. For each $n$, consider the open cover:
$$\mathcal{U}_n = \{B(y, 1/n) : y \in K\} \cup \{B(x, 1/n)^c\}$$

If $x \notin K$, this covers $K$. By compactness, finitely many sets suffice, but this leads to a contradiction for large $n$.

**($\Leftarrow$)** Suppose $K$ is closed and bounded. Let $\mathcal{U}$ be an open cover of $K$.

Since $K$ is bounded, $K \subset [-M, M]^n$ for some $M$. We use the **Lebesgue number lemma** and a covering argument to extract a finite subcover.
:::

:::{.example title="Pathological Example"}
Consider the function:
$$f(x) = \begin{cases}
x^2 \sin(1/x) & \text{if } x \neq 0 \\
0 & \text{if } x = 0
\end{cases}$$

This function is:
- Continuous at $x = 0$
- Differentiable at $x = 0$ with $f'(0) = 0$
- Has derivative $f'(x) = 2x\sin(1/x) - \cos(1/x)$ for $x \neq 0$
- The derivative is **not continuous** at $x = 0$

This shows that differentiability does not imply continuous differentiability.
:::

:::{.remark}
The study of metric spaces, topological spaces, and their properties forms the foundation of modern analysis. Key concepts include:

- **Completeness** vs **Compactness**
- **Uniform continuity** vs **Continuity**  
- **Pointwise** vs **Uniform convergence**
- **Weak** vs **Strong topologies**

Understanding these distinctions is crucial for advanced mathematics.
::: 