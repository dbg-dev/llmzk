# Source Ingest Protocol

The purpose of source ingest is to turn raw source material into a useful Zettelkasten graph.

## Source note

Capture:

- reference metadata;
- short summary;
- key sections;
- key source claims;
- central formal machinery, if any;
- derived notes;
- related sources.

## Literature note

Capture what the source says, source-specifically:

- thesis / central claim;
- important definitions and terms;
- argument structure;
- important equations or algorithms;
- examples and interpretations;
- useful quotations only when short and necessary;
- open questions.

## Durable notes

Extract durable notes only in write-approved mode, after creating and reviewing the candidate review file.

For technical sources, look especially for:

- named concepts;
- notation;
- definitions;
- assumptions;
- named equations or algorithms;
- durable claims;
- trade-offs or tensions;
- conceptual bridges.

Do not create concept notes for authors, source titles, paper titles, publishers, years, or URLs.


## Candidate review gate

For source ingest, `/llmzk-ingest` and `/llmzk-ingest-candidates` should first create a candidate review file in `Logs/Candidate Reviews/`. Do not create source, literature, concept, permanent, bridge, contradiction, or index notes until `/llmzk-write-approved` is run on that review file.
