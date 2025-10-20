# Commit Guide

- Format: All commit messages MUST follow the Conventional Commits specification: `<type>[optional scope]: <description>`.
- Type (Mandatory): Use one of the following lowercase types to indicate the nature of the change:
    - `feat`: A new feature or capability.
    - `fix`: A bug fix (user-facing).
    - `docs`: Documentation changes only (e.g., README, docstrings).
    - `style`: Formatting changes (whitespace, missing semicolons, etc.) that do not affect code logic.
    - `refactor`: Code restructuring/rewrites that neither fix a bug nor add a feature.
    - `perf`: A code change that improves performance.
    - `test`: Adding missing tests or correcting existing tests.
    - `chore`: Routine maintenance, tooling, or dependency updates (e.g., `chore(deps): update pyside6`).
    - `build`: Changes that affect the build system or external dependencies (e.g., `PyInstaller` config).
- Scope (Optional): Use a scope in parentheses to specify the affected area (e.g., `feat(model)`, `fix(ui)`, `test(scheduler)`).
- Description: Use the imperative, present tense ("add" not "added"). Do not capitalize the first letter and do not end with a period, do not use icons.
- Breaking Changes: If the commit introduces a non-backward-compatible change, include `BREAKING CHANGE:` in the body or footer (or append `!` to the type/scope, e.g., `feat(api)!: remove old endpoint`).
- Atomic Commits: Each commit SHOULD represent a single, isolated logical change.
