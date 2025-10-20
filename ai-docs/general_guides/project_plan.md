# Flash Cards Learning App — Project Blueprint & Code-Generation Prompts

## 1. High-Level Blueprint
1. Project setup & test environment
2. Database models & schema with tests
3. Core business logic (scheduling, selection) with unit tests
4. Error handling & logging infrastructure
5. Data backup & recovery system
6. UI foundation (PySide6, main window, sidebar) with UI tests
7. CRUD operations with integration tests
8. Scheduling UI & logic with behavioral tests
9. Import/export CSV with validation tests
10. Review log & feedback with data integrity tests
11. Settings & persistence with configuration tests
12. Security & encryption implementation
13. System tray & background operation with system tests
14. Performance optimization & monitoring
15. Packaging & installer with deployment tests


## 2. Iterative Chunks & Steps
### Chunk 1: Project Setup
- Step 1.1: Initialize Python project, create virtual environment, install dependencies (PySide6, SQLAlchemy, pytest, etc.)
- Step 1.2: Create project folder structure (`ui/`, `database/`, `core/`, `tests/`, `main.py`, `ai-docs/`)
- Step 1.3: Set up pytest configuration and write first smoke test to verify environment

### Chunk 2: Database Models & Serialization
- Step 2.1: Set up serialization infrastructure
  - Create base serialization interfaces
  - Implement JSON serializer with versioning
  - Create CSV serializer with header mapping
  - Add binary serializer with compression
- Step 2.2: Implement base models with serialization
  - Create FlashCard model with all serialization methods
  - Add Category model with serialization support
  - Write comprehensive serialization tests
- Step 2.3: Implement schedule-related models
  - Add Schedule and ScheduledEvent with serialization
  - Create Settings model with JSON support
  - Write serialization integration tests
- Step 2.4: Database initialization and migration
  - Create DB init script with serialization support
  - Add format migration utilities
  - Write comprehensive testing suite

### Chunk 3: Core Logic
- Step 3.1: Implement scheduling logic with unit tests for each rule type
- Step 3.2: Implement selection algorithm with statistical distribution tests
- Step 3.3: Implement settings persistence with integration tests
- Step 3.4: Write performance tests for selection algorithm

### Chunk 4: Error Handling & Logging
- Step 4.1: Implement multi-level logging system (file, DB, Windows Event Log)
- Step 4.2: Create error handling middleware with retry logic
- Step 4.3: Implement user notification system (toast, modal, status bar)
- Step 4.4: Add automated error reporting and analysis
- Step 4.5: Write tests for error scenarios and recovery

### Chunk 5: Data Backup & Recovery
- Step 5.1: Implement automated backup system with compression
- Step 5.2: Create backup rotation and retention logic
- Step 5.3: Implement point-in-time recovery system
- Step 5.4: Add backup verification and integrity checks
- Step 5.5: Write backup/recovery integration tests

### Chunk 6: UI Foundation
- Step 4.1: Create main window and sidebar navigation (PySide6)
- Step 4.2: Write UI component tests using pytest-qt
- Step 4.3: Wire up basic navigation between sections
- Step 4.4: Write integration tests for navigation flow

### Chunk 5: CRUD Operations
- Step 5.1: Implement Cards section with CRUD operation tests
- Step 5.2: Implement Categories section with relationship tests
- Step 5.3: Wire up activation/deactivation with state change tests
- Step 5.4: Write integration tests for card-category assignments
- Step 5.5: Create UI tests for CRUD operations

### Chunk 6: Scheduling UI & Logic
- Step 6.1: Implement scheduling UI with component tests
- Step 6.2: Wire up schedule modification with state management tests
- Step 6.3: Implement preview logic with calculation tests
- Step 6.4: Write behavioral tests for scheduling workflows
- Step 6.5: Create integration tests for schedule changes

### Chunk 7: Import/Export & Data Exchange
- Step 7.1: Enhanced import/export system
  - Implement multi-format import (CSV, JSON, Binary)
  - Add data validation and type checking
  - Create format auto-detection
  - Write format-specific tests
- Step 7.2: Error handling and logging
  - Implement detailed error reporting
  - Add partial import recovery
  - Create error aggregation system
  - Write error handling tests
- Step 7.3: Export system enhancements
  - Implement multi-format export
  - Add compression options
  - Create progress tracking
  - Write data integrity tests
- Step 7.4: Data merge and conflict resolution
  - Implement smart merge strategies
  - Add conflict detection
  - Create resolution UI
  - Write conflict handling tests
- Step 7.5: Integration and performance
  - Create end-to-end workflow tests
  - Add performance benchmarks
  - Implement batch processing
  - Write stress tests

### Chunk 8: Review Log & Feedback
- Step 8.1: Implement review log model and UI
- Step 8.2: Log user feedback (Yes/So so/No) and difficulty changes
- Step 8.3: Export review log to CSV

