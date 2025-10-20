# Python M-V-C/P Desktop Design Guide

1. Architectural Principles (M-V-C/P Focus)
Architectural Principles (M-V-C/P Focus)
Separation of Concerns: Strictly adhere to an Model-View-Controller (MVC) or Model-View-Presenter (MVP) pattern.
- Model: All database interaction (SQLAlchemy models/sessions) and business logic must be isolated from the GUI code.
- View: PySide/PyQt widgets should handle only the presentation. Views must not contain direct database access logic, it should emit signals for all user actions.
- Controller/Presenter: Logic for connecting the View's events to the Model's functions should be in dedicated controller classes.
- Initialization: The application entry point (main.py) must correctly initialize the GUI, the SQLAlchemy engine/session, and the controller layers.
- Application Logic and Event Handling. Acts as the intermediary. Receives signals from the View, calls appropriate methods in the Model, and updates the View based on Model changes
- Use object-oriented programming for model architectures, applying SOLID principles, and functional programming for data processing pipelines.

2. GUI Guidelines (PySide6)
- Standard Widgets: Prefer standard PySide widgets (e.g., QMainWindow, QDialog, QPushButton, QTableView) for a native Windows look.
- Signal/Slot: Use the PySide Signal/Slot mechanism to connect UI events to Controller methods. Avoid tightly coupling widgets to business logic.
- Data Display: Use QTableView with a custom QAbstractTableModel for displaying database query results, ensuring efficient and reactive data binding.
- Resource Management: Ensure all resources, especially database connections, are managed properly during application shutdown.

