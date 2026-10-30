# Documentation Guide



This directory contains technical documentation for the Self-Healing Technical Documentation project.



## Python Analyzer



The Python analyzer examines Python source files and extracts information about functions, classes, method signatures, decorators, and docstrings.



## Markdown Parser



The Markdown parser extracts headings, nested heading paths, section content, and heading line numbers from Markdown files. It ignores headings inside fenced code blocks.



## Documentation Matcher



The documentation matcher compares Python function and class names with Markdown section headings to identify potential documentation matches.



## Coverage Reporter



The coverage reporter identifies documented and undocumented Python symbols and calculates documentation coverage.



## Git Change Detector



The Git change detector compares two Git references and identifies added, modified, deleted, renamed, and copied files.



## Change Mapper



The change mapper analyzes a changed Python file and searches Markdown files for sections matching its Python symbols.



## Impact Reporter



The impact reporter combines Git change detection and documentation mapping to identify potentially affected documentation. It reports matching sections, unmatched symbols, deleted Python files, and analysis errors.



## Command-Line Interface



The command-line interface runs the impact reporter and prints the results as JSON. It can optionally save the report to a JSON file.

