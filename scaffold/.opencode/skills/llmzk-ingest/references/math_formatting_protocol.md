# Math Formatting Protocol

Use the installed `obsidian-markdown` skill for Obsidian Markdown syntax.

llmzk-specific rule:

> Mathematics is prose content, not code.

## Inline math

Use `$...$`:

```markdown
The local error is $\delta^l$.
```

## Display math

Use `$$...$$`:

```markdown
$$
\delta^l = ((w^{l+1})^T \delta^{l+1}) \odot \sigma'(z^l)
$$
```

## Aligned equations

```markdown
$$
\begin{aligned}
\frac{\partial C}{\partial b^l_j} &= \delta^l_j \\
\frac{\partial C}{\partial w^l_{jk}} &= a^{l-1}_k\delta^l_j
\end{aligned}
$$
```

## Do not use code fences for math

Do not write ordinary equations as:

````markdown
```latex
\delta^l = ((w^{l+1})^T \delta^{l+1}) \odot \sigma'(z^l)
```
````

Code fences are only for code, shell commands, YAML, JSON, Mermaid, or literal file content.
