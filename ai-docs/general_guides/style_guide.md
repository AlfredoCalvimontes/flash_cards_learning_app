## Python Style Guide

### Core Principles
- Adherence: Strictly follow PEP 8 and pass Flake8 checks (E & W series).
- Formatting: Respect Black's formatting rules (88 characters max line length, double quotes).
- Imports: Respect isort's grouping: Future, Standard Library, Third-Party, Local/Project.
- Type Safety: Always include Mypy compatible type hints for functions/methods.
- Type Safety: Always include explicit, Mypy compatible type hints for functions/methods, attributes, and variables.
- Stack Focus: Prioritize idioms for PySide6 and modern SQLAlchemy 2.0+.

### 1. General Formatting and Layout
- Line Length: Maximum 88 characters
- Indentation: 4 spaces, no tabs
- Quotes: Use double quotes (`"`) for strings
- Trailing Commas: Use trailing commas for multiline lists, tuples, dicts, and function arguments
- Whitespace: Maintain proper PEP 8 spacing around operators and assignments
- Blank Lines: Two blank lines for top-level definitions; one blank line for class methods

### 2. Imports
- Import Structure: Group and sort imports (isort standard)
- Absolute Imports: Prefer absolute imports over relative imports
- Unused Imports: Never generate unused imports (Flake8 F401)
- Wildcard Imports: Avoid `from module import *` (Flake8 F403)

### 3. Naming Conventions
- Modules: `lowercase_with_underscores`
- Classes: `CapWords` (PascalCase) for PySide6 widgets and SQLAlchemy models
- Functions/Methods/Variables: `lowercase_with_underscores` (snake_case)
- Constants: `ALL_CAPS_WITH_UNDERSCORES`
- Arguments: Use clear, concise parameter names (`self`, `cls` mandatory)

### 4. Docstrings and Type Hinting
- Docstrings: Use triple double quotes (`"""..."""`) for all public elements. Prefer Google style or reStructuredText
- Type Hinting: Always include Mypy-compatible type hints for arguments and return values
- Class Context: Correctly use `self` for instance methods and `cls` for class methods

### 5. Specific Stack Idioms (PySide6 & SQLAlchemy)
- PySide6 Signals/Slots: Use the `QtCore.Slot` decorator for explicit slot definition
- SQLAlchemy Models: Use Declarative Base with modern Mapped types (e.g., `Mapped[str]`)
- Session Handling: Prefer context managers (`with Session(...) as session:`) for database operations
- Logging: Use the built-in `logging` module for application messages; avoid `print()`