3. Database, ORM, and Serialization Guidelines
### Database (SQLite + SQLAlchemy)
- File Location: The SQLite database file (.db) must be stored in a cross-platform location (e.g., the user's application data folder) or bundled as a data file in the PyInstaller build process. DO NOT hardcode the path.
- Session Management: Use SQLAlchemy's Sessionmaker to manage database sessions. Every block of database code (e.g., a query or an update) should use a session in a try...finally block to ensure it is correctly closed or rolled back and a context manager.
- Transactions: Wrap data modification operations (INSERT, UPDATE, DELETE) within explicit transactions to maintain data integrity.
- Initial Data: Include a function to check if the database file exists; if not, create it and populate it with initial schema/data using SQLAlchemy's Base.metadata.create_all(engine).
- Make explicit relations and models to prevent circular dependencies.

### Serialization (Marshmallow)
- Schema Organization: All schemas must be organized in a `schemas` module, with clear separation between model schemas and specialized schemas.
- Inheritance: Use a base schema class that provides common functionality (e.g., safe loading, error handling).
- Validation Rules: 
  - Define all validation rules in schema classes, not models
  - Use marshmallow's built-in validators where possible
  - Create custom validators for complex business rules
  - Include clear error messages for all validation failures
- Type Safety:
  - Use strict type checking and coercion
  - Handle date/time fields consistently with proper formats
  - Support UUID fields with proper serialization
- Error Handling:
  - Provide both strict and relaxed validation modes
  - Use custom error messages that are user-friendly
  - Handle nested validation errors properly
- Performance:
  - Cache schema instances where appropriate
  - Use schema-level options to optimize serialization
  - Consider partial loading for large datasets
- Make explicit relations and models to prevent circular dependencies.

4. Packaging and Distribution
- PyInstaller Spec: When generating the build command or spec file (.spec), ensure the SQLite database file and any PySide/Qt plugins are correctly included using the --add-data or datas= array in the spec file.
- Rule: The PyInstaller command should always use the --onefile flag for a single executable and must explicitly include the application icon.
- Final Installer: The generated code should be ready to be bundled by an external installer tool (like Inno Setup), which will place the single exe and the blank/initial database.db file in the correct installation directory.

5. Error Handling and Exceptions
- Specific Exceptions: Always use and catch specific, built-in exception types (e.g., `FileNotFoundError`, `ValueError`). Never use a bare `except:`.
- If necessary create new custom Exceptions.
- Exception Context: When catching an exception, use `raise ... from ...` to preserve the original traceback context if the exception is re-raised or converted.
- Controller Boundary: The Controller is the primary layer for translating exceptions (e.g., an `SQLAlchemyError` from the Model) into user-friendly messages for the View.
- Resource Cleanup: Use `try...finally` or context managers (`with`) for operations that require guaranteed resource cleanup (e.g., file handles, database connections).
- Handle missing data appropriately (imputation, removal, or flagging).
- Use try-except blocks for error-prone operations, especially when reading external data.
- Validate data types and ranges to ensure data integrity.

6. Logging and Observability
- Log Source: Utilize the built-in `logging` module exclusively. Configure a consistent log format with timestamps and module names.
- Log Levels: Use appropriate log levels:
    - `DEBUG`: Detailed information, typically only of interest when diagnosing problems.
    - `INFO`: Confirmation that things are working as expected.
    - `WARNING`: An indication that something unexpected happened, or indicative of some problem in the near future (e.g., 'DB path not found, using default').
    - `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
    - `CRITICAL`: A serious error, indicating the program itself may be unable to continue running.
- No `print()`: Absolutely no use of `print()` statements for application output or debugging (S504).
- Sensitive Data: Never log sensitive information (e.g., user passwords, API keys) at any log level.
- Traceability: Include relevant IDs (e.g., a card ID, a session ID) in log messages to improve traceability during debugging.
- Include a small context in the logs, like timestamps, function, module, operation, etc.

7. Testing Guide (Pytest, pytest-qt, pytest-cov)
- Framework: All tests must use pytest fixtures and standard assertion style. Test files must be named `test_*.py`.
- Make a test file for each new module.
- Group several small related tests of the same function or method into a single bigger one.
- Unit Testing (Model):
    - Focus: The Model (business logic, scheduling, data services) must be unit-tested independently of the GUI.
    - Isolation: Use Mocks or in-memory SQLite instances to ensure tests are fast, reliable, and isolated from external dependencies.
- Integration Testing (View/Controller):
    - GUI Testing: Use pytest-qt fixtures (e.g., `qtbot`, `qapp`) for simulating user interactions with PySide6 widgets.
    - Flow: Test the entire flow from a View signal emission through the Controller, into the Model, and back to the View update.
- Coverage: Aim for high code coverage (90%+) using pytest-cov. Copilot should prioritize writing tests for complex logic and critical paths.
- Fixtures: Prefer the use of concise, reusable pytest fixtures and conftest for setting up test data, database sessions, and PySide6 widgets.
- Always when patching use context manager.

8. Security and Vulnerabilities
- SQL Injection Prevention: Always use parameterized queries via SQLAlchemy ORM methods (e.g., `.filter_by()`, `.where()`) and never construct SQL query strings using f-strings or string concatenation with user input.
- Input Validation: Perform strict validation and sanitization of all external input, especially during the Import/Export process. Assume all external data is hostile.
- XSS/HTML Sanitization (PySide6): When accepting user text that might be displayed in a rich text widget (e.g., card content), sanitize the input to prevent any form of Cross-Site Scripting (XSS) if HTML rendering is enabled.
- Path Traversal: When handling file paths (e.g., for import/export), use functions like `os.path.abspath` and `os.path.normpath` and check against a safe base directory to prevent directory traversal attacks.
- Sensitive Data Storage: Given the SQLite DB is local, ensure the database file permissions are set correctly on installation (though the primary protection is OS-level).

9. Performance Guide
- SQLAlchemy Efficiency:
    - Selectinloading: Use `selectinload` or other appropriate relationship loading strategies to prevent the N+1 problem during data retrieval.
    - Bulk Operations: For import/export and mass updates, prefer SQLAlchemy's bulk insert/update methods over iterating and saving individual objects.
- Vectorized Operations: For algorithms like weighted selection (in the Model), prefer Python built-ins or optimized libraries (if needed) over inefficient, explicit Python loops.
- PySide6 Rendering: Avoid triggering unnecessary expensive layout recalculations or repaints in the View. Batch updates when possible.
- Thread Safety: Ensure any long-running or blocking operations (e.g., large database imports, complex scheduling calculations) are executed off the main GUI thread (using `QThreadPool` or Python's `threading`/`multiprocessing`) to keep the UI responsive.
- Utilize efficient data structures (e.g., categorical data types for low-cardinality string columns).
