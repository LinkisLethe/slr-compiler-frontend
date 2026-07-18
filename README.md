# SLR compiler front end

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white&style=flat-square)](https://www.python.org/)
[![Parser](https://img.shields.io/badge/Parser-SLR-6A5ACD?style=flat-square)](https://en.wikipedia.org/wiki/Simple_LR_parser)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[中文说明](README.zh-CN.md)

A standard-library Python compiler front end for a small typed expression language. It tokenizes source files, parses them with an external SLR table, performs semantic and type checks, and writes lexer, parse-tree, typed-tree, and AST results as JSON.

## Run

Python 3.10 or newer is required. No third-party packages are needed.

```bash
python main.py examples/ultra.math
```

The command writes four files beside the input: `*_lexer.json`, `*_parse.json`, `*_type.json`, and `*_ast.json`.

Run the regression tests with:

```bash
python -m unittest discover -s tests -v
```

## Capabilities

- Recognizes keywords, literals, identifiers, punctuation, arithmetic and relational operators.
- Uses the checked-in Level 4 grammar and SLR parsing table instead of hard-coded parser actions.
- Tracks variable and function types through a symbol table and reports lexical, syntax, or type errors by phase.
- Builds parse trees, typed parse trees, and simplified AST forests.
- Handles multi-argument, partial, and recursive function calls in the included full-language example.

The `examples/expected` files are the verified reference outputs for `bpt1.math`. The larger `ultra.math` example exercises declarations, branching, recursion, partial application, and integer division.

## Provenance and limits

The compiler was completed for COMP3173 Compiler Principles in December 2025. Stable resource paths, UTF-8 output, automated tests, CI, and documentation were added in July 2026. The project implements front-end analysis only; it does not evaluate programs or generate target code.

Source code is available under the [MIT License](LICENSE). The course grammar and parsing table are included only as inputs required to reproduce the analyzer.
