# Self-Healing Technical Documentation

An AI-assisted Python documentation maintenance tool that analyzes source code, parses Markdown documentation, detects Git changes, identifies potentially affected documentation, and supports structured discrepancy reports and approval-based correction proposals.

The goal is to reduce the manual effort required to keep technical documentation aligned with evolving source code.

> **Project status:** Active development. Python AST analysis, Markdown parsing, documentation matching, coverage reporting, Git change detection, documentation impact reporting, a Gemini-powered discrepancy detection pipeline, and correction-proposal utilities are implemented. The automated test suite currently passes 54 tests. Live Gemini audit reliability, broader documentation matching, stronger repair validation, Docker packaging, and GitHub Actions integration remain areas for improvement.

## Table of Contents

- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [Documentation Repair Workflow](#documentation-repair-workflow)
- [Testing](#testing)
- [Example Output](#example-output)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)

## Problem Statement

Technical documentation often becomes outdated when developers modify source code without updating the corresponding documentation.

Examples include:

- Function parameters change while documentation describes the old interface.
- A function's behavior changes but its description remains unchanged.
- New functions or classes are introduced without corresponding documentation.
- Documentation describes behavior that contradicts the implementation.
- Developers struggle to identify which documentation files may be affected by a code change.

This project explores an automated workflow that combines structural source-code analysis, documentation matching, Git change detection, and AI-assisted discrepancy detection.

## Key Features

### 1. Python Source Analysis

Uses Python's built-in Abstract Syntax Tree (AST) module to extract structured information about source-code symbols.

Extracted information includes:

- Functions and asynchronous functions.
- Classes and methods.
- Function parameters and signatures.
- Return and parameter annotations.
- Default parameter values.
- Decorators and docstrings.
- Source line numbers and qualified symbol names.

### 2. Markdown Documentation Parsing

Extracts structured Markdown sections, including:

- Heading text and heading levels.
- Source line numbers.
- Heading hierarchy.
- Section content.

The parser also avoids treating headings inside fenced code blocks as actual Markdown headings.

### 3. Documentation Matching

Matches Python symbols to candidate Markdown documentation sections using symbol names, qualified names, and configured aliases.

The results include candidate documentation sections and symbols without matching headings.

**Important:** A matching heading is evidence of a potential documentation relationship, not proof that the documentation is accurate.

### 4. Git Change Detection

Compares two Git references and identifies relevant changes, including added, modified, deleted, renamed, and copied files.

The impact-report workflow analyzes eligible added or modified Python files and reports deleted Python files separately.

### 5. Documentation Impact Reporting

Combines Git change detection with source-to-documentation mapping.

The JSON report includes:

- Base and target Git references.
- Number of changed files.
- Number of Python files analyzed.
- Documentation matches.
- Unmatched symbols.
- Deleted Python files.
- Ignored changes.
- Analysis errors.

Test files and non-Python changes are excluded from source documentation matching but remain represented in the Git change summary where applicable.

### 6. AI-Assisted Discrepancy Detection

Uses the configured Gemini model to compare structured Python source analysis with Markdown documentation.

The detector requests structured findings containing:

- Symbol name.
- Documentation heading.
- Severity.
- Description of the potential discrepancy.
- Supporting evidence.
- Suggested correction.

The response is parsed and validated before being returned by the application.

The detector is designed to avoid reporting discrepancies when the supplied evidence is insufficient. However, AI-generated findings still require human review.

### 7. Documentation Correction Proposals

The correction utility can create a proposal containing:

- The original and proposed text.
- A unified diff.
- Finding metadata.
- A SHA-256 hash of the original documentation file.
- A pending-approval status.

Applying a proposal requires explicit approval, matching file paths, and an unchanged source-file hash.

The utility also checks that the original text appears exactly once before replacing it.

**This is an approval-gated MVP, not a production-grade authorization system.** Approval is supplied by the caller, and replacement is not yet restricted to a specific Markdown section.

### 8. Automated Tests

The test suite covers source analysis, Markdown parsing, matching, Git change detection, impact reporting, discrepancy detection, pipeline behavior, and correction-proposal safeguards.

The current recorded test result is **54 passing tests**.

## Architecture

The implemented workflow is organized around the following components:

```text
                 Git Repository
                       |
                       v
                Git Change Detection
                       |
                       v
             Changed Python File Selection
                       |
                       v
                Python AST Analysis
                       |
                       v
             Documentation Symbol Matching
                       |
                       v
              Git Impact Report (JSON)


Python Source File                 Markdown Documentation
        |                                    |
        v                                    v
   AST Analysis                         Markdown Parsing
        |                                    |
        +----------------+-------------------+
                         |
                         v
                Gemini Discrepancy Detector
                         |
                         v
                Structured Findings (JSON)
                         |
                         v
               Human-Reviewed Correction
                         |
                         v
                 Approval-Gated Apply
```

The Git impact-report workflow and AI documentation-audit workflow can be invoked through the command-line interface.

The AI audit requires a working Gemini API configuration. The complete workflow has not yet been validated reliably against a live model because a development request encountered a `504 DEADLINE_EXCEEDED` error.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Core implementation |
| Python `ast` module | Structural source-code analysis |
| Regular expressions | Markdown heading and code-fence parsing |
| Gemini API | AI-assisted discrepancy detection |
| `google-genai` | Gemini Python SDK |
| `python-dotenv` | Environment-variable configuration |
| `pytest` | Automated testing |
| Git | Change detection between repository references |
| JSON | Structured analysis and impact reports |

Docker packaging and GitHub Actions integration are planned but not implemented.

## Project Structure

The principal implementation modules are organized as follows:

```text
self-healing-docs/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── docs/
│   └── documentation-guide.md
├── src/
│   ├── config.py
│   ├── ai/
│   │   ├── llm_client.py
│   │   ├── discrepancy_detector.py
│   │   ├── documentation_pipeline.py
│   │   └── documentation_repair.py
│   ├── analyzers/
│   │   └── python_analyzer.py
│   ├── git_tools/
│   │   └── change_detector.py
│   ├── mapping/
│   │   └── change_mapper.py
│   ├── matching/
│   │   └── documentation_matcher.py
│   ├── parsers/
│   │   └── markdown_parser.py
│   ├── reporting/
│   │   ├── coverage_report.py
│   │   └── impact_report.py
│   └── cli.py
├── tests/
│   ├── fixtures/
│   ├── test_discrepancy_detector.py
│   ├── test_documentation_pipeline.py
│   ├── test_documentation_repair.py
│   ├── test_impact_report.py
│   └── ...
└── reports/
    └── impact_report.json
```

This is a simplified overview of the principal modules. Additional test files and local development utilities may exist in the repository.

The `.env` file is intentionally excluded from this overview because it contains local configuration and must not be committed.

## Getting Started

### Prerequisites

- Python 3.11 or a compatible Python version.
- Git.
- A Gemini API key for live AI documentation audits.

### 1. Clone the repository

After publishing the project to a remote repository:

```cmd
git clone <your-repository-url>
cd self-healing-docs
```

Replace `<your-repository-url>` with your repository's actual URL.

### 2. Create a virtual environment

On Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```cmd
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root or copy `.env.example` and edit the copy.

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=your_supported_gemini_model_id
```

Use a model identifier supported by your Gemini API account.

Never commit your actual API key. The repository's `.gitignore` excludes `.env`.

### 5. Verify the installation

Run:

```cmd
python -m pytest -q
```

The most recent recorded run completed with 54 passing tests. Run the suite again after making changes to verify the current state of your checkout.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes for live AI calls | API key used to authenticate with Gemini |
| `GEMINI_MODEL` | Yes for live AI calls | Supported Gemini model identifier |

The application loads these values through its configuration module.

Unit tests that use mocked Gemini responses should not require a live API request.

## Usage

Run CLI commands from the project root.

### 1. Display CLI help

```cmd
python -m src.cli --help
```

### 2. Generate a Git documentation impact report

Compare the previous commit with the current commit:

```cmd
python -m src.cli --repo . --base HEAD~1 --target HEAD --docs docs --output reports\impact_report.json
```

The command compares the selected Git references, identifies changed Python files, maps their symbols to documentation, and prints a JSON report.

The report is also written to:

```text
reports/impact_report.json
```

The parent directory is created when necessary.

### 3. Run an AI documentation audit

Compare a Python source file with its Markdown documentation:

```cmd
python -m src.cli --repo . --base HEAD~1 --target HEAD --docs docs --audit-source src\analyzers\python_analyzer.py --audit-doc docs\documentation-guide.md --audit-output reports\python_analyzer_audit.json
```

This command performs the Git impact analysis and then requests an AI audit.

The audit report is intended to be written to:

```text
reports/python_analyzer_audit.json
```

Live execution depends on Gemini API availability, valid credentials, supported model configuration, and successful completion of the request. API failures are reported by the CLI.

**Note:** The audit command compares the specified files; it does not automatically audit every changed file.

### 4. Run the complete test suite

```cmd
python -m pytest -v
```

For a concise result:

```cmd
python -m pytest -q
```

### 5. Inspect the generated impact report

Open:

```text
reports/impact_report.json
```

The report contains the Git comparison, documentation matches, unmatched symbols, ignored changes, and analysis errors.

An unmatched symbol does not automatically mean the documentation is incorrect. Internal helpers and test utilities may not require their own documentation sections.

## Documentation Repair Workflow

The correction utility is designed to separate proposal generation from application.

A proposal includes the original text, replacement text, finding metadata, a diff, and a hash representing the documentation file at proposal time.

The application step checks that:

1. Explicit approval was supplied.
2. The proposal is pending approval.
3. The supplied documentation file matches the proposal's file.
4. The documentation file has not changed since the proposal was generated.
5. The original text occurs exactly once.

If a validation check fails, the correction is rejected.

These checks reduce the risk of applying an outdated or ambiguous replacement. They do not replace a proper review and authorization system, and the current implementation does not automatically validate the semantic correctness of the replacement.

## Example Output

A recorded Git impact report from development contained the following summary:

```json
{
  "documentation_matches": 2,
  "unmatched_symbols": 1,
  "deleted_python_files": 0,
  "analysis_errors": 0
}
```

These figures describe one particular comparison between Git references. They are not benchmark results or a measurement of documentation accuracy.

The unmatched symbol in that run was an internal helper function. The report correctly distinguished an unmatched symbol from an analysis error.

## Current Limitations

- Documentation matching primarily relies on symbol names, aliases, and heading text rather than a comprehensive semantic relationship model.
- A heading match does not establish that the documentation accurately describes runtime behavior.
- AI findings may be incomplete or incorrect and require human review.
- Live Gemini execution has encountered a `504 DEADLINE_EXCEEDED` error during development; successful live auditing has not yet been consistently verified.
- The audit operates on explicitly supplied source and documentation files.
- The correction utility performs text replacement rather than a section-aware Markdown edit.
- The approval flag is not a production-grade identity or authorization mechanism.
- Automated rollback, persistent approval records, and multi-user review are not implemented.
- Docker packaging is not implemented.
- GitHub Actions integration is not implemented.
- Automatic pull-request creation is not implemented.
- Large repositories, concurrent edits, and end-to-end performance have not been comprehensively benchmarked.

## Roadmap

### Phase 1: Foundational Components

- [x] Python AST analysis.
- [x] Markdown section parsing.
- [x] Symbol-to-documentation matching.
- [x] Documentation coverage reporting.
- [x] Gemini client and configuration.
- [x] Automated component tests.

### Phase 2: Git Change Detection

- [x] Compare Git references.
- [x] Detect relevant file changes.
- [x] Add tests using temporary Git repositories.

### Phase 3: Documentation Impact Analysis

- [x] Map changed Python files to candidate documentation.
- [x] Report unmatched symbols.
- [x] Generate a JSON documentation impact report.
- [x] Exclude test files from source documentation matching.

### Phase 4: AI-Assisted Discrepancy Detection

- [x] Build a structured discrepancy detector.
- [x] Validate the structure of model findings.
- [x] Integrate source analysis and Markdown parsing into an audit pipeline.
- [x] Add mocked-response tests.
- [ ] Verify successful live audits reliably.
- [ ] Improve timeout handling, retry policy, and API usage controls.
- [ ] Add confidence calibration and stronger evidence validation.

### Phase 5: Documentation Repair

- [x] Generate correction proposals.
- [x] Produce unified diffs.
- [x] Require explicit approval before applying corrections.
- [x] Check for stale documentation using a file hash.
- [ ] Restrict edits to the intended Markdown section.
- [ ] Add Markdown structural validation.
- [ ] Add stronger authorization and audit logging.
- [ ] Validate repairs against realistic stale-documentation examples.

### Phase 6: Deployment and Integration

- [ ] Package the application in Docker.
- [ ] Create a reusable GitHub Action.
- [ ] Configure least-privilege workflow permissions.
- [ ] Support report-only execution.
- [ ] Add secure pull-request integration.

### Phase 7: End-to-End Validation

- [ ] Test against intentionally stale documentation.
- [ ] Measure precision and recall against labeled examples.
- [ ] Test API failures and malformed model responses.
- [ ] Test concurrent edits and repair safeguards.
- [ ] Benchmark performance on larger repositories.

## Security Considerations

The project processes source code, Markdown content, and model-generated suggestions. These inputs must not be treated as inherently trustworthy.

Security principles include:

- Never commit API keys or other secrets.
- Treat source code, documentation, and pull-request content as untrusted input.
- Do not execute analyzed source code.
- Avoid exposing secrets in prompts, reports, or logs.
- Validate model-generated findings before using them.
- Require review before applying documentation changes.
- Use least-privilege permissions when integrating with GitHub Actions.
- Avoid granting privileged write access to workflows processing untrusted pull requests.
- Prefer report-only behavior until automated modifications have been thoroughly validated.

The existing approval and file-hash checks are useful safeguards, but they do not constitute a complete production security model.

## Contributing

Development follows an incremental process:

1. Implement a component.
2. Add or update automated tests.
3. Run the relevant tests.
4. Run the full test suite at important milestones.
5. Update the documentation to reflect actual behavior.
6. Review changes before committing.

Features should be described as complete only when their implementation and relevant validation support that claim.

## License

No license has been selected yet. Add an appropriate license before distributing the project publicly.