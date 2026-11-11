---
title: "autopep8 --aggressive can split an f-string inside its braces — valid on Python 3.12+, a SyntaxError on the 3.11 CI"
date: 2026-11-11
category: runtime-errors
module: "tools/*.py; .github/workflows/ci.yml (Python lint on 3.11)"
problem_type: runtime_error
component: tooling
severity: medium
applies_when:
  - "running autopep8 --aggressive (or any formatter) on long f-strings to meet the 100-column lint"
  - "local Python is newer than the CI interpreter (here 3.13 locally, 3.11 in CI)"
related_components:
  - tools/nacelle64_optD_glove.py
  - .github/workflows/ci.yml
tags: [python-version, f-string, pep-701, autopep8, flake8, ci]
root_cause: "PEP 701 (Python 3.12) allows newlines inside an f-string's replacement fields; autopep8 used that freedom to wrap a long expression, and flake8 on CI's 3.11 reported E999 SyntaxError"
---

# autopep8 can split f-strings in a way only Python 3.12+ parses

## What happened

`autopep8 --aggressive --max-line-length 100` wrapped this line inside the braces:

```python
f'= {add.volume() * 1.11e-3 / 453.6:.3f} lbm ({add.volume() * 1.11e-3:.1f} g) solid'
```

The result ran locally on Python 3.13 and passed local flake8. The CI "Python lint" job runs 3.11 and
failed with `E999 SyntaxError: unterminated string literal` (PR #281, commit 03bff926).

## Rule

- Don't let a formatter wrap inside an f-string. Hoist the expression into a variable first
  (`add_v = float(add.volume())`), then keep the f-string on one line or split it into adjacent literals.
- Before pushing tool changes, byte-compile them on the CI interpreter:
  `for f in $(git ls-files 'tools/*.py'); do python3.11 -m py_compile "$f" || echo FAIL "$f"; done`
  (`/usr/bin/python3.11` is installed in the cloud container).