### Chunk 9: Settings & Persistence
- Step 9.1: Implement settings UI (scheduling defaults, selection params, theme)
- Step 9.2: Wire up settings persistence in DB
- Step 9.3: Implement export/import settings as JSON

### Chunk 10: Security Implementation
- Step 10.1: Implement database encryption system
- Step 10.2: Add secure storage for sensitive settings
- Step 10.3: Create user authentication system
- Step 10.4: Implement audit logging
- Step 10.5: Add security-focused integration tests

### Chunk 11: System Tray & Background Operation
- Step 11.1: Implement Windows autostart/service logic
- Step 11.2: Create system tray icon and menu system
- Step 11.3: Implement notification management
- Step 11.4: Add window management and hotkeys
- Step 11.5: Create background task scheduler
- Step 11.6: Implement "Do Not Disturb" mode
- Step 11.7: Add system tests for background operation

### Chunk 11: Packaging & Installer
- Step 11.1: Configure PyInstaller with build verification tests
- Step 11.2: Prepare Inno Setup script with installation tests
- Step 11.3: Create deployment tests for packaged app
- Step 11.4: Write system tests for installed application
- Step 11.5: Create QA checklist and automated test suite for deployment


## 3. Small, Actionable Steps (Example for Chunks 1–3)
### Chunk 1: Project Setup
```text
Prompt 1.1: Initialize a Python project for a Windows desktop app. Create a virtual environment and install PySide6, SQLAlchemy, pytest, pytest-qt, and pytest-cov. Output requirements.txt.

Prompt 1.2: Create the following folder structure: ui/, database/, core/, tests/, ai-docs/, and a main.py entry point. Include test directories that mirror the main project structure.

Prompt 1.3: Set up pytest.ini configuration with coverage settings and create the first smoke test in tests/test_smoke.py to verify the environment is working.
```

### Chunk 2: Database Models
```text
Prompt 2.1.1: Create database/models.py with FlashCard model and tests/database/test_flashcard.py with comprehensive unit tests.
Prompt 2.1.2: Add Category model to database/models.py and tests/database/test_category.py with relationship tests.
Prompt 2.2.1: Add Schedule and ScheduledEvent models with tests/database/test_schedule.py including rule validation tests.
Prompt 2.2.2: Add Settings model and tests/database/test_settings.py with configuration tests.
Prompt 2.3.1: Create database/init_db.py with table creation and seeding logic.
Prompt 2.3.2: Add tests/database/test_init_db.py with database initialization tests.
Prompt 2.4.1: Create tests/conftest.py with pytest fixtures for database testing.
```

### Chunk 3: Core Logic
```text
Prompt 3.1.1: Create core/scheduling.py with basic scheduling logic and tests/core/test_scheduling.py with unit tests.
Prompt 3.1.2: Add rule precedence logic with tests for each rule type and combination.
Prompt 3.1.3: Add timeframe and frequency calculations with comprehensive test cases.

Prompt 3.2.1: Create core/selection.py with weighted random selection algorithm.
Prompt 3.2.2: Add tests/core/test_selection.py with statistical distribution tests.
Prompt 3.2.3: Implement parameter adjustment with settings integration tests.

Prompt 3.3.1: Create core/settings.py with persistence logic and tests/core/test_settings.py.
Prompt 3.3.2: Add integration tests for settings storage and retrieval.

Prompt 3.4.1: Create performance test suite in tests/core/test_performance.py.
Prompt 3.4.2: Add benchmarks for selection algorithm under various loads.
```

### Chunk 4: Error Handling & Logging
```text
Prompt 4.1.1: Create core/logging.py with multi-level logging configuration.
Prompt 4.1.2: Implement file-based logging with rotation.
Prompt 4.1.3: Add database logging table and handlers.
Prompt 4.1.4: Configure Windows Event Log integration.

Prompt 4.2.1: Create core/error_handling.py with middleware class.
Prompt 4.2.2: Implement retry mechanisms for transient failures.
Prompt 4.2.3: Add transaction rollback handlers.
Prompt 4.2.4: Create error categorization and priority system.

Prompt 4.3.1: Implement ui/notifications.py for user alerts.
Prompt 4.3.2: Create toast notification system.
Prompt 4.3.3: Add modal dialog handlers for critical errors.
Prompt 4.3.4: Implement status bar update system.

Prompt 4.4.1: Create automated error analysis system.
Prompt 4.4.2: Implement error pattern detection.
Prompt 4.4.3: Add error reporting and aggregation.

Prompt 4.5.1: Write tests/core/test_error_handling.py.
Prompt 4.5.2: Create integration tests for error recovery.
Prompt 4.5.3: Add UI tests for error notifications.
```

