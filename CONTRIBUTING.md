# AHMS Contributing Guidelines

Welcome to the Asset Health Management System (AHMS) engineering repository. To maintain code quality, security, and schema stability, all team members must adhere to the following rules:

---

## 1. Branching Strategy
- **Nobody commits directly to `main`.** The `main` branch is protected.
- Create one branch per task, strictly following the naming convention:
  ```bash
  feature/<task-name>
  ```
  *Example:* `feature/signup-view`, `feature/hhi-calculation`

---

## 2. Pull Requests & Code Reviews
- Push your feature branch and open a Pull Request (PR) targeting `main`.
- Every PR requires **at least one approving review** from a senior engineer before merging.
- PRs must have passing automated CI checks (GitHub Actions).

---

## 3. Portfolio Model Ownership
- **Only Abdul Jabbar edits `portfolio/models.py`.**
- Every model change **must include its corresponding migration file** generated via `python manage.py makemigrations`.
- Never edit existing migration files that have already been merged into `main`.

---

## 4. Testing & Validation
- **Run `pytest` locally before submitting every pull request.**
- All existing tests, including the must-pass analytics test suite, must pass with 0 failures:
  ```bash
  pytest
  ```
- Always write tests for new views, permissions, or analytics logic.

---

## 5. Security & Architectural Integrity
- All money math strictly uses `Decimal`. Never use `float` for monetary amounts.
- All calculations belong in the `analytics/` package — never in views, forms, or templates.
- Never commit secrets, passwords, tokens, or personal emails to the repository or logs.
