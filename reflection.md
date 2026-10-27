# Lab 5 – Reflection

**1. Which issues were the easiest and which were the hardest to fix?**
The easiest were the mechanical ones: removing unused imports, renaming `printShortlist`, replacing `== True`, adding docstrings and fixing blank lines. The hardest was `eval()`. Simply deleting it would break the "change the formula" feature, so I had to write a small `ast`-based evaluator that keeps the feature but only permits numbers, `gpa`, `credits` and basic arithmetic. The input-validation bug was also hard because no tool reported it; I only found it by running the program and noticing that U003 (GPA 12.5, credits −3, income −1) was shortlisted.

**2. Did the tools report any false positives or unhelpful suggestions?**
Pylint reported "unused argument" for `gpa` and `credits` in `calculate_merit_score`. This is a false positive caused by `eval`: the arguments were used, but only through names inside a string. Bandit's B307 message suggests `ast.literal_eval`, which cannot evaluate expressions like `gpa * 10 + credits * 2`, so that suggestion did not apply directly and a custom safe evaluator was needed.

**3. How would you integrate static analysis into a real development workflow?**
Run Flake8 and Pylint as a pre-commit hook so style and quality problems are caught before code is committed, and run Pylint, Flake8 and Bandit in a CI pipeline (for example GitHub Actions) on every pull request, failing the build on Bandit Medium/High findings or a Pylint score below a threshold. Editors can also run them live while coding.

**4. What tangible improvements did you see after fixing the issues?**
Pylint went from 4.69 to 10.00, Bandit from 2 findings to 0, and Flake8 from 12 warnings to 0. More importantly, the code is safer (no arbitrary code execution through the formula), more robust (invalid applicants are rejected, errors are no longer silently swallowed, files are closed properly), easier to read and test (docstrings, snake_case names, no globals, `main()` guard), and the wrong shortlist result for U003 is gone.
