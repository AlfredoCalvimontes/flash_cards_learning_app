# Code Review Guide

- Security Vetting: Specifically check Model and Controller logic for SQL Injection risks (ensure only ORM parameterized queries are used). Validate that all external inputs (e.g., import/export data) are sanitized.
- Architectural Integrity (MVC): Ensure strict separation: Views only emit signals; Models only handle data/logic and are GUI-agnostic; Controllers mediate. No database access is allowed in View code.
- Performance: Review SQLAlchemy code for the N+1 problem (look for missing selectinload). Flag any explicit Python loops that could be replaced by more efficient vectorized operations or bulk database methods.
- Error Handling: Verify that all error-prone code (file I/O, database calls) uses specific exception handling and appropriate logging levels (ERROR, CRITICAL). Bare except: statements are forbidden.
- Testing: Confirm that new or modified code is accompanied by unit tests (for Model logic) or integration tests (for Controller/View flow) that leverage pytest and pytest-qt.
- Clarity and Documentation: Ensure all public classes, methods, and functions have clear, concise docstrings and meaningful variable names. Complex or "clever" logic must be explained with comments.