### Chunk 5: Data Backup & Recovery
```text
Prompt 5.1.1: Create core/backup.py with backup manager class.
Prompt 5.1.2: Implement database dump functionality.
Prompt 5.1.3: Add compression handling.
Prompt 5.1.4: Create backup scheduling system.

Prompt 5.2.1: Implement backup rotation logic.
Prompt 5.2.2: Add retention policy enforcement.
Prompt 5.2.3: Create cleanup procedures for old backups.

Prompt 5.3.1: Create recovery manager class.
Prompt 5.3.2: Implement point-in-time restore functionality.
Prompt 5.3.3: Add partial restore capabilities.
Prompt 5.3.4: Create recovery verification system.

Prompt 5.4.1: Implement backup integrity checking.
Prompt 5.4.2: Add checksum verification.
Prompt 5.4.3: Create backup validation procedures.

Prompt 5.5.1: Write tests/core/test_backup.py.
Prompt 5.5.2: Create integration tests for backup/restore.
Prompt 5.5.3: Add performance tests for backup operations.
```


## 4. Further Subdivision & Iteration
- For each chunk, break steps into atomic actions (e.g., "Add field X to model Y", "Write test for function Z", "Wire up button to handler").
- Ensure each prompt builds on previous code and integrates with the project structure.
- Avoid orphaned code; always wire up new features to the UI or logic as soon as possible.
- Example for Chunk 2:
```text
Prompt 2.1.1: Add FlashCard model to database/models.py with all required fields.
Prompt 2.1.2: Add Category model to database/models.py with all required fields.
Prompt 2.2.1: Add Schedule model to database/models.py.
Prompt 2.2.2: Add ScheduledEvent model to database/models.py.
Prompt 2.2.3: Add Settings model to database/models.py.
Prompt 2.3.1: Write database/init_db.py to create all tables.
Prompt 2.3.2: Write a test to verify all tables are created.
```


## 5. Review & Right-Sizing
- Review all steps for atomicity and integration.
- Ensure no step is too large or too small; each should be implementable in a short session and move the project forward.
- Iterate on step breakdown until all are actionable and safe.


## 6. Code-Generation Prompt Series
- Each prompt is tagged as `text` and sequenced for incremental development.
- Prompts reference previous steps and files, ensuring integration.
- Example:
```text
Prompt 4.1: Implement the main window in ui/main_window.py using PySide6. Add sidebar navigation with sections: Dashboard, Cards, Categories, Schedule, Import/Export, Review Log, Settings. Wire up navigation to placeholder views.
```


### Chunk 10: Security Implementation
```text
Prompt 10.1.1: Create core/security/encryption.py for database encryption.
Prompt 10.1.2: Implement key management system.
Prompt 10.1.3: Add encrypted database connections.

Prompt 10.2.1: Create secure settings storage system.
Prompt 10.2.2: Implement encrypted config file handling.
Prompt 10.2.3: Add secure memory handling for sensitive data.

Prompt 10.3.1: Implement user authentication manager.
Prompt 10.3.2: Add password hashing and validation.
Prompt 10.3.3: Create session management system.

Prompt 10.4.1: Implement security audit logging.
Prompt 10.4.2: Add audit trail for sensitive operations.
Prompt 10.4.3: Create audit log viewer and export.

Prompt 10.5.1: Write security-focused integration tests.
Prompt 10.5.2: Add penetration testing scenarios.
Prompt 10.5.3: Create security compliance checks.
```

### Chunk 11: System Tray & Background Operation
```text
Prompt 11.1.1: Create core/service/windows_service.py for autostart.
Prompt 11.1.2: Implement service registration and management.
Prompt 11.1.3: Add service recovery procedures.

Prompt 11.2.1: Create ui/tray/tray_icon.py for system tray.
Prompt 11.2.2: Implement context menu and actions.
Prompt 11.2.3: Add status indication system.

Prompt 11.3.1: Create notification manager class.
Prompt 11.3.2: Implement toast notification system.
Prompt 11.3.3: Add notification queuing and aggregation.

Prompt 11.4.1: Implement window state management.
Prompt 11.4.2: Add global hotkey registration.
Prompt 11.4.3: Create window restoration logic.

Prompt 11.5.1: Implement background task scheduler.
Prompt 11.5.2: Add task prioritization system.
Prompt 11.5.3: Create resource usage monitoring.

Prompt 11.6.1: Implement Do Not Disturb mode.
Prompt 11.6.2: Add time-based DND scheduling.
Prompt 11.6.3: Create notification suppression logic.

Prompt 11.7.1: Write system integration tests.
Prompt 11.7.2: Add background operation tests.
Prompt 11.7.3: Create notification delivery tests.
```

## 7. Next Steps
- Use this plan to drive code-generation, implementation, and review
- Update the plan as needed for new requirements or refinements
- Monitor performance metrics during implementation
- Conduct security audits at key milestones
- Perform user acceptance testing for critical features
- Document API and integration points
- Create deployment and maintenance guides
