# High-Judgement Notes Protocol

Use this protocol when deciding whether to create bridge notes and contradiction/tension notes.

These note types require judgement. They should not be created merely to satisfy a checklist. It is valid to write `No bridge note warranted` or `No contradiction/tension note warranted` in the candidate inventory when the material does not support a durable note.

## Bridge notes

A bridge note should capture a meaningful transformation, translation, equivalence, representation shift, dependency, or conceptual transfer between ideas.

A bridge note should answer:

- What two or more ideas are being connected?
- What changes when one idea is viewed through the other?
- Why does this connection help future thinking?

Prefer bridge notes that use patterns like:

- `X reframes Y as Z`
- `X makes Y local / computable / reusable`
- `X is the same computational pattern as Y under different notation`
- `X transfers an intuition from A to B`
- `X exposes why Y works`

Avoid bridge notes that only say:

- two concepts are related;
- a notation appears in an equation;
- one concept is used by another;
- a source mentions both ideas.

### Bridge quality tests

Before creating a bridge note, check:

1. **Non-obviousness** — would the connection still be useful in a month?
2. **Directionality** — does the note explain how one idea clarifies or transforms another?
3. **Reusability** — can the bridge help with another source or problem?
4. **Specificity** — does the title make a claim rather than name two topics?

If a candidate fails these tests, fold it into a concept, permanent note, index note, or literature note instead.

### Bridge examples

Weak:

- `Hadamard product is used in backpropagation`
- `Backpropagation and neural networks`
- `JVP and VJP are related`

Strong:

- `Weighted input makes neuron error a local chain-rule variable`
- `Defining error with respect to weighted input makes backpropagation compositional`
- `Backpropagation is reverse-mode automatic differentiation specialized to layered networks`
- `A VJP is the linear-algebra form of propagating an adjoint backward`
- `Dual numbers turn a local derivative rule into a forward-mode computation`

## Contradiction/tension notes

A contradiction/tension note should preserve a real tension, trade-off, ambiguity, limitation, disagreement, or apparent conflict.

A contradiction note should answer:

- What are the two sides of the tension?
- Why do both sides seem plausible or important?
- Is the tension resolved, unresolved, contextual, or a design trade-off?
- What should a future reader remember?

Do not create a contradiction note merely because:

- the notation is hard;
- the topic is subtle;
- a source is pedagogically confusing;
- there is a caveat that fits naturally in a concept or permanent note.

### Contradiction quality tests

Before creating a contradiction/tension note, check:

1. **Two-sidedness** — are there genuinely competing claims, pressures, or interpretations?
2. **Durability** — will this tension matter beyond the current source?
3. **Consequence** — does the tension affect method choice, interpretation, implementation, or learning?
4. **Status** — is it resolved, unresolved, context-dependent, or a trade-off?

If these are weak, do not create a contradiction note. Record `No durable contradiction/tension note warranted` in the decision log.

### Contradiction examples

Weak:

- `Backpropagation is simple but notation is hard`
- `The source is intuitive but the equations are complex`
- `Gradient descent can be slow`

Strong:

- `Backpropagation is efficient because it computes gradients indirectly through error variables`
- `Backpropagation replaces direct per-parameter sensitivity estimates with a backward error-propagation computation`
- `Inference-time scaling can improve reasoning while making deployment more expensive`
- `Forward-mode AD is natural for few inputs-to-many outputs, while reverse-mode AD is natural for many inputs-to-few outputs`
- `Finite differences are intuitive but scale poorly with parameter count`

## Demotion rules

When a bridge or contradiction candidate is weak:

- put ordinary relationships in an index note;
- put formula details in a concept note;
- put source-specific caveats in a literature note;
- put durable one-sided claims in a permanent note;
- record the decision under `Notes deliberately not created`.

## Titles

Use claim-like titles for high-judgement notes.

Weak titles:

- `Backpropagation and weighted input`
- `Hadamard product bridge`
- `Notation tension`

Strong titles:

- `Weighted input makes neuron error a local chain-rule variable`
- `Backpropagation computes gradients cheaply by introducing indirect error variables`
- `Inference-time scaling trades reasoning quality against deployment cost`

## Mathematical precision guardrails

When creating a contradiction/tension note about finite differences versus backpropagation, do not say the finite-difference method is “exponentially worse”. The cost difference is tied to parameter count: finite differences require extra forward evaluations proportional to the number of parameters, while backpropagation computes all gradients with one backward pass. Use “orders of magnitude more expensive” or “worse by a factor proportional to the number of parameters” when that is the intended claim.
