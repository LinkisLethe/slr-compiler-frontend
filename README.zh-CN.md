# SLR 编译器前端

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white&style=flat-square)](https://www.python.org/)
[![Parser](https://img.shields.io/badge/Parser-SLR-6A5ACD?style=flat-square)](https://en.wikipedia.org/wiki/Simple_LR_parser)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[English](README.md)

这是一个仅使用 Python 标准库实现的小型编译器前端。程序读取带类型的表达式语言，依次完成词法分析、SLR 语法分析、语义与类型检查，并将词法结果、解析树、类型树和 AST 写入 JSON 文件。

## 运行

需要 Python 3.10 或更高版本，不依赖第三方包。

```bash
python main.py examples/ultra.math
```

程序会在输入文件旁生成 `*_lexer.json`、`*_parse.json`、`*_type.json` 和 `*_ast.json`。

运行回归测试：

```bash
python -m unittest discover -s tests -v
```

## 功能

- 识别关键字、字面量、标识符、标点符号、算术运算符和关系运算符。
- 从 Level 4 文法和 SLR 分析表读取规则，不在代码中硬编码状态表。
- 通过符号表跟踪变量和函数类型，并按阶段报告词法、语法或类型错误。
- 生成解析树、带类型的解析树和简化 AST 森林。
- 完整示例覆盖多参数函数、部分调用和递归调用。

`examples/expected` 保存了 `bpt1.math` 的已核验参考输出。`ultra.math` 进一步覆盖声明、条件分支、递归、部分调用和整数除法。

## 来源与限制

该编译器完成于 2025 年 12 月的 COMP3173 Compiler Principles 课程。稳定资源路径、UTF-8 输出、自动化测试、CI 和文档整理于 2026 年 7 月补充。项目只实现编译器前端分析，不执行程序，也不生成目标代码。

源代码采用 [MIT License](LICENSE)。课程文法和分析表仅作为复现分析器所需的输入文件保留。
