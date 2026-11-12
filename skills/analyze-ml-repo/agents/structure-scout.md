# Structure Scout — Project Structure Analysis

Agent that maps the overall structure, entry points, and execution
flow of an ML project.

## Procedure

### 1. Map the directory structure

Summarize the main directories and the role of each. Include file
counts and key file names.

### 2. Analyze entry points

Read `__main__.py` or the entry-point files:
- List of CLI commands
- The Job/Runner class each command invokes
- Dependencies between commands

### 3. Catalog the config files

Start from the reconnaissance config summary in your prompt; read the
config files only to fill gaps, not from scratch. Produce:
- All hyperparameters and their defaults, as a table
- Grouped by category (model, training, data, ...)

### 4. Summarize README/docs

- Project overview
- Architecture description
- Extract term definitions

### 5. End-to-end container diagram

Draw the full flow — data preparation -> training -> inference ->
output — as a C4 container diagram. **You own the whole-system
top-level diagram** (the final document's "End-to-end workflow"
section). The inference-analyst draws the component diagram of the
inference container; do not overlap.

Follow rule D1 (system diagrams) and the C4 rules from the diagram
rules included in your prompt when drawing diagrams.

## Output rules

Beyond the report contract in your prompt:

- Every diagram must annotate tensor shapes.
