# Fleeting Promotion Protocol

A fleeting note may become:

- a concept note;
- a permanent claim note;
- a bridge note;
- a contradiction/tension note;
- an index entry;
- a project note;
- archived or discarded.

Do not promote all fleeting notes. Do not convert all fleeting notes into concepts.

For bridge and contradiction/tension candidates, apply `../llmzk-ingest/references/high_judgement_notes_protocol.md`. These note types require judgement and should not be created merely to satisfy a workflow shape.

## Classification examples

- `Hadamard product means elementwise multiplication` → concept note.
- `Backpropagation is reverse-mode AD specialised to neural networks` → permanent note or strong bridge note if it explains the translation between neural-network notation and reverse-mode AD.
- `Why is delta defined with respect to z?` → permanent note after answer, or strong bridge note if it explains why weighted input is the right intermediate variable.
- `Compare Nielsen with reverse-mode AD` → bridge candidate only if the note captures a specific transformation, such as error propagation as a VJP/pullback.
- `This notation is ugly` → usually a decision-log observation, not a contradiction note.
- `Finite differences are intuitive but scale poorly with parameter count` → contradiction/tension note if the trade-off is central.


## Candidate review gate

For fleeting promotion, `/llmzk-promote` and `/llmzk-promote-candidates` should first create a candidate review file in `Logs/Candidate Reviews/`. Do not create durable concept, permanent, bridge, contradiction/tension, or index notes until `/llmzk-write-approved` is run on that review file.
