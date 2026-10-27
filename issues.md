# Lab 5 – Issues Found and Fixed (`scholarship_system.py`)

Line numbers refer to the **original** file. Tools: Bandit (B), Pylint (P), Flake8 (F).

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | Use of `eval()` on a user-supplied formula (B307 / P W0123) – **Medium** | Security | 12, 53–55 | `calculate_merit_score` runs `eval(MERIT_FORMULA)`, and the formula comes from `input()`, so a user can type `__import__("os").system(...)` and execute arbitrary code (code injection). | Replaced `eval` with an `ast`-based evaluator that allows only numbers, `gpa`, `credits` and `+ - * /`. Anything else raises `ValueError`. `change_formula` validates the formula before accepting it. |
| 2 | Bare `except:` with `pass` (B110 – **Low**, P W0702, F E722) | Bug / Security | 35–38 | Swallows every error (even `KeyboardInterrupt`) silently, hiding corrupted or missing files. | Catch only `OSError` and `json.JSONDecodeError`, and report the problem to the user. |
| 3 | Mutable default argument `logs=[]` (P W0102) | Bug | 14 | The same list is shared across every call, so logs leak between calls. | Default to `None` and create a new list inside the function. |
| 4 | Missing input validation (not flagged by any tool) | Logic bug | 15–19 | U003 (GPA 12.5, credits −3, income −1) scores 119 and is **shortlisted**; U004 with no income is treated as income 0. | Added `validate_scores()`: GPA must be 0–10, credits ≥ 0, income present and ≥ 0. Invalid applicants are skipped with a message. |
| 5 | File opened without `with` / encoding (P R1732, W1514) | Resource leak | 29–31, 36 | `open()` + manual `close()` leaks the file handle if `write` raises. No explicit encoding. | Use `with open(..., encoding="utf-8")` and `json.dump` / `json.load`. |
| 6 | Unused imports `math`, `sys` (P W0611, F F401) | Style | 2–3 | Dead code and extra dependencies. | Removed. |
| 7 | Redefining built-in `credits` (P W0622) | Style / Bug risk | 11, 16 | Parameter shadows Python's built-in `credits`. | Renamed to `extra_credits` (the formula variable name `credits` is unchanged). |
| 8 | `global` statements (P W0603) | Design | 25, 34 | Mutable module-level state rebound via `global`. | Use `RESULTS` dict (`.clear()`/`.update()`) and a `CONFIG` dict instead of rebinding globals. |
| 9 | `== True` comparison (P C0121, F E712) | Style | 43 | Redundant comparison to a boolean. | `if record["eligible"]:` |
| 10 | Function name `printShortlist` (P C0103) | Style | 40 | Not snake_case (PEP 8). | Renamed `print_shortlist`. |
| 11 | `%` string formatting (P C0209) | Style | 21 | Old-style formatting. | f-string. |
| 12 | Missing docstrings (P C0114, C0116) | Documentation | 1, 11, 14, 24, 28, 33, 40, 46 | Module and all functions undocumented. | Added module and function docstrings. |
| 13 | Blank-line errors E302 / E305 (F) | Formatting | 11, 14, 24, 28, 33, 40, 46, 59 | PEP 8 requires two blank lines around top-level definitions. | Fixed spacing. |
| 14 | `main()` runs on import | Design | 59 | Importing the module runs the whole program. | Added `if __name__ == "__main__":` guard. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 4.69 / 10 | 10.00 / 10 |
| Bandit | 2 issues (1 Medium, 1 Low) | 0 |
| Flake8 | 12 warnings | 0 |
