# Self-Healing Technical Documentation

An AI-powered documentation maintenance system designed to identify potentially outdated technical documentation when source code changes and, eventually, propose validated documentation updates.

The long-term goal is to build a reusable Docker-based GitHub Action that analyzes code changes, identifies affected documentation, uses a large language model to evaluate potential inconsistencies, and proposes safe documentation fixes.

> **Project status:** In development. Python source analysis, Markdown parsing, basic symbol matching, documentation coverage reporting, and a Gemini client have been implemented. Git-based change detection, AI-powered stale-documentation detection, automated repairs, and GitHub Action integration are planned.

## Table of Contents

- [Problem Statement](#problem-statement)
- [Project Objectives](#project-objectives)
- [How It Will Work](#how-it-will-work)
- [Technology Stack](#technology-stack)
- [Current Implementation](#current-implementation)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Security Considerations](#security-considerations)

## Problem Statement

Technical documentation frequently becomes outdated when developers modify source code without updating the corresponding documentation.

Examples include:

- A function's behavior changes, but its description remains unchanged.
- Function parameters or return values change without corresponding documentation updates.
- New functions or classes are introduced without documentation.
- Existing documentation describes behavior that no longer matches the implementation.

Manually identifying these inconsistencies becomes increasingly difficult as a project grows.

This project aims to automate documentation maintenance by connecting source-code analysis, documentation parsing, change detection, and AI-assisted validation.

## Project Objectives

The project aims to:

1. Analyze Python source files to extract functions, classes, signatures, docstrings, and source locations.
2. Parse Markdown documentation into structured sections.
3. Match source-code symbols to relevant documentation sections.
4. Generate reports identifying documented and undocumented symbols.
5. Detect source-code changes using Git.
6. Identify documentation potentially affected by those changes.
7. Use Gemini to evaluate whether existing documentation accurately describes the current implementation.
8. Generate proposed documentation corrections.
9. Validate proposed changes before accepting them.
10. Package the solution as a reusable Docker-based GitHub Action.
11. Support safe reporting or creation of a separate documentation-fix pull request.

Objectives 5–11 are planned capabilities and are not yet implemented.

## How It Will Work

The intended workflow is:

```text
Source Code Changes
        |
        v
Git Change Detection
        |
        v
Python Source Analysis
        |
        v
Identify Affected Symbols
        |
        v
Match Symbols to Markdown Sections
        |
        v
Evaluate Documentation with Gemini
        |
        v
Generate Proposed Documentation Updates
        |
        v
Validate Proposed Changes
        |
        v
Report Findings or Propose a Separate PR
```

The final GitHub Action is intended to run automatically when relevant source files change.

The current implementation covers foundational analysis and matching components. The complete workflow above represents the intended architecture, not a fully operational pipeline.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Core implementation |
| Python `ast` module | Structural analysis of Python source code |
| Regular expressions | Initial Markdown heading and code-fence recognition |
| Gemini API | Planned AI-assisted stale-documentation analysis |
| `google-genai` | Gemini Python SDK |
| `python-dotenv` | Local environment-variable configuration |
| `pytest` | Automated testing |
| Git | Planned source-code change detection |
| Docker | Planned portable execution environment |
| GitHub Actions | Planned CI/CD integration |

## Current Implementation

### 1. Gemini Client

**Location:** `src/ai/llm_client.py`

The Gemini client:

- Initializes the Google GenAI client.
- Reads the model and API key from configuration.
- Sends text prompts to the configured Gemini model.
- Returns generated text.
- Rejects empty prompts.
- Raises an error if the model returns no text.
- Configures an HTTP timeout.

The client has unit tests using mocked responses. A live Gemini API request was also tested during development. Normal unit tests use mocks to avoid unnecessary API calls, latency, and costs.

### 2. Configuration Management

**Location:** `src/config.py`

Configuration is loaded from environment variables, using a local `.env` file during development.

Required settings:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`

The API key must remain private and must not be committed to version control.

### 3. Python Source Analyzer

**Location:** `src/analyzers/python_analyzer.py`

The analyzer uses Python's built-in Abstract Syntax Tree (AST) module to extract:

- Functions and asynchronous functions.
- Classes.
- Methods and nested symbols.
- Function parameters and signatures.
- Parameter and return annotations.
- Default parameter values.
- Decorators.
- Docstrings.
- Source line numbers.
- Qualified symbol names.

### 4. Markdown Parser

**Location:** `src/parsers/markdown_parser.py`

The parser extracts Markdown sections and their metadata:

- Heading text.
- Heading level.
- Source line number.
- Heading hierarchy.
- Section content.

It also ignores Markdown-style headings inside fenced code blocks.

### 5. Documentation Matcher

**Location:** `src/matching/documentation_matcher.py`

The matcher connects Python functions and classes to Markdown sections using heading names. Candidate matches include the Python symbol, its qualified name and type, source line, matching heading, heading hierarchy, and documentation content.

Matching currently relies on exact heading names. Semantic matching and broader documentation relationships are not implemented.

### 6. Documentation Coverage Reporter

**Location:** `src/reporting/coverage_report.py`

The reporter produces a structured report containing:

- Total Python symbols analyzed.
- Number of symbols with matching documentation headings.
- Number of symbols without matching headings.
- Documentation coverage percentage.
- Lists of documented and undocumented symbols.

**Important:** A matching heading does not guarantee that its description is correct or current. This report measures basic heading-based coverage, not semantic documentation accuracy.

## Project Structure

The current project structure is organized as follows:

```text
self-healing-docs/
|-- .env
|-- .env.example
|-- .gitignore
|-- README.md
|-- requirements.txt
|
|-- src/
|   |-- __init__.py
|   |-- config.py
|   |
|   |-- ai/
|   |   |-- __init__.py
|   |   `-- llm_client.py
|   |
|   |-- analyzers/
|   |   |-- __init__.py
|   |   `-- python_analyzer.py
|   |
|   |-- parsers/
|   |   |-- __init__.py
|   |   `-- markdown_parser.py
|   |
|   |-- matching/
|   |   |-- __init__.py
|   |   `-- documentation_matcher.py
|   |
|   `-- reporting/
|       |-- __init__.py
|       `-- coverage_report.py
|
`-- tests/
    |-- fixtures/
    |   |-- sample_module.py
    |   |-- sample_docs.md
    |   |-- matcher_example.py
    |   `-- matcher_example.md
    |
    |-- test_gemini_client.py
    |-- test_python_analyzer.py
    |-- test_markdown_parser.py
    |-- test_documentation_matcher.py
    `-- test_coverage_report.py
```

This reflects the files created so far; the repository may contain additional local files.

## Getting Started

### Prerequisites

- Python 3.11 or a compatible Python version.
- A Gemini API key for live Gemini requests.
- Git, once Git-based change detection is implemented.

### 1. Clone the repository

After pushing the project to a remote Git repository:

```bash
git clone <your-repository-url>
cd self-healing-docs
```

Replace `<your-repository-url>` with your actual repository URL.

### 2. Create a virtual environment

**Windows Command Prompt:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```cmd
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

Use the model identifier supported by your Gemini API account. The value above reflects the model configured during development; model availability can change.

Never publish your real API key in this README or commit it to Git.

### 5. Run the tests

```cmd
python -m pytest -v
```

## Configuration

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | API key used to authenticate with Gemini |
| `GEMINI_MODEL` | Gemini model identifier |

The `.env.example` file should contain placeholder values only. The actual `.env` file must remain excluded from version control.

## Running Tests

Run the complete test suite:

```cmd
python -m pytest -v
```

Run individual component tests:

```cmd
python -m pytest tests/test_gemini_client.py -v
python -m pytest tests/test_python_analyzer.py -v
python -m pytest tests/test_markdown_parser.py -v
python -m pytest tests/test_documentation_matcher.py -v
python -m pytest tests/test_coverage_report.py -v
```

Gemini unit tests use mocked API responses and do not require a live API call.

The latest reported full test run had 17 passing tests. Run the suite locally to confirm the current result after changes.

## Current Limitations

- Git-based change detection is not implemented.
- The system does not yet identify which symbols changed between revisions.
- Documentation matching currently relies on exact heading names.
- Documentation coverage does not establish semantic accuracy.
- Gemini is not yet integrated into an end-to-end stale-documentation detection pipeline.
- Automated documentation repairs have not been implemented.
- Proposed changes are not yet validated against source behavior.
- Docker packaging is not implemented.
- GitHub Action integration is not implemented.
- Automated pull-request creation is not implemented.

These limitations define the next stages of development.

## Roadmap

### Phase 1: Foundational Components

- [x] Set up the Python project and virtual environment.
- [x] Configure the Gemini client.
- [x] Implement Python source analysis.
- [x] Implement Markdown parsing.
- [x] Implement basic symbol-to-documentation matching.
- [x] Implement documentation coverage reporting.
- [x] Add automated tests for implemented components.

### Phase 2: Git Change Detection

- [ ] Identify changed files between Git revisions.
- [ ] Filter relevant source-code changes.
- [ ] Handle added, modified, renamed, and deleted files appropriately.
- [ ] Add tests using controlled Git repositories or fixtures.

### Phase 3: Affected Documentation Detection

- [ ] Identify affected Python symbols.
- [ ] Map changed symbols to documentation sections.
- [ ] Improve matching for methods, qualified names, and nested sections.
- [ ] Report documentation sections requiring review.

### Phase 4: AI-Assisted Staleness Analysis

- [ ] Design structured prompts for Gemini.
- [ ] Compare source behavior with existing documentation.
- [ ] Identify potentially stale, incomplete, or contradictory descriptions.
- [ ] Return structured findings with reasons and confidence information.
- [ ] Add tests using mocked model responses.
- [ ] Add error handling and API usage limits.

### Phase 5: Documentation Repair and Validation

- [ ] Generate proposed Markdown changes.
- [ ] Restrict modifications to relevant documentation sections.
- [ ] Validate Markdown syntax and structural integrity.
- [ ] Review diffs to ensure unrelated content is preserved.
- [ ] Test invalid, incomplete, and unsafe proposed changes.

### Phase 6: Docker and GitHub Actions

- [ ] Create a Dockerfile.
- [ ] Implement the GitHub Action entry point.
- [ ] Configure required permissions and secrets.
- [ ] Support report-only mode.
- [ ] Add safe handling of pull-request events.
- [ ] Optionally propose fixes through a separate pull request.
- [ ] Document installation and usage for other repositories.

### Phase 7: End-to-End Testing

- [ ] Test against a repository containing intentionally stale documentation.
- [ ] Verify unrelated documentation is not modified.
- [ ] Test API failures and malformed model responses.
- [ ] Test security boundaries and permission restrictions.
- [ ] Document known limitations and operational requirements.

## Security Considerations

The intended GitHub Action will process source code and documentation that may contain untrusted content.

Security principles include:

- Never commit API keys, tokens, or other secrets.
- Use least-privilege GitHub token permissions.
- Treat source code, Markdown files, and pull-request content as untrusted input.
- Do not allow documentation content to override system instructions or security constraints.
- Validate AI-generated changes before applying them.
- Avoid executing analyzed source code.
- Avoid exposing secrets in logs, prompts, or generated reports.
- Do not grant privileged write access to workflows processing untrusted pull-request code.
- Prefer report-only execution initially.
- Use a separate, appropriately secured workflow for automated pull-request creation.

These controls must be implemented and tested as the project progresses.

## Contributing

The project is under active development. Development follows an incremental approach:

1. Implement one component.
2. Add or update automated tests.
3. Run the relevant tests.
4. Verify the full test suite at important milestones.
5. Update this README to reflect actual behavior.
6. Proceed to the next component.

Features should be marked complete only after implementation and testing.

## License

No license has been selected yet. Add an appropriate license before distributing the project publicly.
